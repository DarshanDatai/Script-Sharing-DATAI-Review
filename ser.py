import pandas as pd
import re
import unicodedata

def compute_sentence_level_ser(file_path):
    try:
        # Load the CSV
        df = pd.read_csv(file_path, header=None, names=['user_id', 'annotator', 'reviewer'])
    except Exception as e:
        print(f"Error: {e}")
        return

    def get_sentences(text):
        if pd.isna(text):
            return []
        # Normalize and lowercase
        text = unicodedata.normalize('NFKC', str(text)).lower()
        # Split by periods (one or more)
        # We use filter(None) to remove empty strings caused by trailing periods
        sentences = [s.strip() for s in re.split(r'\.+', text) if s.strip()]
        
        # Final cleaning for each sentence (remove remaining punctuation but keep (??) and *)
        cleaned = []
        for s in sentences:
            s = re.sub(r'[^\w\s\(\)\?\*]', '', s)
            cleaned.append(" ".join(s.split()))
        return cleaned

    expanded_data = []

    # Iterate through each row (task) to split into sentences
    for _, row in df.iterrows():
        user_id = row['user_id']
        ann_sentences = get_sentences(row['annotator'])
        rev_sentences = get_sentences(row['reviewer'])

        # We must align them. If the sentence counts don't match, 
        # the annotator automatically has errors for the missing/extra sentences.
        max_len = max(len(ann_sentences), len(rev_sentences))
        
        for i in range(max_len):
            # Get sentence or empty string if it doesn't exist
            s_ann = ann_sentences[i] if i < len(ann_sentences) else "<MISSING>"
            s_rev = rev_sentences[i] if i < len(rev_sentences) else "<EXTRA_SENTENCE>"
            
            is_error = 1 if s_ann != s_rev else 0
            
            expanded_data.append({
                'user_id': user_id,
                'orig_task_row': _, # Track which row it came from
                'annotator_sentence': s_ann,
                'reviewer_sentence': s_rev,
                'is_error': is_error
            })

    # Create a new dataframe where 1 row = 1 sentence
    sentence_df = pd.DataFrame(expanded_data)

    # 1. Error Log (Detailed sentence-by-sentence comparison)
    sentence_df.to_csv('sentence_debug_log.csv', index=False)

    # 2. Final Aggregation per Annotator
    # SER = Total Incorrect Sentences / Total Expected Sentences (Reviewer's count)
    summary = sentence_df.groupby('user_id').agg(
        Total_Sentences=('is_error', 'count'),
        Total_Errors=('is_error', 'sum')
    ).reset_index()

    summary['SER'] = (summary['Total_Errors'] / summary['Total_Sentences']).round(4)
    summary.to_csv('annotator_ser_summary.csv', index=False)

    print("Processing complete.")
    print(f"Log saved: sentence_debug_log.csv")
    print(f"Summary saved: annotator_ser_summary.csv")
    return summary

# Run the script
results = compute_sentence_level_ser('totalser.csv')
print(results)