# Báo cáo QC — Nhóm 101-102-142

> Bàn giao vòng QC **2**. Mọi tỉ lệ kèm mẫu số. Đường dẫn tương đối từ gốc repo.

## 1. Mục đích, dữ liệu và phiên bản

- Mục đích và giới hạn sử dụng: Nhãn bounding box 2D cho bài thực hành phát hiện người và phương tiện trên 40 ảnh đường phố (Day 07). Chỉ dùng cho học tập; 40 ảnh không đại diện cho phân bố giao thông thực tế.
- Nguồn và phép sử dụng dữ liệu: 40 ảnh Wikimedia Commons, giấy phép CC BY / CC BY-SA / CC0 / public domain, ghi công trong `data/ATTRIBUTION.csv` (giữ nguyên).
- Manifest và checksum nhãn cuối: `submission/qc/batch_manifest.json`; `labels_calibrated.json` SHA-256 `16946864c3305a66be77f59ce8888821de78fa5350d812e934c134087f31bb4e` (40 ảnh, 479 annotation, trong đó 9 `ignore_region`)
- Guideline và taxonomy khi gán / khi bàn giao: Gán theo `guideline_v1.0_agreed.md` và `taxonomy.json` v1.0 (8 lớp). Khi bàn giao: `guideline_v1.1_calibrated.md`, thay đổi `semantic` (`submission/guideline_change.json`); taxonomy giữ nguyên v1.0, không có `taxonomy_v1.1.json`

## 2. Phân công và đồng thuận trước calibration

- Lượt hoàn thành / được giao: 80/80 (3 người 101, 102, 142; mỗi ảnh 2 người; 26/27/27 ảnh). `validate_labels.py --all` sạch.
- Số cặp box ghép, IoU TB, đồng thuận lớp và mẫu số:

  | Cặp | Ảnh chung | Cặp box ghép | IoU TB | Cùng lớp | Cùng `occluded_level` | Đạt IAA |
  |---|---|---|---|---|---|---|
  | Tổng (theo script) | 40 | 342 | 0.888 | 96.8% (331/342) | 63.7% | ĐẠT |
  | 101 \| 102 | 13 | 121 | 0.806 | 94.2% (114/121) | 87.6% | CHƯA ĐẠT |
  | 101 \| 142 | 13 | 142 | 0.994 | 99.3% (141/142) | 57.0% | ĐẠT — **không dùng được, xem dưới** |
  | 102 \| 142 | 14 | 79 | 0.822 | 96.2% (76/79) | 39.2% | CHƯA ĐẠT |
  | **Tổng loại cặp 101 \| 142** | 27 | **200** | **0.812** | **95.0% (190/200)** | — | **CHƯA ĐẠT** (IoU < 0.85) |

  **Số IAA nhóm dùng để kết luận là dòng cuối (200 cặp box, hai cặp có 102).**

- Box chưa ghép, loại do ignore, bất đồng vùng ignore: chưa ghép 88 (bên A) / 127 (bên B) trên toàn bộ cặp; 2 box bỏ qua do nằm trong `ignore_region`; 48 ca `bat_dong_ignore`. Tổng 523 ca bất thường trên 35 ảnh (`bo_sot_thua` 177, `sai_thuoc_tinh` 133, `iou_thap` 94, `co_can_review` 60, `bat_dong_ignore` 48, `sai_lop` 11).
- **Vấn đề độc lập của cặp 101 | 142:** so tọa độ box làm tròn 0,1 px trên ảnh chung:

  | Cặp | Box trùng tọa độ tuyệt đối |
  |---|---|
  | 101 \| 102 | 0/209 |
  | 102 \| 142 | 0/93 |
  | 101 \| 142 | **110/171** (cả 12 ảnh chung) |

  Hai người vẽ tay độc lập không cho box trùng tới 0,1 px (cặp có 102 là 0). Nhãn 142 đã export lại ba lần nhưng vẫn giữ 256/264 box của bản đầu. Nguyên nhân chưa xác định (nghi do dùng chung Task / nạp annotation trên CVAT local). Vì vậy **IAA cặp 101 | 142 không được tính là đo độc lập**, và con số "ĐẠT" của dòng tổng bị cặp này kéo lên.
- Ca hai người có thể cùng sai sau khi đối chiếu tham chiếu: img_012, R-05: pickup chở hàng tiền cảnh được cả 102 và 142 gán `car` (IAA tính là khớp lớp), trong khi bảng ca khó 4.2 ghi `truck`. Phát hiện khi đối chiếu nhãn đồng thuận với bảng ca khó của guideline (chưa có ca tham chiếu của coach). Đã sửa thành `truck`, ghi ca `C524`. Tương tự, QC vòng 1 phát hiện vỏ xe vàng trên nóc img_024 vẫn còn box `car` sau calibration (R-10, ca `Q04`).

## 3. Calibration và kiểm lại

