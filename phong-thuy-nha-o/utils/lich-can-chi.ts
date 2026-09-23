import { Menh, Huong, LichNgay } from '../types';

const THIEN_CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const DIA_CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];

const CAN_HANH: Record<string, Menh> = {
  'Giáp': 'Mộc', 'Ất': 'Mộc',
  'Bính': 'Hỏa', 'Đinh': 'Hỏa',
  'Mậu': 'Thổ', 'Kỷ': 'Thổ',
  'Canh': 'Kim', 'Tân': 'Kim',
  'Nhâm': 'Thủy', 'Quý': 'Thủy',
};

/**
 * Tra Can Chi và Hành của ngày
 * Lưu ý: Đây là bảng tra đơn giản hóa — thực tế cần đối chiếu Vạn Niên Lịch
 */
export function traLichNgay(ngay: number, thang: number, nam: number): LichNgay {
  // Công thức đơn giản hóa cho mục đích tham khảo
  const canIdx = (nam * 5 + Math.floor(nam / 4) + ngay + thang * 2) % 10;
  const chiIdx = (nam + Math.floor(nam / 4) + ngay + thang) % 12;

  const canNgay = THIEN_CAN[canIdx];
  const chiNgay = DIA_CHI[chiIdx];
  const hanhNgay = CAN_HANH[canNgay];

  const huongPhuHop: Huong[] = (() => {
    switch (hanhNgay) {
      case 'Kim': return ['Tây', 'Tây Bắc'];
      case 'Mộc': return ['Đông', 'Đông Nam'];
      case 'Thủy': return ['Bắc', 'Đông Bắc'];
      case 'Hỏa': return ['Nam', 'Đông Nam'];
      case 'Thổ': return ['Tây Nam', 'Đông Bắc'];
    }
  })();

  return {
    ngay, thang, nam,
    canChi: `${canNgay} ${chiNgay}`,
    hanhNgay,
    huongPhuHop,
    viecNenLam: ['cúng tế', 'tu sửa bàn thờ', 'thăm viếng mộ phần'],
    viecTranh: ['đào đất sâu ban đêm', 'chặt cây cổ thụ gần mộ'],
  };
}
