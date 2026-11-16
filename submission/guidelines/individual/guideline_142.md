# Guideline gán nhãn — v1.0-draft — thành viên 142

- Phiên bản: v1.0-draft (bản cá nhân, sửa từ v0)
- Ngày: 2026-11-16
- Người viết: 142 · Người duyệt: (nhóm, Pha 2)
- Phạm vi: 40 ảnh `data/images/img_001.jpg` … `img_040.jpg`, bounding box trên CVAT, xuất COCO 1.0

> Quy ước đọc: mỗi quy tắc có mã `R-xx`. Bảng ca khó (mục 4) dẫn lại mã này. Ca ghi **[Hỏi reviewer]** là ca mình chưa chắc, cần nhóm chốt ở Pha 2.

---

## 1. Mục tiêu

- **Mô hình dùng nhãn:** mô hình phát hiện vật 2D (object detection) cho camera giao thông / xe tự hành, chạy trên ảnh đường phố châu Á và châu Âu.
- **Mô hình cần trả lời:** trong ảnh có **người** và **phương tiện giao thông thật** nào, ở đâu (box), thuộc loại nào.
- **Sai chỗ nào nguy hiểm nhất:**
  1. **Bỏ sót người hoặc xe thật** (nhất là người đi xe máy, người đi bộ băng qua đường). Đây là lỗi nghiêm trọng nhất vì xe tự hành không phanh.
  2. **Gán vật không thật** (tượng, ảnh in, phản chiếu, đồ chơi) thành người/xe. Mô hình học sai sẽ phanh gấp vô cớ, nhưng ít nguy hiểm hơn bỏ sót.
  3. Sai lớp giữa các loại xe (car/van/truck/bus) ảnh hưởng dự đoán kích thước và quỹ đạo, mức độ trung bình.
- **Không thuộc mục tiêu:** xe đạp, xích lô, xe đẩy, động vật, biển báo, cọc giao thông. Các vật này không gán box (xem R-04), nhưng **người ngồi/đẩy chúng vẫn gán `person`**.

---

## 2. Lớp và thuộc tính

### 2.1 Lớp

Phép thử khi phân vân lớp hay thuộc tính: *"Mô hình phát hiện vật có cần tự đoán ra điều này lúc suy luận không?"* Có → là lớp. Không (chỉ dùng để lọc, kiểm QC) → là thuộc tính.

So với v0, mình **đề xuất thêm 2 lớp `bus` và `tuk_tuk`**, vì trong 40 ảnh có nhiều xe buýt (img_009, 021, 031, 037, 040) và xe ba bánh (img_004, 016, 035, 040). Nếu ép vào `van`/`truck`/`motorcycle` thì người gán sẽ chọn khác nhau.

