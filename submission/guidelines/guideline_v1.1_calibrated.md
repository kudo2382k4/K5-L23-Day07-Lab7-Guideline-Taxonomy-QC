# Guideline gán nhãn — v1.1 — bản sau calibration

- Phiên bản: **v1.1** (sau calibration Pha 5; thay cho v1.0 khi sửa nhãn và QC)
- Ngày: 2026-11-17
- Gốc: `guideline_v1.0_agreed.md`. Chỗ đổi đánh dấu **[v1.1]**; tóm tắt ở mục 6. Loại thay đổi: `semantic` (xem `submission/guideline_change.json`)
- Nguồn: hợp nhất ba bản cá nhân `guideline_101.md` (v0.1-101), `guideline_102.md` (v0.9-102), `guideline_142.md` (v1.0-draft-142)
- Người viết / duyệt: 101, 102, 142
- Taxonomy đi kèm: `submission/taxonomy.json` (version `v1.0`, 8 lớp, mục `rules` giữ nguyên) → `cvat/labels_generated.json`
- Phạm vi: 40 ảnh `data/images/img_001.jpg` … `img_040.jpg`, bounding box trên CVAT, xuất COCO 1.0

> Mỗi quy tắc có mã `R-xx`. Phiếu calibration (`calibration_decisions.csv`) và phiếu QC (`qc_review.csv`) dẫn lại đúng mã này. Taxonomy **không đổi** (vẫn `submission/taxonomy.json` v1.0: 8 lớp, 3 thuộc tính, mục `rules`).

---

## 0. Tra nhanh khi gán

| Thấy gì | Làm gì | Quy tắc |
|---|---|---|
| Sedan, hatchback, SUV, MPV, wagon, taxi, xe cổ, xe diễu hành chạy được | `car` | R-05, R-09 |
| Xe thân hộp liền khối, < 16 chỗ (Hiace, Transit) | `van` | R-05 |
| Pickup (kể cả có nắp thùng), xe tải, xe thùng, đầu kéo, xe chở xe, songthaew | `truck` | R-05 |
| Xe buýt, minibus ≥ 16 chỗ | `bus` | R-05 |
| Xe 3 bánh có động cơ, có mui/cabin (tuk-tuk, auto-rickshaw) | `tuk_tuk` | R-05 |
| Xe máy, tay ga, mô tô, xe điện 2 bánh (kể cả sidecar, thùng kéo bên hông) | `motorcycle`, chỉ phần xe | R-02, R-06 |
| Người thật (đi bộ, ngồi, lái xe hở, ngồi sau xe máy) | `person`, mỗi người một box | R-03 |
| Người trong cabin kín (ô tô, buýt, van, nhìn qua kính) | không box | R-04 |
| Xe đạp, xích lô, xe đẩy, động vật, cọc tiêu | không box (người đi cùng vẫn `person`) | R-07 |
| Tượng, ma-nơ-canh, đồ chơi, mô hình, hình in, phản chiếu | không box, không ignore | R-08 |
| Xe được chở trên xe chở ô tô | `truck` cho xe chở + `car` cho từng xe con | R-10 |
| Vật cao < 20 px; cụm dày không tách được | không box; cụm ≥ 3 vật → `ignore_region` | R-14, R-15 |
| Phần xe gắn camera / xe người chụp ngồi | không box | R-16 |
| Chưa chắc | vẫn box nếu nhận ra lớp, tick `can_review` | R-19 |

---

## 1. Mục tiêu

**Mô hình dùng nhãn:** phát hiện vật 2D (object detection) cho camera giao thông và hỗ trợ lái (ADAS), trên ảnh đường phố có nhiều xe máy, xe ba bánh, đường đông, ban đêm, trời mưa.

**Mô hình phải trả lời:** trong ảnh có **người** và **phương tiện cơ giới thật** nào, ở đâu (box nhìn thấy), thuộc lớp nào.

**Sai ở đâu thì nguy hiểm** (xếp theo mức độ):

1. **Bỏ sót người hoặc xe thật** (false negative): xe không phanh trước vật cản. Nguy hiểm nhất, nhất là người đi bộ và người đi xe máy.
2. **Gán box lên vật không thật** (tượng, ma-nơ-canh, hình in, phản chiếu): mô hình phanh gấp vô cớ (phantom braking), dễ gây tai nạn từ xe phía sau.
3. **Cùng một tình huống mỗi người gán một kiểu** (xe máy lúc gộp người, lúc tách; tuk-tuk lúc là xe máy, lúc bỏ qua): IAA thấp, mô hình học nhiễu.
4. Sai lớp giữa các loại xe hoặc box lệch: ảnh hưởng ước lượng kích thước, khoảng cách, quỹ đạo.

**Ba nguyên tắc để quyết ca chưa có quy tắc:**

1. *"Mô hình có phải đoán ra điều này từ ảnh 2D không?"* Không thấy trong ảnh (phần bị che hết, người sau kính tối) thì không gán.
2. **Gán cái nhìn thấy, đo được, lặp lại được.** Hai người độc lập phải ra cùng kết quả.
3. **Vật không thật thì không đánh dấu gì** (mô hình phải học đó *không phải* người/xe). `ignore_region` chỉ dành cho vật thật quá nhỏ hoặc quá dày (R-15).

---

## 2. Lớp và thuộc tính

### 2.1 Lớp (mỗi vật thuộc đúng một lớp)

