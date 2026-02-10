"""
DynamoDB Schema - 2 Systems Architecture

System A: Dataset Processing (Chuẩn hóa công số)
- 案件一覧: Project master data
- 開発工数一覧: Screen/API detail rows
- 工数基準表: Average workload standards (calculated from dataset)

System B: User Upload Evaluation (Đánh giá dự án mới)
- WorkflowExecutions: Track user upload processing
- AnalysisResults: Final AI evaluation results
"""

# ===== SYSTEM A: DATASET PROCESSING =====

# Table 1: 案件一覽 (ProjectList) - Master data from dataset
{
    "TableName": "案件一覽",
    "AttributeDefinitions": [
        {"AttributeName": "projectNumber", "AttributeType": "S"},
        {"AttributeName": "createdDate", "AttributeType": "S"}
    ],
    "KeySchema": [
        {"AttributeName": "projectNumber", "KeyType": "HASH"},
        {"AttributeName": "createdDate", "KeyType": "RANGE"}
    ],
    "BillingMode": "PAY_PER_REQUEST"
}

# Sample item:
{
    "projectNumber": "PRJ-2024-001",
    "createdDate": "2024-01-15T10:00:00Z",
    "totalWorkload": 120.5,
    "totalPage": 15,
    "totalApi": 8,
    "projectDay": "2024-01-20",
    "status": "COMPLETED",
    "statistics": {
        "avgWorkloadPerScreen": 8.03,
        "avgWorkloadPerApi": 15.06
    }
}


# Table 2: 開發工數一覧 (DevelopmentWorkload) - Detail rows from dataset
{
    "TableName": "開發工數一覧",
    "AttributeDefinitions": [
        {"AttributeName": "projectNumber", "AttributeType": "S"},
        {"AttributeName": "itemId", "AttributeType": "S"}
    ],
    "KeySchema": [
        {"AttributeName": "projectNumber", "KeyType": "HASH"},
        {"AttributeName": "itemId", "KeyType": "RANGE"}
    ],
    "BillingMode": "PAY_PER_REQUEST"
}

# Sample item:
{
    "projectNumber": "PRJ-2024-001",
    "itemId": "SCR-001",
    "class": "畫面",          # 畫面 or API
    "difficulty": "中",      # 低, 中, 高
    "workload": 8.5,        # 工数
    "name": "登入畫面",
    "createdAt": "2024-01-15T10:00:00Z"
}


# Table 3: 工數基準表 (WorkloadStandards) - CALCULATED FROM DATASET
# This table is populated by System A (no user input)
# Contains: average workload by class + difficulty
{
    "TableName": "工數基準表",
    "AttributeDefinitions": [
        {"AttributeName": "class", "AttributeType": "S"},
        {"AttributeName": "difficulty", "AttributeType": "S"}
    ],
    "KeySchema": [
        {"AttributeName": "class", "KeyType": "HASH"},
        {"AttributeName": "difficulty", "KeyType": "RANGE"}
    ],
    "BillingMode": "PAY_PER_REQUEST"
}

# Sample items (calculated from historical projects):
{
    "class": "畫面",
    "difficulty": "低",
    "averageWorkload": 4.2,        # Average from 42 screens
    "minWorkload": 2.5,
    "maxWorkload": 6.0,
    "sampleCount": 42,
    "totalSampleWorkload": 176.4,  # For recalculation
    "variance": 1.2,
    "updatedAt": "2024-01-15T15:30:00Z"
}

{
    "class": "畫面",
    "difficulty": "中",
    "averageWorkload": 8.7,        # Average from 68 screens
    "minWorkload": 6.0,
    "maxWorkload": 12.0,
    "sampleCount": 68,
    "totalSampleWorkload": 591.6,
    "variance": 2.1,
    "updatedAt": "2024-01-15T15:30:00Z"
}

{
    "class": "畫面",
    "difficulty": "高",
    "averageWorkload": 15.3,       # Average from 35 screens
    "minWorkload": 10.0,
    "maxWorkload": 22.0,
    "sampleCount": 35,
    "totalSampleWorkload": 535.5,
    "variance": 3.5,
    "updatedAt": "2024-01-15T15:30:00Z"
}

{
    "class": "API",
    "difficulty": "低",
    "averageWorkload": 3.1,        # Average from 55 APIs
    "minWorkload": 1.5,
    "maxWorkload": 5.0,
    "sampleCount": 55,
    "totalSampleWorkload": 170.5,
    "variance": 0.9,
    "updatedAt": "2024-01-15T15:30:00Z"
}

{
    "class": "API",
    "difficulty": "中",
    "averageWorkload": 7.2,        # Average from 72 APIs
    "minWorkload": 5.0,
    "maxWorkload": 10.0,
    "sampleCount": 72,
    "totalSampleWorkload": 518.4,
    "variance": 1.8,
    "updatedAt": "2024-01-15T15:30:00Z"
}

{
    "class": "API",
    "difficulty": "高",
    "averageWorkload": 12.5,       # Average from 48 APIs
    "minWorkload": 9.0,
    "maxWorkload": 18.0,
    "sampleCount": 48,
    "totalSampleWorkload": 600.0,
    "variance": 2.8,
    "updatedAt": "2024-01-15T15:30:00Z"
}


