import random
import csv
from label_studio_sdk import LabelStudio

# 1. Setup
LS_URL = "http://35.247.144.173"
API_KEY = "722c55e67bcf557625372f7c0eb18a85110aa69e"
PROJECT_ID = 53 

# 2. Define our 3 Review Tiers (min_sec, max_sec, target_min)
BATCH_CONFIGS = [
    {"min": 20,  "max": 60,   "target_m": 42, "title": "Review 20-60s"},
    {"min": 60,  "max": 100,  "target_m": 14, "title": "Review 60-100s"},
    {"min": 100, "max": 9999, "target_m": 10, "title": "Review 100s Plus"}
]

ls = LabelStudio(base_url=LS_URL, api_key=API_KEY)

print(f"Fetching tasks from Project {PROJECT_ID}...")

# 3. Categorize Tasks into Pools
task_pager = ls.tasks.list(project=PROJECT_ID, fields="all")
pools = {i: [] for i in range(len(BATCH_CONFIGS))}

for task in task_pager:
    if task.annotations:
        duration = task.data.get("duration_s", 0)
        
        for idx, config in enumerate(BATCH_CONFIGS):
            if config["min"] <= duration < config["max"]:
                pools[idx].append(task)
                break
    
    # Stop if all pools have a healthy amount of tasks (e.g., 2000 per pool)
    if all(len(p) >= 2000 for p in pools.values()):
        break

# 4. Process Each Batch
for idx, config in enumerate(BATCH_CONFIGS):
    pool = pools[idx]
    random.shuffle(pool)
    
    target_seconds = config["target_m"] * 60
    selected_tasks = []
    current_duration = 0.0
    
    for task in pool:
        duration = task.data.get("duration_s", 0)
        if current_duration + duration <= target_seconds:
            selected_tasks.append(task)
            current_duration += duration
        if current_duration >= target_seconds:
            break
            
    if not selected_tasks:
        print(f"No tasks found for {config['title']}")
        continue

    # --- Create Label Studio View ---
    task_ids = [t.id for t in selected_tasks]
    ls.views.create(
        project=PROJECT_ID,
        data={
            "title": f"{config['title']} ({config['target_m']}m)",
            "filters": {
                "conjunction": "or",
                "items": [{"filter": "filter:tasks:id", "operator": "equal", "type": "Number", "value": tid} for tid in task_ids]
            }
        }
    )

    # --- Create CSV ---
    csv_filename = f"{config['title'].replace(' ', '_').lower()}.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['task_id', 'annotator_id', 'duration_s', 'corrected_text'])
        
        for task in selected_tasks:
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

    print(f"Created: {config['title']} | Duration: {round(current_duration/60, 2)}m | File: {csv_filename}")

print("\nAll views and CSVs generated.")