Phép thử lớp hay thuộc tính: *"Mô hình phát hiện vật có cần tự đoán ra điều này lúc suy luận không?"* Có → lớp. Không (chỉ để lọc, kiểm QC) → thuộc tính.

| Lớp | Định nghĩa (một câu) | Ví dụ trong 40 ảnh | Phản ví dụ / dễ nhầm |
|---|---|---|---|
| `car` | Ô tô chở người 4 bánh thân liền, gầm thấp: sedan, hatchback, SUV, crossover, MPV, wagon, taxi, xe cổ, xe trưng bày, xe diễu hành chạy được. | img_023 (Honda đen), img_012 (Mazda CX-5), img_040 (taxi xanh), img_024 (Pacer đen), 8 xe con trên sàn img_002, img_019 (xe diễu hành) | Pickup → `truck`; Hiace → `van`; xe đồ chơi img_038, bia mộ hình xe img_027 → không gán |
| `truck` | Xe chở hàng có **cabin tách khỏi thùng/sàn**: pickup (có hoặc không nắp thùng), xe tải nhỏ, xe tải thùng, xe phủ bạt, đầu kéo, xe chở ô tô, songthaew. | img_001 (Suzuki Carry), img_002 (xe chở xe), img_007 (Hilux gắn hộp, Isuzu Elf), img_012, img_028, img_036 (Veryca), img_037 (pickup nắp thùng cao) | Xe thân liền một khối → `van`; xe 3 bánh chở hàng → `tuk_tuk` |
| `van` | Xe thân hộp **liền khối một khoang** (cabin và khoang sau chung vỏ), cỡ nhỏ–trung, dưới 16 chỗ, chở người hoặc hàng nhẹ. | img_005 (Hiace bạc), img_016 (Hiace trắng) | SUV/MPV thân thấp → `car`; xe dài, ≥ 16 chỗ → `bus`; pickup có nắp thùng → `truck` |
| `bus` | Xe chở khách cỡ lớn hoặc minibus **từ 16 chỗ trở lên**: nhiều hàng cửa sổ khách, cửa lên xuống riêng. | img_009 (minibus), img_031 (buýt đêm), img_037 (buýt GO), img_040 (buýt cam, buýt nền) | Hiace mui cao → `van` |
| `tuk_tuk` | Xe **3 bánh có động cơ**, có mui hoặc cabin, chở khách hoặc hàng (tuk-tuk, auto-rickshaw, xe lam). | img_004 (2 xe), img_016 (xanh dương, xanh lá), img_035 (vàng, chở bao tải), img_040 | Xe máy kéo thùng bên hông (img_025) → `motorcycle`; xích lô đạp (img_023) → không gán |
| `motorcycle` | Xe **2 bánh có động cơ** (xe số, tay ga, mô tô, Vespa, xe điện 2 bánh), kể cả sidecar hoặc thùng kéo gắn liền; xe đậu không người vẫn tính. | img_006, img_010, img_016 (Vespa), img_022 (sidecar), img_025 (kéo thùng), img_029 (xe điện) | Xe đạp (img_006, img_029) → không gán; tuk-tuk → `tuk_tuk` |
| `person` | Người thật ở mọi tư thế (đi, đứng, ngồi, lái hoặc ngồi trên xe hở), kể cả người mặc đồ hóa trang đang đi/đứng. | img_014 (người qua đường), img_005 (người đi xe máy), img_004 (tài xế tuk-tuk), img_023 (người đạp xích lô) | Tượng (img_011, img_017), ma-nơ-canh (img_033), chân dung trên pano (img_018), ảnh dán kính (img_040), linh vật nhồi bông (img_019) → không gán |
| `ignore_region` | **Vùng** chứa vật thật quá nhỏ (< 20 px) hoặc quá dày không tách được; bỏ sót trong vùng không tính lỗi. | Đám đông sau rào img_019, cụm xe máy sâu trong bãi img_030, dòng xe xa img_021 | Không dùng để né vật rõ, đủ lớn; không dùng cho vật không thật hay vật ngoài taxonomy |

**Vật không thuộc lớp nào:**
- Xe đạp, xích lô, xe đẩy, xe lăn, xe kéo tay, động vật, cọc tiêu, biển báo → **không gán gì** (R-07). Người đi cùng vẫn `person`.
- Vật không thật → **không gán gì** (R-08).
- Không tự tạo lớp khi gán. Thêm lớp chỉ qua taxonomy và phiên bản guideline mới.

### 2.2 Thuộc tính

Áp dụng cho mọi lớp **trừ** `ignore_region`. Dùng thuộc tính `occluded_level` trong panel Objects, **không** dùng cờ `occluded` (phím `Q`) của CVAT.

#### `occluded_level` (R-11)

Tỉ lệ **diện tích** vật bị **vật khác** che, so với vật đầy đủ **ở tư thế hiện tại** (người ngồi xe tính theo dáng ngồi). Phần bị mép ảnh cắt **không** tính (thuộc `truncated`).

| Mức | Phần bị che | Neo nhận biết bằng mắt |
|---|---|---|
| `0` | ≤ 10% | thấy gần trọn vẹn |
| `1` | > 10% đến 40% | mất một góc, một bánh, một chân |
| `2` | > 40% đến 75% | thấy khoảng nửa vật hoặc ít hơn |
| `3` | > 75%, vẫn chắc chắn nhận ra lớp | chỉ thấy mảnh (đầu và vai, nửa bánh và đèn) |

