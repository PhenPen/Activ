import pandas as pd
import hashlib
import os
from datetime import datetime

CSV_FILE = "activity_log.csv"

def generate_activity_id(activity):
    """Generates a unique ID for an activity based on its content."""
    # Combine relevant fields to create a unique signature
    unique_string = f"{activity.get('market_name')}_{activity.get('description')}_{activity.get('type')}"
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

def load_existing_activities():
    if not os.path.exists(CSV_FILE):
        return set()
    try:
        df = pd.read_csv(CSV_FILE)
        if 'id' in df.columns:
            return set(df['id'].tolist())
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return set()

def save_new_activities(activities):
    """
    Saves new activities to the CSV file.
    Returns the count of new items added.
    """
    existing_ids = load_existing_activities()
    new_items = []
    
    current_scrape_time = datetime.now().isoformat()

    for item in activities:
        item_id = generate_activity_id(item)
        
        if item_id not in existing_ids:
            # enrich with scrape time and id
            item['id'] = item_id
            item['scraped_at'] = current_scrape_time
            new_items.append(item)
            existing_ids.add(item_id) # prevent dupes within the same batch

    if new_items:
        df_new = pd.DataFrame(new_items)
        # Append to CSV
        header = not os.path.exists(CSV_FILE)
        df_new.to_csv(CSV_FILE, mode='a', header=header, index=False)
        print(f"Saved {len(new_items)} new activities.")
    else:
        print("No new activities found.")
    
    return len(new_items)
