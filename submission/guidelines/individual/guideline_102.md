# Guideline gán nhãn — v0.9-cá-nhân — mã thành viên: 102

> Bản cá nhân (Pha 1). Khi nộp, đổi tên thành `guideline_102.md` và đặt vào `submission/guidelines/individual/`.
> Các quyết định dưới đây là **quyết định ban đầu của tôi** để mang đi họp Pha 2; chưa phải quy tắc của nhóm.

- Ngày: 2026-11-16
- Dữ liệu: 40 ảnh `img_001`–`img_040`, bounding box, CVAT, xuất COCO 1.0

## 1. Mục tiêu

Nhãn dùng huấn luyện mô hình phát hiện **người và phương tiện cơ giới** trên ảnh 2D đường phố (camera giao thông, hỗ trợ lái).
Sai nguy hiểm nhất: (a) **dương tính giả** trên tượng, đồ chơi, hình in, phản chiếu, vì mô hình sẽ phanh/báo động với vật không thật; (b) **bỏ sót** người đi bộ hoặc xe thật; (c) mỗi người một kiểu xử lý xe ba bánh, xe đạp, xe buýt nên nhãn không nhất quán.

Phép thử cho mọi quyết định: *"Mô hình có phải đoán điều này từ ảnh 2D không?"* Nếu phải đoán (vật quá nhỏ, mờ, khuất gần hết) thì không ép gán box mà đưa vào `ignore_region` hoặc tick `can_review`.

## 2. Lớp và thuộc tính

### Lớp (mỗi vật thật thuộc đúng một lớp)

| Lớp | Định nghĩa (một câu) | Ví dụ | Phản ví dụ / dễ nhầm |
|---|---|---|---|
| `car` | Xe bốn bánh chở người, thân kín, không có thùng hàng rời. | img_023 (Honda đen), img_024 (Pacer đen), img_015 | Pickup (→ `truck`); xe đồ chơi/mô hình (img_038, không gán) |
| `truck` | Xe có thùng hàng riêng: xe tải, xe tải nhỏ, **pickup**, xe chở xe. | img_002, img_007, img_036, img_012, img_001, img_037 | Xe thùng kín nhỏ giống minivan (→ `van`) |
| `van` | Xe thùng kín cỡ nhỏ, cabin và khoang chở liền một khối (minivan, xe chở khách nhỏ). | img_005 (nền), img_016 (xe trắng) | Pickup có nắp thùng (img_037) vẫn là `truck` vì cabin và thùng là hai khối |
| `motorcycle` | Xe hai bánh có động cơ, gồm xe máy, xe côn tay, **xe ba bánh kiểu tuk-tuk / xe lam** (R-04), xe có sidecar. | img_006, img_029, img_022, img_004 | Xe đạp, xích lô (không gán) |
| `person` | Người thật nhìn thấy ít nhất đầu hoặc thân trên: người đi bộ, người lái, người ngồi sau. | img_014, img_034, img_003 | Ma-nơ-canh (img_033), tượng (img_017), người trên áp phích (img_018) |
| `ignore_region` | Vùng không gán từng vật: đám đông, đàn xe dày đặc, vật quá nhỏ hoặc mờ. | img_032, img_030, img_025 | Một vật rõ, đủ lớn — phải có box riêng |

**Vật không thuộc lớp nào** (xe buýt, xe đạp, xích lô, máy bay, vật nuôi…): **không vẽ box, không dùng `ignore_region`**, ghi vào `image_issues.csv` khi nhóm hỏi (R-05). Không tự tạo lớp mới.

### Thuộc tính

`occluded_level` — đo trên **phần thân vật** (không tính phần bị cắt mép ảnh):

| Mức | Phần bị che | Ghi chú |
|---|---|---|
| 0 | ≤ 10% | thấy rõ |
| 1 | > 10% – 40% | che ít |
| 2 | > 40% – 75% | che nhiều |
| 3 | > 75% | chỉ thấy vài mảng; nếu không nhận ra lớp → không gán, dùng `ignore_region` |

`truncated` — `yes` khi mép ảnh cắt mất **> 5%** thân vật (ước bằng mắt); còn lại `no`. Bị che bởi vật khác là `occluded_level`, **không** phải `truncated`.

`can_review` — tick khi tôi chưa chắc về lớp, ranh giới ca, hoặc ca thuộc R-04/R-07/R-09.

## 3. Quy tắc vẽ box