- Phân vân giữa hai mức → **chọn mức cao hơn**.
- Phần bị che bởi chính phụ kiện của vật (mũ, áo mưa, hàng mang theo) **không** tính.
- Người lái che xe máy, xe máy che chân người lái: **có** tính (thường mức `1`).
- Che bởi vật mảnh (hàng rào thưa, dây, cành cây) → mức `1`–`2` tùy mật độ (img_018).
- **[v1.1]** Hai người lệch mức (133 ca `sai_thuoc_tinh`, phần lớn 0 vs 1): luôn chốt **mức cao hơn**. Người lái và xe máy che nhau **bắt buộc** tính, tối thiểu mức `1` (img_003, img_034). Người ngồi sau bị người trước che → tối thiểu `1`, thường `2`.

#### `truncated` (R-12)

| Giá trị | Khi nào |
|---|---|
| `no` | Vật nằm trọn trong ảnh, hoặc phần ngoài khung ≤ 5% |
| `yes` | Phần vật nằm ngoài khung > 5%: cạnh box trùng mép ảnh (≤ 2 px) và vật còn tiếp tục ra ngoài |

Chỉ xét mép **ảnh**. Vật vừa bị cắt mép vừa bị che → gán cả hai.

**[v1.1]** Đo bằng tọa độ: cạnh box cách mép ảnh ≤ 2 px → `yes`; ngược lại `no`. Không gán `yes` theo cảm giác "xe to, gần camera".

#### `can_review` (R-19)

Tick khi: (a) phân vân giữa hai lớp; (b) gặp loại vật guideline chưa nói tới; (c) mức che lưng chừng ở vật nổi bật; (d) vật mờ hoặc tối khó nhận. Nếu hơn ~10% box trong một ảnh bị tick, guideline còn thiếu quy tắc → ghi vấn đề cấp ảnh.

---

## 3. Quy tắc vẽ box

### R-01. Box chung (ôm phần nhìn thấy)
- Box là hình chữ nhật **nhỏ nhất chứa mọi pixel nhìn thấy** của vật (modal box). Không đoán phần bị che hay phần ngoài ảnh.
- Sai số mục tiêu ≤ 2 px mỗi cạnh; không chừa lề, không cắt mất thân vật.
- Vật bị cột, thân cây, người che cắt làm hai phần: vẫn **một box** từ biên ngoài bên này sang biên ngoài bên kia.
- **Gồm:** thân xe, bánh, gương, tay lái, baga, giá đồ gắn chặt, hàng nằm trong đường viền thân xe (R-13).
- **Không gồm:** bóng đổ, phản chiếu trên nền ướt, ăng-ten, cần mảnh, dây cáp, hàng nhô hoặc chất vượt khung xe (R-13).
- Người: từ đỉnh đầu (gồm mũ, nón) đến điểm thấp nhất thấy được, gồm đồ mang sát người (ba lô, túi). Đồ gánh, vật dài nhô xa khỏi người → bỏ ra.

### R-02. Xe máy
- `motorcycle` là **chỉ phần xe**: từ mép ngoài bánh trước đến bánh/đuôi sau, gồm yếm, pô, tay lái, gương, baga và phần thân xe thấy quanh người lái. **Không** gộp người vào box xe.
- Xe đậu không người vẫn `motorcycle`.
- Chỉ thấy gương hoặc tay lái (< ~25% xe, img_040 tiền cảnh) → không box xe.

### R-03. Người trên xe
- Mỗi người (lái, ngồi sau, trẻ em ngồi trước) **một box `person` riêng**. 2 người trên một xe → 2 `person` + 1 `motorcycle` (img_010, img_026).
- Box `person` và box xe **được chồng lấn**.
- Người ngồi sau bị người trước che → thường `occluded_level` 1–2.
- Áp dụng tương tự cho tài xế/khách trên tuk-tuk, người đạp xe đạp/xích lô (xe đạp, xích lô không có box, R-07).

### R-04. Người trong cabin kín
- Người **trong cabin kín** (ô tô, xe tải, buýt, van, nhìn qua kính) → **không gán**, kể cả thấy mặt (img_009 hành khách minibus).
- Người trên phương tiện **hở hoặc bán hở** (xe máy, tuk-tuk, xích lô, thùng pickup hở) → gán `person` (img_004 tài xế tuk-tuk).
- Xe không mui hoặc cabin mở, người thấy rõ (img_019 tài xế xe diễu hành) → gán `person`.

### R-05. Phân lớp xe 4 bánh trở lên (cây quyết định)
1. Có thùng hàng hoặc sàn **tách khỏi cabin** (thùng hở, bạt, thùng rời, nắp thùng), hoặc là đầu kéo, xe chở xe → `truck`. **Pickup có nắp thùng cao vẫn là `truck`** (img_007, img_037): một box ôm cabin, thùng, nắp.
2. Xe chở khách có nhiều hàng cửa sổ, ≥ 16 chỗ → `bus` (img_009, img_031, img_037, img_040).
3. Thân hộp liền khối một khoang, cao, cửa trượt hoặc kính hông kéo dài, < 16 chỗ → `van` (img_005, img_016).
4. Còn lại → `car`.
5. Vẫn phân vân giữa hai lớp → chọn lớp gần nhất theo hình dáng nhìn ngoài và tick `can_review`.
6. **[v1.1]** Ca đã chốt khi calibration: Hiace img_005 → `van` (box ôm cả thân tới mép phải); xe trắng nhỏ cắt mép trái img_005 → `car`; SUV và xe đỏ sau hàng rào img_018 → `car`; xe diễu hành img_019 → `car`; xe sau tượng img_011 → `car`; Veryca phủ bạt img_036 → `truck`; xe xanh lá sau pickup img_037 → `bus` (buýt GO); hai xe 3 bánh img_040 → `tuk_tuk`. **Pickup chở hàng tiền cảnh img_012 → `truck`** (cả hai người cùng gán `car`, IAA không bắt được, sửa theo bảng 4.2).

