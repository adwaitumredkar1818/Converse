import os
import pandas as pd

TABULAR_DIR = "data/raw/tabular"

def classify_columns(columns):
    col_lower = [c.lower() for c in columns]
    
    date_cols = [c for c in columns if any(kw in c.lower() for kw in ["date", "time", "day", "timestamp", "year", "month"])]
    household_cols = [c for c in columns if any(kw in c.lower() for kw in ["lclid", "household", "id", "acorn", "macn"])]
    energy_cols = [c for c in columns if any(kw in c.lower() for kw in ["kwh", "energy", "power", "kw", "consumption"])]
    weather_cols = [c for c in columns if any(kw in c.lower() for kw in ["temp", "humidity", "wind", "precip", "weather", "pressure", "visibility", "uv", "dew", "cloud", "summary", "icon"])]
    
    return {
        "date_time": date_cols,
        "household_id": household_cols,
        "energy": energy_cols,
        "weather": weather_cols
    }

def analyze_single_csv(file_path):
    print("\n" + "=" * 60)
    print(f"📄 ANALYZING FILE: {file_path}")
    print("=" * 60)

    try:
        # Read only top 5 rows for sample & column analysis
        df_sample = pd.read_csv(file_path, nrows=5)
        num_cols = len(df_sample.columns)
        
        # Fast line count for estimation
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            total_lines = sum(1 for _ in f)
        est_rows = max(0, total_lines - 1)

        print(f"📊 Dimensions: ~{est_rows} rows x {num_cols} columns")
        print(f"📋 Columns ({num_cols}): {df_sample.columns.tolist()}")

        classified = classify_columns(df_sample.columns)
        print("\n🔍 DETECTED COLUMN CATEGORIES:")
        print(f"  • Date/Time Columns:      {classified['date_time']}")
        print(f"  • Household ID Columns:   {classified['household_id']}")
        print(f"  • Energy Data Columns:    {classified['energy']}")
        print(f"  • Weather Data Columns:   {classified['weather']}")

        print("\n🔎 SAMPLE PREVIEW (Top 3 rows):")
        print(df_sample.head(3).to_string(index=False))

        return {
            "file": os.path.basename(file_path),
            "rows": est_rows,
            "cols": num_cols,
            "columns": df_sample.columns.tolist(),
            "classified": classified
        }

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def analyze_all_csvs():
    print("🚀 STARTING TABULAR DATASET ANALYSIS...")
    
    summary_list = []

    # 1. Analyze Root CSV Files
    root_csvs = [os.path.join(TABULAR_DIR, f) for f in os.listdir(TABULAR_DIR) if f.endswith('.csv')]
    for csv_file in sorted(root_csvs):
        info = analyze_single_csv(csv_file)
        if info:
            summary_list.append(info)

    # 2. Analyze Sample from Partitioned Directory Blocks
    for item in sorted(os.listdir(TABULAR_DIR)):
        item_path = os.path.join(TABULAR_DIR, item)
        if os.path.isdir(item_path):
            # find all csvs in subfolder recursively
            sub_csvs = []
            for r, d, files in os.walk(item_path):
                for f in files:
                    if f.endswith('.csv'):
                        sub_csvs.append(os.path.join(r, f))
            
            if sub_csvs:
                print("\n" + "📂" * 30)
                print(f"📁 PARTITIONED DATASET FOLDER: {item} ({len(sub_csvs)} block files)")
                print("📂" * 30)
                sample_file = sorted(sub_csvs)[0]
                info = analyze_single_csv(sample_file)
                if info:
                    info["partitioned_folder"] = item
                    info["partitioned_count"] = len(sub_csvs)
                    summary_list.append(info)

    # 3. Overall Dataset Summary
    print("\n" + "═" * 60)
    print("📊 OVERALL TABULAR DATASET SUMMARY")
    print("═" * 60)
    for s in summary_list:
        folder_tag = f" (Folder: {s['partitioned_folder']}, {s['partitioned_count']} blocks)" if "partitioned_folder" in s else ""
        print(f"• File: {s['file']}{folder_tag}")
        print(f"  - Rows: ~{s['rows']:,} | Cols: {s['cols']}")
        print(f"  - Key Detected Fields: Date={s['classified']['date_time']}, Household={s['classified']['household_id']}, Energy={s['classified']['energy']}, Weather={s['classified']['weather']}")
        print("-" * 50)

if __name__ == "__main__":
    analyze_all_csvs()
