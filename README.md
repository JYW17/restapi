# **이미지 업로드 및 변환 REST API**

## **1. 소개**
이 애플리케이션은 **이미지 파일을 업로드**하고 해당 파일의 정보를 반환하는 간단한 **REST API**입니다.  
**FastAPI**를 사용하여 개발되었으며, **Swagger UI**를 통한 API 명세와 테스트도 가능합니다.

---

## **2. 기능**
- **이미지 파일 업로드**: 사용자는 JPG, PNG 등의 이미지 파일을 업로드할 수 있습니다.
- **파일 정보 반환**: 업로드된 이미지의 **파일명과 크기**를 반환합니다.
- **에러 처리**: 파일이 누락되거나 잘못된 요청이 있을 경우 **에러 메시지**를 반환합니다.

---

## **3. 설치 절차**
1. **Python 설치 확인**  
   - Python 3.8 이상이 설치되어 있어야 합니다.
   ```bash
   sudo apt-get update
   # Python3 및 pip 설치
   sudo apt-get install -y python3 python3-pip
   ```
2. **GitHub 저장소 클론**
   ```
   git clone https://github.com/JYW17/restapi.git
   cd restapi
   ```

4. **필수 라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```
   만약 error: externally-managed-environment 오류 시 아래 실행
   ```
   sudo apt install \
   python3-fastapi \
   python3-pillow \
   python3-uvicorn \
   python3-multipart
   ```

---

## **4. 실행 방법**
1. 서버 실행
   아래 명령어를 입력하여 FastAPI 서버를 실행합니다.
   ```
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
2. API 예시 리퀘스트 및 리스폰스

   - 업로드 요청 (POST /upload)
     ```bash
     curl -X POST http://localhost:8000/upload \
     -F "file=@example.jpg" \
     -F "resize=200,200" \
     -F "convert_to=png"
     ```
     - 요청 데이터:
       - file: 업로드할 이미지 파일
       - resize: (선택사항) 크기 조정 [가로, 세로]
       - convert_to: (선택사항) 이미지 포맷 변환 (예: png, jpg)
     - 응답 예시:
       ```json
       {
         "original_id": "abc123",
         "message": "Image uploaded and converted successfully.",
         "converted_id": "abc456"
       }
       ```
   - 이미지 다운로드 요청 (GET /download/{file_id})
     ```bash
     curl -O http://localhost:8000/download/abc123
     ```
     - 요청 데이터: 없음 (파일 ID만 필요)
     - 응답: 변환된 이미지 파일 다운로드

   - 이미지 삭제 요청 (DELETE /delete/{file_id})
     ```bash
     curl -X DELETE http://localhost:8000/delete/abc123
     ```
     - 응답 예시:
     ```json
     {
       "message": "File abc123.png has been deleted."
     }
     ```
3. test_api.sh로 테스트
   - 각 api의 모든 기능을 실행하여 테스트 할 수 있는 스크립트입니다.
     ```
     # 실행 권한 부여
     chmod +x ./test_api.sh
     # 실행
     ./test_api.sh
     ```

---

## **5. 파일 설명**
- main.py: REST API의 핵심 로직이 담긴 메인 코드 파일입니다.
  - API 경로
    - / : 기본 경로로 간단한 메시지를 반환합니다.
    - /upload-image/ : 이미지 파일을 업로드하고 파일명과 크기를 반환합니다.
    - /upload/ : 이미지를 업로드하고 해당 파일을 서버에 저장합니다.
    - /download/ : 서버에 저장된 이미지를 다운로드할 수 있습니다.
    - /delete/ : 서버에 저장된 이미지를 삭제할 수 있습니다.
    - /error/ : 에러 예시를 확인할 수 있는 경로로, 404 상태 코드를 반환합니다.
- requirements.txt: 필수 라이브러리 목록이 작성된 파일입니다.
- images/ : 테스트 이미지(test_id_1234.jpg)가 들어있습니다.
- test_api.sh: 모든 기능을 실행하여 테스트 해볼 수 있는 쉘 스크립트입니다.



