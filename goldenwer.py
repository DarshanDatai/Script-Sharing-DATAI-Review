import pandas as pd
import re
import unicodedata

def wer_calc(reference, hypothesis):
    """
    Standard Levenshtein Word Error Rate calculation.
    Reference (Reviewer) vs Hypothesis (Annotator).
    """
    ref = reference.split()
    hyp = hypothesis.split()
    
    # Building the cost matrix
    d = [[0 for _ in range(len(hyp) + 1)] for _ in range(len(ref) + 1)]
    for i in range(len(ref) + 1): d[i][0] = i
    for j in range(len(hyp) + 1): d[0][j] = j

    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            if ref[i-1] == hyp[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion = d[i][j-1] + 1
                deletion = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    
    # Returns (Total Edits, Total Reference Words)
    return d[len(ref)][len(hyp)], len(ref)

def compute_project_wer(file_path):
    try:
        # Col 0: user_id, Col 1: annotator (Hypothesis), Col 2: reviewer (Reference)
        df = pd.read_csv(file_path, header=None, names=['user_id', 'annotator', 'reviewer'])
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    def clean_text(text):
        if pd.isna(text): return ""
        # Normalize unicode and lowercase
        text = unicodedata.normalize('NFKC', str(text)).lower()
        
        # 1. Protect (??) by turning it into a single unique word
        text = text.replace("(??)", "unsuretag")
        
        # 2. Define and remove stop words (barely heard, won't impact quality)
        stop_words = r'\b(uh|um|a)\b'
        text = re.sub(stop_words, '', text)
        
        # 3. Strip punctuation but keep alphanumeric and our unsuretag
        text = re.sub(r'[^\w\s]', '', text)
        
        # 4. Collapse multiple spaces and strip edges
        return " ".join(text.split()).strip()

    total_project_edits = 0
    total_project_words = 0
    log_data = []

    # First pass to get total words for impact_percent calculation
    # We clean Column 3 because it is the "Reference" word count
    temp_cleaned_refs = df['reviewer'].apply(clean_text)
    global_word_count = sum(len(str(x).split()) for x in temp_cleaned_refs)

    for index, row in df.iterrows():
        # Clean both columns
        c_hyp = clean_text(row['annotator']) # Column 2
        c_ref = clean_text(row['reviewer'])  # Column 3
        
        edits, ref_word_count = wer_calc(c_ref, c_hyp)
        
        # Track totals for Weighted Project WER
        total_project_edits += edits
        total_project_words += ref_word_count
        
        # Row-level Metrics
        row_wer = round(edits / ref_word_count, 4) if ref_word_count > 0 else 0
        impact_pct = round((ref_word_count / global_word_count) * 100, 4) if global_word_count > 0 else 0
        
        log_data.append({
            'row_index': index,
            'user_id': row['user_id'],
            'cleaned_annotator_hyp': c_hyp,
            'cleaned_reviewer_ref': c_ref,
            'edits': edits,
            'ref_word_count': ref_word_count,
            'row_wer': row_wer,
            'impact_percent': impact_pct
        })

    # Weighted Final Calculation
    final_weighted_wer = total_project_edits / total_project_words if total_project_words > 0 else 0
    
    # Save the Audit Log
    log_df = pd.DataFrame(log_data)
    log_df.to_csv('weighted_wer_audit_log.csv', index=False)

    print("-" * 40)
    print(f"METRIC: Weighted Word Error Rate")
    print(f"REFERENCE: Column 3 (Reviewer)")
    print(f"HYPOTHESIS: Column 2 (Annotator)")
    print("-" * 40)
    print(f"Total Words in Project: {total_project_words}")
    print(f"Total Edits (Errors): {total_project_edits}")
    print(f"FINAL WEIGHTED WER: {final_weighted_wer:.2%}")
    print("-" * 40)
    print("Log saved to: weighted_wer_audit_log.csv")
    
    return final_weighted_wer

# Run the process
compute_project_wer('goldenser.csv')