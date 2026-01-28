import pandas as pd

# 1. Configuration - Change these filenames to match yours
LARGE_CSV_FILE = 'SA0127.csv'   # Your 93k+ row file
TARGET_IDS_FILE = 'ids.txt' # Your file with 286 IDs
OUTPUT_FILE = 'extracted_results.csv'
ID_COLUMN_NAME = 'id'              # The name of the first column

def extract_rows():
    try:
        # 2. Load the target IDs from the text file
        print(f"Reading target IDs from {TARGET_IDS_FILE}...")
        with open(TARGET_IDS_FILE, 'r') as f:
            # strip() removes newlines/spaces; excludes empty lines
            target_ids = [line.strip() for line in f if line.strip()]
        
        # 3. Load the large CSV
        print(f"Loading {LARGE_CSV_FILE}...")
        df = pd.read_csv(LARGE_CSV_FILE)

        # 4. Data Type Alignment
        # CSVs often read IDs as numbers, but text files read them as strings.
        # We convert both to strings to ensure they match perfectly.
        df[ID_COLUMN_NAME] = df[ID_COLUMN_NAME].astype(str)
        target_ids = [str(i) for i in target_ids]

        # 5. Filter the data
        print(f"Searching for {len(target_ids)} IDs...")
        filtered_df = df[df[ID_COLUMN_NAME].isin(target_ids)]

        # 6. Export and Summary
        filtered_df.to_csv(OUTPUT_FILE, index=False)
        print("-" * 30)
        print(f"Success! Extracted {len(filtered_df)} rows.")
        print(f"Results saved to: {OUTPUT_FILE}")
        
        # Check if any IDs were missed
        found_count = filtered_df[ID_COLUMN_NAME].nunique()
        if found_count < len(target_ids):
            print(f"Note: Only {found_count} out of {len(target_ids)} IDs were found.")

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    extract_rows()