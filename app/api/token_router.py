from fastapi import Depends, HTTPException, APIRouter


router = APIRouter(prefix="/token", tags=["Oauth2 "])
