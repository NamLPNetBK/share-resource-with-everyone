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
  "prefix":"B/InputProject/"
}
```

### 📋 Parameters

| Field    | Type   | Required | Description             |
| -------- | ------ | -------- | ----------------------- |
| fileName | string | Yes      | Tên file gốc cần upload |
| prefix | string | Yes      | B/InputProject/ hoặc B/Document/ |

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
  "aiEvaluation": "### 1. 総合評価\n\n本プロジェクト（24S156）の見積もりは、全体的にはほぼ妥当な範囲内にあります。全42項目中、警告フラグがついたのは13項目（約31%）で、やや懸念があるレベルです。特にAPIの一部で過大見積もりの傾向が見られます。画面の見積もりは概ね適切ですが、APIの見直しが必要です。総合的には、一部見直しを推奨します。特に中難易度のAPIに注目し、工数の再検討を行うことで、より精度の高い見積もりになると考えられます。\n\n### 2. 詳細分析\n\n#### 乖離が大きい項目（警告フラグ）\n1. 取引時確認登録API: 乖離率+35.6%（過大見積）\n2. 申込照会API: 乖離率+35.6%（過大見積）\n3. 顧客（個人）登録事項変更申込書PDF作成API: 乖離率+35.6%（過大見積）\n4. 口座開設（個人）PDF作成API: 乖離率+35.6%（過大見積）\n5. NEOBANK住所情報取得: 乖離率+35.6%（過大見積）\n6. 書類アップロード切替: 乖離率+35.6%（過大見積）\n7. 取引時確認照会API: 乖離率+15.5%（過大見積）\n8. 本人確認方法照会API: 乖離率+15.5%（過大見積）\n9. 本人確認方法改竄チェックAPI: 乖離率+15.5%（過大見積）\n10. 認証トークン要求API: 乖離率+15.5%（過大見積）\n11. 申込変更API: 乖離率+15.5%（過大見積）\n12. DI02290105：本人確認方法の選択画面: 乖離率+17.9%（過大見積）\n13. DI02290135：本人確認申請完了（郵送）（口座開設）画面: 乖離率+17.9%（過大見積）\n\n#### 特記事項\n- 難易度別の傾向：中難易度のAPIで過大見積もりが目立ちます。\n- 画面とAPIのバランス：画面の見積もりは概ね適切ですが、APIで過大見積もりの傾向が見られます。\n- その他気づいた点：低難易度のAPIでも若干の過大見積もりが見られます。\n\n### 3. 推奨事項\n\n1. 中難易度APIの見直し（優先度：高）\n   - 取引時確認登録API、申込照会API、PDF作成関連APIの工数を再検討\n   - 平均工数との乖離を20%以内に抑えることを目標に調整\n\n2. 低難易度APIの微調整（優先度：中）\n   - 取引時確認照会API、本人確認方法関連APIの工数を精査\n   - 平均工数に近づけるよう0.1MM程度の削減を検討\n\n3. 画面の過大見積もり項目の確認（優先度：低）\n   - 本人確認方法の選択画面、本人確認申請完了（郵送）（口座開設）画面の工数を再確認\n   - 特殊な要件がない場合、平均工数に合わせる\n\n4. 全体的な見積もり方法の見直し（優先度：中）\n   - APIの見積もり基準を再検討し、特に中難易度の項目で過大見積もりにならないよう注意\n   - 難易度の判断基準を明確化し、チーム内で共有\n\n5. プロジェクト特性の考慮（優先度：中）\n   - 本プロジェクトの特殊性や難易度を加味した上で、標準値からの適切な調整を行う\n   - 必要に応じて、過去の類似プロジェクトのデータを参照し、より精度の高い見積もりを目指す\n\nこれらの推奨事項を実施することで、より精度の高い工数見積もりが可能となり、プロジェクトの成功確率が向上すると考えられます。",
  "projectFileName": "1ab6789d-57cf-4732-90d9-d93a21ac5320_【概算見積】24S156_本人確認方法へ方式導入（新WEB移行分）v1.xlsx",
  "uploadedAt": "2026-02-27T11:43:02.016145+00:00",
  "parsedData": [
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "DI02290100：本人確認受付画面",
      "workload": 0.56,
      "avgWorkload": 0.5947,
      "isWithinStandard": true,
      "category": "画面",
      "differenceFromAverage": -0.0347
    },
    {
      "difficulty": "高",
      "diffRate": 10,
      "name": "DI02290105：本人確認方法の選択画面",
      "workload": 0.8,
      "avgWorkload": 0.6786,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": 0.1214
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "DI02290110：本人確認書類の選択画面",
      "workload": 0.33,
      "avgWorkload": 0.3822,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": -0.0522
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "DI02290115：本人確認流れ画面",
      "workload": 0.33,
      "avgWorkload": 0.3822,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": -0.0522
    },
    {
      "difficulty": "高",
      "diffRate": 10,
      "name": "DI02290120：申請内容の照合画面",
      "workload": 0.8,
      "avgWorkload": 0.6786,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": 0.1214
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "DI02290125：申請内容の確認画面",
      "workload": 0.56,
      "avgWorkload": 0.5947,
      "isWithinStandard": true,
      "category": "画面",
      "differenceFromAverage": -0.0347
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "DI02290130：本人確認申請完了（ワ方式、ホ方式）画面",
      "workload": 0.33,
      "avgWorkload": 0.3822,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": -0.0522
    },
    {
      "difficulty": "高",
      "diffRate": 10,
      "name": "DI02290135：本人確認申請完了（郵送）（口座開設）画面",
      "workload": 0.8,
      "avgWorkload": 0.6786,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": 0.1214
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "DI02290140：スマホで本人確認画面",
      "workload": 0.33,
      "avgWorkload": 0.3822,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": -0.0522
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "DI02290150：口座開設補足情報入力",
      "workload": 0.56,
      "avgWorkload": 0.5947,
      "isWithinStandard": true,
      "category": "画面",
      "differenceFromAverage": -0.0347
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "DI02290160：本人確認申請完了（郵送）",
      "workload": 0.56,
      "avgWorkload": 0.5947,
      "isWithinStandard": true,
      "category": "画面",
      "differenceFromAverage": -0.0347
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "DI02290170：登録情報不一致エラー画面",
      "workload": 0.33,
      "avgWorkload": 0.3822,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": -0.0522
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "DI02290180：申請内容（グレー）の確認画面",
      "workload": 0.56,
      "avgWorkload": 0.5947,
      "isWithinStandard": true,
      "category": "画面",
      "differenceFromAverage": -0.0347
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "DI02290190：書類アップロード切替-確認画面",
      "workload": 0.56,
      "avgWorkload": 0.5947,
      "isWithinStandard": true,
      "category": "画面",
      "differenceFromAverage": -0.0347
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "DI02290195：書類アップロード切替-完了画面",
      "workload": 0.33,
      "avgWorkload": 0.3822,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": -0.0522
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "DI02290200：収入情報提出-確認画面",
      "workload": 0.33,
      "avgWorkload": 0.3822,
      "isWithinStandard": false,
      "category": "画面",
      "differenceFromAverage": -0.0522
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "本人確認受付画面初期表示API",
      "workload": 0.57,
      "avgWorkload": 0.5533,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0.0167
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "本人確認受付画面次へAPI",
      "workload": 0.57,
      "avgWorkload": 0.5533,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0.0167
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "本人確認方法照会API",
      "workload": 0.4,
      "avgWorkload": 0.4071,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": -0.0071
    },
    {
      "difficulty": "超高",
      "diffRate": 10,
      "name": "本人確認の申請をするAPI",
      "workload": 0.9359999999999999,
      "avgWorkload": 0.884,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0.052
    },
    {
      "difficulty": "汎用",
      "diffRate": 10,
      "name": "認証トークン要求API",
      "workload": 0.05,
      "avgWorkload": 0.05,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0
    },
    {
      "difficulty": "高",
      "diffRate": 10,
      "name": "マイナンバカード情報照合API",
      "workload": 0.78,
      "avgWorkload": 0.7225,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0.0575
    },
    {
      "difficulty": "汎用",
      "diffRate": 10,
      "name": "新ホ方式本人確認申込",
      "workload": 0.05,
      "avgWorkload": 0.05,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "口座開設補足情報登録API",
      "workload": 0.4,
      "avgWorkload": 0.4071,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": -0.0071
    },
    {
      "difficulty": "汎用",
      "diffRate": 10,
      "name": "顧客（個人）登録事項変更申込書PDF作成API",
      "workload": 0.05,
      "avgWorkload": 0.05,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0
    },
    {
      "difficulty": "汎用",
      "diffRate": 10,
      "name": "口座開設（個人）PDF作成API",
      "workload": 0.05,
      "avgWorkload": 0.05,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "ワ方式本人確認申込（口座開設）",
      "workload": 0.57,
      "avgWorkload": 0.5533,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0.0167
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "ワ方式本人確認申込（諸届）",
      "workload": 0.57,
      "avgWorkload": 0.5533,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0.0167
    },
    {
      "difficulty": "汎用",
      "diffRate": 10,
      "name": "書類アップロード切替（収入情報提出（口座開設)）",
      "workload": 0.05,
      "avgWorkload": 0.05,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0
    },
    {
      "difficulty": "汎用",
      "diffRate": 10,
      "name": "書類アップロード切替（収入情報提出）",
      "workload": 0.05,
      "avgWorkload": 0.05,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0
    },
    {
      "difficulty": "汎用",
      "diffRate": 10,
      "name": "収入情報提出取引時確認登録",
      "workload": 0.05,
      "avgWorkload": 0.05,
      "isWithinStandard": true,
      "category": "API",
      "differenceFromAverage": 0
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "取引時確認登録API",
      "workload": 0.75,
      "avgWorkload": 0.5533,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.1967
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "取引時確認照会API",
      "workload": 0.47,
      "avgWorkload": 0.4071,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.0629
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "本人確認方法照会API",
      "workload": 0.47,
      "avgWorkload": 0.4071,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.0629
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "本人確認方法改竄チェックAPI",
      "workload": 0.47,
      "avgWorkload": 0.4071,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.0629
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "認証トークン要求API",
      "workload": 0.47,
      "avgWorkload": 0.4071,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.0629
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "申込照会API",
      "workload": 0.75,
      "avgWorkload": 0.5533,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.1967
    },
    {
      "difficulty": "低",
      "diffRate": 10,
      "name": "申込変更API",
      "workload": 0.47,
      "avgWorkload": 0.4071,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.0629
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "顧客（個人）登録事項変更申込書PDF作成API",
      "workload": 0.75,
      "avgWorkload": 0.5533,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.1967
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "口座開設（個人）PDF作成API",
      "workload": 0.75,
      "avgWorkload": 0.5533,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.1967
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "NEOBANK住所情報取得",
      "workload": 0.75,
      "avgWorkload": 0.5533,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.1967
    },
    {
      "difficulty": "中",
      "diffRate": 10,
      "name": "書類アップロード切替",
      "workload": 0.75,
      "avgWorkload": 0.5533,
      "isWithinStandard": false,
      "category": "API",
      "differenceFromAverage": 0.1967
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