### R-06. Xe 3 bánh và xe ghép
- Xe 3 bánh có động cơ, có mui/cabin → `tuk_tuk`, một box ôm thân xe (không kèm hàng chất vượt mui, R-13).
- Mô tô + sidecar (img_022), xe máy kéo thùng bên hông (img_025) → **một** box `motorcycle` ôm cả xe và phần gắn liền. Không gán `tuk_tuk`.

### R-07. Vật ngoài taxonomy
- Xe đạp, xích lô, xe đẩy, xe lăn, xe kéo tay, động vật, cọc tiêu → **không box, không `ignore_region`**.
- Người đạp/ngồi/đẩy vẫn `person` (R-03).

### R-08. Vật không thật → không gán, không ignore
- Gồm: tượng, điêu khắc (img_011 đầu quái vật, img_013 rồng vàng, img_017, ngựa trên xe img_028), bia/công trình hình xe (img_027), ma-nơ-canh (img_033), búp bê, linh vật nhồi bông (img_019), xe đồ chơi và mô hình (img_038), hình in (pano img_018, tranh tường img_026, poster img_030, ảnh dán kính img_040), mọi **phản chiếu** (gương img_020, kính img_033, mặt đường ướt img_013, img_015).
- **Ngoại lệ:** người thật mặc trang phục hóa trang, thấy rõ là người đang đứng/đi → `person` + `can_review`. Vật cao lớn bất thường, đặt trên bục, không có thân người (img_011) là tượng.
- Không chắc người thật hay mô hình → không box, ghi vấn đề cấp ảnh (ảnh, vùng, lý do).

### R-09. Xe thật nhưng kiểu lạ
- Tiêu chí "thật": kích thước thật, có bánh chạy được, có biển số hoặc người lái, hoặc đặt trong bảo tàng/showroom/khu trưng bày đúng nghĩa.
- Xe diễu hành, xe độ, xe cổ, xe trưng bày → gán theo **lớp tương đương về hình dáng và kích thước**, tick `can_review` (img_019 → `car`; img_024 các xe trong bảo tàng → `car`; img_011 xe mô tô độ bằng kim loại cỡ thật → `motorcycle` + `can_review`).

### R-10. Xe được chở trên xe khác
- **Xe chở ô tô** (img_002): một box `truck` ôm đầu kéo, rơ-moóc và khung chở; **mỗi ô tô con nguyên chiếc** trên sàn thêm một box `car`, `occluded_level` theo khung sắt và xe bên cạnh. Box `car` nằm trong box `truck` là được phép.
- **Thân vỏ, nửa xe, mô hình** đặt trên nóc hoặc thùng xe khác (img_024 vỏ xe vàng trên nóc): **không box**; box xe bên dưới **không** kéo lên phần đó.
- Vật khác trên xe (tượng ngựa img_028): không box (R-08); box xe không kéo theo phần nhô.

### R-11. Che khuất
- Áp dụng bảng `occluded_level` (mục 2.2).
- Vật bị che vẫn gán nếu **thấy ≥ ~25%** và chắc chắn nhận ra lớp. Thấp hơn → không box lớp; nếu nằm trong cụm thì thuộc `ignore_region` (R-15).

### R-12. Cắt mép ảnh
- Áp dụng `truncated` (mục 2.2). Vẫn gán nếu phần trong ảnh nhận ra lớp. Box kéo đúng tới mép ảnh, **không vượt** ra ngoài khung (chú ý ảnh dọc img_017, img_020, img_026 rộng 768–784 px).

### R-13. Hàng hóa trên xe
- Hàng **nằm trong đường viền thân xe** (ống thép trong thùng img_001, hàng trong thùng pickup img_012) → nằm sẵn trong box xe, không làm gì thêm.
- Hàng **chất vượt mui/khung** hoặc **nhô dài** ra khỏi xe (bao tải trên nóc tuk-tuk img_035, thanh dài trên xe điện img_029) → **không** kéo box theo hàng; box chỉ ôm thân xe.
- Hàng gánh, mang trên người (img_003) → không vào box `person`.

### R-14. Vật nhỏ
- Box cao **< 20 px** → không vẽ box lớp (ngưỡng `min_box_height_px` của taxonomy).
- Vật nhỏ đứng lẻ → không gán gì, không tính lỗi.
- **≥ 3 vật nhỏ** gần nhau → một `ignore_region` ôm cụm.
- Vật sát ngưỡng: **đo** bằng công cụ CVAT, không đoán. Từ 20 px trở lên và nhận ra lớp → **phải gán**.

