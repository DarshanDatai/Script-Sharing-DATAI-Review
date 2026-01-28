import random
import csv
from label_studio_sdk import LabelStudio

# 1. Setup
LS_URL = "http://35.247.144.173"
API_KEY = "722c55e67bcf557625372f7c0eb18a85110aa69e"
PROJECT_ID = 53 
VIEW_COUNT = 2
TOTAL_TARGET_MINUTES = 54
TARGET_SECONDS_PER_VIEW = (TOTAL_TARGET_MINUTES * 60) / VIEW_COUNT # 1620 seconds per view

ls = LabelStudio(base_url=LS_URL, api_key=API_KEY)

print(f"Fetching tasks from Project {PROJECT_ID}...")

# 2. Fetch tasks and filter for 0-20s duration
task_pager = ls.tasks.list(project=PROJECT_ID, fields="all")
eligible_tasks = []

for task in task_pager:
    # Only include annotated tasks that fall within 0-20 seconds
    if task.annotations:
        duration = task.data.get("duration_s", 0)
        if 0 < duration <= 20:
            eligible_tasks.append(task)
    
    # Safety break to avoid scanning 100k tasks if we already have enough pool
    if len(eligible_tasks) >= 10000:
        break

# 3. Randomize and Distribute into 2 Batches
random.shuffle(eligible_tasks)

used_task_ids = set()
batches = []

for i in range(VIEW_COUNT):
    current_batch_tasks = []
    current_batch_duration = 0.0
    
    for task in eligible_tasks:
        if task.id in used_task_ids:
            continue
            
        duration = task.data.get("duration_s", 0)
        
        if current_batch_duration + duration <= TARGET_SECONDS_PER_VIEW:
            current_batch_tasks.append(task)
            used_task_ids.add(task.id)
            current_batch_duration += duration
        
        if current_batch_duration >= TARGET_SECONDS_PER_VIEW:
            break
            
    batches.append({
        "tasks": current_batch_tasks,
        "duration": current_batch_duration
    })

# 4. Create Views and Export CSVs
for idx, batch in enumerate(batches, 1):
    batch_tasks = batch["tasks"]
    if not batch_tasks:
        print(f"Warning: Not enough unique tasks for Batch {idx}.")
        continue
    
    # --- Create Label Studio View ---
    task_ids = [t.id for t in batch_tasks]
    ls.views.create(
        project=PROJECT_ID,
        data={
            "title": f"Review Batch {idx} (27m | 0-20s Audio)",
            "filters": {
                "conjunction": "or",
                "items": [{"filter": "filter:tasks:id", "operator": "equal", "type": "Number", "value": tid} for tid in task_ids]
            }
        }
    )

    # --- Create CSV ---
    csv_filename = f"review_batch_{idx}_0-20s_export.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['task_id', 'annotator_id', 'duration_s', 'corrected_text'])
        
        for task in batch_tasks:
            for ann in task.annotations:
                if not ann.get('was_cancelled', False):
                    uid = ann.get('completed_by')
                    results = ann.get('result', [])
                    
                    text = ""
                    for r in results:
                        if r.get('type') == 'textarea':
                            txt_vals = r.get('value', {}).get('text', [])
                            if txt_vals and txt_vals[0].strip():
                                text = txt_vals[0]
                                break
                    
                    writer.writerow([task.id, uid, task.data.get("duration_s"), text])
                    break 

    print(f"Success: Created 'Review Batch {idx}' and '{csv_filename}' ({round(batch['duration'] / 60, 2)} mins).")

print(f"\nFinished. Processed {TOTAL_TARGET_MINUTES} minutes total across 2 views.")