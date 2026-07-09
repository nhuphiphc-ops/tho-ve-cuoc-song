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

def convert_kinh_dich():
    paths_to_try = [
        r"e:\IRPORT-ẢNH\KINH DICH\KINH DICH.xlsx",
        "KINH DICH.xlsx"
    ]
    excel_file = None
    for p in paths_to_try:
        if os.path.exists(p):
            excel_file = p
            break
            
    if not excel_file:
        print("Kinh Dich Excel file not found. Skipping...")
        return
        
    print(f"Reading Kinh Dich data from {excel_file}...")
    xl = pd.ExcelFile(excel_file)
    
    # 1. 01_64_Que_Kinh_Dich
    df_64 = pd.read_excel(excel_file, sheet_name='01_64_Que_Kinh_Dich')
    df_64 = clean_df(df_64)
    que_list = []
    for _, row in df_64.iterrows():
        que_list.append({
            "stt": int(row["STT"]) if row["STT"] else 0,
            "ten_que": row["Tên quẻ"],
            "cat_hung": row["Phân loại"],
            "hinh_tuong": row["Tên hình tượng"],
            "cau_truc": row["Cấu trúc quẻ"],
            "giai_nghia": row["Luận giải"],
            "chi_tiet": row["Chú giải bổ sung"]
        })
        
    # 2. 02_Thien_Can
    df_can = pd.read_excel(excel_file, sheet_name='02_Thien_Can')
    df_can = clean_df(df_can)
    can_list = []
    for _, row in df_can.iterrows():
        can_list.append({
            "stt": int(row["STT"]) if row["STT"] else 0,
            "thien_can": row["Thiên Can"],
            "am_duong": row["Âm/Dương"],
            "y_nghia_goc": row["Ý nghĩa gốc"],
            "giai_nghia_mo_rong": row["Giải nghĩa mở rộng"]
        })
        
    # 3. 03_Dia_Chi
    df_chi = pd.read_excel(excel_file, sheet_name='03_Dia_Chi')
    df_chi = clean_df(df_chi)
    chi_list = []
    for _, row in df_chi.iterrows():
        chi_list.append({
            "stt": int(row["STT"]) if row["STT"] else 0,
            "dia_chi": row["Địa Chi"],
            "am_duong": row["Âm/Dương"],
            "y_nghia": row["Ý nghĩa"]
        })

    # 4. 04_Cung_Menh_Ngu_Hanh
    df_menh = pd.read_excel(excel_file, sheet_name='04_Cung_Menh_Ngu_Hanh')
    df_menh = clean_df(df_menh)
    menh_list = []
    for _, row in df_menh.iterrows():
        menh_list.append({
            "cung_menh": row["Cung mệnh"],
            "can_am": row["Thiên Can Âm"],
            "can_duong": row["Thiên Can Dương"],
            "dia_chi": row["Địa Chi"],
            "huong": row["Hướng"],
            "mua_vuong": row["Mùa vượng"],
            "tang_phu": row["Tạng phủ tương ứng"]
        })

    # 5. 05_Can_Chi_Xung_Khac
    df_xung = pd.read_excel(excel_file, sheet_name='05_Can_Chi_Xung_Khac')
    df_xung = clean_df(df_xung)
    xung_list = []
    for _, row in df_xung.iterrows():
        xung_list.append({
            "quan_he": row["Nhóm quan hệ"],
            "noi_dung": row["Nội dung"]
        })

    # 6. 06_Vong_Giap_Ty
    df_vong = pd.read_excel(excel_file, sheet_name='06_Vong_Giap_Ty')
    df_vong = clean_df(df_vong)
    vong_list = []
    for _, row in df_vong.iterrows():
        vong_list.append({
            "stt": int(row["STT"]) if row["STT"] else 0,
            "vong_giap_ty": row["Vòng Giáp Tý"],
            "chi_tiet": row["Chi tiết & Địa Chi Không Vong"]
        })

    # 7. 07_Luc_Than_Hao
    df_luc = pd.read_excel(excel_file, sheet_name='07_Luc_Than_Hao')
    df_luc = clean_df(df_luc)
    luc_list = []
    for _, row in df_luc.iterrows():
        luc_list.append({
            "stt": int(row["STT"]) if row["STT"] else 0,
            "hao": row["Hào"],
            "y_nghia": row["Ý nghĩa khi luận đoán"]
        })

    # 8. 08_Ghi_chu_bo_sung
    df_notes = pd.read_excel(excel_file, sheet_name='08_Ghi_chu_bo_sung')
    df_notes = clean_df(df_notes)
    notes_list = []
    for _, row in df_notes.iterrows():
        notes_list.append({
            "chu_de": row["Chủ đề"],
            "noi_dung": row["Nội dung"]
        })
            
    data = {
        "que_64": que_list,
        "thien_can": can_list,
        "dia_chi": chi_list,
        "ngu_hanh": menh_list,
        "xung_khac": xung_list,
        "vong_giap_ty": vong_list,
        "luc_than": luc_list,
        "ghi_chu": notes_list
    }
    
    output_file = "kinh_dich.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully converted Kinh Dich sheets into {output_file}")

def main():
    convert_poems()
    convert_chinese()
    convert_kinh_dich()

if __name__ == "__main__":
    main()
