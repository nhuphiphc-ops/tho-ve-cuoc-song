import { Huong } from '../types';

/**
 * Tính Nhà Tứ (Đông Tứ / Tây Tứ) theo Bát Trạch
 * Áp dụng cho nam giới — nữ giới cần điều chỉnh riêng
 */
export function tinhBatTrach(namSinh: number, gioiTinh: 'nam' | 'nu'): {
  loai: 'Đông Tứ' | 'Tây Tứ';
  soQua: number;
  cungMenh: string;
  huongTot: Huong[];
  huongXau: Huong[];
} {
  let soQua: number;

  if (gioiTinh === 'nam') {
    soQua = (100 - (namSinh % 100)) % 9;
  } else {
    soQua = ((namSinh % 100) - 4) % 9;
  }
  if (soQua <= 0) soQua += 9;
  if (soQua === 5) soQua = gioiTinh === 'nam' ? 2 : 8; // Quy ước cung Khôn / Cấn

  const cungMap: Record<number, string> = {
    1: 'Khảm', 2: 'Khôn', 3: 'Chấn', 4: 'Tốn',
    6: 'Càn', 7: 'Đoài', 8: 'Cấn', 9: 'Ly',
  };

  const dongTu = [1, 3, 4, 9];
  const loai = dongTu.includes(soQua) ? 'Đông Tứ' as const : 'Tây Tứ' as const;

  const huongDong: Huong[] = ['Đông', 'Đông Nam', 'Bắc', 'Nam'];
  const huongTay: Huong[] = ['Tây', 'Tây Bắc', 'Tây Nam', 'Đông Bắc'];

  return {
    loai,
    soQua,
    cungMenh: cungMap[soQua] || 'Khôn',
    huongTot: loai === 'Đông Tứ' ? huongDong : huongTay,
    huongXau: loai === 'Đông Tứ' ? huongTay : huongDong,
  };
}
