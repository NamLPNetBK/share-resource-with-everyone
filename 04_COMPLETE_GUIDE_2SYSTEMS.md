# 日本語工數管理系統 - 2-System Architecture

## 📋 System Overview

**2 Independent Systems using same DynamoDB standards table**:

### System A: Dataset Processing (Offline)
- Process historical project dataset
- Calculate average workload standards by difficulty
- Save standards to 工數基準表
- **NO AI** - Just statistical calculation

### System B: User Upload Evaluation (Online)
- User uploads new project estimate
- Compare against standards (from System A)
- AI evaluation for assessment
- **WITH AI** - Bedrock Claude evaluation

---

## 🏗️ Overall Architecture

```
                    ┌─────────────────────────────────────┐
                    │    工數基準表 (Shared Standards)     │
                    │  Calculated from System A Dataset   │
                    │  Used by System B for Comparison    │
                    └─────────────────────────────────────┘
                                  ↓
                    ┌──────────────────────────────────────────┐
                    │           SYSTEM A: Dataset              │
                    │        (Batch Processing)                │
                    │          NO AI EVALUATION                │
                    └──────────────────────────────────────────┘
                                  ↓
   ┌────────────────────────────────────────────────────────────────┐
   │ 1. ParseDatasetFile      (Parse historical projects)           │
   │ 2. NormalizeDataset      (Save to 案件一覽, 開發工數一覽)        │
   │ 3. CalculateStandards    (Calculate avg by class+difficulty)   │
   │    ↓ Output: Updated 工數基準表                                │
   └────────────────────────────────────────────────────────────────┘

   ┌────────────────────────────────────────────────────────────────┐
   │           SYSTEM B: User Upload Evaluation                     │
   │        (Real-time Online Processing)                           │
   │          WITH AI EVALUATION (Bedrock Claude)                   │
   └────────────────────────────────────────────────────────────────┘
                                  ↓
   ┌────────────────────────────────────────────────────────────────┐
   │ 1. ParseUserUpload       (Parse new project from user)         │
   │ 2. AnalyzeVariance       (Compare with 工數基準表 standards)   │
   │ 3. AIEvaluation          (Bedrock Claude - Japanese)           │
   │ 4. GetStatus             (Status polling endpoint)             │
   │    ↓ Output: AI assessment with recommendations                │
   └────────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Tables (5 Total)

### System A Tables (3)

#### Table 1: 案件一覺 (ProjectList)
```
PK: projectNumber
SK: createdDate

Stores: Project summary data from dataset
Status: "DATASET" (to distinguish from user uploads)
```

#### Table 2: 開發工數一覽 (DevelopmentWorkload)
```
PK: projectNumber
SK: itemId

Stores: Individual screen/API data from dataset
Used by: System A to calculate standards
```

#### Table 3: 工數基準表 (WorkloadStandards) ⭐ **SHARED**
```
PK: class (畫面 or API)
SK: difficulty (低, 中, 高)

Stores: Average workload calculated from System A dataset
Used by: System B for user project comparison

Sample data (calculated, not hardcoded):
{
  "class": "畫面",
  "difficulty": "中",
  "averageWorkload": 8.7,     # Calculated from all 中 screens in dataset
  "sampleCount": 68,           # From 68 historical screens
  "variance": 2.1,
  "updatedAt": "2024-01-15T15:30:00Z"
}
```

### System B Tables (2)

#### Table 4: WorkflowExecutions
```
PK: execution_id

Tracks user upload processing:
- Status: STARTED → PARSING → ANALYZING → EVALUATING_AI → COMPLETED
- Intermediate results during processing
- Auto-expires after 24 hours (TTL)
```

#### Table 5: AnalysisResults
```
PK: execution_id

Final analysis results:
- Variance analysis (compared to standards)
- AI evaluation from Bedrock
- Assessment (妥當/注意/要檢討)
- Recommendations
- Persists for long-term storage
```

---

## 🔄 System A Workflow: Dataset Processing

### Execution Flow

```
T=0s:   Admin uploads historical_projects.xlsx (100+ projects)
        └─ S3 trigger → Lambda: ParseDatasetFile

