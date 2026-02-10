"""
SYSTEM A: DATASET PROCESSING
- Parse dataset Excel files
- Normalize to 案件一覽 & 開發工數一覽
- Calculate average workload standards by difficulty
- NO AI evaluation
"""

# ====== LAMBDA 1: ParseDatasetFile ======

import boto3
import openpyxl
from io import BytesIO
from decimal import Decimal
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
eventbridge_client = boto3.client('events')

def parse_dataset_file(file_content):
    """
    Parse dataset Excel file
    Expected format:
    Row 1: Headers
    Row 2+: Project data rows
    
    Columns:
    A: Project Number (案件番號)
    B: Total Workload (總工數)
    C: Total Screens (畫面總數)
    D: Total APIs (API總數)
    E: Project Date (案件對應日)
    F: Item ID (項目編號)
    G: Item Name (畫面・API名)
    H: Class (區分: 畫面 or API)
    I: Difficulty (難易度: 低, 中, 高)
    J: Workload (工數)
    """
    
    wb = openpyxl.load_workbook(BytesIO(file_content))
    ws = wb.active
    
    projects = {}  # Group by project number
    
    for row_idx in range(2, ws.max_row + 1):
        row = ws[row_idx]
        
        project_num = row[0].value
        total_workload = row[1].value
        total_page = row[2].value
        total_api = row[3].value
        project_day = row[4].value
        
        item_id = row[5].value
        item_name = row[6].value
        class_type = row[7].value
        difficulty = row[8].value
        workload = row[9].value
        
        if not project_num or not item_id:
            continue
        
        if project_num not in projects:
            projects[project_num] = {
                'summary': {
                    'projectNumber': str(project_num),
                    'totalWorkload': float(total_workload),
                    'totalPage': int(total_page),
                    'totalApi': int(total_api),
                    'projectDay': str(project_day)
                },
                'items': []
            }
        
        projects[project_num]['items'].append({
            'itemId': str(item_id),
            'name': str(item_name),
            'class': class_type,
            'difficulty': difficulty,
            'workload': float(workload)
        })
    
    return projects


def lambda_parse_dataset(event, context):
    """
    Lambda 1: Parse dataset file
    Trigger: S3 upload to data-input bucket
    
    Event:
    {
      "bucket": "dataset-input",
      "file_key": "datasets/historical_projects_2023.xlsx"
    }
    """
    try:
        bucket = event['bucket']
        file_key = event['file_key']
        
        print(f"[ParseDataset] Processing: s3://{bucket}/{file_key}")
        
        # Download file
        obj = s3_client.get_object(Bucket=bucket, Key=file_key)
        file_content = obj['Body'].read()
        
        # Parse
        projects = parse_dataset_file(file_content)
        
        print(f"[ParseDataset] Parsed {len(projects)} projects")
        
        # Publish event
        eventbridge_client.put_events(
            Entries=[{
                'Source': 'workload.dataset',
                'DetailType': 'DatasetParsed',
                'Detail': json.dumps({
                    'projects': projects,
                    'projectCount': len(projects),
                    'totalItems': sum(len(p['items']) for p in projects.values())
                }, default=str)
            }]
        )
        
        return {'statusCode': 200, 'projectCount': len(projects)}
        
    except Exception as e:
        print(f"[ParseDataset] Error: {str(e)}")
        return {'statusCode': 500, 'error': str(e)}


# ====== LAMBDA 2: NormalizeDataset ======

