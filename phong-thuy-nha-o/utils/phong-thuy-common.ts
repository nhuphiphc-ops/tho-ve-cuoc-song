import { Menh } from '../types';

/**
 * Tính mệnh Ngũ Hành theo năm sinh Âm lịch (Nạp Âm)
 * Bảng rút gọn — dùng chu kỳ 60 Giáp Tý
 */
export function tinhMenhTheoNamSinh(nam: number): { menh: Menh; loai: string } {
  const bangNapAm: Record<number, { menh: Menh; loai: string }> = {
    0: { menh: 'Kim', loai: 'Hải Trung Kim' },
    1: { menh: 'Kim', loai: 'Hải Trung Kim' },
    2: { menh: 'Hỏa', loai: 'Lư Trung Hỏa' },
    3: { menh: 'Hỏa', loai: 'Lư Trung Hỏa' },
    4: { menh: 'Mộc', loai: 'Đại Lâm Mộc' },
    5: { menh: 'Mộc', loai: 'Đại Lâm Mộc' },
    6: { menh: 'Thổ', loai: 'Lộ Bàng Thổ' },
    7: { menh: 'Thổ', loai: 'Lộ Bàng Thổ' },
    8: { menh: 'Kim', loai: 'Kiếm Phong Kim' },
    9: { menh: 'Kim', loai: 'Kiếm Phong Kim' },
    10: { menh: 'Thủy', loai: 'Sơn Đầu Hỏa' },
    11: { menh: 'Thủy', loai: 'Sơn Đầu Hỏa' },
  };
  const key = nam % 12;
  return bangNapAm[key] || { menh: 'Thổ', loai: 'Bích Thượng Thổ' };
}

/**
 * Kiểm tra tương quan giữa 2 mệnh
 */
export function kiemTraTuongQuanMenh(a: Menh, b: Menh): 'tuong-sinh' | 'binh-hoa' | 'tuong-khac' {
  const sinhMap: Record<Menh, Menh> = {
    Kim: 'Thủy',
    Thủy: 'Mộc',
    Mộc: 'Hỏa',
    Hỏa: 'Thổ',
    Thổ: 'Kim',
  };
  if (sinhMap[a] === b || sinhMap[b] === a) return 'tuong-sinh';
  if (a === b) return 'binh-hoa';
  return 'tuong-khac';
}

/**
 * Màu sắc phù hợp và cần tránh theo mệnh
 */
export function mauSacTheoMenh(m: Menh): { tot: string[]; tranh: string[] } {
  const map: Record<Menh, { tot: string[]; tranh: string[] }> = {
    Kim: { tot: ['trắng', 'bạc', 'vàng nhạt'], tranh: ['đỏ', 'hồng', 'tím'] },
    Mộc: { tot: ['xanh lá', 'xanh đậm'], tranh: ['trắng', 'bạc', 'vàng kem'] },
    Thủy: { tot: ['đen', 'xanh đậm', 'xanh dương'], tranh: ['vàng', 'nâu đất', 'be'] },
    Hỏa: { tot: ['đỏ', 'cam', 'hồng', 'tím'], tranh: ['đen', 'xanh đậm'] },
    Thổ: { tot: ['vàng', 'nâu đất', 'be', 'kem'], tranh: ['xanh lá', 'xanh dương'] },
  };
  return map[m];
}

/**
 * Số lượng (đèn, bình hoa, bậc thang...) phù hợp theo mệnh
 */
export function soLuongTheoMenh(m: Menh): { tot: number[]; tranh: number[] } {
  const map: Record<Menh, { tot: number[]; tranh: number[] }> = {
    Kim: { tot: [4, 7, 9], tranh: [2, 3] },
    Mộc: { tot: [1, 2, 3, 8], tranh: [7, 9] },
    Thủy: { tot: [1, 6], tranh: [5, 10] },
    Hỏa: { tot: [3, 7, 9], tranh: [1, 6] },
    Thổ: { tot: [5, 10], tranh: [3, 8] },
  };
  return map[m];
}
