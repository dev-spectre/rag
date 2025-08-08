# src/auth.py
from fastapi import Depends
from fastapi.security import HTTPBearer
from typing import Optional

# scheme will extract the bearer token
scheme = HTTPBearer(auto_error=False)

async def get_optional_api_key(token: Optional[HTTPBearer] = Depends(scheme)) -> Optional[str]:
    """
    Returns the bearer token if one is provided, otherwise returns None.
    No validation is performed here.
    """
    if token:
        return token.credentials
    return None