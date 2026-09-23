export type Menh = 'Kim' | 'Mộc' | 'Thủy' | 'Hỏa' | 'Thổ';
export type Huong = 'Bắc' | 'Nam' | 'Đông' | 'Tây' | 'Đông Bắc' | 'Tây Bắc' | 'Đông Nam' | 'Tây Nam';
export type MucDo = 'tot' | 'binh-thuong' | 'can-luu-y' | 'khong-nen';

export interface NguoiDung {
  tuoiAmLich: number;
  can: string;
  chi: string;
  menh: Menh;
}

export interface KetQuaKiemTra {
  mucDo: MucDo;
  nhanXet: string;
  kienNghi: string;
}

export interface LichNgay {
  ngay: number;
  thang: number;
  nam: number;
  canChi: string;
  hanhNgay?: Menh;
  huongPhuHop: Huong[];
  viecNenLam: string[];
  viecTranh: string[];
}
