import pandas as pd
import json
import os

def clean_df(df):
    df.columns = [str(c).strip() for c in df.columns]
    df = df.fillna("")
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df

def convert_poems():
    excel_file = "Tho_chiet_ly_cuoc_song_FullVersion.xlsx"
    if not os.path.exists(excel_file):
        print(f"Error: {excel_file} not found.")
        return False
    
    print("Reading 'Danh Sách Bài Thơ' sheet...")
    df_meta = pd.read_excel(excel_file, sheet_name='Danh Sách Bài Thơ')
    df_meta.columns = [c.strip() for c in df_meta.columns]
    
    print("Reading 'Nội Dung Bài Thơ' sheet...")
    df_content = pd.read_excel(excel_file, sheet_name='Nội Dung Bài Thơ')
    df_content.columns = df_content.iloc[0]
    df_content = df_content[1:].copy()
    df_content.columns = [str(c).strip() for c in df_content.columns]
    
    df_meta['STT'] = df_meta['STT'].astype(int)
    df_content['STT'] = df_content['STT'].astype(int)
    
    merged = pd.merge(df_meta, df_content[['STT', 'NỘI DUNG TOÀN BÀI', 'GỢI Ý NHANH (Tình huống đọc)']], on='STT', how='left')
    merged['ĐỌC BÀI THƠ'] = merged['NỘI DUNG TOÀN BÀI'].fillna("")
    merged['Gợi Ý Đọc'] = merged['GỢI Ý NHANH (Tình huống đọc)'].fillna("")
    merged = merged.drop(columns=['NỘI DUNG TOÀN BÀI', 'GỢI Ý NHANH (Tình huống đọc)'])
    merged = merged.fillna("")
    
    records = merged.to_dict(orient='records')
    output_file = "data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"Successfully merged metadata and content for {len(records)} records into {output_file}")
    return True

def convert_chinese():
    paths_to_try = [
        r"e:\IRPORT-ẢNH\TIENG TRUNG\Tu_hoc_tieng_Trung_tong_hop.xlsx",
        "Tu_hoc_tieng_Trung_tong_hop.xlsx"
    ]
    excel_file = None
    for p in paths_to_try:
        if os.path.exists(p):
            excel_file = p
            break
            
    if not excel_file:
        print("Chinese learning Excel file not found. Skipping...")
        return
        
    print(f"Reading Chinese learning data from {excel_file}...")
    xl = pd.ExcelFile(excel_file)
    data = {}
    for sheet in xl.sheet_names:
        print(f"Processing sheet: {sheet}...")
        df = pd.read_excel(excel_file, sheet_name=sheet)
        df = clean_df(df)
        data[sheet] = df.to_dict(orient='records')
        
    output_file = "tieng_trung.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully converted Chinese learning sheets into {output_file}")

def main():
    convert_poems()
    convert_chinese()

if __name__ == "__main__":
    main()