- Ca đã xử lý, rule ID, bản sửa và người xác nhận: `submission/qc/calibration_decisions.csv` có 529 dòng: 523 ca IAA (C001–C523), 1 ca cả hai cùng sai (C524), 5 ca QC vòng 1 (Q01–Q05). Mỗi dòng có rule ID (R-01…R-20), người chốt (người thứ ba không gán ảnh đó), phiếu sửa (ảnh, lớp, box) và người kiểm lại. Sửa nhãn bằng `scripts/calib_apply.py` (áp quyết định lên nhãn 101/102/142), log từng thay đổi ở `submission/qc/calib_apply.log`. Ca sai lớp đã xem ảnh gốc trước khi chốt (img_005 van/car, img_018 car, img_037 bus, img_040 tuk_tuk).
- Tác động v1.1 lên nhãn và ảnh: phạm vi **cả lô 40/40 ảnh** (181 quyết định `pham_vi=lo`, thay đổi `semantic`), không cần mapping lớp. Nháp đồng thuận có 558 annotation, nhãn sau sửa còn 479: bỏ box < 20 px và box đám đông nằm trong `ignore_region` ở 7 ảnh R-15, bỏ box trùng/mảnh vỡ theo R-20, `occluded_level` lấy mức cao hơn, `truncated` đo bằng tọa độ, bỏ mọi `can_review`. COCO sau sửa: `submission/qc/labels_calibrated_123eeb64318d6fd7.json`.
- Tham chiếu bằng chứng khi Rework: vòng 1 (`submission/qc/reviews/round-01/`, nhãn `labels_calibrated_b78da5c1b79735f6.json`) kết luận **Rework**: 5/40 ảnh lỗi = 12.5% (5/473 annotation = 1.1%). Các lỗi: 3 `thua`, 1 `sai_lop`, 1 `sai_vi_tri_kich_thuoc`, ở img_007, 014, 018, 024, 028. Đã sửa thành Q01–Q05 trong `scripts/calib_apply.py` (`QC_FIX`) rồi mở vòng 2 (`submission/qc/reviews/round-02/`).

## 4. Kết quả duyệt

- Vòng QC: 2
- Người review và ngày: 142, 2026-11-17 (rà toàn lô trên ảnh overlay `work/review/round-0N/` với sự hỗ trợ của Claude; 101 hoặc 102 nên xem lại độc lập trước khi Release)
- Đã duyệt / cả lô: 40/40 (duyệt toàn lô)
- Ảnh lỗi / ảnh đã duyệt: 0/40 = 0.0% (vòng 1: 5/40 = 12.5%)
- Annotation đối tượng hiện có bị lỗi / annotation đối tượng đã duyệt: 0/470 = 0.0% (vòng 1: 5/473 = 1.1%)
- Vật bỏ sót, ảnh và vùng: 0 ghi nhận ở cả hai vòng. Giới hạn: ảnh đám đông (img_003, 019, 021, 030, 032) được rà ở mức nhìn tổng thể, vật nhỏ sát ngưỡng 20 px có thể còn sót
- Ca khó / phần còn lại, lỗi lặp và ví dụ: vòng 2 ca khó 0/35, phần còn lại 0/5. Vòng 1 ca khó 5/35 = 14.3%, phần còn lại 0/5. Lỗi lặp ở vòng 1 là `thua` trên vật không thật hoặc vật đặt trên xe (R-08, R-10): pano img_018 #223, vỏ xe img_024 #304, vật trên bàn img_007 #91. Xem `reviews/round-01/qc_review.csv`
- Một lỗi máy chặn được và một lỗi cần người đọc ảnh: Máy chặn được: box trùng tọa độ giữa 101 và 142 (phát hiện bằng so tọa độ, IoU 0.994 bất thường). Cần người đọc ảnh: chân dung trên pano img_018 bị gán `person` (script chỉ thấy một box person hợp lệ, phải nhìn ảnh mới biết đó là hình in, R-08)

## 5. Quyết định bàn giao

- Quyết định: Hold
- Lý do, người nhận và phạm vi sử dụng: Số đo QC vòng 2 đạt: 0/40 ảnh lỗi, script gợi ý Release khi không có cờ. Nhóm vẫn chọn **Hold** (`qc_report.py --round 2 --data-problem 1`) vì thiếu bằng chứng gán độc lập cho cặp 101 \| 142: 110/171 box trùng tọa độ tuyệt đối. IAA dùng để chẩn đoán trước calibration vì vậy không đáng tin cho 13 ảnh của cặp này. Người nhận là coach lớp Day 07. Phạm vi: chỉ dùng học tập, chưa dùng để huấn luyện.
- Nếu còn việc: (1) xác định nguyên nhân trùng box 101 \| 142, ghi vào ghi chú cá nhân 101 và 142; nếu không chứng minh được gán độc lập thì 142 gán lại 13 ảnh chung với 101 trên Task trống rồi chạy lại từ `qc_compare.py`. Người xử lý: 101, 142. (2) Một thành viên khác 142 (101 hoặc 102) duyệt lại vòng 2 độc lập. (3) 102 nộp `submission/individual_notes/102.md`. Calibration các ca đám đông và xe máy dày (img_008, 019, 021) đã xong trong v1.1.
- Kiểm ngược từ báo cáo tới ảnh, rule và nhãn: ca `Q05` → `reviews/round-01/qc_review.csv` (img_028, object 323, `sai_vi_tri_kich_thuoc`, R-10: box truck kéo lên tượng ngựa) → `calibration_decisions.csv` dòng Q05 → `calib_apply.log` ("Q05 sửa box truck … → [35, 298, 925, 693]") → `labels_calibrated.json` img_028 truck bbox [35, 298, 890, 395] → `reviews/round-02/qc_review.csv` img_028 "Đã kiểm lại Q05 sau Rework: đạt". Kết quả: lần theo được đủ chuỗi.
