# Tóm tắt IAA (taxonomy v1.0)

- Ảnh được so sánh (có >=2 người gán): **40**; số người gán: 3
- Lượt gán đủ **80/80**.
- IoU trung bình và % cùng lớp **chỉ tính trên các cặp box đã ghép** (IoU >= 0.5, ghép 1-1 không phân biệt lớp). Box chưa ghép được thống kê riêng ở cột bỏ sót/thừa.
- Mẫu số: 342 cặp box ghép (tổng mọi cặp người gán, ảnh chung).

| Cặp | Ảnh | Cặp box ghép | IoU TB | Cùng lớp | Cùng occluded_level | Cùng truncated | Chưa ghép (A/B) | Bỏ qua do ignore | Đạt IAA |
|---|---|---|---|---|---|---|---|---|---|
| **TỔNG** | 40 | 342 | 0.888 | 96.8% | 63.7% | 96.5% | 88/127 | 2 | ĐẠT |
| 101|102 | 13 | 121 | 0.806 | 94.2% | 87.6% | 93.4% | 15/88 | 0 | CHƯA ĐẠT |
| 101|142 | 13 | 142 | 0.994 | 99.3% | 57.0% | 100.0% | 14/28 | 2 | ĐẠT |
| 102|142 | 14 | 79 | 0.822 | 96.2% | 39.2% | 94.9% | 59/11 | 0 | CHƯA ĐẠT |

Ngưỡng IAA: IoU TB >= 0.85, đồng thuận lớp >= 95%.

Số ca bất thường: 523 ({'bat_dong_ignore': 48, 'bo_sot_thua': 177, 'sai_thuoc_tinh': 133, 'iou_thap': 94, 'co_can_review': 60, 'sai_lop': 11}), trên 35 ảnh cần calibration.
