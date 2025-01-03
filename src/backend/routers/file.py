from fastapi import FastAPI,APIRouter,UploadFile, HTTPException, Form

from fastapi import File, UploadFile,FastAPI
app = FastAPI()

router = APIRouter()


@router.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    return {"message": f"Successfully uploaded {file.filename}"}