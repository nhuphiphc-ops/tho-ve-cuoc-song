import pandas as pd
import json
import os
import zipfile
import xml.etree.ElementTree as ET
import re

def clean_df(df):
    df.columns = [str(c).strip() for c in df.columns]
    df = df.fillna("")
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df

SUPPLEMENT_FILE = "du_lieu_bo_sung.json"


def load_supplement(section_key):
    """Doc phan du lieu bo sung thu cong cho mot file dich (neu co)."""
    if not os.path.exists(SUPPLEMENT_FILE):
        return None
    try:
        with open(SUPPLEMENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get(section_key)
    except Exception as e:
        print(f"  [CANH BAO] Khong doc duoc {SUPPLEMENT_FILE}: {e}")
        return None


def apply_supplement(data, section_key):
    """Ghep du lieu bien soan thu cong vao dict sinh ra tu Excel.

    Giu Excel lam nguon chinh cho du lieu hang loat, dong thoi bao toan cac noi dung
    them/sua bang tay (Bat Quai Do, Ngu Phap Co Ban, Lo Trinh Hoc, ban va que Dich...)
    de chung khong bi mat moi lan chay lai script nay.
    """
    sup = load_supplement(section_key)
    if not sup:
        return data

    # 1. Chuan hoa gia tri mot truong (vd cat_hung viet hoa/thuong khong nhat quan)
    vm = sup.get("value_map")
    if vm:
        coll, field, mapping = vm.get("collection"), vm.get("field"), vm.get("map") or {}
        rows = data.get(coll) or []
        changed = 0
        for row in rows:
            cur = row.get(field)
            if cur in mapping and mapping[cur] != cur:
                row[field] = mapping[cur]
                changed += 1
        if changed:
            print(f"  + Chuan hoa '{field}' cho {changed} dong trong '{coll}'")

    # 2. Ghi de tung truong theo khoa dinh danh
    ro = sup.get("row_overrides")
    if ro:
        coll, key, rows_map = ro.get("collection"), ro.get("key"), ro.get("rows") or {}
        rows = data.get(coll) or []
        index = {str(r.get(key)): r for r in rows}
        hit = 0
        for rid, fields in rows_map.items():
            target = index.get(str(rid))
            if target is None:
                print(f"  [CANH BAO] Khong tim thay {coll}.{key}={rid} de ghi de")
                continue
            for fname, fval in fields.items():
                target[fname] = fval
            hit += 1
        if hit:
            print(f"  + Ap dung ban va thu cong cho {hit} dong trong '{coll}'")

        # Chuan hoa lai sau khi ghi de (vd que 32 vua duoc cap cat_hung)
        if vm:
            coll2, field2, mapping2 = vm.get("collection"), vm.get("field"), vm.get("map") or {}
            for row in (data.get(coll2) or []):
                cur = row.get(field2)
                if cur in mapping2:
                    row[field2] = mapping2[cur]

    # 3. Them cac muc du lieu khong co trong Excel
    for name, rows in (sup.get("sections") or {}).items():
        data[name] = rows
        print(f"  + Them muc bien soan thu cong '{name}' ({len(rows)} dong)")

    # 4. Sap xep lai thu tu cac muc; '*' = giu nguyen phan con lai
    order = sup.get("section_order")
    if order:
        ordered = {}
        explicit = [k for k in order if k != "*"]
        for name in order:
            if name == "*":
                for k in data:
                    if k not in explicit and k not in ordered:
                        ordered[k] = data[k]
            elif name in data:
                ordered[name] = data[name]
        for k in data:
            if k not in ordered:
                ordered[k] = data[k]
        data = ordered

    return data


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
        
    data = apply_supplement(data, "tieng_trung")

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
    
    data = apply_supplement(data, "kinh_dich")

    output_file = "kinh_dich.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully converted Kinh Dich sheets into {output_file}")

