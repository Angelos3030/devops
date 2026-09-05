# SiteEditingModel interface and DeepSeek implementation
from __future__ import annotations

import abc
import json
import time
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import requests

from src import config as cfg
from src import ai

class Operation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    op: str = Field(..., description="The name of the operation")
    params: Dict[str, Any] = Field(..., description="The parameters for the operation")

class EditPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field("1.0", description="Strict version must be 1.0")
    intent: str = Field(..., description="The overall intent of the edit")
    operations: List[Operation] = Field(..., description="List of operations to execute")
    explanation: str = Field(..., description="concise explanation in Greek describing the changes")
    requires_confirmation: bool = Field(False, description="Whether this edit requires user confirmation")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != "1.0":
            raise ValueError("unsupported edit schema version")
        return value

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return value

class SiteEditingModel(abc.ABC):
    @abc.abstractmethod
    def plan_edit(self, context: Dict[str, Any], message: str) -> Optional[EditPlan]:
        """Plan edits based on context and user message."""
        pass

# The structured output tool definition compatible with DeepSeek / OpenAI API
EDIT_SITE_TOOL = {
    "type": "function",
    "function": {
        "name": "edit_site",
        "description": "Plan structured edits to the user's business website.",
        "parameters": {
            "type": "object",
            "properties": {
                "schema_version": {
                    "type": "string",
                    "enum": ["1.0"]
                },
                "intent": {
                    "type": "string",
                    "description": "Short description of what the user wants to do, e.g. update_phone_number"
                },
                "explanation": {
                    "type": "string",
                    "description": "A concise, natural Greek response summarizing what you changed or why you need confirmation."
                },
                "requires_confirmation": {
                    "type": "boolean",
                    "description": "True if changing template or deleting significant content, otherwise False."
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score of the mapping, from 0.0 to 1.0."
                },
                "operations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "op": {
                                "type": "string",
                                "enum": [
                                    "update_business_field",
                                    "update_hours",
                                    "update_phone",
                                    "update_service",
                                    "reorder_media",
                                    "set_palette"
                                ]
                            },
                            "params": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "field": {
                                        "type": "string",
                                        "enum": [
                                            "name", "trade", "city", "address", "tagline", "intro",
                                            "story_title", "story_paragraphs", "cta_title",
                                            "email", "facebook", "instagram"
                                        ]
                                    },
                                    "value": {
                                        "type": "string"
                                    },
                                    "hours": {
                                        "type": "string"
                                    },
                                    "phone": {
                                        "type": "string"
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "The service name"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Service description"
                                    },
                                    "price": {
                                        "type": "string",
                                        "description": "Service price e.g. 45€"
                                    },
                                    "duration": {
                                        "type": "string",
                                        "description": "Service duration"
                                    },
                                    "order": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "description": "List of photo indices"
                                    },
                                    "palette": {
                                        "type": "string",
                                        "enum": ["original", "warm", "forest", "ocean", "rose", "mono"]
                                    }
                                }
                            }
                        },
                        "required": ["op", "params"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["schema_version", "intent", "explanation", "requires_confirmation", "confidence", "operations"],
            "additionalProperties": False
        }
    }
}

