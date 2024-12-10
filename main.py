from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from uuid import uuid4
from PIL import Image
from pydantic import BaseModel

app = FastAPI()

# 이미지 저장 경로
IMAGE_DIR = "./images"
os.makedirs(IMAGE_DIR, exist_ok=True)


# Pydantic 스키마 모델 정의
class ImageResponse(BaseModel):
    filename: str
    file_size: int

# 지원되는 이미지 확장자 목록
SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']

# 기본 경로
@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# 파일 업로드 경로
@app.post("/upload-image/", response_model=ImageResponse)
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "file_size": len(content)}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), resize: str = None, convert_to: str = None):
    try:
        file_extension = file.filename.split(".")[-1]
        
        # 변환이나 리사이즈가 필요한 경우
        if resize or convert_to:
            image = Image.open(file.file)
            file_id = uuid4().hex
            target_extension = convert_to or file_extension
            file_path = os.path.join(IMAGE_DIR, f"{file_id}.{target_extension}")
            
            if resize:
                width, height = map(int, resize.split(","))
                image = image.resize((width, height))
            
            image.save(file_path)
            image.close()
            
            return {
                "file_id": file_id,
                "message": "Image uploaded and processed successfully."
            }
            
        # 변환이나 리사이즈가 없는 경우
        else:
            file_id = uuid4().hex
            file_path = os.path.join(IMAGE_DIR, f"{file_id}.{file_extension}")
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
                
            return {
                "file_id": file_id,
                "message": "Image uploaded successfully."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_id}")
async def download_image(file_id: str):
    # 디렉토리에서 file_id와 이름이 일치하는 파일 찾기
    for filename in os.listdir(IMAGE_DIR):
        name, ext = os.path.splitext(filename)
        if name == file_id:
            file_path = os.path.join(IMAGE_DIR, filename)
            return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/delete/{file_id}")
async def delete_image(file_id: str):
    # 디렉토리에서 file_id와 이름이 일치하는 파일 찾기
    for filename in os.listdir(IMAGE_DIR):
        name, ext = os.path.splitext(filename)
        if name == file_id:
            file_path = os.path.join(IMAGE_DIR, filename)
            os.remove(file_path)
            return {"message": f"File {filename} has been deleted."}
    raise HTTPException(status_code=404, detail="File not found")

