"""
Adaptive model routing for BRD Forge.

The router chooses a model by task purpose, modality, input length, and risk.
It also returns human-readable reasons so the decision can be shown in demos.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

import config


@dataclass
class ModelRoute:
    provider: str
    purpose: str
    modality: str
    model: str
    tier: str
    complexity: str
    estimated_tokens: int
    reasons: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


HIGH_RISK_TERMS = (
    "compliance",
    "pci",
    "hipaa",
    "gdpr",
    "sox",
    "security",
    "encryption",
    "audit",
    "regulatory",
    "bank",
    "payment",
    "medical",
    "health",
    "identity",
    "authentication",
    "contradiction",
    "conflict",
    "must not",
    "only",
)


def estimate_tokens(text: str) -> int:
    """Fast approximation good enough for routing decisions."""
    return max(1, len(text or "") // 4)


def route_model(
    *,
    purpose: str,
    modality: str,
    text: str = "",
    input_count: int = 1,
    has_image: bool = False,
) -> ModelRoute:
    estimated_tokens = estimate_tokens(text)
    lowered = (text or "").lower()
    reasons: List[str] = []
    provider = config.AI_PROVIDER
    fast_model = config.OPENAI_FAST_MODEL if provider == "openai" else config.GEMINI_FAST_MODEL
    advanced_model = config.OPENAI_ADVANCED_MODEL if provider == "openai" else config.GEMINI_ADVANCED_MODEL
    vision_model = config.OPENAI_VISION_MODEL if provider == "openai" else config.GEMINI_VISION_MODEL

    risk_hits = sorted({term for term in HIGH_RISK_TERMS if term in lowered})
    if risk_hits:
        reasons.append(f"Risk/compliance language detected: {', '.join(risk_hits[:4])}")

    if input_count > 1:
        reasons.append(f"Multi-source synthesis required across {input_count} inputs")

    if has_image or modality == "image":
        reasons.append("Visual or wireframe input requires multimodal understanding")
        return ModelRoute(
            provider=provider,
            purpose=purpose,
            modality=modality,
            model=vision_model,
            tier="multimodal",
            complexity="advanced",
            estimated_tokens=estimated_tokens,
            reasons=reasons,
        )

    if purpose in {"synthesis", "conflict_detection"}:
        reasons.append(f"{purpose.replace('_', ' ').title()} needs cross-requirement reasoning")
        return ModelRoute(
            provider=provider,
            purpose=purpose,
            modality=modality,
            model=advanced_model,
            tier="advanced_reasoning",
            complexity="advanced",
            estimated_tokens=estimated_tokens,
            reasons=reasons,
        )

    if estimated_tokens >= config.MODEL_ROUTER_ADVANCED_TOKEN_THRESHOLD:
        reasons.append(f"Long input estimated at {estimated_tokens} tokens")
        return ModelRoute(
            provider=provider,
            purpose=purpose,
            modality=modality,
            model=advanced_model,
            tier="advanced_reasoning",
            complexity="advanced",
            estimated_tokens=estimated_tokens,
            reasons=reasons,
        )

    if risk_hits and estimated_tokens >= config.MODEL_ROUTER_RISK_TOKEN_THRESHOLD:
        reasons.append("Risk-sensitive medium document escalated for accuracy")
        return ModelRoute(
            provider=provider,
            purpose=purpose,
            modality=modality,
            model=advanced_model,
            tier="advanced_reasoning",
            complexity="medium",
            estimated_tokens=estimated_tokens,
            reasons=reasons,
        )

    reasons.append("Short/simple extraction can use low-latency model")
    return ModelRoute(
        provider=provider,
        purpose=purpose,
        modality=modality,
        model=fast_model,
        tier="fast_extraction",
        complexity="basic",
        estimated_tokens=estimated_tokens,
        reasons=reasons,
    )


def summarize_routes(routes: List[Dict[str, Any]]) -> Dict[str, Any]:
    models = sorted({r.get("model") for r in routes if r.get("model")})
    tiers = sorted({r.get("tier") for r in routes if r.get("tier")})
    advanced_count = sum(1 for r in routes if r.get("complexity") == "advanced")
    provider_label = "OpenAI" if config.AI_PROVIDER == "openai" else "Gemini"
    return {
        "adaptive_model_routing": True,
        "primary_provider": config.AI_PROVIDER,
        "models_used": models,
        "tiers_used": tiers,
        "advanced_decisions": advanced_count,
        "total_decisions": len(routes),
        "strategy": (
            f"Route short text to a fast {provider_label} model, route long documents, "
            "multi-source synthesis, multimodal inputs, and conflict reasoning "
            f"to advanced {provider_label} models."
        ),
    }
