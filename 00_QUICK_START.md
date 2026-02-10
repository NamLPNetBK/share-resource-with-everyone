# Quick Start Guide - 2-System Japanese Workload Architecture

## 🎯 What You Have

### 2 Independent Systems
1. **System A**: Dataset processing → Calculate standards (NO AI)
2. **System B**: User upload evaluation → AI assessment (WITH AI)

### Files Provided
- **04_COMPLETE_GUIDE_2SYSTEMS.md** ← START HERE (Full architecture)
- **01_DATABASE_SCHEMA_2SYSTEMS.py** (5 DynamoDB tables)
- **02_SYSTEM_A_LAMBDAS.py** (3 Lambda functions)
- **03_SYSTEM_B_LAMBDAS.py** (4 Lambda functions)

---

## ⚡ 5-Minute Overview

### System A: Dataset Processing
```
1. Admin uploads historical_projects.xlsx (100+ historical projects)
2. System A parses and normalizes the data
3. System A calculates average workload by difficulty:
   - 畫面/低: average 4.2 人日 (from 42 screens)
   - 畫面/中: average 8.7 人日 (from 68 screens)
   - 畫面/高: average 15.3 人日 (from 35 screens)
   - API/低: average 3.1 人日 (from 55 APIs)
   - API/中: average 7.2 人日 (from 72 APIs)
   - API/高: average 12.5 人日 (from 48 APIs)
4. Results saved to 工數基準表 (shared standards table)

⏱️ Takes ~10 seconds, one-time or periodic
💰 Cost: ~$0.15 per run
```

### System B: User Upload Evaluation
```
1. User uploads new project (PRJ-USER-001.xlsx)
2. System B parses the project
3. System B compares each item with standards from System A:
   - User's 畫面/中 screen: 9.5 人日
   - Standard: 8.7 人日
   - Variance: +9.2% → OK ✓
   
   - User's API/高: 18.0 人日
   - Standard: 12.5 人日
   - Variance: +44.0% → WARNING ⚠️
4. System B calls Bedrock Claude for AI evaluation
5. AI returns assessment: 妥當 / 注意 / 要檢討
   + Recommendations in Japanese

⏱️ Takes ~20 seconds per user upload
💰 Cost: ~$0.40 per upload (includes Bedrock)
```

---

## 📋 Deployment Checklist

### Pre-Deployment (Day 1)
- [ ] Review 04_COMPLETE_GUIDE_2SYSTEMS.md
- [ ] Review database schema (01_DATABASE_SCHEMA_2SYSTEMS.py)
- [ ] Review code comments in Lambda functions
- [ ] AWS account with Bedrock access enabled
- [ ] Prepare historical project dataset (for System A)

### Database Setup (30 minutes)
- [ ] Create 5 DynamoDB tables:
  ```bash
  aws dynamodb create-table --table-name 案件一覺 ...
  aws dynamodb create-table --table-name 開發工數一覽 ...
  aws dynamodb create-table --table-name 工數基準表 ...
  aws dynamodb create-table --table-name WorkflowExecutions ...
  aws dynamodb create-table --table-name AnalysisResults ...
  ```

### Lambda Deployment (30 minutes)
- [ ] Package System A Lambda functions (3):
  - ParseDatasetFile
  - NormalizeDataset
  - CalculateStandards
  
- [ ] Package System B Lambda functions (4):
  - ParseUserUpload
  - AnalyzeVariance
  - AIEvaluation
  - GetStatus

### EventBridge Setup (15 minutes)
- [ ] Create 4 EventBridge rules:
  ```
  Rule 1: DatasetParsed → ParseDatasetFile Lambda
  Rule 2: DatasetNormalized → NormalizeDataset Lambda
  Rule 3: UserUploadParsed → AnalyzeVariance Lambda
  Rule 4: VarianceAnalyzed → AIEvaluation Lambda
  ```

### API Gateway (20 minutes)
- [ ] Create REST API
- [ ] Create endpoints:
  - POST /api/analyze (triggers System B)
  - GET /api/status (polls for results)

