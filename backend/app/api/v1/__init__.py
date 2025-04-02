
    
def error_descriptions(name: str, _404: bool = False, _410: bool = False, _204: bool = False, _403: bool = False ) -> dict:
    descriptions = {}
    if _204:
        descriptions[204] = {
            "description": "No content",
            "content": {"application/json": {"example": {"detail": "No content"}}},
        }
    if _403:
        descriptions[403] = {
            "description": "Forbidden",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        }
    if _404:
        descriptions[404] = {
            "description": f"{name} not found",
            "content": {"application/json": {"example": {"detail": f"{name} not found"}}},
        }
    if _410:
        descriptions[410] = {
            "description": f"{name} is gone",
            "content": {"application/json": {"example": {"detail": f"{name} is gone"}}},
        }
    return descriptions