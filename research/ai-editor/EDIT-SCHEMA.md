# Edit Plan Schema & Allowed Operations

This document defines the strict versioned JSON schema for conversational edits. The LLM must generate plans adhering strictly to this schema, and the execution engine must reject any malformed or unexpected fields.

## 1. EditPlan JSON Schema

The `EditPlan` produced by the intent planner has the following schema:

```json
{
  "schema_version": "1.0",
  "intent": "string (e.g. 'update_contact_info')",
  "explanation": "string (Greek message summarizing the intent & changes)",
  "confidence": 0.95,
  "requires_confirmation": false,
  "operations": [
    {
      "op": "operation_name",
      "params": {
        "key1": "value1",
        "key2": "value2"
      }
    }
  ]
}
```

### Constraints:
1. **Schema Version**: Must be exactly `"1.0"`.
2. **Operations Allowlist**: The `op` field must belong to the list of 6 approved operations below.
3. **No Code Execution**: Parameters must never contain code, selectors, or script commands.
4. **Validation**: Any unknown operation or parameter forces a complete transaction rejection.

---

## 2. Allowed Operations Allowlist

Only the following six operations are supported in the initial production vertical slice:

### 1. `update_business_field`
Modifies a single text field in the business profile.
- **Parameters**:
  - `field`: string (must be one of: `"name"`, `"trade"`, `"city"`, `"address"`, `"tagline"`, `"intro"`, `"story_title"`, `"story_paragraphs"`, `"cta_title"`, `"email"`, `"facebook"`, `"instagram"`)
  - `value`: string (or list of strings for `story_paragraphs`)

### 2. `update_hours`
Updates the business operating hours.
- **Parameters**:
  - `hours`: string (e.g., `"Δευτέρα–Παρασκευή: 09:00–21:00, Σάββατο: 09:00–15:00, Κυριακή: Κλειστά"`)

### 3. `update_phone`
Updates the primary phone contact information.
- **Parameters**:
  - `phone`: string (numbers, spaces, and optional + prefix)

### 4. `update_service`
Adds or modifies a business service. If the service already exists (by name matching), it is updated; otherwise, it is appended.
- **Parameters**:
  - `name`: string (e.g., `"Balayage"`, unique service identifier)
  - `description`: string (optional service details)
  - `price`: string (optional, e.g., `"45€"`)
  - `duration`: string (optional, e.g., `"60 λεπτά"`)

### 5. `reorder_media`
Reorders existing photos in the client's gallery using indices.
- **Parameters**:
  - `order`: array of integers (e.g., `[1, 0, 2]` to swap the first and second images)

### 6. `set_palette`
Updates the design color palette.
- **Parameters**:
  - `palette`: string (must be one of: `"original"`, `"warm"`, `"forest"`, `"ocean"`, `"rose"`, `"mono"`)