### R-15. Đám đông, cụm dày và `ignore_region`
- Gán từng `person`/`motorcycle` khi: **cao ≥ 20 px, thấy ≥ ~25%, tách được biên**.
- Phần còn lại (nền xa, chồng chéo không tách được, quá nhỏ) → **một `ignore_region`** ôm cụm; cụm rời nhau thì vài vùng.
- Ví dụ: đám đông sau rào img_019; khách ngồi xa lẫn bàn ghế img_001; cụm xe máy sâu trong bãi img_030; dòng xe phía xa img_021; người ghế bãi biển img_025; người sau hàng đầu ở trạm chờ img_032.
- `ignore_region` **chỉ** dùng cho vật thật quá nhỏ, quá dày, thấy quá ít. **Không** dùng cho vật ngoài taxonomy, vật không thật, hay để né ca khó còn gán được.
- `ignore_region` **không phủ lên** box lớp đã gán. Vùng sát nhau cùng loại → gộp làm một.
- **[v1.1]** Chỉ dùng `ignore_region` thay cho box từng vật ở các ảnh đám đông/xe dày đã nêu (img_001, 003, 019, 021, 025, 030, 032). Ở các ảnh này, vật nằm trong vùng ignore của cụm thì **không** vẽ thêm box riêng (img_019: đám đông sau rào, kể cả người ở hàng đầu rào). Ở ảnh khác, người/xe cao ≥ 20 px và tách được biên **phải** có box (img_011: khách tham quan cao 40–60 px phải box, không phủ ignore).
- **[v1.1]** Ca một người vẽ, người kia không: giữ box nếu cao ≥ 20 px, thấy ≥ 25%, là vật thật; không đạt thì xóa (R-14).

### R-16. Xe chủ (ego)
- Phần xe gắn camera hoặc xe người chụp ngồi trong (khung cửa, gương nhìn từ trong xe, nắp ca-pô, bảng điều khiển) → **không gán** (img_020).
- Xe khác sát camera bị cắt mép → vẫn gán, `truncated=yes` (img_015). Không thấy dấu hiệu camera gắn trên xe (img_012) → coi là xe khác, gán bình thường.

### R-17. Điều kiện ảnh khó
- **Mờ chuyển động:** nhận ra lớp và ước lượng được biên (±10 px) → box ôm **lõi** vật (không ôm vệt mờ), tick `can_review` (img_014, img_015 xe nền). Không nhận ra → cụm thì `ignore_region`, lẻ thì không gán.
- **Ban đêm, ngược sáng:** gán những gì thấy được; chỉ thấy đèn mà không nhận ra lớp → không gán (img_007, img_013, img_031).
- **Qua kính, hàng rào:** xe thật phía sau vẫn gán, `occluded_level` theo R-11 (img_018).
- **Ảnh đen trắng, ảnh cũ:** luật không đổi (img_022).

### R-18. Ảnh không có vật cần gán
- Ảnh vẫn nằm trong Task, xuất COCO với **0 annotation** (img_017, img_020, img_027, img_033, img_038).
- Không "gán bù" lên vật giả.

### R-19. `can_review` và vấn đề cấp ảnh
- **Tick:** ca theo R-08 ngoại lệ, R-09, phân vân `car`/`van`/`truck`/`bus`, mức che lưng chừng, R-17 mờ.
- **Không tick:** ca quy tắc đã rõ, chỉ lệch tọa độ nhỏ.
- **[v1.1]** Sau calibration, mọi `can_review` của lô đã được chốt và bỏ tick; nhãn cuối không còn box `can_review`.
- Chỗ **không vẽ được box**: ghi (ảnh, vùng, lý do) để nhóm thu vào `submission/qc/image_issues.csv` (cột `image,annotator,region,note`) **sau khi khóa nhãn**.

### R-20. Box lồng nhau và trùng lặp
- Chỉ cho phép chồng/lồng: `person` với `motorcycle`/`tuk_tuk` (R-03); `car` trong `truck` chở xe (R-10).
- Một vật một box, một lớp. Hai box cùng vật (IoU > ~0.7) → xóa bớt.
- Không vẽ box riêng cho bộ phận (bánh xe, đầu người).
- **[v1.1]** Vật bị che cắt thành nhiều mảnh vẫn là **một box** (R-01): không vẽ 3 box `car` cho một chiếc van bị người che (img_005), không vẽ thêm box cho nửa phải của taxi (img_040), không vẽ hai box cho cùng một người tiền cảnh (img_019).

---

## 4. Ca khó và cách giải quyết bất đồng

### 4.1 Bất đồng giữa ba bản cá nhân và quyết định của nhóm