| ID | Quy tắc |
|---|---|
| R-01 | **Box ôm phần nhìn thấy**, sát mép trong 1–2 px; không suy đoán phần khuất. Bị che thì box chỉ ôm phần thấy. |
| R-02 | **Người đi xe máy = nhiều box chồng nhau**: 1 box `motorcycle` (chỉ thân xe, bánh, tay lái, không tính người) + 1 box `person` cho **mỗi** người trên xe (lái, ngồi sau). Cho phép chồng lên nhau. Áp dụng img_005, 006, 010, 026, 029. |
| R-03 | **Hàng hóa/vật mang theo không nằm trong box**: gánh hàng (img_003), cây dài trên xe máy (img_029), bao tải chồng cao (img_035), hàng trong thùng pickup (img_012). Riêng **xe chở xe** (img_002): chỉ một box `truck` cho cả đầu kéo và rơ-moóc; **xe được chở không gán box riêng**. |
| R-04 | **Xe ba bánh có động cơ (tuk-tuk, xe lam, auto-rickshaw)** → `motorcycle`, tick `can_review`; người lái trong cabin gán `person` nếu thấy rõ. Áp dụng img_004, 016, 035, 040. *Lý do:* dựng trên khung xe máy, lái bằng ghi-đông, không đủ định nghĩa `car`. |
| R-05 | **Vật ngoài taxonomy** (xe buýt: img_009, 031, 032, 040; xe đạp và xích lô: img_003, 006, 023, 034, 039): **không vẽ box**. Người đi xe đạp/xích lô vẫn gán `person`. Nếu cả nhóm thấy cần thì sẽ thêm lớp ở v1.1. |
| R-06 | **Cắt mép ảnh**: vẫn gán nếu còn nhận ra lớp; `truncated=yes`, box ôm phần còn thấy tới sát mép (img_015, 032, 034, 040). Nếu chỉ còn mảnh nhỏ không nhận ra lớp → bỏ. |
| R-07 | **Vật không thật không gán**: tượng (img_017 tượng ngựa, img_027 tượng pickup bằng đá, img_028 con ngựa trắng trên thùng xe), ma-nơ-canh (img_033), đồ chơi và mô hình xe (img_038), người in trên áp phích (img_018), người/xe trong ảnh phản chiếu (img_020, 033), tranh tường (img_026). **Xe thật chở tượng vẫn gán**: pickup ở img_028 là `truck`, con ngựa không có box. |
| R-08 | **Vật quá nhỏ**: chiều cao box < 20 px (đúng ngưỡng `min_box_height_px` trong taxonomy) → **không vẽ từng vật**; nếu có cụm thì phủ một `ignore_region`. Áp dụng nền xa của img_013, 025, 039, 031. |
| R-09 | **Đám đông và xe dày đặc**: gán box cho vật **rõ và đủ lớn** ở tiền cảnh; phần còn lại (cao < 20 px, bị che > 75%, chồng chéo không tách được) phủ bằng **một** `ignore_region` ôm cụm. Áp dụng img_021, 030, 008 (đàn xe), img_032 và img_019 (đám đông xem diễu hành). Không để `ignore_region` che vật rõ đã có box. |
| R-10 | **Mờ do chuyển động** (img_014): người rõ nét gán `person`; bóng mờ không tách được hình dạng → `ignore_region`. |
| R-11 | **Xe chủ (ego) và gương**: phần thân xe của camera, gương, kính chắn gió (img_020) không gán. Xe thấy qua kính/gương cũng không gán. |
| R-12 | **Phương tiện tưởng tượng / diễu hành có thật chạy trên đường** (img_019 xe Dangermouse): gán `car` + `can_review`; người ngồi lái gán `person`; nhân vật bông (chuột) không gán. |
| R-13 | **Người hóa trang** (img_011 nhân vật Predator): thấy là người mặc trang phục → `person` + `can_review`. Nếu chỉ còn là đầu/mặt nạ đặt trên giá → không gán. |
| R-14 | **Xe được đặt trên xe khác** (img_024, xe vàng trên nóc xe đen): xe đen → `car`. Xe vàng là vật trưng bày dạng xe nhỏ nên coi là mô hình → **không gán**, tick `can_review` trên xe đen để reviewer xem. |

## 4. Ca khó

