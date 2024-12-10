from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import shutil
from uuid import uuid4
from PIL import Image

app = FastAPI()

# 이미지 저장 경로
IMAGE_DIR = "./images"
os.makedirs(IMAGE_DIR, exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), resize: str = None, convert_to: str = None):
    try:
        # 고유 파일 ID 생성
        file_extension = file.filename.split(".")[-1]
        new_filename = f"{uuid4().hex}.{convert_to or file_extension}"

        file_path = os.path.join(IMAGE_DIR, new_filename)
        
        # 파일 저장
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 이미지 변환
        image = Image.open(file_path)
        
        if resize:
            width, height = map(int, resize.split(","))
            image = image.resize((width, height))
        
        if convert_to:
            new_path = os.path.join(IMAGE_DIR, f"{uuid4().hex}.{convert_to}")
            image.save(new_path)
            file_path = new_path
        
        image.close()
        
        return {"file_id": os.path.basename(file_path), "message": "Image uploaded and converted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_id}")
async def download_image(file_id: str):
    file_path = os.path.join(IMAGE_DIR, file_id)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.delete("/delete/{file_id}")
async def delete_image(file_id: str):
    file_path = os.path.join(IMAGE_DIR, file_id)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return {"message": f"File {file_id} has been deleted."}
    else:
        raise HTTPException(status_code=404, detail="File not found")