### Testing (30 minutes)
#### Test System A:
- [ ] Upload historical project dataset
- [ ] Verify Lambda execution
- [ ] Check 工數基準表 populated with 6 standards
- [ ] Verify calculations are correct

#### Test System B:
- [ ] Upload sample user project
- [ ] GET /api/status to track progress
- [ ] Verify variance analysis
- [ ] Review AI evaluation output

---

## 📊 File Structure

```
1. Database Schema & Setup
   └─ 01_DATABASE_SCHEMA_2SYSTEMS.py
      Contains: 5 table definitions, sample data, AWS CLI commands

2. System A: Dataset Processing (NO AI)
   ├─ Lambda 1: ParseDatasetFile (Parse historical projects)
   ├─ Lambda 2: NormalizeDataset (Save to DynamoDB)
   └─ Lambda 3: CalculateStandards (Calculate averages)
   
   Code: 02_SYSTEM_A_LAMBDAS.py

3. System B: User Upload Evaluation (WITH AI)
   ├─ Lambda 1: ParseUserUpload (Parse user project)
   ├─ Lambda 2: AnalyzeVariance (Compare with standards)
   ├─ Lambda 3: AIEvaluation (Bedrock Claude evaluation)
   └─ Lambda 4: GetStatus (API status endpoint)
   
   Code: 03_SYSTEM_B_LAMBDAS.py

4. Complete Guide
   └─ 04_COMPLETE_GUIDE_2SYSTEMS.md
      Contains: Architecture, workflows, examples, deployment steps
```

---

## 🔑 Key Concepts

### 工數基準表 (Shared Standards Table)
```
This table is:
✅ CREATED by System A (calculated from dataset)
✅ USED by System B (for comparison with user projects)
✅ UPDATED periodically when System A runs with new data

Structure:
{
  "class": "畫面",        # 畫面 or API
  "difficulty": "中",    # 低, 中, 高
  "averageWorkload": 8.7, # Calculated from all 中 screens
  "sampleCount": 68,     # From 68 historical screens
  "variance": 2.1
}
```

### Variance Calculation
```
For each item in user project:
  variance = (actual - standard) / standard * 100
  
Example:
  User's 畫面/中 screen: 9.5 人日
  Standard: 8.7 人日 (from 工數基準表)
  Variance: (9.5 - 8.7) / 8.7 * 100 = 9.2%
  Status: OK (≤ ±20%)
```

### Assessment Levels (System B Only)
```
妥當 (Good/Acceptable)
  → All items OK, average variance ≤ 20%
  → No alerts, ≤ 2 warnings

注意 (Warning/Caution)
  → Some items have warnings
  → Average variance 20-30%
  → ≥ 3 warnings or 1+ alerts

要檢討 (Needs Review)
  → Average variance > 30%
  → 2+ alerts
  → Requires careful review
```

---

## 🚀 How to Run

### System A: One-Time Setup (Admin Task)
```bash
# 1. Prepare historical projects dataset
# File format: PROJECT_NUM | TOTAL_WL | SCREENS | APIS | DATE | ITEM_ID | NAME | CLASS | DIFF | WORKLOAD

# 2. Upload to S3
aws s3 cp historical_projects.xlsx s3://dataset-input/

# 3. Trigger System A processing
# Event: {bucket: "dataset-input", file_key: "historical_projects.xlsx"}

# 4. Check results
# Query 工數基準表 to see calculated standards
aws dynamodb scan --table-name 工數基準表

# 5. Verify: Should have 6 standards (畫面低/中/高, API低/中/高)
```

### System B: Per User (Repeatable)
```bash
# 1. User uploads project via web UI
# curl -X POST /api/analyze -F "file=@project.xlsx"
# Returns: execution_id

# 2. Poll for results
# curl /api/status?execution_id=exec-user-001

# 3. When status == "COMPLETED"
# Get: variance analysis + AI evaluation

# 4. Display to user on frontend
```

---

