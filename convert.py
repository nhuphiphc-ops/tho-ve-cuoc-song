import pandas as pd
import json
import os

def main():
    excel_file = "Tho_chiet_ly_cuoc_song_FullVersion.xlsx"
    if not os.path.exists(excel_file):
        print(f"Error: {excel_file} not found.")
        return
    
    print("Reading 'Danh Sách Bài Thơ' sheet...")
    # Read metadata sheet
    df_meta = pd.read_excel(excel_file, sheet_name='Danh Sách Bài Thơ')
    df_meta.columns = [c.strip() for c in df_meta.columns]
    
    print("Reading 'Nội Dung Bài Thơ' sheet...")
    # Read content sheet
    df_content = pd.read_excel(excel_file, sheet_name='Nội Dung Bài Thơ')
    # Row 0 contains headers: ['STT', 'TÊN BÀI THƠ', 'NỘI DUNG TOÀN BÀI', 'GỢI Ý NHANH (Tình huống đọc)', 'LIÊN KẾT NHANH']
    df_content.columns = df_content.iloc[0]
    df_content = df_content[1:].copy() # Drop header row
    df_content.columns = [str(c).strip() for c in df_content.columns]
    
    # Cast STT in both to int/string for merging
    df_meta['STT'] = df_meta['STT'].astype(int)
    df_content['STT'] = df_content['STT'].astype(int)
    
    # Merge the metadata with full content and suggestions
    merged = pd.merge(df_meta, df_content[['STT', 'NỘI DUNG TOÀN BÀI', 'GỢI Ý NHANH (Tình huống đọc)']], on='STT', how='left')
    
    # Replace 'ĐỌC BÀI THƠ' with the full content
    merged['ĐỌC BÀI THƠ'] = merged['NỘI DUNG TOÀN BÀI'].fillna("")
    # Add new field 'Gợi Ý Đọc' map to the suggestions
    merged['Gợi Ý Đọc'] = merged['GỢI Ý NHANH (Tình huống đọc)'].fillna("")
    
    merged = merged.drop(columns=['NỘI DUNG TOÀN BÀI', 'GỢI Ý NHANH (Tình huống đọc)'])
    
    # Replace NaN with empty string
    merged = merged.fillna("")
    
    # Convert to JSON
    records = merged.to_dict(orient='records')
    
    output_file = "data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully merged metadata and content for {len(records)} records into {output_file}")

if __name__ == "__main__":
    main()
