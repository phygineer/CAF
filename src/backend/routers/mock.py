from fastapi import FastAPI,APIRouter,UploadFile, HTTPException, Form


router = APIRouter()


@router.get("/")
def _():
    return {"Message": "Mock Hello World!"}