def convert_than_chu():
    paths_to_try = [
        r"e:\IRPORT-ẢNH\THAN CHU CAC LOAI\Chu dai bi-Thap than chu-7-11-2025.docx",
        "Chu dai bi-Thap than chu-7-11-2025.docx"
    ]
    docx_file = None
    for p in paths_to_try:
        if os.path.exists(p):
            docx_file = p
            break
            
    if not docx_file:
        print("Mantra DOCX file not found. Skipping...")
        return
        
    print(f"Reading Mantra data from {docx_file}...")
    try:
        doc = zipfile.ZipFile(docx_file)
        xml_content = doc.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        paragraphs = []
        for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
            if texts:
                paragraphs.append("".join(texts).strip())
            else:
                paragraphs.append("")
                
        sections = {
            "phat_nguyen": [],
            "chu_dai_bi": [],
            "hoi_huong": [],
            "thap_than_chu": [],
            "bat_nha_tieng_phan": [],
            "bat_nha_tieng_viet": [],
            "kim_cuong_tat_doa": [],
            "muoi_than_chu_linh_nghiem": []
        }
        
        current_sec = None
        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue
                
            p_upper = p_clean.upper()
            is_list_item = re.match(r"^\d+\.", p_clean)
            
            if p_upper == "PHÁT NGUYỆN":
                current_sec = "phat_nguyen"
                continue
            elif p_upper in ["CHÚ ĐẠI BI", "CHÚ ĐẠI BỊ"]:
                current_sec = "chu_dai_bi"
                continue
            elif p_upper == "HỒI HƯỚNG":
                current_sec = "hoi_huong"
                continue
            elif p_upper == "THẬP THẦN CHÚ":
                current_sec = "thap_than_chu"
                continue
            elif ("BÁT NHÃ TÂM KINH-TIẾNG PHẠN" in p_upper or "BÁT NHÃ TÂM KINH - TIẾNG PHẠN" in p_upper) and not is_list_item:
                current_sec = "bat_nha_tieng_phan"
                continue
            elif "BÁT NHÃ TÂM KINH" in p_upper and not is_list_item:
                current_sec = "bat_nha_tieng_viet"
                continue
            elif ("KIM CƯƠNG TẤT ĐỎA" in p_upper or "KIM CƯƠNG TÁT ĐỎA" in p_upper) and not is_list_item:
                current_sec = "kim_cuong_tat_doa"
                continue
            elif "10 CÂU THẦN CHÚ LINH NGHIỆM" in p_upper and not is_list_item:
                current_sec = "muoi_than_chu_linh_nghiem"
                continue
                
            if current_sec:
                sections[current_sec].append(p_clean)
                
        # Process Thập Thần Chú
        thap_than_chu = []
        for line in sections["thap_than_chu"]:
            match_first = re.match(r"^(NHƯ Ý BẢO LUÂN VƯƠNG ĐÀ LA NI)(.*)$", line)
            match_numbered = re.match(r"^(\d+)\.\s*(.*?)(THẦN CHÚ|ĐÀ LA NI|CHƠN NGÔN)(.*)$", line)
            
            if match_first:
                title = match_first.group(1).strip()
                content = match_first.group(2).strip()
                thap_than_chu.append({"stt": 1, "ten": title, "noi_dung": content})
            elif match_numbered:
                stt = int(match_numbered.group(1))
                title = (match_numbered.group(2) + match_numbered.group(3)).strip()
                content = match_numbered.group(4).strip()
                thap_than_chu.append({"stt": stt, "ten": title, "noi_dung": content})
            else:
                if thap_than_chu:
                    thap_than_chu[-1]["noi_dung"] += "\n" + line
                else:
                    thap_than_chu.append({"stt": 0, "ten": "Khác", "noi_dung": line})

        # Process 10 Câu Thần Chú Linh Nghiệm
        muoi_than_chu = []
        for line in sections["muoi_than_chu_linh_nghiem"]:
            match = re.match(r"^(\d+)\.\s*(.*?)(?::\s*)?(OM|GATE|ÔM)(.*)$", line, re.IGNORECASE)
            if match:
                stt = int(match.group(1))
                title = match.group(2).strip()
                content = (match.group(3) + match.group(4)).strip()
                muoi_than_chu.append({"stt": stt, "ten": title, "noi_dung": content})
            else:
                if muoi_than_chu:
                    muoi_than_chu[-1]["noi_dung"] += "\n" + line
                else:
                    muoi_than_chu.append({"stt": 0, "ten": "Khác", "noi_dung": line})
                    
        data = {
            "phat_nguyen": "\n".join(sections["phat_nguyen"]),
            "chu_dai_bi": "\n".join(sections["chu_dai_bi"]),
            "hoi_huong": "\n".join(sections["hoi_huong"]),
            "thap_than_chu": thap_than_chu,
            "bat_nha_tieng_phan": "\n".join(sections["bat_nha_tieng_phan"]),
            "bat_nha_tieng_viet": "\n".join(sections["bat_nha_tieng_viet"]),
            "kim_cuong_tat_doa": "\n".join(sections["kim_cuong_tat_doa"]),
            "muoi_than_chu_linh_nghiem": muoi_than_chu
        }
        
        output_file = "than_chu.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Successfully converted Mantra document into {output_file}")
    except Exception as e:
        print("Error converting Mantra docx:", e)

def convert_phap_cu():
    paths_to_try = [
        r"e:\IRPORT-ẢNH\KINH PHAP CU\Kinh Phap Cu - Tuyen tap ke ngon.docx",
        "Kinh Phap Cu - Tuyen tap ke ngon.docx"
    ]
    docx_file = None
    for p in paths_to_try:
        if os.path.exists(p):
            docx_file = p
            break
            
    if not docx_file:
        print("Dhammapada DOCX file not found. Skipping...")
        return
        
    print(f"Reading Dhammapada data from {docx_file}...")
    try:
        doc = zipfile.ZipFile(docx_file)
        xml_content = doc.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        paragraphs = []
        for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
            if texts:
                paragraphs.append("".join(texts).strip())
            else:
                paragraphs.append("")
                
        verses = []
        current_ke = None
        current_content = []
        
        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue
                
            match_ke = re.match(r"^Kệ\s+(\d+)", p_clean, re.IGNORECASE)
            if match_ke:
                if current_ke is not None:
                    verses.append({
                        "ke": current_ke,
                        "noi_dung": "\n".join(current_content)
                    })
                current_ke = int(match_ke.group(1))
                current_content = []
            else:
                if p_clean.upper() in ["KINH PHÁP CÚ", "TUYỂN TẬP CÁC KỆ NGÔN"]:
                    continue
                if current_ke is not None:
                    current_content.append(p_clean)
                    
        if current_ke is not None:
            verses.append({
                "ke": current_ke,
                "noi_dung": "\n".join(current_content)
            })
            
        output_file = "phap_cu.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(verses, f, ensure_ascii=False, indent=2)
        print(f"Successfully converted Dhammapada document into {output_file}")
    except Exception as e:
        print("Error converting Dhammapada docx:", e)

def main():
    convert_poems()
    convert_chinese()
    convert_kinh_dich()
    convert_than_chu()
    convert_phap_cu()

if __name__ == "__main__":
    main()