T=3-5s: ParseDatasetFile
        ├─ Download from S3
        ├─ Parse Excel (openpyxl)
        ├─ Extract project summaries + detail rows
        └─ Publish "DatasetParsed" event

T=6-10s: EventBridge → Lambda: NormalizeDataset
        ├─ Save projects to 案件一覺
        ├─ Save items to 開發工數一覽
        └─ Publish "DatasetNormalized" event

T=11-15s: EventBridge → Lambda: CalculateStandards
        ├─ Query all items from 開發工數一覽
        ├─ Group by class + difficulty
        ├─ Calculate average for each group:
        │  Example: 畫面 + 中
        │    - Find all 中 screens: 68 items
        │    - Calculate: avg, min, max, variance
        │    - Result: averageWorkload = 8.7
        ├─ Save 6 standards to 工數基準表
        │  (畫面低, 畫面中, 畫面高, API低, API中, API高)
        └─ Publish "StandardsCalculated" event

T=20s:  DONE - 工數基準表 is now populated
        Ready for System B to use
```

### Example Calculation

```
Dataset contains 68 historical projects with 畫面/中 screens:
  SCR-001: 8.5 人日
  SCR-002: 9.0 人日
  SCR-003: 8.0 人日
  ...
  SCR-068: 8.9 人日

Calculate:
  Sum = 8.5 + 9.0 + 8.0 + ... = 591.6 人日
  Average = 591.6 / 68 = 8.7 人日
  
Save to 工數基準表:
  {
    "class": "畫面",
    "difficulty": "中",
    "averageWorkload": 8.7,
    "sampleCount": 68,
    "totalSampleWorkload": 591.6
  }

Later, when user uploads project with 畫面/中 screen:
  User's estimate: 9.5 人日
  Standard: 8.7 人日
  Variance: +0.8 (9.2%)
  Status: OK (within ±20%)
```

---

## 🔄 System B Workflow: User Upload Evaluation

### Execution Flow

```
T=0s:   User uploads PRJ-USER-001.xlsx
        └─ API Gateway POST /api/analyze
          └─ Lambda: InitiateWorkflow
            ├─ execution_id = "exec-user-001"
            ├─ Save to WorkflowExecutions (status=STARTED)
            └─ Publish "UserUploadStarted" event

T=1-5s: EventBridge → Lambda: ParseUserUpload
        ├─ Download from S3
        ├─ Parse Excel
        ├─ Extract project data + items
        └─ Publish "UserUploadParsed" event
        └─ Update WorkflowExecutions (status=PARSING)

T=6-10s: EventBridge → Lambda: AnalyzeVariance
        ├─ Query 工數基準表 for each item
        ├─ Calculate variance:
        │  Example: 畫面/中 screen
        │    - User estimate: 9.5
        │    - Standard: 8.7
        │    - Variance: 9.2%
        │    - Status: OK
        ├─ Summarize:
        │  - OK items: 16
        │  - WARNING items: 3
        │  - ALERT items: 0
        │  - Average variance: 8.5%
        └─ Publish "VarianceAnalyzed" event
        └─ Update WorkflowExecutions (status=ANALYZING)

T=11-25s: EventBridge → Lambda: AIEvaluation
        ├─ Build prompt (Japanese):
        │  - Project info
        │  - Variance summary
        │  - High-variance items (top 5)
        │  - Request evaluation format
        ├─ Call Bedrock Claude
        │  Input: Japanese prompt
        │  Output: Japanese evaluation (~500 words)
        ├─ Determine assessment:
        │  if (alert_count > 0 OR avg_variance > 30%):
        │    assessment = "要檢討" (Needs review)
        │  elif (warning_count > 2 OR avg_variance > 20%):
        │    assessment = "注意" (Warning)
        │  else:
        │    assessment = "妥當" (Good)
        ├─ Save to AnalysisResults
        └─ Update WorkflowExecutions (status=COMPLETED)