## 📈 Cost Estimate

### System A (One-time)
- Lambda (3 functions): $0.05
- DynamoDB writes: $0.05
- EventBridge: $0.01
- **Total: ~$0.15**

### System B (Per user upload)
- Lambda (4 functions): $0.10
- DynamoDB reads/writes: $0.05
- Bedrock Claude: $0.20-0.30
- EventBridge: $0.01
- **Total: ~$0.35-0.45**

### Monthly (Example: 1000 user uploads)
- System A: $0.15 (once or monthly)
- System B: $0.35-0.45 × 1000 = $350-450
- **Total: ~$350-450/month**

---

## 🔗 Data Flow Examples

### System A Example
```
Dataset file contains:
  Project 1: 15 screens, 8 APIs
    - SCR-001: 畫面/中, 8.5 人日
    - SCR-002: 畫面/中, 9.0 人日
    - API-001: API/中, 7.0 人日
  ...
  Project 68: 12 screens, 7 APIs
    - SCR-N: 畫面/中, 8.9 人日

System A processes and calculates:
  畫面/中 average = (8.5 + 9.0 + ... + 8.9) / 68 = 8.7 人日
  API/中 average = (7.0 + ... ) / 72 = 7.2 人日
  ...

Saves to 工數基準表
```

### System B Example
```
User uploads:
  Project: PRJ-USER-001
  - SCR-001: 畫面/中, 9.5 人日 (vs std 8.7 → +9.2% OK)
  - API-001: API/中, 7.0 人日 (vs std 7.2 → -2.8% OK)
  ...
  Total: 16 OK, 3 WARNING, 0 ALERT

AI Evaluation (Japanese):
  "プロジェクトの工數見積もりは全體的に妥當であると
   判斷されます。注意が必要な項目が3件ありますが、
   整體的な精度は良好です。..."

Assessment: 妥當
```

---

## ❓ FAQs

**Q: Can I run System B without System A?**
A: No, System B needs the standards from System A. Run System A first to populate 工數基準表.

**Q: How often should I run System A?**
A: As often as you add new historical projects. Maybe weekly/monthly. Recalculates averages with new data.

**Q: Can I customize the standards?**
A: Yes, edit 工數基準表 directly or update System A calculation logic.

**Q: How long does System B take?**
A: ~20 seconds per user upload (AI evaluation takes most time).

**Q: What if AI evaluation fails?**
A: Lambda has error handling. Workflow saves to "FAILED" status. Error message is logged.

**Q: Can I change the assessment criteria?**
A: Yes, edit lambda_analyze_variance in 03_SYSTEM_B_LAMBDAS.py to adjust OK/WARNING/ALERT thresholds.

**Q: Does System B need internet?**
A: Yes, to call Bedrock Claude. Other parts are AWS-internal.

**Q: Can I integrate with other systems?**
A: Yes, API endpoints can be called from any system. EventBridge can trigger external webhooks.

---

## 📞 Support

### Documentation
- Full guide: **04_COMPLETE_GUIDE_2SYSTEMS.md**
- Database: **01_DATABASE_SCHEMA_2SYSTEMS.py**
- Code: **02_SYSTEM_A_LAMBDAS.py** & **03_SYSTEM_B_LAMBDAS.py**

### Troubleshooting
1. **Standards not calculated**: Check System A Lambda logs
2. **Variance calculation wrong**: Verify 工數基準表 has correct standards
3. **AI not responding**: Check Bedrock access permissions
4. **User upload fails**: Verify Excel file format matches expected columns

---

## ✅ Summary

✨ **System A** = Build standards from historical data (one-time)
✨ **System B** = Evaluate new projects against standards with AI (per-user)
✨ **工數基準表** = Shared standards table connecting both systems
✨ **No Hardcoding** = Standards are calculated, not hardcoded

**Ready to start? → Read 04_COMPLETE_GUIDE_2SYSTEMS.md**

---

**Version**: 2.0.0
**Status**: ✅ Production Ready
**Last Updated**: February 2024
