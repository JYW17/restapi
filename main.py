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
        # 고유 파일 ID 생성
        file_extension = file.filename.split(".")[-1]
        original_id = uuid4().hex
        new_filename = f"{original_id}.{file_extension}"

        file_path = os.path.join(IMAGE_DIR, new_filename)
        
        response = {
            "original_id": original_id,
        }
        
        # 파일 저장
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        response ["message"] = "Image uploaded successfully."

        # 이미지 변환
        image = Image.open(file_path)
        converted_id = None
        
        # 현재 확장자와 동일한 경우 변환 건너뛰기
        if convert_to and convert_to.lower() == file_extension.lower():
            convert_to = None
        
        if convert_to or resize:
            
            # convert_to가 지원되는 확장자인지 확인
            if convert_to and convert_to.lower() not in SUPPORTED_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported format. Supported formats are: {', '.join(SUPPORTED_FORMATS)}"
                )
            
            converted_id = uuid4().hex
            new_path = os.path.join(IMAGE_DIR, f"{converted_id}.{convert_to or file_extension}")
            
            if resize:
                width, height = map(int, resize.split(","))
                image = image.resize((width, height))
        
            image.save(new_path) 
        
        image.close()
        
        if converted_id:
            response["converted_id"] = converted_id
            response["message"] = "Image uploaded and converted successfully."
            
        return response
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