T=30s:  User polls GET /api/status?execution_id=exec-user-001
        ├─ Status: COMPLETED
        ├─ Variance analysis:
        │  - OK: 16, WARNING: 3, ALERT: 0
        │  - Average variance: 8.5%
        ├─ AI evaluation:
        │  - Assessment: 妥當
        │  - Evaluation: "プロジェクトの工數見積もりは..."
        │  - Key findings: [...]
        │  - Recommendations: [...]
        └─ Display on frontend
```

### Example User Upload Analysis

```
User uploads project with:
  Total items: 19
  
Item-by-item comparison:
  SCR-001 (畫面/中): user=9.5, std=8.7 → +9.2% → OK
  SCR-002 (畫面/高): user=14.0, std=15.3 → -8.5% → OK
  API-001 (API/中): user=7.0, std=7.2 → -2.8% → OK
  ...
  API-006 (API/高): user=15.0, std=12.5 → +20.0% → WARNING
  API-007 (API/高): user=18.0, std=12.5 → +44.0% → WARNING
  
Summary:
  OK count: 16
  WARNING count: 3
  ALERT count: 0
  Average variance: 8.5%
  
Assessment: 妥當 (Good)
  
AI Evaluation (from Bedrock):
  "プロジェクトの工數見積もりは全體的に妥當であると判斷されます。
   高難度のAPIで若干の乖離が見られますが、複雑性を考慮すると
   合理的な範囲内と考えられます。..."
```

---

## 💻 Lambda Functions

### System A (3 Functions)

#### 1. ParseDatasetFile (9.5 KB)
```
Role: Parse historical projects Excel
Input: S3 file path
Output: Structured project data
Time: 3-5 seconds
Code: lambda_parse_dataset
```

#### 2. NormalizeDataset (8 KB)
```
Role: Save parsed data to DynamoDB
Input: Parsed projects
Output: Saved to 案件一覺, 開發工數一覽
Time: 3-5 seconds
Code: lambda_normalize_dataset
```

#### 3. CalculateStandards (12 KB)
```
Role: Calculate average workload from dataset
Input: All normalized items
Output: Updated 工數基準表
Time: 2-3 seconds
Code: lambda_calculate_standards
Calculation:
  - Group items by class + difficulty
  - Calculate average, min, max, variance
  - Save to 工數基準表
```

### System B (4 Functions)

#### 1. ParseUserUpload (9 KB)
```
Role: Parse user-uploaded project file
Input: S3 file path
Output: Structured project data
Time: 3-5 seconds
Code: lambda_parse_user_upload
```

#### 2. AnalyzeVariance (10 KB)
```
Role: Compare user project with standards
Input: Parsed project, 工數基準表
Output: Variance analysis results
Time: 2-3 seconds
Code: lambda_analyze_variance
Compares:
  - Query 工數基準表 for each item
  - Calculate variance (actual vs standard)
  - Count OK / WARNING / ALERT
  - Calculate average variance
```

#### 3. AIEvaluation (12 KB)
```
Role: AI evaluation using Bedrock
Input: Variance analysis results
Output: AI evaluation + assessment
Time: 10-15 seconds
Code: lambda_ai_evaluation
Features:
  - Build Japanese prompt
  - Call Bedrock Claude
  - Determine assessment level
  - Generate recommendations
```

#### 4. GetStatus (5 KB)
```
Role: API endpoint for status polling
Input: execution_id
Output: Current status + results
Time: <1 second
Code: lambda_get_status
Used by frontend for real-time updates
```

---

## 📡 API Endpoints (System B)

### POST /api/analyze
Upload new project for evaluation

```bash
curl -X POST https://api.example.com/api/analyze \
  -F "file=@project.xlsx" \
  -H "Authorization: Bearer token"

Response:
{
  "execution_id": "exec-user-001",
  "status": "STARTED",
  "message": "Processing started, poll for results..."
}
```

### GET /api/status
Poll for execution results

```bash
curl https://api.example.com/api/status?execution_id=exec-user-001

