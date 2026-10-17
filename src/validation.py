"""Validate the records against the schema"""

def validate_records(record,schema):
    """Function to validate the schema"""
    errors=[]
    for column, rules in schema.items():
        value=record.get(column)
        if value is None and not rules.get("nullable", True):
            errors.append(
                f"Required column '{column}' is missing."
            )
    return errors