def lambda_normalize_dataset(event, context):
    """
    Lambda 2: Normalize dataset to DynamoDB
    Trigger: EventBridge (DatasetParsed)
    
    Saves to:
    - 案件一覽 (ProjectList)
    - 開發工數一覽 (DevelopmentWorkload)
    """
    try:
        projects = json.loads(event['detail']['projects'])
        
        project_list_table = dynamodb.Table('案件一覽')
        workload_table = dynamodb.Table('開發工數一覽')
        
        now = datetime.now().isoformat()
        
        for project_num, project_data in projects.items():
            # Save to 案件一覽
            summary = project_data['summary']
            project_item = {
                'projectNumber': summary['projectNumber'],
                'createdDate': now,
                'totalWorkload': Decimal(str(summary['totalWorkload'])),
                'totalPage': summary['totalPage'],
                'totalApi': summary['totalApi'],
                'projectDay': summary['projectDay'],
                'status': 'DATASET',
                'itemCount': len(project_data['items'])
            }
            
            project_list_table.put_item(Item=project_item)
            print(f"[Normalize] Saved project: {project_num}")
            
            # Save detail rows to 開發工數一覽
            for item in project_data['items']:
                workload_item = {
                    'projectNumber': project_num,
                    'itemId': item['itemId'],
                    'class': item['class'],
                    'difficulty': item['difficulty'],
                    'workload': Decimal(str(item['workload'])),
                    'name': item['name'],
                    'createdAt': now
                }
                
                workload_table.put_item(Item=workload_item)
        
        print(f"[Normalize] Successfully normalized {len(projects)} projects")
        
        # Publish event
        eventbridge_client.put_events(
            Entries=[{
                'Source': 'workload.dataset',
                'DetailType': 'DatasetNormalized',
                'Detail': json.dumps({
                    'projectCount': len(projects),
                    'status': 'Ready for standard calculation'
                })
            }]
        )
        
        return {'statusCode': 200, 'projectCount': len(projects)}
        
    except Exception as e:
        print(f"[Normalize] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'statusCode': 500, 'error': str(e)}


# ====== LAMBDA 3: CalculateAverageStandards ======

def lambda_calculate_standards(event, context):
    """
    Lambda 3: Calculate average workload standards from dataset
    Trigger: EventBridge (DatasetNormalized)
    
    Calculates average for each combination:
    - 畫面 + 低
    - 畫面 + 中
    - 畫面 + 高
    - API + 低
    - API + 中
    - API + 高
    
    Saves to 工數基準表
    NO AI - just statistical calculation
    """
    try:
        workload_table = dynamodb.Table('開發工數一覽')
        standards_table = dynamodb.Table('工數基準表')
        
        print("[CalcStandards] Calculating average workload standards...")
        
        # Scan all items from dataset
        response = workload_table.scan()
        items = response.get('Items', [])
        
        # Group by class + difficulty
        groups = {}
        for item in items:
            key = (item['class'], item['difficulty'])
            if key not in groups:
                groups[key] = []
            groups[key].append(float(item['workload']))
        
        print(f"[CalcStandards] Found {len(groups)} class/difficulty combinations")
        
        # Calculate statistics for each group
        for (class_type, difficulty), workloads in groups.items():
            count = len(workloads)
            total = sum(workloads)
            average = total / count if count > 0 else 0
            
            # Calculate variance
            variance_sum = sum((w - average) ** 2 for w in workloads)
            variance = (variance_sum / count) ** 0.5 if count > 0 else 0
            
            min_workload = min(workloads)
            max_workload = max(workloads)
            
            # Save to 工數基準表
            standard_item = {
                'class': class_type,
                'difficulty': difficulty,
                'averageWorkload': Decimal(str(round(average, 2))),
                'minWorkload': Decimal(str(min_workload)),
                'maxWorkload': Decimal(str(max_workload)),
                'sampleCount': count,
                'totalSampleWorkload': Decimal(str(total)),
                'variance': Decimal(str(round(variance, 2))),
                'updatedAt': datetime.now().isoformat()
            }
            
            standards_table.put_item(Item=standard_item)
            
            print(f"[CalcStandards] {class_type}/{difficulty}: "
                  f"avg={average:.2f}, count={count}, variance={variance:.2f}")
        
        print(f"[CalcStandards] Completed - {len(groups)} standards calculated")
        
        # Publish completion event
        eventbridge_client.put_events(
            Entries=[{
                'Source': 'workload.dataset',
                'DetailType': 'StandardsCalculated',
                'Detail': json.dumps({
                    'standardsCount': len(groups),
                    'status': 'Dataset processing complete',
                    'ready_for_user_evaluation': True
                })
            }]
        )
        
        return {
            'statusCode': 200,
            'standardsCalculated': len(groups),
            'message': 'Average workload standards calculated successfully'
        }
        
    except Exception as e:
        print(f"[CalcStandards] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'statusCode': 500, 'error': str(e)}