| Ảnh | Tình huống | Rule ID | Quyết định | Lý do |
|---|---|---|---|---|
| img_005 | 4 người trên xe máy sát nhau, mũ che mặt; van ở nền | R-02, R-09 | box `person` cho từng người thấy ít nhất đầu, `occluded_level` 1–2; `motorcycle` khuất nhiều → 2; van nền → `van` | tránh bỏ sót người bị che, giữ quy tắc một người một box |
| img_006 | Hàng xe máy chạy ngược camera, xích lô/xe đạp lẫn trong | R-02, R-05 | mỗi xe máy: `motorcycle` + `person` cho từng người; xe đạp không gán, người đi xe đạp vẫn gán | thống nhất nhãn khi ca nhiều lớp |
| img_002 | Xe chở 6–8 xe con | R-03 | 1 `truck`, không gán xe đang bị chở | xe được chở không di chuyển độc lập; tránh trùng box lồng nhau |
| img_004, 016, 035, 040 | Tuk-tuk / xe lam | R-04 | `motorcycle` + `can_review` | không có lớp xe ba bánh |
| img_035 | Xe lam chở hàng cao ngất | R-03, R-04 | box ôm thân xe, không tính chồng bao tải | hàng không phải vật của lớp |
| img_017 | Tượng cưỡi ngựa, có nón lưu thông | R-07 | không gán | vật không thật |
| img_027 | Tượng pickup bằng đá ở nghĩa trang | R-07 | không gán `truck` | mô hình tĩnh, không phải phương tiện |
| img_028 | Pickup thật chở tượng ngựa | R-07 | `truck` có, ngựa không | tách vật thật khỏi vật không thật |
| img_033 | Ma-nơ-canh và phản chiếu cửa kính | R-07, R-11 | không gán | ma-nơ-canh và phản chiếu |
| img_038 | Tủ trưng bày xe và búp bê đồ chơi | R-07 | không gán | mô hình thu nhỏ |
| img_018 | Áp phích có ảnh người, nền có xe đỗ phía sau hàng rào | R-07, R-08 | không gán người trên áp phích; xe nền nếu cao < 20 px → `ignore_region` | ảnh in không phải người thật |
| img_020 | Gương chiếu hậu có phản chiếu xe | R-11 | không gán | phản chiếu |
| img_026 | Cặp đôi xe máy trước bức tranh tường cảng | R-02, R-07 | `motorcycle` + 2 `person`; tranh tường không gán | tranh là hình in |
| img_029 | Xe máy chở thanh dài vắt ngang, người đạp xe đạp bên cạnh | R-03, R-05 | `motorcycle` + 2 `person`; xe đạp không gán; thanh dài không đưa vào box | tải trọng ngoài định nghĩa |
| img_021, 030 | Đàn xe máy rất dày | R-09 | box cho xe/người rõ ở tiền cảnh, phần còn lại một `ignore_region` | không thể phân tách từng vật |
| img_032 | Đám đông chờ xe buýt, xe con bị cắt mép | R-06, R-09 | đám đông → `ignore_region`; xe con `car` `truncated=yes` | người nhỏ chen nhau |
| img_014 | Người đi bộ rõ nét nhưng nền xe máy bị nhòe | R-10 | 2 `person` rõ; nền nhòe → `ignore_region` | không phân loại được xe nhòe |
| img_024 | Xe nhỏ màu vàng đặt trên nóc xe đen | R-14 | `car` cho xe đen, xe vàng không gán, `can_review` | vật trưng bày dạng mô hình |
| img_019 | Xe Dangermouse trong diễu hành đông người | R-09, R-12 | `car` + `can_review`; đám đông phía sau `ignore_region` | xe thật chạy được nhưng hình dạng lạ |
| img_011 | Nhân vật Predator hóa trang | R-13 | `person` + `can_review` | không chắc người thật hay mô hình |
| img_022 | Xe máy sidecar, ảnh đen trắng, nhỏ | R-01, R-08 | một `motorcycle` ôm cả sidecar nếu cao ≥ 20 px; không thì bỏ | xe và sidecar là một phương tiện |
| img_007 | Pickup + xe tải thùng kín trong kho ban đêm, đèn chói | R-01 | cả hai `truck`; box ôm phần thấy dù ngược sáng | đèn không làm đổi lớp |
| img_015 | Trời mưa, xe đỏ và xe bạc bị cắt mép ở tiền cảnh, xe nền mờ | R-06, R-08 | 2 xe tiền cảnh `car` `truncated=yes`; xe nền nhỏ/mờ → `ignore_region` | phản chiếu mặt đường không gán |

**Ca cần hỏi reviewer (chưa tự chốt được):** tuk-tuk → `motorcycle` hay thêm lớp mới (R-04); xe nhỏ đặt trên xe khác có phải xe thật không (R-14); người hóa trang (R-13).

## 5. QC và phiên bản

- Ngưỡng IoU: box cao ≥ 50 px cần ≥ 0.85, box nhỏ hơn ≥ 0.7; IAA cần IoU TB ≥ 0.85, cùng lớp ≥ 95% (xem `taxonomy.json` mục `rules`, không sửa).
- Ca mơ hồ: tick `can_review`; ca không vẽ được box: ghi (ảnh, vùng, lý do) để nhóm đưa vào `image_issues.csv`.
- Ca R-04, R-05, R-14 mang sang họp Pha 2: đây là chỗ hai người có nhiều khả năng quyết khác nhau nhất, nên IAA dễ lệch ở đây.

| Phiên bản | Thay đổi | Lý do (ca nào) |
|---|---|---|
| v0.9-cá-nhân | Viết lại từ v0: thêm R-01…R-14, ngưỡng thuộc tính, bảng ca khó | v0 không nêu xe máy + người, tuk-tuk, tượng, hàng hóa, đám đông (img_002, 004, 005, 017, 021, 033…) |

---
*Ghi chú kiểm lại:* bản này được soạn có AI hỗ trợ và dựa trên xem 40 ảnh qua ảnh thu nhỏ. Cần mở lại từng ảnh gốc trong CVAT để xác nhận mức che, số người và chiều cao box (R-08) trước khi gửi coach.