| Lớp | Định nghĩa (một câu) | Ví dụ | Phản ví dụ / dễ nhầm với |
|---|---|---|---|
| `car` | Ô tô chở người 4 bánh, thân liền (sedan, hatchback, SUV, crossover, taxi, xe cổ, xe diễu hành chạy được và có biển số). | Sedan đen img_023, taxi xanh img_040, Mazda CX-5 img_012, 8 xe con trên xe chở xe img_002, xe vàng diễu hành img_019 | Bán tải có thùng hở → `truck`. Minivan chở khách thân hộp (Hiace) → `van`. Xe mô hình/đồ chơi img_038, tượng xe img_027 → **không gán** |
| `truck` | Xe chở hàng có **cabin tách khỏi thùng hàng**: bán tải (kể cả có nắp thùng/canopy), xe tải nhỏ, xe tải thùng, đầu kéo, xe chở ô tô, songthaew. | Suzuki Carry img_001, xe chở ô tô img_002, Isuzu Elf img_007, Mitsubishi Veryca phủ bạt img_036, bán tải canopy cao img_037, bán tải cổ img_028 | Minivan thân liền → `van`. Bán tải đá làm bia mộ img_027 → **không gán** |
| `van` | Xe thân hộp liền khối (cabin và khoang sau chung một khối), cỡ nhỏ–trung, dưới khoảng 16 chỗ, chở người hoặc hàng. | Toyota Hiace img_005, img_016 | Xe dài ≥ 2 cửa khách, ≥ 16 chỗ (Hyundai County img_009) → `bus`. SUV → `car` |
| `bus` | Xe chở khách cỡ lớn hoặc minibus ≥ 16 chỗ: có nhiều hàng cửa sổ khách và cửa lên xuống riêng. | Minibus img_009, xe buýt GO img_037, xe buýt đêm img_031, buýt cam img_040 | Hiace cao mui → `van` |
| `tuk_tuk` | Xe 3 bánh có động cơ, có mui/khoang chở khách hoặc hàng (tuk-tuk Thái, auto-rickshaw Ấn Độ). | img_004 (2 xe), img_016 (xanh dương, xanh lá), img_035 (vàng), img_040 | Xe máy kéo thùng bên hông (img_025) → `motorcycle` (R-08). Xích lô đạp img_023 → **không gán** |
| `motorcycle` | Xe 2 bánh có động cơ (xe máy, tay ga, mô tô, xe điện 2 bánh, Vespa), **kể cả thùng/sidecar gắn liền**. | Xe máy img_006, img_010, Vespa img_016, mô tô sidecar img_022, xe điện chở ống img_029 | Xe đạp img_006, img_029 → **không gán**. Mô tô điêu khắc kim loại img_011 → **không gán** |
| `person` | Người thật, bất kể tư thế (đi, đứng, ngồi, lái xe máy/xe đạp/xích lô, ngồi trên tuk-tuk). | Người đi bộ img_014, người lái xe máy img_005, tài xế tuk-tuk img_004, người đạp xích lô img_023 | Tượng img_017, ma-nơ-canh img_033, chân dung trên biển quảng cáo img_018, ảnh dán kính img_040, linh vật/thú nhồi img_019 → **không gán** |
| `ignore_region` | **Vùng** (không phải vật) chứa nhiều người/xe mà không thể hoặc không cần box từng cái. Bỏ sót trong vùng này không tính lỗi. | Bãi xe máy dày đặc img_030, đám đông sau rào img_019, dòng xe phía xa img_021 | Không dùng để che vật to rõ đáng ra phải box, không dùng cho vật không thật |

**Vật không thuộc lớp nào** (R-04): **không gán gì**, không dùng `ignore_region` để đánh dấu. Áp dụng cho: xe đạp, xích lô, xe đẩy hàng, xe đẩy em bé, chó/ngựa, cọc giao thông. Riêng **người** đi cùng các vật này vẫn gán `person`.

### 2.2 Thuộc tính

Áp dụng cho mọi lớp trừ `ignore_region`.

**`occluded_level`**: tỉ lệ **diện tích ước lượng của vật** bị **vật khác** che (không tính phần bị mép ảnh cắt, phần đó thuộc `truncated`).

| Mức | Ngưỡng | Ví dụ |
|---|---|---|
| `0` | che ≤ 10% | Xe chở ô tô img_002 (đầu xe), người đàn ông đi bộ img_014 |
| `1` | 11–40% | Xe máy bị người lái che phần giữa img_010, xe tải img_001 bị cô gái che đuôi |
| `2` | 41–70% | Xe SUV đỏ phía sau bán tải img_028, xe ô tô bị che bởi tượng img_011 |
| `3` | > 70% nhưng **vẫn chắc chắn nhận ra lớp** | Xe con chỉ thấy nóc giữa dòng xe máy img_021. Nếu không nhận ra lớp → không box (hoặc nằm trong `ignore_region`) |

- Cách ước lượng nhanh: tưởng tượng hình dạng đầy đủ của vật, so phần bị che với tổng.
- Người lái xe máy che xe máy: tính là che (thường mức `1`). Xe máy che chân người lái: cũng tính (thường mức `1`).
- Hàng rào **thưa nhìn xuyên được** (img_018): nếu thấy rõ đường viền vật qua khe, tính mức theo phần bị thanh rào/biển che thật sự, thường `1`.
- Dùng thuộc tính `occluded_level` trong panel Objects, **không** dùng cờ `Q` mặc định của CVAT.

**`truncated`**: vật bị **mép ảnh** cắt.

| Giá trị | Ngưỡng |
|---|---|
| `no` | Box không chạm mép ảnh, hoặc chạm nhưng phần ước lượng nằm ngoài ảnh ≤ 5% |
| `yes` | Phần vật nằm ngoài khung ảnh > 5% |

Ví dụ `yes`: xe tải img_001 (mép phải), xe đỏ và SUV bạc img_015, người lái xe máy tiền cảnh img_005, img_040, cô gái áo đỏ img_016.

