import pandas as pd
import os
from datetime import datetime
import ast

now = datetime.now().strftime("%y_%m_%d-%H_%M")

loc_dist = [
    #"09_complex_combined_2P_old.csv",  # only for structure, not included in combination
    "Normal_final_summary_results.csv",
    "Normal_final_summary_results.csv",
    "Normal_final_summary_results-2.csv",
    "Normal_final_summary_results-3.csv",
    "Normal_final_summary_results-4.csv",
    "Normal_final_summary_results-5.csv",
    "Normal_final_summary_results-6.csv",
]

path = os.path.join(os.getcwd(), "01_ANALYSIS_RESULTS", "complex_2_0.001")
files = [os.path.join(path, loc) for loc in loc_dist]
output_file = os.path.join(path, "complex_combined_2P_new.csv")

drop_col_list = ['sim_det', 'analysis_det', 'base_det'] 

dfs = []
template_columns = None

for i, f in enumerate(files):
    if not os.path.exists(f):
        print(f"⚠️ Warning: File not found -> {f}")
        continue

    df = pd.read_csv(f)

    # For the first file: only take the column structure, skip adding its rows
    if i == 0:
        template_columns = df.columns.tolist()
        print(f"📌 Template structure loaded from: {f}")
        continue

    # --- Clean and adjust columns ---
    # Scale sigma_feature for files after the first
    if 'sigma_feature' in df.columns:
        df["sigma_feature"] = df["sigma_feature"] * 1000

    # Scale sigma if present
    if "sigma" in df.columns:
        df["sigma"] = df["sigma"] * 1000

    """
    # Fix pulse_shape names
    if "pulse_shape" in df.columns:
        df['pulse_shape'] = df['pulse_shape'].replace({
            'complex_pulse_short_2p3ms': 'complex_short_3ms',
            'complex_pulse_short_2p10ms': 'complex_short_10ms'
        })
    """
    
    # --- Enforce the template columns ---
    df = df.reindex(columns=template_columns)

    dfs.append(df) 

if dfs:
    combined_df = pd.concat(dfs, ignore_index=True)

    # Convert analysis_det strings to lists if present
    if 'analysis_det' in combined_df.columns:
        combined_df['analysis_det'] = combined_df['analysis_det'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
        combined_df['num_analysis_det'] = combined_df['analysis_det'].apply(
            lambda x: len(x) if isinstance(x, list) else pd.NA
        )

    # Drop unwanted columns
    combined_df = combined_df.drop(columns=drop_col_list, errors='ignore')

    # Save final CSV
    combined_df.to_csv(output_file, index=False)
    print(f"✅ Combined CSV saved to:\n{output_file}")
else:
    print("No CSVs found to combine.")
