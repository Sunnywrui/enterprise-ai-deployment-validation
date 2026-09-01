from __future__ import annotations
import json
from jsonschema import Draft202012Validator

def validate_tool_arguments(schema_value, arguments):
    if not schema_value:
        return True, []
    schema = schema_value if isinstance(schema_value, dict) else json.loads(schema_value)
    errors = sorted(Draft202012Validator(schema).iter_errors(arguments or {}), key=lambda e: list(e.path))
    return (not errors), [{"path":".".join(map(str,e.path)), "message":e.message} for e in errors]