**`can_review`** (checkbox): tick khi **không chắc** về lớp, về có nên gán hay không, hoặc về đường biên box. Ghi ca vào bảng ca khó (mục 4) để nhóm chốt. Không dùng `can_review` thay cho quyết định đã có quy tắc rõ.

---

## 3. Quy tắc vẽ box

| Mã | Quy tắc |
|---|---|
| **R-01 Box ôm phần nhìn thấy** | Box là hình chữ nhật nhỏ nhất chứa **mọi pixel nhìn thấy** của vật (modal box). Không đoán phần bị che hay phần ngoài ảnh. Sai lệch cho phép ≤ 2 px mỗi cạnh. Gương chiếu hậu, cột ăng-ten mảnh, dây buộc hàng **không** tính vào box xe. |
| **R-02 Người đi xe máy = 2 loại box** | Mỗi **người** trên xe một box `person` (gồm mũ bảo hiểm, chân). Chiếc **xe** một box `motorcycle` (từ bánh trước đến bánh/đuôi sau, gồm phần nhìn thấy quanh người lái). Hai box được phép chồng nhau. Hai người trên một xe → 2 `person` + 1 `motorcycle` (img_010, img_026). Áp dụng tương tự cho tài xế/khách trên tuk-tuk và người đạp xe đạp/xích lô (xe đạp, xích lô không có box). |
| **R-03 Chỉ gán vật thật** | **Không gán**: tượng (img_011, img_013, img_017, img_027, ngựa trên xe img_028), ma-nơ-canh (img_033), đồ chơi/mô hình (img_038, mô tô điêu khắc img_011), người/xe trên ảnh in, biển quảng cáo, tranh tường, poster, ảnh dán kính (img_018, img_026, img_030, img_040), **phản chiếu** trên gương, kính, mặt đường ướt (img_020, img_033, img_013, img_015). |
| **R-04 Vật ngoài taxonomy** | Xe đạp, xích lô, xe đẩy, động vật, cọc giao thông: **không gán**. Người đi cùng vẫn gán `person` (R-02). |
| **R-05 Không gán xe chủ (ego)** | Phần xe gắn camera / xe người chụp đang ngồi (khung cửa, gương, nắp capo của chính mình): **không gán** (img_020). Xe khác chỉ thấy một phần vẫn gán bình thường, `truncated=yes`. |
| **R-06 Xe chở xe** | Xe chở: một box `truck` ôm toàn bộ đầu kéo + khung chở (gồm cả phần khung bị xe con che). **Mỗi xe con thật** trên sàn: một box `car` riêng, tính `occluded_level` theo khung sắt và xe bên cạnh (img_002: 1 truck + 8 car). Xe được chở **là thân vỏ trưng bày / không phải xe nguyên chiếc** (img_024): không gán, tick ghi chú ca khó. |
| **R-07 Hàng hóa trên xe** | Hàng hóa **nằm trong thùng/khung xe** (ống thép img_001, bao hàng img_012): tính vào box xe nếu không vượt ra ngoài đường viền xe. Hàng **chất cao/vượt quá khung xe** (bao tải trên nóc tuk-tuk img_035, ống dài xe điện chở img_029): **không** kéo box theo hàng, box chỉ ôm thân xe. **[Hỏi reviewer]**: an toàn giao thông có thể cần box gồm cả hàng. |
| **R-08 Xe ghép (sidecar, kéo thùng)** | Mô tô + sidecar (img_022) hoặc xe máy kéo thùng bên hông (img_025): **một** box `motorcycle` ôm cả xe và phần gắn liền. Không gán thành `tuk_tuk`. |
| **R-09 Che khuất** | Vật bị che vẫn gán nếu nhìn thấy ≥ khoảng 30% hoặc **chắc chắn nhận ra lớp**. Box theo phần nhìn thấy (R-01), có thể gồm vật che nằm giữa hai phần nhìn thấy. Ghi `occluded_level` theo bảng 2.2. Người trong xe kín (ô tô, buýt, van) nhìn qua kính: **không gán**. Người trên xe hở (tuk-tuk, thùng xe tải, xe máy): gán. |
| **R-10 Cắt mép** | Vật bị mép ảnh cắt vẫn gán nếu phần trong ảnh nhận ra được lớp, `truncated=yes`, box kéo tới đúng mép ảnh. |
| **R-11 Vật nhỏ** | Vật có chiều cao box **< 20 px**: không box riêng. Nếu nhiều vật nhỏ tụ lại thành cụm (≥ 3 vật) thì phủ một `ignore_region`. Vật nhỏ đứng lẻ: bỏ qua, không tính lỗi. |
| **R-12 Đám đông / cụm dày** | Nhóm ≥ 5 vật cùng lớp chồng lên nhau mà phần lớn sẽ có `occluded_level ≥ 2` hoặc không tách được biên → một `ignore_region` ôm cả cụm. Vật **ở hàng đầu, tách rõ, cao ≥ 20 px** nằm sát cụm vẫn box riêng và **không** bị `ignore_region` phủ lên. Ví dụ: đám đông sau rào img_019, cụm xe máy phía sau bãi img_030, dòng xe xa img_021. |
| **R-13 Ảnh mờ do chuyển động** | Vật mờ nhưng **nhận ra lớp và ước lượng được biên** ±10 px: box bình thường, tick `can_review` (img_014 xe máy mờ, img_015 xe nền). Vệt mờ không nhận ra lớp: không box; nếu là cụm thì `ignore_region`. |
| **R-14 Xe kỳ dị / diễu hành** | Xe thật chạy trên đường, có người lái, có biển số → gán theo hình dáng gần nhất (img_019 → `car`). Hình nộm/linh vật ngồi trên xe → không gán. |
| **R-15 Ảnh không có vật** | Ảnh chỉ có tượng, đồ chơi, phản chiếu (img_017, img_020, img_027, img_033, img_038) vẫn giữ trong Task và xuất COCO với 0 annotation. |
| **R-16 Một vật = một box** | Mỗi vật đúng một box, một lớp. Không box riêng bộ phận (bánh xe, đầu người). Không box trùng hai lớp cho cùng một vật. |