| # | Vấn đề | 101 | 102 | 142 | **Quyết định v1.0** | Lý do |
|---|---|---|---|---|---|---|
| D1 | Xe buýt | `ignore_region` | không gán | lớp mới `bus` | **Thêm lớp `bus`** (R-05) | Có ở ≥ 4 ảnh (img_009, 031, 037, 040); là vật cản lớn, bỏ qua thì mô hình mù với xe to nhất trên đường. |
| D2 | Tuk-tuk / xe 3 bánh | `ignore_region` | `motorcycle` + `can_review` | lớp mới `tuk_tuk` | **Thêm lớp `tuk_tuk`** (R-06) | Có ở 4 ảnh; hình dáng và kích thước khác hẳn xe máy, ép vào `motorcycle` làm nhiễu lớp này; `ignore_region` làm mô hình không học được. |
| D3 | Xe đạp, xích lô | `ignore_region` | không gán | không gán | **Không gán**, người vẫn `person` (R-07) | 2/3 đồng ý. Không phải phương tiện cơ giới; dùng `ignore_region` cho vật rõ, lớn sẽ trái R-15. |
| D4 | Xe chở ô tô img_002 | 1 `truck`, xe con không box | 1 `truck`, xe con không box | `truck` + 8 `car` | **`truck` + `car` cho từng xe con** (R-10) | Xe con là ô tô thật nhìn rõ; nếu không gán, mô hình bị phạt khi phát hiện đúng hình dạng ô tô và học "ức chế" lớp `car`. Thân vỏ/mô hình (img_024) vẫn không gán, cả ba bản đều đồng ý. |
| D5 | Hàng hóa | gồm hàng chất gọn, bỏ vật nhô xa | không bao giờ gồm hàng | gồm hàng trong viền xe, bỏ hàng vượt khung | **Gồm hàng trong viền thân xe; bỏ hàng vượt mui/nhô dài** (R-13) | Kết hợp: đo được bằng đường viền thân xe, tránh box méo (img_035, img_029). |
| D6 | Ngưỡng `occluded_level` | 10/40/75% | 10/40/75% | 10/40/70% | **10 / 40 / 75%**, phân vân chọn mức cao hơn | 2/3 đồng ý; quy tắc "chọn mức cao hơn" của 101 giảm lệch ở ranh giới. |
| D7 | Người hóa trang img_011 | hóa trang là `person` | Predator là người hóa trang → `person` | là tượng | **Là tượng, không gán**; quy tắc hóa trang giữ lại cho người thật đang đi/đứng (R-08) | Xem ảnh gốc: đầu cao gần bằng người, đặt trên bục, không có thân người → điêu khắc. |
| D8 | Mờ chuyển động img_014 | gán lõi nếu nhận ra | → `ignore_region` | gán + `can_review` | **Nhận ra lớp và biên → box lõi + `can_review`; không → `ignore_region`** (R-17) | Không bỏ sót người/xe thật nhận ra được; vệt mờ không nhận ra thì không ép. |
| D9 | Đám đông img_032 | gán nếu ≥ 20 px, thấy ≥ 25% | cả đám → `ignore_region` | box người tách được | **Tiêu chí đo được: cao ≥ 20 px, thấy ≥ 25%, tách được biên → box; còn lại `ignore_region`** (R-15) | Người hàng đầu cao 70–100 px, rõ; phủ ignore cả đám là né vật rõ. |
| D10 | Người trong cabin | không gán | gán tài xế tuk-tuk | không gán | **Cabin kín không gán; xe hở (tuk-tuk, xe máy, xích lô) gán** (R-04) | Ba bản thực chất cùng ý; ghi rõ ranh giới kín/hở. |
| D11 | Minibus img_009 | ≤ 15 chỗ là `van` | — | `bus` | **`bus`** | Xe nhiều hàng cửa sổ, cửa khách riêng, cỡ ~29 chỗ, vượt ngưỡng 16. |
| D12 | Mô tô kim loại img_011 | — | — | không gán (điêu khắc) | **`motorcycle` + `can_review`** (R-09) | Cỡ thật, đủ bánh, yên, tay lái, đặt ở khu trưng bày → coi như xe trưng bày; ghi `can_review` để calibration xác nhận. |

### 4.2 Bảng ca khó theo ảnh

