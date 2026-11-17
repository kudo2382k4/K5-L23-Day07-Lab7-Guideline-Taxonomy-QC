# Thông tin nhóm

- Tên nhóm: Nhóm 101-102-142
- Mã thành viên (ba chữ số): 101, 102, 142
- Người điều phối:
- Người review bản cuối:
- Commit chốt bài (điền ở kênh nộp sau khi commit):

## Kết quả tóm tắt (điền cuối bài)

- Lượt gán hoàn tất / được giao: 80/80
- IAA trước calibration (kèm mẫu số): IoU TB 0.888, cùng lớp 96.8% trên 342 cặp box; bỏ cặp 101|142 (box trùng tọa độ): IoU 0.812, cùng lớp 95.0% trên 200 cặp — chưa đạt
- Số ảnh phải calibration: 35 / 40 (thay đổi semantic nên rà lại cả 40/40)
- Vòng QC và số ảnh đã duyệt / cả lô: vòng 2, 40/40 (vòng 1 Rework)
- Tỉ lệ lỗi: 0.0 % theo ảnh (0/40), 0.0 % theo đối tượng (0/470); vòng 1: 12.5 % (5/40), 1.1 % (5/473)
- **Quyết định** (Release / Hold / Rework) và lý do một dòng: **Hold** — số đo QC đạt nhưng thiếu bằng chứng gán độc lập cho cặp 101|142
