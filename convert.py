import pandas as pd
import json
import os

def main():
    excel_file = "Tho_chiet_ly_cuoc_song_FullVersion.xlsx"
    if not os.path.exists(excel_file):
        print(f"Error: {excel_file} not found.")
        return
    
    print("Reading Excel file...")
    # Read the Excel file
    df = pd.read_excel(excel_file)
    
    # Required columns
    required_cols = ['STT', 'Tên Bài Thơ', 'Chủ Đề Chính', 'Số Khổ Thơ', 'Từ Khóa Cảm Xúc', 'ĐỌC BÀI THƠ']
    
    # Check if all required columns exist, otherwise try to map them or print columns
    print("Available columns:", df.columns.tolist())
    
    # Ensure they exist (clean column names if necessary)
    df.columns = [c.strip() for c in df.columns]
    
    # Filter to required columns
    valid_cols = [c for c in required_cols if c in df.columns]
    df_filtered = df[valid_cols].copy()
    
    # Replace NaN with empty string or appropriate default
    df_filtered = df_filtered.fillna("")
    
    # Convert to list of dicts
    records = df_filtered.to_dict(orient='records')
    
    # Save to data.json
    output_file = "data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully converted {len(records)} records and saved to {output_file}")

if __name__ == "__main__":
    main()
