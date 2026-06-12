import io
import pandas as pd
from typing import Dict, Any

def export_to_excel(brd_data: Dict[str, Any]) -> bytes:
    """
    Export the Functional and Non-Functional requirements of a BRD to an Excel workbook.
    Returns the binary bytes of the generated spreadsheet.
    """
    fr_list = brd_data.get("functional_requirements", [])
    nfr_list = brd_data.get("non_functional_requirements", [])
    
    # 1. Prepare Functional Requirements Data
    fr_records = []
    for fr in fr_list:
        fr_records.append({
            "Requirement ID": fr.get("id", ""),
            "Title": fr.get("title", ""),
            "Description": fr.get("description", ""),
            "Source Document": fr.get("source", ""),
            "Priority": fr.get("priority", "MUST HAVE"),
            "Confidence Level": fr.get("confidence", "HIGH"),
            "Logical Conflict": "YES: " + fr.get("conflict") if fr.get("conflict") else "NO"
        })
        
    df_fr = pd.DataFrame(fr_records)
    if df_fr.empty:
        df_fr = pd.DataFrame(columns=[
            "Requirement ID", "Title", "Description", "Source Document", "Priority", "Confidence Level", "Logical Conflict"
        ])
        
    # 2. Prepare Non-Functional Requirements Data
    nfr_records = []
    for nfr in nfr_list:
        nfr_records.append({
            "Requirement ID": nfr.get("id", ""),
            "Title": nfr.get("title", ""),
            "Description": nfr.get("description", ""),
            "Source Document": nfr.get("source", ""),
            "Confidence Level": nfr.get("confidence", "HIGH")
        })
        
    df_nfr = pd.DataFrame(nfr_records)
    if df_nfr.empty:
        df_nfr = pd.DataFrame(columns=[
            "Requirement ID", "Title", "Description", "Source Document", "Confidence Level"
        ])
        
    # 3. Write DataFrames into Excel sheet in memory
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_fr.to_excel(writer, sheet_name='Functional Specs', index=False)
        df_nfr.to_excel(writer, sheet_name='Non-Functional Specs', index=False)
        
        # Access openpyxl objects to auto-adjust column widths
        workbook = writer.book
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            # Autofit column widths
            for col in worksheet.columns:
                max_len = 0
                col_letter = col[0].column_letter
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                # Constrain width between 10 and 50
                worksheet.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 50)
                
    excel_bytes = excel_buffer.getvalue()
    excel_buffer.close()
    return excel_bytes