class DeepSeekSiteEditingModel(SiteEditingModel):
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        *,
        temperature: float = 0.0,
        provider_name: str = "deepseek",
        tool_choice: Any = None,
    ):
        self.base_url = base_url or cfg.AI_BASE_URL or "https://api.deepseek.com/v1"
        # ΚΛΕΙΔΙ ΠΟΥ ΤΑΙΡΙΑΖΕΙ ΣΤΟ ENDPOINT.
        #
        # Αυτή η κλάση μιλάει ΜΟΝΟ πρωτόκολλο OpenAI. Το `AI_API_KEY` όμως
        # εξυπηρετεί και το `src/ai.py`, που τιμά το `AI_PROVIDER=anthropic`
        # και στέλνει στο api.anthropic.com. Όταν το ένα κλειδί σερβίρει δύο
        # διαφορετικά πρωτόκολλα, κάποιος από τους δύο παίρνει 401.
        #
        # Μετρήθηκε: κλειδί `sk-ant-…` έφτανε στο DeepSeek και κάθε μήνυμα
        # πελάτη στον βοηθό γύριζε 502 — ο chat editor ήταν νεκρός.
        self.api_key = api_key or cfg.AI_API_KEY
        if self.api_key.startswith("sk-ant-") and "anthropic" not in self.base_url:
            self.api_key = cfg.DEEPSEEK_API_KEY or self.api_key
        self.model_name = model_name or cfg.AI_MODEL or "deepseek-chat"
        # Moonshot's current Kimi models reject temperature=0 and require 1.
        # Keep deterministic zero for providers that support it; adapt only
        # when the configured endpoint is Moonshot.
        self.temperature = 1.0 if "api.moonshot.ai" in self.base_url else temperature
        self.provider_name = provider_name
        if tool_choice is not None:
            self.tool_choice = tool_choice
        elif "api.moonshot.ai" in self.base_url:
            # Kimi thinking models support tools but reject a forced/specified
            # tool choice. The strict schema still validates anything returned.
            self.tool_choice = "auto"
        else:
            self.tool_choice = {
                "type": "function",
                "function": {"name": "edit_site"},
            }

    @staticmethod
    def _canonical_intent(plan: EditPlan) -> str:
        """Intent is protocol data, not provider-authored prose."""
        if plan.intent == "undo":
            return "undo"
        if not plan.operations:
            return "reject"
        if len(plan.operations) > 1:
            return "multi_edit"
        operation = plan.operations[0]
        if operation.op == "update_business_field":
            field = operation.params.get("field")
            return f"update_{field}" if field else operation.op
        return operation.op

    def plan_edit(self, context: Dict[str, Any], message: str) -> Optional[EditPlan]:
        if not self.api_key:
            print("[ai_editor] API key missing for editing model.")
            return None

        system_prompt = (
            "You are the Vitrina website conversational editing assistant.\n"
            "Analyze the site context and the user request, and generate structured edit operations.\n"
            "CRITICAL RULES:\n"
            "1. Output ONLY structured arguments via the edit_site function call.\n"
            "2. The explanation MUST be in natural Greek, explaining what you changed or why you need confirmation.\n"
            "3. If the user asks for a change that is unsupported or requires a manual step (like uploading a new photo, or deleting a photo, or changing billing), plan zero operations and set the explanation to explain where they can perform this manually (refer to form/media/billing/design tabs).\n"
            "4. NEVER output internal keys or slugs (like 'rose', 'palette', 'cta_title') in the Greek explanation. Translate them to friendly terms like 'τα χρώματα', 'ταχυδρομική διεύθυνση', etc.\n"
            "5. If the request is malicious, tries to run code, inject scripts, or modify another client, plan zero operations and set explanation to a polite refusal.\n"
            "6. Support 'undo' implicitly if requested by matching it, but the engine handles revisions. Set intent='undo' and operations=[] for undo requests.\n"
            "7. For reorder_media, return a complete permutation of every available media index. Move the requested item and preserve the relative order of all others."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        user_content = (
            f"Current Site Context:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
            f"User Instruction:\n{message}"
        )

        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "tools": [EDIT_SITE_TOOL],
                "tool_choice": self.tool_choice,
                "temperature": self.temperature
            }
            r = None
            for attempt in range(3):
                try:
                    r = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers, json=payload, timeout=60,
                    )
                except (requests.Timeout, requests.ConnectionError):
                    if attempt == 2:
                        raise
                    time.sleep(0.4 * (2 ** attempt))
                    continue
                if r.status_code not in (429, 500, 502, 503, 504) or attempt == 2:
                    break
                r.close()
                time.sleep(0.4 * (2 ** attempt))
            assert r is not None

            if not r.ok:
                print(f"[ai_editor] {self.provider_name} API returned HTTP {r.status_code}: {r.text[:200]}")
                return None

            res_json = r.json()
            tool_calls = res_json.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
            if not tool_calls:
                print("[ai_editor] No tool call returned by the model.")
                return None

            args_str = tool_calls[0].get("function", {}).get("arguments", "{}")
            parsed_args = json.loads(args_str)
            plan = EditPlan(**parsed_args)
            return plan.model_copy(update={"intent": self._canonical_intent(plan)})

        except Exception as e:
            print(f"[ai_editor] Failed to plan edit: {e}")
            return None