| Ảnh | Tình huống | Rule | Quyết định | Lý do |
|---|---|---|---|---|
| img_001 | Xe tải nhỏ chở ống thép, bị cô gái che, cắt mép phải; khách ngồi phía sau | R-05, R-11, R-12, R-15 | `truck` (`occluded_level` 1, `truncated=yes`); `person` cho người đứng và người ngồi tách được; khách xa lẫn bàn ghế → `ignore_region`; poster không gán | Ống nằm trong thùng nên trong box. |
| img_002 | Xe chở 8 ô tô con trên 2 tầng; công nhân bên phải | R-10 | 1 `truck` + 8 `car`; công nhân `person` | D4. |
| img_003 | Xe đạp, người gánh hàng, dãy xe máy dựng | R-07, R-13, R-15 | Xe đạp không gán; người `person` (không kèm gánh); xe máy rõ box riêng, cụm xa `ignore_region` | — |
| img_004 | Hai tuk-tuk, tài xế ngồi trong | R-06, R-04 | 2 `tuk_tuk`; tài xế thấy rõ → `person` (`occluded_level` 2) | D2, D10. |
| img_005 | Nhiều người đội mũ chen nhau, cắt mép; van phía sau | R-03, R-11, R-12 | `person` từng người (`occluded_level` 1–3, `truncated` nếu chạm mép); xe máy thấy ≥ 25% → `motorcycle`; Hiace `van` | Che chồng nặng → chọn mức cao hơn. |
| img_007 | Hilux gắn hộp sau, Isuzu Elf cắt mép, ngược sáng | R-05, R-12, R-17 | Cả hai `truck`; Isuzu `truncated=yes` | Cabin tách thùng. |
| img_008 | Đêm, xe máy dựng dày, songthaew phía xa | R-05, R-15 | Xe máy/người tách được box riêng; cụm sâu `ignore_region`; songthaew `truck` | — |
| img_009 | Minibus, hành khách sau kính | R-05, R-04 | `bus`; hành khách không gán; xe máy, người ≥ 20 px gán | D11. |
| img_011 | Đầu quái vật điêu khắc, mô tô kim loại, ô tô thật bị che, người xa | R-08, R-09, R-11, R-14 | Tượng không gán; mô tô `motorcycle` + `can_review`; ô tô `car` (`occluded_level` 2); người ≥ 20 px gán, cụm nhỏ `ignore_region` | D7, D12. |
| img_012 | Pickup chở hàng tiền cảnh, cắt mép; CX-5; xe tải phía trước | R-16, R-12, R-13 | Pickup `truck` `truncated=yes`; `car`; `truck` | Không có dấu hiệu camera gắn trên xe. |
| img_013 | Đêm, tượng rồng vàng, phản chiếu trên đường ướt | R-08, R-17 | 2 `person`; tượng, phản chiếu không gán; xe xa ≥ 20 px gán | — |
| img_014 | Hai người đi bộ rõ; xe máy, người mờ chuyển động | R-17 | 2 `person`; mờ còn nhận ra → box lõi + `can_review`; không → `ignore_region` | D8. |
| img_015 | Xe đỏ, SUV bạc cắt mép; xe nền nhòe; đường ướt | R-12, R-17, R-08 | 2 `car` `truncated=yes`; xe nền nhận ra → `car` + `can_review`; phản chiếu không gán | — |
| img_016 | 2 tuk-tuk, Vespa, Hiace, pickup, người áo đỏ cắt mép | R-06, R-03, R-05 | 2 `tuk_tuk`; `motorcycle` + `person`; `van`; `truck`; `car` (xe đen bị che); `person` `truncated=yes` | — |
| img_017 | Tượng người cưỡi ngựa | R-08, R-18 | 0 annotation | — |
| img_018 | Chân dung trên pano; xe sau hàng rào; chụp qua kính | R-08, R-11, R-17 | Pano không gán; xe ≥ 20 px → `car`/`truck` (`occluded_level` 1–2) | — |
| img_019 | Xe diễu hành có tài xế; linh vật chuột; đám đông sau rào | R-09, R-04, R-08, R-15 | `car` + `can_review`; tài xế `person`; linh vật không gán; đám đông `ignore_region`; đầu người mờ tiền cảnh → `person` + `can_review` | — |
| img_020 | Gương chiếu hậu phản chiếu xe | R-08, R-16, R-18 | 0 annotation | — |
| img_021 | Dòng xe máy rất dày, xe con lẫn trong | R-03, R-15 | Hàng gần: `person` + `motorcycle` từng xe; xe con thấy ≥ 25% → `car`; phần xa `ignore_region` | — |
| img_022 | Ảnh đen trắng, mô tô sidecar | R-06, R-17 | 1 `motorcycle` gồm sidecar + `person` (nếu ≥ 20 px) | — |
| img_023 | Xích lô có người đạp, sedan, xe máy xa | R-07, R-03 | Xích lô không gán; người đạp `person`; `car`; `motorcycle` + `person` | — |
| img_024 | Vỏ xe vàng trên nóc xe đen trong bảo tàng | R-10, R-09 | Xe đen và các xe trưng bày `car`; vỏ vàng không gán, box xe đen không kéo lên | Cả ba bản đồng ý. |
| img_025 | Xe máy kéo thùng bên hông; taxi; đám người bãi biển | R-06, R-15 | `motorcycle` (gồm thùng) + `person`; `car`; người đi bộ rõ gán, đám ghế bãi biển `ignore_region` | — |
| img_026 | Hai người trên xe máy, ảnh mờ, tranh tường cảng | R-03, R-08, R-12 | 1 `motorcycle` + 2 `person`; tranh không gán; box không vượt biên 784 px | — |
| img_027 | Bia mộ đá hình pickup | R-08, R-18 | 0 annotation | — |
| img_028 | Pickup cổ chở tượng ngựa; SUV đỏ phía sau | R-10, R-08, R-11 | `truck` (không kéo lên ngựa); SUV `car` (`occluded_level` 2) | — |
| img_029 | Xe điện chở thanh dài; người đi xe đạp | R-13, R-07 | `motorcycle` (không kèm thanh) + `person`; xe đạp không gán, người đạp `person` | D5. |
| img_030 | Bãi xe máy dày; bảo vệ; poster người | R-15, R-08 | Xe tiền cảnh tách được box riêng; cụm sau `ignore_region`; bảo vệ `person`; poster không gán | — |
| img_031 | Đêm, xe con, buýt, xe máy, người đi bộ | R-05, R-17 | `car`, `bus`, `motorcycle` + `person`, `person` | — |
| img_032 | Đám đông chờ xe; xe con cắt mép trái | R-15, R-12 | Người hàng đầu tách được → `person` từng người; phần chồng dày phía sau `ignore_region`; `car` `truncated=yes` | D9. |
| img_033 | Ma-nơ-canh, ảnh in, phản chiếu xe qua kính | R-08, R-18 | 0 annotation | — |
| img_035 | Tuk-tuk chất bao tải cao gấp đôi | R-06, R-13 | `tuk_tuk` chỉ ôm thân xe; `motorcycle` + `person`; `car` | D5. |
| img_036 | Xe tải nhỏ phủ bạt | R-05 | `truck` | Cabin tách thùng. |
| img_037 | Pickup nắp thùng cao "Master 75"; xe buýt GO | R-05 | `truck`; 2 `bus` (một bị che); người đi bộ `person` | Cả ba bản đồng ý `truck`. |
| img_038 | Tủ kính xe đồ chơi, búp bê | R-08, R-18 | 0 annotation | — |
| img_040 | Người đội mũ cận cảnh, chỉ thấy gương xe; taxi; tuk-tuk; SUV; buýt; ảnh dán kính | R-02, R-03, R-08, R-12 | `person` `truncated=yes`; xe máy không box (chỉ thấy gương); `car` ×2; `tuk_tuk`; `bus`; ảnh dán không gán | — |

