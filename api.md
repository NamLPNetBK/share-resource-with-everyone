# 📘 API DOCUMENTATION

## File Upload & AI Processing Service

**Version:** v1.0
**Region:** ap-northeast-1
**Base URL:**

```
https://hfvasnpqo9.execute-api.ap-northeast-1.amazonaws.com/dev-teamB/TeamB
```

**Protocol:** HTTPS
**Data Format:** JSON
**Architecture:** Amazon API Gateway + Amazon S3

---

# 1️⃣ Generate Presigned Upload URL

## 📌 Overview

Tạo presigned URL để client upload file trực tiếp lên S3 mà không cần đi qua backend server.

---

## 🔹 Endpoint

```
POST /file/presigned-upload-url
```


---

## 🔹 Request Body

```json
{
  "fileName": "file1.xlsx"
}
```

### 📋 Parameters

| Field    | Type   | Required | Description             |
| -------- | ------ | -------- | ----------------------- |
| fileName | string | Yes      | Tên file gốc cần upload |

---

## 🔹 Response (200 OK)

```json
{
  "uploadUrl": "https://teamb-content.s3.amazonaws.com/B/InputProject/ddb19d9d-4082-4f8a-b2e7-6c4fb7d225cf_file1.xlsx?...",
  "s3Key": "B/InputProject/ddb19d9d-4082-4f8a-b2e7-6c4fb7d225cf_file1.xlsx"
}
```

### 📋 Response Fields

| Field     | Type   | Description                             |
| --------- | ------ | --------------------------------------- |
| uploadUrl | string | Presigned URL để upload file (HTTP PUT) |
| s3Key     | string | Đường dẫn object trong S3               |

---

## 🔹 Upload File to S3

Sau khi nhận `uploadUrl`, client thực hiện:

```
PUT <uploadUrl>
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Body: (binary file)
```

---

## 🔹 Error Responses

### 400 Bad Request

```json
{
  "message": "fileName is required"
}
```

---

# 2️⃣ Get Project Workload Analytic & Evaluation

## 📌 Overview

API này trả về kết quả phân tích.

---

## 🔹 Endpoint

```
POST /file/process-result
```

---

## 🔹 Request Body

```json
{
  "s3Key": "B/InputProject/01b6789d-57cf-4732-90d9-d93a21ac5320_【概算見積】24S156_本人確認方法へ方式導入（新WEB移行分）v1.xlsx"
}
```

### 📋 Parameters

| Field | Type   | Required | Description                          |
| ----- | ------ | -------- | ------------------------------------ |
| s3Key | string | Yes      | Object key của file đã upload lên S3 đã nhận từ response của API  Generate Presigned Upload URL|

---

## 🔹 Response (200 OK)

```json
{
  "aiEvaluation": "...",
  "projectFileName": "01b6789d-57cf-4732-90d9-d93a21ac5320_【概算見積】24S156_本人確認方法へ方式導入（新WEB移行分）v1.xlsx",
  "uploadedAt": "2026-02-24T10:33:45.211691+00:00",
  "parsedData": [
    {
      "name": "DI02290100：本人確認受付画面",
      "difficulty": "中",
      "workload": 0.56,
      "avgWorkload": 0.5947,
      "category": "画面",
      "differenceFromAverage": -0.0347
    }
  ],
  "status": "COMPLETED"
}
```

---

## 🔹 Response Fields

| Field           | Type                | Description                                        |
| --------------- | ------------------- | -------------------------------------------------- |
| aiEvaluation    | string              | Nội dung phân tích & đánh giá từ AI                |
| projectFileName | string              | Tên file đã xử lý                                  |
| uploadedAt      | datetime (ISO 8601) | Thời điểm upload                                   |
| parsedData      | array               | Danh sách dữ liệu đã parse                         |
| status          | string              | Trạng thái xử lý (PROCESSING / COMPLETED / FAILED) |

---

## 🔹 parsedData Object Structure

| Field                 | Type   | Description                  |
| --------------------- | ------ | ---------------------------- |
| name                  | string | Tên hạng mục                 |
| difficulty            | string | Mức độ (低 / 中 / 高)           |
| workload              | float  | Công số thực tế              |
| avgWorkload           | float  | Công số trung bình chuẩn     |
| category              | string | Loại (画面 / API)              |
| differenceFromAverage | float  | Chênh lệch so với trung bình |

---

## 🔹 Error Responses

### 400 Bad Request

```json
{
  "message": "Missing s3Key in event"
}
```

### 404 Not Found

```json
{
  "message": "No record found for projectFileName: s3_key"
}
```

---

# 🔐 Flow:

1. Frontend -> Generate Presigned Upload URL
2. Frontend -> PUT file to S3 by Presigned URL
3. Frontend -> Get Project Workload Analytic & Evaluation
```
    getReusult(
        if status == FAILED : XỬ LÝ FILE THẤT BẠI
        if status == PROCESSING : setTimeout(3000, getReusult())
    )
```

---

