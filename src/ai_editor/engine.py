# Transactional Editing Engine and Validators
from __future__ import annotations

import re
import html
from typing import Any, Dict, List, Tuple
from src.ai_editor.model import EditPlan, Operation
from src.ai_editor.store import DatabaseEditorStore, EditorStore

class ExecutionResult:
    def __init__(self, success: bool, message: str, before_state: Dict[str, Any], after_state: Dict[str, Any]):
        self.success = success
        self.message = message
        self.before_state = before_state
        self.after_state = after_state

class EditingEngine:
    @staticmethod
    def validate_operation(
        op: Operation,
        client_id: str,
        current_content: Dict[str, Any],
        store: EditorStore | None = None,
        capabilities: Dict[str, Any] | None = None,
    ) -> Tuple[bool, str]:
        """Validate single operation before applying."""
        op_name = op.op
        params = op.params

        # 1. Check allowed operation
        allowed_ops = {"update_business_field", "update_hours", "update_phone", "update_service", "reorder_media", "set_palette"}
        if op_name not in allowed_ops:
            return False, f"Μη επιτρεπτή ενέργεια: {op_name}"

        allowed_params = {
            "update_business_field": {"field", "value"},
            "update_hours": {"hours"},
            "update_phone": {"phone"},
            "update_service": {"name", "description", "price", "duration"},
            "reorder_media": {"order"},
            "set_palette": {"palette"},
        }
        unexpected = set(params) - allowed_params[op_name]
        if unexpected:
            return False, f"Μη αναμενόμενες παράμετροι: {', '.join(sorted(unexpected))}"

        # 2. update_business_field validation
        if op_name == "update_business_field":
            field = params.get("field")
            value = params.get("value")
            allowed_fields = {
                "name", "trade", "city", "address", "tagline", "intro",
                "story_title", "story_paragraphs", "cta_title",
                "email", "facebook", "instagram"
            }
            if field not in allowed_fields:
                return False, f"Μη επιτρεπτό πεδίο επεξεργασίας: {field}"
            if field == "story_paragraphs":
                if not isinstance(value, list):
                    return False, "Το story_paragraphs πρέπει να είναι λίστα κειμένων."
                for p in value:
                    if not isinstance(p, str) or len(p) > 1200:
                        return False, "Κάθε παράγραφος του story πρέπει να είναι κείμενο έως 1200 χαρακτήρες."
            else:
                if not isinstance(value, str):
                    return False, f"Η τιμή για το πεδίο {field} πρέπει να είναι κείμενο."
                if len(value) > 1200:
                    return False, f"Το κείμενο για το πεδίο {field} υπερβαίνει το όριο των 1200 χαρακτήρων."
                if re.search(r"<\s*/?\s*(script|style|iframe|object|embed)|javascript:|data:text/html", value, re.I):
                    return False, "Δεν επιτρέπεται ενεργό HTML ή κώδικας στο περιεχόμενο."
                # Safety checks on links
                if field in ("facebook", "instagram", "gbp_url"):
                    if value and not value.startswith("https://"):
                        return False, "Οι σύνδεσμοι κοινωνικών δικτύων πρέπει να ξεκινούν με https://"
                    if "javascript:" in value.lower() or "data:" in value.lower():
                        return False, "Μη έγκυρος σύνδεσμος."

        # 3. update_hours validation
        elif op_name == "update_hours":
            hours = params.get("hours")
            if not isinstance(hours, str) or not hours.strip() or len(hours) > 500:
                return False, "Το ωράριο πρέπει να είναι κείμενο έως 500 χαρακτήρες."
            time_tokens = re.findall(r"(?<!\d)([0-2]?\d):([0-5]\d)(?!\d)", hours)
            if any(int(h) > 23 for h, _ in time_tokens):
                return False, "Το ωράριο περιέχει μη έγκυρη ώρα."
            if re.search(r"<|>|javascript:|data:", hours, re.I):
                return False, "Το ωράριο δεν μπορεί να περιέχει markup ή κώδικα."

        # 4. update_phone validation
        elif op_name == "update_phone":
            phone = params.get("phone")
            if not isinstance(phone, str) or len(phone) > 40:
                return False, "Το τηλέφωνο πρέπει να είναι κείμενο έως 40 χαρακτήρες."
            # Phone digits check (allow numbers, spaces, dashes, parentheses, +)
            if phone and not re.match(r"^[+\d\s\-\(\)]+$", phone):
                return False, "Το τηλέφωνο περιέχει μη έγκυρους χαρακτήρες."
            digits = re.sub(r"\D", "", phone or "")
            if not 7 <= len(digits) <= 15:
                return False, "Το τηλέφωνο πρέπει να έχει από 7 έως 15 ψηφία."

        # 5. update_service validation
        elif op_name == "update_service":
            name = params.get("name")
            desc = params.get("description") or ""
            price = params.get("price") or ""
            duration = params.get("duration") or ""
            if not isinstance(name, str) or not name.strip() or len(name) > 80:
                return False, "Το όνομα της υπηρεσίας είναι υποχρεωτικό (έως 80 χαρακτήρες)."
            if len(desc) > 400:
                return False, "Η περιγραφή της υπηρεσίας υπερβαίνει τους 400 χαρακτήρες."
            if len(price) > 30:
                return False, "Η τιμή της υπηρεσίας υπερβαίνει τους 30 χαρακτήρες."
            if len(duration) > 40:
                return False, "Η διάρκεια της υπηρεσίας υπερβαίνει τους 40 χαρακτήρες."

        # 6. reorder_media validation
        elif op_name == "reorder_media":
            order = params.get("order")
            if not isinstance(order, list):
                return False, "Η σειρά (order) πρέπει να είναι λίστα δεικτών."
            # Get actual media length
            assets = (store or DatabaseEditorStore()).get_assets(client_id)
            photos = [a for a in assets if a.get("type") == "photo"]
            if len(order) != len(photos):
                return False, f"Το μέγεθος της σειράς ({len(order)}) δεν ταιριάζει με τον αριθμό των φωτογραφιών ({len(photos)})."
            for idx in order:
                if not isinstance(idx, int) or idx < 0 or idx >= len(photos):
                    return False, f"Μη έγκυρος δείκτης φωτογραφίας: {idx}"
            if sorted(order) != list(range(len(photos))):
                return False, "Η νέα σειρά πρέπει να περιέχει κάθε φωτογραφία ακριβώς μία φορά."

        # 7. set_palette validation
        elif op_name == "set_palette":
            palette = params.get("palette")
            allowed_palettes = {"original", "warm", "forest", "ocean", "rose", "mono"}
            if palette not in allowed_palettes:
                return False, f"Άγνωστο χρωματικό σχήμα: {palette}"
            capability_palettes = (capabilities or {}).get("palettes")
            if capability_palettes is not None and palette not in set(capability_palettes):
                return False, f"Το επιλεγμένο σχέδιο δεν υποστηρίζει το χρωματικό σχήμα: {palette}"

        return True, ""

    @staticmethod
    def execute_plan(
        client_id: str,
        plan: EditPlan,
        *,
        store: EditorStore | None = None,
        capabilities: Dict[str, Any] | None = None,
        persist: bool = False,
    ) -> ExecutionResult:
        """Execute EditPlan atomically. Returns ExecutionResult with rollback on failure."""
        try:
            # 1. Fetch current content (acts as transaction read snapshot)
            active_store = store or DatabaseEditorStore()
            before_state = active_store.get_content(client_id) or {}
            # Deep copy to manipulate safely
            import copy
            after_state = copy.deepcopy(before_state)

            # 2. Validate all operations first
            for op in plan.operations:
                ok, err_msg = EditingEngine.validate_operation(
                    op, client_id, after_state, active_store, capabilities
                )
                if not ok:
                    return ExecutionResult(False, f"Validation failed: {err_msg}", before_state, before_state)

            # 3. Apply operations sequentially
            for op in plan.operations:
                op_name = op.op
                params = op.params

                if op_name == "update_business_field":
                    field_name = params["field"]
                    val = params["value"]
                    if field_name == "story_paragraphs":
                        after_state[field_name] = [html.escape(p) for p in val]
                    else:
                        after_state[field_name] = html.escape(val)

                elif op_name == "update_hours":
                    after_state["hours"] = html.escape(params["hours"])

                elif op_name == "update_phone":
                    after_state["phone"] = html.escape(params["phone"])

                elif op_name == "update_service":
                    # Manage service updates in content["services"]
                    services = after_state.get("services", [])
                    s_name = params["name"].strip()
                    s_desc = html.escape(params.get("description") or "")
                    s_price = html.escape(params.get("price") or "")
                    s_dur = html.escape(params.get("duration") or "")

                    updated = False
                    for s in services:
                        # Case insensitive match for service name
                        if s.get("name", "").strip().lower() == s_name.lower():
                            s["name"] = s_name
                            s["description"] = s_desc
                            s["price"] = s_price
                            s["duration"] = s_dur
                            updated = True
                            break

                    if not updated:
                        if len(services) >= 8:
                            return ExecutionResult(
                                False, "Execution failed: Υπάρχει ήδη το όριο των 8 υπηρεσιών.", before_state, before_state
                            )
                        services.append({
                            "name": s_name,
                            "description": s_desc,
                            "price": s_price,
                            "duration": s_dur
                        })
                    after_state["services"] = services

                elif op_name == "reorder_media":
                    order = params["order"]
                    assets = active_store.get_assets(client_id)
                    photos = [a for a in assets if a.get("type") == "photo"]
                    # Sort actual photos list based on the new order index
                    ordered_photos = [photos[i] for i in order]
                    # Save the photo order as a list of asset IDs
                    after_state["photo_order"] = [p["id"] for p in ordered_photos]

                elif op_name == "set_palette":
                    after_state["palette"] = params["palette"]

            # Persistence is deliberately outside the engine. Only
            # EditingService/DatabaseEditorStore may call the atomic RPC.
            if persist:
                raise RuntimeError("direct engine persistence is forbidden; use EditingService")
            return ExecutionResult(True, "Plan executed successfully.", before_state, after_state)

        except Exception as e:
            # Automatic rollback on server / database exception since we only write on success
            return ExecutionResult(False, f"Exception during execution: {e}", {}, {})