---

## 5. QC và phiên bản

### 5.1 Ngưỡng áp dụng (mục `rules` của `taxonomy.json`, không sửa)

| Đại lượng | Ngưỡng |
|---|---|
| Chiều cao box tối thiểu | 20 px (R-14) |
| IoU ghép cặp box | ≥ 0.5 |
| IoU đạt | box cao ≥ 50 px: ≥ 0.85; nhỏ hơn: ≥ 0.7 |
| IAA (trên cặp box ghép 1–1) | IoU trung bình ≥ 0.85; cùng lớp ≥ 95% |
| Độ phủ | 100% lượt gán theo `assignment.csv` mới đo IAA |
| Release | duyệt toàn lô, ảnh lỗi ≤ 2% (lô 40 ảnh: 0 ảnh lỗi), không lỗi lặp |

### 5.2 Quy trình
- **Pha 3 (gán độc lập):** dùng đúng v1.0 này. Chưa chắc → `can_review` hoặc ghi vấn đề cấp ảnh; **không hỏi nhau**.
- **Tự kiểm trước khi export:** đủ ảnh được giao (kể cả ảnh 0 annotation); không box lớp cao < 20 px; mọi `ignore_region` có lý do theo R-15; vật giả không có box; đã điền `occluded_level`, `truncated`.
- **Ca mơ hồ sau khi khóa nhãn:** cả nhóm họp calibration; người chốt ghi vào `calibration_decisions.csv` kèm mã `R-xx`, phạm vi `anh` hoặc `lo`.
- **Thay đổi:** chỉ sửa câu chữ → `editorial`. Đổi cách chọn vật, lớp, box, thuộc tính → `semantic`, cần ít nhất một quyết định `pham_vi=lo` và kiểm lại cả lô; tăng lên v1.1.
- **Script không kiểm được** (cần mắt người): box có ôm sát không, lớp có đúng thực tế không, vật cả nhóm cùng bỏ sót, cả nhóm cùng hiểu sai quy tắc (ví dụ cùng gán box lên tượng).

### 5.3 Lịch sử phiên bản

| Phiên bản | Thay đổi | Lý do (ca nào) |
|---|---|---|
| v0 | Bản khởi đầu: 5 lớp + `ignore_region`, thuộc tính định tính, chưa có ca khó | — |
| v0.1-101, v0.9-102, v1.0-draft-142 | Ba bản cá nhân Pha 1 | Khảo sát 40 ảnh độc lập |
| v1.0 | Thêm lớp `bus`, `tuk_tuk` (8 lớp); ngưỡng `occluded_level` 10/40/75%, `truncated` 5%; quy tắc R-01…R-20; giải quyết 12 bất đồng D1–D12; bảng ca khó 36 ảnh | D1, D2 (img_004, 009, 016, 035, 037, 040); D4 (img_002); D7, D12 (img_011); D9 (img_032) |
| **v1.1** | Calibration 523 ca / 35 ảnh: chốt mức che cao hơn (R-11), `truncated` đo bằng tọa độ (R-12), danh sách ảnh đám đông dùng ignore (R-15), một vật một box kể cả khi bị che thành mảnh (R-20), chốt lớp các ca sai_lop (R-05/R-06), bỏ hết `can_review` (R-19) | IAA cặp 101–102 IoU 0.806 và 102–142 IoU 0.822 chưa đạt; 177 bo_sot_thua, 133 sai_thuoc_tinh, 94 iou_thap, 48 bat_dong_ignore, 11 sai_lop |

---

## 6. Thay đổi v1.0 → v1.1 (tóm tắt calibration)

Nguồn: `submission/qc/iaa_summary.md` (342 cặp box ghép, IoU TB 0.888, cùng lớp 96.8%, cùng `occluded_level` chỉ 63.7%) và `submission/qc/calibration_decisions.csv` (523 ca, 181 ca phạm vi `lo`).

| Mã | Vấn đề phát hiện | Quy tắc v1.1 | Phạm vi |
|---|---|---|---|
| R-11 | `occluded_level` lệch 36% cặp box (102–142 chỉ khớp 39%) | Lệch thì lấy mức cao hơn; người lái ↔ xe máy luôn ≥ 1 | lô |
| R-12 | `truncated` đánh theo cảm giác | Cạnh box ≤ 2 px mép ảnh → `yes` | lô |
| R-14 / R-15 | 177 box chỉ một người vẽ; 48 vùng ignore không khớp | Giữ box ≥ 20 px tách được; ignore chỉ ở 7 ảnh đám đông; ảnh khác không phủ ignore lên người rõ | lô |
| R-01 / R-02 | 94 cặp IoU dưới ngưỡng | Box ôm sát phần nhìn thấy; một vật một box, không vẽ theo mảnh | ảnh |
| R-05 / R-06 | 11 ca sai lớp + 1 ca cả hai cùng sai (img_012) | Chốt lớp từng ca (mục R-05 điểm 6) | ảnh |
| R-19 | 60 box `can_review` | Đã chốt; bỏ tick toàn lô | ảnh |
| R-20 | Box trùng/mảnh vỡ (102 vẽ 3 box cho 1 van, img_005; nhiều box cho taxi img_040) | Một vật một box | lô |

Vì đổi cách chọn vật và cách chấm thuộc tính, thay đổi là `semantic`: **cả lô 40 ảnh** được rà lại theo v1.1 (không chỉ 35 ảnh bị cờ).