---

## 4. Ca khó

Phân loại: **[Quy tắc]** = mình tự tin xử lý bằng quy tắc trên. **[Hỏi reviewer]** = cần nhóm chốt ở Pha 2.

| Ảnh | Tình huống | Rule ID | Quyết định | Lý do |
|---|---|---|---|---|
| img_001 | Xe tải nhỏ Suzuki chở ống thép, bị cô gái đứng che đuôi, cắt mép phải; người ngồi phía sau | R-07, R-09, R-10 | 1 `truck` (gồm ống trong thùng), `occluded_level=1`, `truncated=yes`; mỗi người thấy rõ một `person`; poster xúc xích không gán | [Quy tắc] Ống nằm trong thùng nên tính vào xe |
| img_002 | Xe chở 8 ô tô con trên 2 tầng | R-06 | 1 `truck` + 8 `car` (mỗi xe con tính `occluded_level` riêng); người công nhân bên phải `person` | [Quy tắc] Xe con là xe thật, mô hình cần phát hiện |
| img_003 | Xe đạp, người gánh hàng, dãy xe máy dựng dày bên phải | R-02, R-04, R-12 | Xe đạp không gán; người đẩy xe đạp, người gánh `person`; cụm xe máy dựng phía xa → `ignore_region` | [Quy tắc] |
| img_004 | Hai tuk-tuk có tài xế ngồi trong | R-02, R-09 | 2 `tuk_tuk`; tài xế thấy rõ → `person` (`occluded_level` 2) | [Quy tắc] Tuk-tuk là xe hở |
| img_005 | Người lái xe máy cận cảnh, bị cắt mép; van Hiace phía sau | R-02, R-10 | Mỗi người một `person` (`truncated=yes`); xe máy thấy phần đầu → `motorcycle`; Hiace → `van`, `occluded_level=2` | [Quy tắc] |
| img_007 | Bán tải Hilux gắn thùng hộp/canopy; xe tải Isuzu cắt mép phải | R-10 | Hilux → `truck`; Isuzu → `truck`, `truncated=yes` | [Hỏi reviewer] Hilux gắn hộp kín trông giống `van` |
| img_008 | Songthaew (bán tải chở khách) phía xa; nhiều xe máy dựng | R-12 | Songthaew → `truck`; xe máy dựng tách được thì box từng chiếc, cụm sâu phía sau → `ignore_region` | [Hỏi reviewer] Songthaew chở khách, có thể là `bus` |
| img_009 | Minibus Hyundai County; hành khách nhìn qua kính | R-09 | `bus`; hành khách trong xe kín không gán | [Quy tắc] |
| img_011 | Tượng đầu quái vật, mô tô điêu khắc bằng kim loại; ô tô thật bị tượng che | R-03, R-09, R-11 | Tượng, mô tô điêu khắc không gán; ô tô thật → `car`, `occluded_level=2`; người xa < 20 px thành cụm → `ignore_region` | [Quy tắc] |
| img_012 | Bán tải chở hàng ở tiền cảnh, cắt mép đáy/phải; người chụp có thể đứng ngay sau | R-05, R-10 | Bán tải → `truck`, `truncated=yes`, tick `can_review` | [Hỏi reviewer] Có phải xe chủ (ego) không |
| img_013 | Đêm; tượng rồng vàng; phản chiếu trên đường ướt | R-03 | 2 người đi bộ → `person`; tượng rồng, phản chiếu không gán; ô tô xa ≥ 20 px → `car` | [Quy tắc] |
| img_014 | Hai người đi bộ rõ nét; xe máy và người lái mờ vì chuyển động | R-13 | 2 `person` rõ; người/xe mờ còn nhận ra lớp → box + `can_review` | [Hỏi reviewer] Mức mờ bao nhiêu thì bỏ |
| img_015 | Xe đỏ, SUV bạc cắt mép; xe nền bị nhòe | R-10, R-13 | `car` ×2 `truncated=yes`; xe nền nhận ra → `car` + `can_review` | [Quy tắc] |
| img_016 | Tuk-tuk xanh dương, xanh lá; Vespa; Hiace; bán tải Mighty-X; người áo đỏ cắt mép | R-02, R-10 | 2 `tuk_tuk`, `motorcycle` + `person` (Vespa), `van`, `truck`, `person` (`truncated=yes`) | [Quy tắc] |
| img_017 | Tượng người cưỡi ngựa đội nón giao thông | R-03, R-15 | Không gán, 0 annotation | [Quy tắc] |
| img_018 | Chân dung trên biển quảng cáo; ô tô sau hàng rào; chụp qua kính | R-03, R-09 | Chân dung không gán; mỗi xe sau rào → `car`/`truck` (bán tải), `occluded_level=1` | [Quy tắc] |
| img_019 | Xe diễu hành kỳ dị có tài xế; hình nộm chuột; đám đông sau rào | R-14, R-12 | `car` + `person` (tài xế); hình nộm không gán; đám đông → `ignore_region`; đầu người mờ tiền cảnh cắt mép → `person` + `can_review` | [Hỏi reviewer] Hình nộm có phải người mặc đồ hóa trang |
| img_020 | Gương chiếu hậu phản chiếu ô tô | R-03, R-05, R-15 | 0 annotation | [Quy tắc] |
| img_021 | Dòng xe máy rất dày | R-02, R-12 | Hàng gần (≥ 20 px, tách được) box `person` + `motorcycle`; phần xa → `ignore_region` | [Hỏi reviewer] Ranh giới chỗ dừng box từng chiếc |
| img_022 | Ảnh đen trắng, mô tô sidecar có người | R-08 | 1 `motorcycle` gồm sidecar + 1 `person` | [Quy tắc] |
| img_023 | Xích lô có người đạp; sedan; xe máy xa | R-02, R-04 | Xích lô không gán; người đạp `person`; `car`; `motorcycle` + `person` | [Quy tắc] |
| img_024 | Thân vỏ xe vàng đặt trên nóc xe đen trong bảo tàng | R-06 | Xe đen và xe trưng bày khác → `car`; thân vỏ vàng không gán | [Hỏi reviewer] Đó là xe thật hay chỉ là vỏ |
| img_025 | Xe máy kéo thùng bên hông (salaeng); taxi; đám người trên bãi biển | R-08, R-11, R-12 | `motorcycle` (gồm thùng) + `person`; taxi `car`; người ghế bãi biển dày → `ignore_region` | [Quy tắc] |
| img_026 | Hai người trên xe máy, ảnh mờ; tranh tường in tàu biển | R-02, R-03 | 2 `person` + 1 `motorcycle`; tranh tường không gán | [Quy tắc] |
| img_027 | Bia mộ bằng đá hình bán tải | R-03, R-15 | 0 annotation | [Quy tắc] |
| img_028 | Bán tải cổ thật chở tượng ngựa; SUV đỏ phía sau | R-03, R-09 | `truck` (không gồm tượng ngựa phần vượt thùng); tượng không gán; SUV → `car`, `occluded_level=2` | [Quy tắc] |
| img_029 | Xe điện chở ống dài; xe đạp | R-04, R-07 | `motorcycle` + `person`, box không kéo theo ống; xe đạp không gán, người đạp `person` | [Quy tắc] |
| img_030 | Bãi xe máy dày đặc; poster người | R-03, R-12 | Xe máy tiền cảnh tách được box riêng; cụm sau → `ignore_region`; bảo vệ → `person`; poster không gán | [Hỏi reviewer] Số xe tiền cảnh cần box |
| img_032 | Đám đông chờ xe buýt (khoảng 30 người) | R-12 | Người tách được, cao ≥ 20 px → box từng người; đoạn chồng dày → `ignore_region` | [Hỏi reviewer] Nhóm có muốn box từng người không |
| img_033 | Ma-nơ-canh, ảnh in, phản chiếu xe qua kính | R-03, R-15 | 0 annotation | [Quy tắc] |
| img_035 | Tuk-tuk chất bao tải cao gấp đôi thân xe | R-07 | `tuk_tuk` chỉ ôm thân xe, tick `can_review` | [Hỏi reviewer] Có tính hàng vào box không |
| img_036 | Xe tải nhỏ Veryca phủ bạt | — | `truck` | [Quy tắc] Cabin tách khỏi thùng |
| img_037 | Bán tải gắn canopy cao "Master 75"; xe buýt GO | — | `truck` (khung gầm bán tải); 2 `bus`; người đi bộ `person` | [Hỏi reviewer] Canopy cao dễ bị nhầm `van` |
| img_038 | Tủ kính trưng bày xe đồ chơi | R-03, R-15 | 0 annotation | [Quy tắc] |
| img_040 | Người đội mũ cận cảnh (chỉ thấy gương xe máy); taxi; tuk-tuk; ảnh dán kính | R-02, R-03, R-10 | `person` (`truncated=yes`); xe máy chỉ thấy gương → không gán; taxi `car`; `tuk_tuk`; SUV `car`; xe buýt `bus`; ảnh dán không gán | [Hỏi reviewer] Xe máy chỉ thấy gương có gán không |

