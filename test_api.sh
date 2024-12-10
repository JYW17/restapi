#!/bin/bash

API_URL="http://localhost:8000"

# 사용자 확인 함수
confirm() {
    read -p "$1 (y/n): " response
    case "$response" in
        [yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# 파일 확장자 확인 함수
get_extension() {
    local file_id=$1
    local content_type=$(curl -sI "${API_URL}/download/${file_id}" | grep -i 'content-type' | cut -d' ' -f2- | tr -d '\r\n')
    case "${content_type}" in
        *"image/jpeg"*) echo "jpg" ;;
        *"image/png"*) echo "png" ;;
        *"image/gif"*) echo "gif" ;;
        *"image/webp"*) echo "webp" ;;
        *) echo "jpg" ;; # 기본값
    esac
}

echo "FastAPI 이미지 처리 API 테스트를 시작합니다."

# 1. 기본 경로 테스트
echo -e "\n1. 기본 경로 테스트 (/)"
curl -X GET "${API_URL}/"
confirm "계속 진행하시겠습니까?" || exit 0

# 2. 이미지 업로드 테스트
echo -e "\n2. 이미지 업로드 테스트 (/upload)"
UPLOAD_RESPONSE=$(curl -X POST "${API_URL}/upload" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@./images/test_id_1234.jpg")
echo $UPLOAD_RESPONSE
ORIGINAL_ID=$(echo $UPLOAD_RESPONSE | grep -o '"file_id":"[^"]*' | cut -d'"' -f4)
confirm "계속 진행하시겠습니까?" || exit 0

# 3. 이미지 리사이즈 테스트
echo -e "\n3. 이미지 리사이즈 테스트 (/upload with resize)"
RESIZE_RESPONSE=$(curl -X 'POST' \
    "${API_URL}/upload?resize=300,300" \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F 'file=@./images/test_id_1234.jpg;type=image/jpeg')
echo $RESIZE_RESPONSE
RESIZE_ID=$(echo $RESIZE_RESPONSE | grep -o '"file_id":"[^"]*' | cut -d'"' -f4)
confirm "계속 진행하시겠습니까?" || exit 0

# 4. 이미지 포맷 변환 테스트
echo -e "\n4. 이미지 포맷 변환 테스트 (/upload with convert)"
FORMAT_RESPONSE=$(curl -X 'POST' \
    "${API_URL}/upload?convert_to=png" \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F 'file=@./images/test_id_1234.jpg;type=image/jpeg')
echo $FORMAT_RESPONSE
FORMAT_ID=$(echo $FORMAT_RESPONSE | grep -o '"file_id":"[^"]*' | cut -d'"' -f4)
confirm "계속 진행하시겠습니까?" || exit 0

# 5. 이미지 다운로드 테스트
echo -e "\n5. 이미지 다운로드 테스트 (/download)"
echo "원본 이미지 다운로드:"
original_ext=$(get_extension "${ORIGINAL_ID}")
curl -X GET "${API_URL}/download/${ORIGINAL_ID}" --output "downloaded_original.${original_ext}"

echo -e "\n리사이즈된 이미지 다운로드:"
resized_ext=$(get_extension "${RESIZE_ID}")
curl -X GET "${API_URL}/download/${RESIZE_ID}" --output "downloaded_resized.${resized_ext}"

echo -e "\n포맷 변환된 이미지 다운로드:"
converted_ext=$(get_extension "${FORMAT_ID}")
curl -X GET "${API_URL}/download/${FORMAT_ID}" --output "downloaded_converted.${converted_ext}"
confirm "계속 진행하시겠습니까?" || exit 0

# 6. 이미지 삭제 테스트
echo -e "\n6. 이미지 삭제 테스트 (/delete)"
echo "기본 업로드 이미지 삭제:"
curl -X DELETE "${API_URL}/delete/${ORIGINAL_ID}"
echo -e "\n리사이즈된 이미지 삭제:"
curl -X DELETE "${API_URL}/delete/${RESIZE_ID}"
echo -e "\n포맷 변환된 이미지 삭제:"
curl -X DELETE "${API_URL}/delete/${FORMAT_ID}"

echo -e "\n다운로드된 로컬 이미지 삭제:"
rm -f downloaded_original.* downloaded_resized.* downloaded_converted.*
echo "로컬 이미지가 삭제되었습니다."

echo -e "\n테스트가 완료되었습니다."
read -n 1 -s -r -p "아무 키나 누르면 종료됩니다..."
echo 