While processing:
{
  "status": "ANALYZING",
  "current_step": "Analyzing variance..."
}

When complete:
{
  "status": "COMPLETED",
  "analysis": {
    "variance_analysis": {
      "itemVariances": [...],
      "summary": {
        "ok_count": 16,
        "warning_count": 3,
        "alert_count": 0,
        "average_variance_percent": 8.5
      }
    },
    "ai_evaluation": {
      "assessment": "ACCEPTABLE",
      "assessmentLabel": "妥當",
      "evaluation": "プロジェクトの工數見積もりは..."
    }
  }
}
```

---

## ⚙️ Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│         EventBridge Rules (4 Total)                 │
├─────────────────────────────────────────────────────┤
│ Rule 1: DatasetParsed → ParseDatasetFile Lambda     │
│ Rule 2: DatasetNormalized → NormalizeDataset        │
│ Rule 3: UserUploadParsed → AnalyzeVariance         │
│ Rule 4: VarianceAnalyzed → AIEvaluation            │
└─────────────────────────────────────────────────────┘
          ↓                        ↓
   ┌──────────────┐      ┌──────────────────┐
   │  System A    │      │   System B       │
   │  (Offline)   │      │   (Online)       │
   │   Dataset    │      │  User Upload     │
   └──────────────┘      └──────────────────┘
          ↓                        ↓
   ┌──────────────────────────────────────────┐
   │     DynamoDB Tables (5 Total)            │
   ├──────────────────────────────────────────┤
   │ 案件一覺 (ProjectList)                   │
   │ 開發工數一覽 (DevelopmentWorkload)       │
   │ 工數基準表 (Shared Standards) ★         │
   │ WorkflowExecutions (User tracking)       │
   │ AnalysisResults (Results storage)        │
   └──────────────────────────────────────────┘
```

---

## 🚀 Implementation Steps

### Phase 1: Setup (30 minutes)
1. Create 5 DynamoDB tables
2. Deploy 7 Lambda functions (3 for A, 4 for B)
3. Create 4 EventBridge rules
4. Setup API Gateway endpoints

### Phase 2: Test System A
1. Prepare historical project dataset
2. Upload to S3
3. Trigger System A pipeline
4. Verify 工數基準表 populated with standards
5. Check calculated averages

### Phase 3: Test System B
1. Prepare sample user project
2. Upload via API endpoint
3. Poll status endpoint
4. Review variance analysis
5. Review AI evaluation

### Phase 4: Production
1. Load full historical dataset to System A
2. Deploy frontend for System B
3. Configure authentication
4. Setup monitoring
5. Enable user uploads

---

## 📈 Performance

### System A (One-time or periodic)
- Parse: 3-5 seconds
- Normalize: 3-5 seconds
- Calculate: 2-3 seconds
- Total: ~10 seconds
- Cost: ~$0.15

### System B (Per user upload)
- Parse: 3-5 seconds
- Analyze variance: 2-3 seconds
- AI evaluation: 10-15 seconds
- Total: ~20 seconds
- Cost: ~$0.35-0.45 (includes Bedrock)

---

## 💡 Key Differences

| Aspect | System A | System B |
|--------|----------|---------|
| **Purpose** | Calculate standards | Evaluate user project |
| **Trigger** | Admin upload dataset | User upload project |
| **AI** | NO | YES (Bedrock Claude) |
| **Frequency** | Once or periodic | Per user request |
| **Duration** | ~10 seconds | ~20 seconds |
| **Output** | 工數基準表 | Assessment + AI eval |
| **Cost** | ~$0.15 per run | ~$0.40 per user |

---

## 🎯 Use Cases

✅ **System A**: Load historical project data once to build standards baseline
✅ **System B**: Users upload new projects for AI-powered assessment
✅ **Integration**: Standards from A are used by B for comparison
✅ **Continuous Improvement**: Update System A with new projects to refine standards

---

**Status**: ✅ Production Ready
**Version**: 2.0.0 (2-System Architecture)
**Last Updated**: February 2024