# ===== SYSTEM B: USER UPLOAD EVALUATION =====

# Table 4: WorkflowExecutions - Track user upload processing
{
    "TableName": "WorkflowExecutions",
    "AttributeDefinitions": [
        {"AttributeName": "execution_id", "AttributeType": "S"}
    ],
    "KeySchema": [
        {"AttributeName": "execution_id", "KeyType": "HASH"}
    ],
    "BillingMode": "PAY_PER_REQUEST",
    "TTL": {
        "AttributeName": "ttl",
        "Enabled": True  # Auto-delete after 24 hours
    }
}

# Sample item:
{
    "execution_id": "exec-user-001",
    "userId": "user@example.com",
    "uploadedAt": "2024-01-20T14:00:00Z",
    "status": "COMPLETED",  # STARTED, PARSING, ANALYZING, COMPLETED, FAILED
    "current_step": "AI evaluation complete",
    "parsed_data": {
        "projectNumber": "PRJ-USER-001",
        "totalWorkload": 95.0,
        "totalPage": 12,
        "totalApi": 7,
        "projectDay": "2024-01-20",
        "items": [...]
    },
    "analysis_result": {
        "itemVariances": [...],
        "similarityToStandards": {...}
    },
    "ai_evaluation": {
        "overallAssessment": "NEEDS_REVIEW",
        "assessmentLabel": "要檢討",
        "evaluation": "AI analysis text..."
    },
    "ttl": 1705785600,  # Unix timestamp for expiry
    "error_msg": null
}


# Table 5: AnalysisResults - Final AI evaluation results
{
    "TableName": "AnalysisResults",
    "AttributeDefinitions": [
        {"AttributeName": "execution_id", "AttributeType": "S"}
    ],
    "KeySchema": [
        {"AttributeName": "execution_id", "KeyType": "HASH"}
    ],
    "BillingMode": "PAY_PER_REQUEST"
}

# Sample item:
{
    "execution_id": "exec-user-001",
    "projectNumber": "PRJ-USER-001",
    "analysisDate": "2024-01-20T14:05:00Z",
    "projectData": {
        "totalWorkload": 95.0,
        "totalPage": 12,
        "totalApi": 7,
        "projectDay": "2024-01-20"
    },
    
    "variance_analysis": {
        "itemVariances": [
            {
                "itemId": "SCR-001",
                "name": "登入畫面",
                "class": "畫面",
                "difficulty": "中",
                "actual": 9.0,
                "standard": 8.7,
                "variance": 0.3,
                "variancePercent": 3.4,
                "status": "OK"
            },
            {
                "itemId": "API-005",
                "name": "搜尋API",
                "class": "API",
                "difficulty": "高",
                "actual": 18.0,
                "standard": 12.5,
                "variance": 5.5,
                "variancePercent": 44.0,
                "status": "WARNING"
            }
        ],
        "summary": {
            "ok_count": 16,
            "warning_count": 3,
            "alert_count": 0,
            "average_variance_percent": 8.5
        }
    },
    
    "ai_evaluation": {
        "overallAssessment": "ACCEPTABLE",  # ACCEPTABLE, CAUTION, NEEDS_REVIEW
        "assessmentLabel": "妥當",
        "evaluation": "AI評論文本 (日文)...",
        "keyFindings": [
            "項目的估算整體符合標準",
            "搜尋API有44%的差異,值得注意",
            "建議進一步確認複雜API的估算"
        ],
        "recommendations": [
            "複查高難度API的估算方法",
            "與團隊討論搜尋功能的複雜性"
        ]
    }
}


# ===== DynamoDB Setup Commands =====

"""
# Create SYSTEM A tables

# Table 1: 案件一覽
aws dynamodb create-table \
  --table-name 案件一覽 \
  --attribute-definitions AttributeName=projectNumber,AttributeType=S \
                           AttributeName=createdDate,AttributeType=S \
  --key-schema AttributeName=projectNumber,KeyType=HASH \
                AttributeName=createdDate,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Table 2: 開發工數一覽
aws dynamodb create-table \
  --table-name 開發工數一覽 \
  --attribute-definitions AttributeName=projectNumber,AttributeType=S \
                           AttributeName=itemId,AttributeType=S \
  --key-schema AttributeName=projectNumber,KeyType=HASH \
                AttributeName=itemId,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Table 3: 工數基準表 (CALCULATED FROM DATASET)
aws dynamodb create-table \
  --table-name 工數基準表 \
  --attribute-definitions AttributeName=class,AttributeType=S \
                           AttributeName=difficulty,AttributeType=S \
  --key-schema AttributeName=class,KeyType=HASH \
                AttributeName=difficulty,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST


# Create SYSTEM B tables

# Table 4: WorkflowExecutions
aws dynamodb create-table \
  --table-name WorkflowExecutions \
  --attribute-definitions AttributeName=execution_id,AttributeType=S \
  --key-schema AttributeName=execution_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --ttl-attribute-name ttl

# Table 5: AnalysisResults
aws dynamodb create-table \
  --table-name AnalysisResults \
  --attribute-definitions AttributeName=execution_id,AttributeType=S \
  --key-schema AttributeName=execution_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
"""