---

## 5. QC và phiên bản

**Ngưỡng QC áp dụng** (giữ nguyên mục `rules` trong `taxonomy.json`):

| Đại lượng | Ngưỡng |
|---|---|
| Chiều cao box tối thiểu | 20 px (dưới mức này áp dụng R-11) |
| IoU khi ghép box | ≥ 0.5 |
| IoU đạt (box cao ≥ 50 px / < 50 px) | ≥ 0.85 / ≥ 0.7 |
| IAA | IoU trung bình ≥ 0.85, đồng thuận lớp ≥ 95% |
| Tỉ lệ ảnh lỗi để Release | ≤ 2% (lô 40 ảnh: 0 ảnh lỗi) |

**Ai quyết ca mơ hồ:**
- Trong lúc gán (Pha 3): người gán tick `can_review` hoặc ghi vấn đề cấp ảnh, **không hỏi nhau**.
- Sau khi khóa nhãn: cả nhóm họp calibration. Người được chỉ định chốt ghi vào `calibration_decisions.csv` kèm mã `R-xx`.
- Quy tắc mới làm đổi cách chọn vật/lớp/box → tăng phiên bản (v1.1), loại `semantic`, kiểm lại cả lô.

**Lịch sử thay đổi:**

| Phiên bản | Thay đổi | Lý do (ca nào) |
|---|---|---|
| v0 | Bản khởi đầu của giảng viên: 6 lớp, thuộc tính định tính | — |
| v1.0-draft (142) | Thêm lớp `bus`, `tuk_tuk`; định nghĩa lớp có ví dụ, phản ví dụ | Xe buýt img_009, 037; tuk-tuk img_004, 016, 035 |
| | Ngưỡng % cho `occluded_level`, ngưỡng 5% cho `truncated` | v0 chỉ ghi "ít/nhiều", hai người sẽ chấm khác |
| | Thêm quy tắc R-01 … R-16 (người đi xe máy, vật không thật, ego, xe chở xe, hàng hóa, vật nhỏ, đám đông, ảnh mờ) | img_002, 017, 020, 024, 027, 033, 035, 038 |
| | Liệt kê 12 ca [Hỏi reviewer] để chốt ở Pha 2 | img_007, 008, 012, 014, 019, 021, 024, 030, 032, 035, 037, 040 |
