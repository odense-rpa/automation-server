

def get_standard_error_descriptions(name: str) -> dict:
    return {
    404: {
        "description": f"{name} not found",
        "content": {"application/json": {"example": {"detail": f"{name} not found"}}},
    },
    410: {
        "description": f"{name} is gone",
        "content": {"application/json": {"example": {"detail": f"{name} is gone"}}},
    },
}