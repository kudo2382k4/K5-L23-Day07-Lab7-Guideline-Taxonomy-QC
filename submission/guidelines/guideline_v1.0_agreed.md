# Guideline gán nhãn dữ liệu đường phố — v1.0 (Bản thống nhất nhóm)

> **Ghi chú Pha 2:** Đây là bản đặc tả chính thức được cả nhóm thảo luận, giải quyết toàn bộ các điểm bất đồng từ các bản cá nhân Pha 1 và khóa cứng trước khi chia ảnh gán nhãn độc lập ở Pha 3. Các quy tắc trọng tâm được đánh mã **`R-01`**, **`R-02`**, **`R-03`**… để dẫn chiếu xuyên suốt trong quá trình đo IAA, họp calibration (Pha 5) và duyệt QC (Pha 6).

- **Phiên bản:** v1.0 (Agreed Specification)
- **Ngày thống nhất:** 16/11/2026
- **Trạng thái:** Đã khóa cho lượt gán độc lập Pha 3
- **Tập nhãn CVAT đồng bộ:** `cvat/labels_generated.json` (tương thích `submission/taxonomy.json` v1.0)
- **Phạm vi dữ liệu:** Toàn bộ 40 ảnh đường phố (`data/images/img_001.jpg` – `img_040.jpg`)

---

## 1. Mục tiêu và Phạm vi mô hình

### 1.1. Mục tiêu ứng dụng
Tập dữ liệu nhãn 2D bounding box này dùng để huấn luyện và kiểm thử mô hình học sâu phát hiện vật thể (**2D Object Detection**) phục vụ:
1. Hệ thống hỗ trợ lái xe an toàn nâng cao (**ADAS**) và xe tự hành cấp độ 2+/3 (nhận diện chướng ngại vật trên làn đường, tính toán khoảng cách an toàn, kích hoạt phanh khẩn cấp tự động AEB).
2. Hệ thống camera giám sát giao thông đô thị thông minh (đếm lưu lượng phương tiện, phân loại thành phần phương tiện tham gia giao thông).

### 1.2. Phân tích rủi ro an toàn
- **Bỏ sót vật thể thật (False Negative):** Nguy cơ cao nhất dẫn đến va chạm gây thương vong, đặc biệt với các đối tượng dễ tổn thương (VRU - Vulnerable Road Users) như người đi bộ, người đi xe máy hoặc xe tải lớn cản trở luồng giao thông.
- **Bắt nhầm đối tượng ảo / phi thực thể (False Positive):** Nhận nhầm tượng đài nghệ thuật, ma-nơ-canh sau kính, hình ảnh phản chiếu qua gương chiếu hậu hoặc hình in 2D trên biển pano quảng cáo thành vật cản thật sẽ kích hoạt hiện tượng phanh khẩn cấp giả (**phantom braking**), gây tai nạn dồn toa từ các xe chạy phía sau.
- **Sai lệch tọa độ ranh giới box (IoU thấp):** Gây nhiễu tín hiệu học sâu, làm giảm độ chính xác ước lượng chiều sâu 3D (3D depth estimation) và dự đoán quỹ đạo di chuyển.

---

## 2. Taxonomy: Lớp đối tượng và Thuộc tính

### 2.1. Bảng định nghĩa các lớp đối tượng (`classes`)

Nhóm đã thống nhất mở rộng từ 5 lớp nguyên thủy của v0 thành **8 lớp** chuẩn hóa để phản ánh đúng thực tế giao thông đa dạng trong 40 ảnh:

| Tên lớp (`name`) | Định nghĩa cốt lõi (1 câu) | Ví dụ thực tế trong tập 40 ảnh | Phản ví dụ / Lưu ý ranh giới |
|---|---|---|---|
| `car` | Phương tiện cơ giới 4 bánh dùng chở người cỡ nhỏ hoặc gia đình (sedan, hatchback, SUV, crossover). | Xe sedan trắng, SUV chạy trên phố (`img_040.jpg`), 8 ô tô con trên sàn xe chở xe (`img_002.jpg`). | **Không** gán xe đồ chơi trong tủ kính (`img_038.jpg`), xe hoạt hình diễu hành (`img_019.jpg`), tượng xe bán tải bằng đá (`img_027.jpg`). |
| `truck` | Phương tiện cơ giới tải trọng trung đến nặng chuyên chở hàng hóa, cabin lái tách rời thùng hàng hoặc sàn kéo. | Xe chở xe Renault (`img_002.jpg`), xe tải trong kho bốc dỡ (`img_007.jpg`), xe tải nhẹ chở hàng (`img_036.jpg`). | **Không** gán xe van thân liền khối; xe bán tải pickup nguyên bản xếp vào `truck` nếu cabin tách rời thùng sau. |
| `van` | Phương tiện cơ giới thân liền khối một khoang (monocoque), dùng chở từ 7–16 người hoặc khoang sau kín chở hàng bưu phẩm. | Xe cứu thương nhỏ, xe van chở khách cỡ nhỏ, xe chuyển phát nội đô. | Khác `truck` ở kết cấu khung vỏ liền khối; khác `bus` ở số chỗ ngồi ($< 16$ chỗ) và kích thước nhỏ hơn. |
| `bus` *(mới v1.0)* | Phương tiện giao thông công cộng chở người cỡ lớn, sức chứa từ 16 chỗ ngồi trở lên. | Xe buýt du lịch chạy sau đoàn xích lô (`img_009.jpg`), xe buýt đêm (`img_031.jpg`), xe buýt tại trạm dừng ETS (`img_032.jpg`), xe buýt hai tầng (`img_040.jpg`). | Khác `van` ở sức chứa lớn và kích thước đồ sộ. Xe buýt trường học hoặc xe khách liên tỉnh đều gán `bus`. |
| `tuk_tuk` *(mới v1.0)* | Xe cơ giới 3 bánh có cabin hoặc mái che, dùng chuyên chở hành khách hoặc hàng hóa nội đô. | 2 xe tuk-tuk xanh đậu vỉa hè (`img_004.jpg`), xe tuk-tuk hẻm Bangkok (`img_016.jpg`), xe auto rickshaw chở hàng (`img_035.jpg`). | Khác `motorcycle` ở kết cấu 3 bánh và khung cabin/mái che cố định; khác `car` ở cơ cấu lái ghi-đông và kích thước nhỏ. |
| `motorcycle` | Phương tiện cơ giới 2 bánh chạy bằng động cơ đốt trong hoặc mô tơ điện (xe máy, xe tay ga, mô tô). | Xe máy di chuyển (`img_005.jpg`, `img_026.jpg`), mô tô phân khối lớn tại lễ hội (`img_011.jpg`), xe máy chở hàng (`img_029.jpg`). | **Không** gán xe đạp sức người, xe đạp chở hàng hoặc xích lô (`img_006.jpg`, `img_023.jpg`, `img_039.jpg`). |
| `person` | Con người bằng xương bằng thịt còn sống ở mọi tư thế (đang đi bộ, đứng, ngồi, lái xe hoặc hành khách). | Người phụ nữ đứng cạnh xe bán tải (`img_001.jpg`), người đi bộ qua đường (`img_014.jpg`), người lái xe máy (`img_005.jpg`, `img_026.jpg`). | **Tuyệt đối không** gán tượng người (`img_011.jpg`, `img_017.jpg`), ma-nơ-canh (`img_033.jpg`), hình in 2D trên biển hiệu pano (`img_018.jpg`). |
| `ignore_region` | Vùng không gian dày đặc hoặc cụm vật thể quá nhỏ không gán chi tiết; lỗi bỏ sót trong vùng này không bị phạt điểm QC. | Đám đông khách ngồi ăn mờ tối phía xa (`img_001.jpg`), cụm người nhỏ ở bờ biển xa (`img_025.jpg`), cụm xe máy dồn cục mờ xa cuối hầm (`img_026.jpg`). | Không dùng `ignore_region` để che lấp các vật thể rõ ràng ở tiền cảnh và trung cảnh. |

---

### 2.2. Bảng thuộc tính định lượng (`attributes`)

Mọi bounding box thuộc các lớp vật thể (trừ `ignore_region`) đều phải có đủ 3 thuộc tính đo lường định lượng:

| Thuộc tính | Kiểu nhập | Giá trị hợp lệ | Định nghĩa ngưỡng định lượng |
|---|---|---|---|
| `occluded_level` | `select` | `0`, `1`, `2`, `3` | **Tỷ lệ diện tích vật thể bị che khuất bởi vật thể khác phía trước:**<br/>• `0`: Nhìn thấy toàn vẹn, tỷ lệ che $\le 5\%$.<br/>• `1` (Che ít): Bị che từ $> 5\%$ đến $\le 30\%$ diện tích.<br/>• `2` (Che vừa/nhiều): Bị che từ $> 30\%$ đến $\le 70\%$ diện tích nhưng còn đủ đặc trưng nhận diện.<br/>• `3` (Che rất nặng): Bị che $> 70\%$ diện tích, chỉ thấy phần nhỏ nhưng vẫn nhận dạng chắc chắn 100% nhờ ngữ cảnh. |
| `truncated` | `select` | `no`, `yes` | **Mức độ bị cắt bởi mép biên ảnh:**<br/>• `no`: Toàn bộ vật thể nằm gọn trong ảnh, cách mép ảnh $\ge 1\text{ px}$.<br/>• `yes`: Bất kỳ phần nào của vật thể chạm vào mép biên bức ảnh ($x=0, y=0, x=W, y=H$) và bị cắt mất do giới hạn góc chụp camera. |
| `can_review` | `checkbox` | `false`, `true` | • `false` (mặc định): Tự tin hoàn toàn về nhãn và tọa độ.<br/>• `true` (tick chọn): Đánh dấu ca nghi vấn biên, phân vân thuộc tính hoặc ranh giới box để đưa ra thảo luận tại buổi họp calibration Pha 5. |

---

## 3. Hệ thống Mã quy tắc chuẩn hóa (`R-xx`)

Để đảm bảo tính nhất quán tuyệt đối giữa các thành viên và phục vụ truy vết lỗi trong nhật ký QC, nhóm quy định hệ thống mã quy tắc sau:

### `R-01`: Loại trừ đối tượng phi thực thể và ảnh ảo
- **Tượng nghệ thuật / Điêu khắc / Đài tưởng niệm:** Tuyệt đối không gán nhãn cho tượng người (`img_011.jpg` Predator, `img_017.jpg` Wellington) hoặc tượng phương tiện bằng đá/kim loại tĩnh (`img_027.jpg` tượng bán tải đá nghĩa trang).
- **Ma-nơ-canh & Búp bê đồ chơi:** Tuyệt đối không gán `person` cho ma-nơ-canh trong tủ kính (`img_033.jpg`), không gán xe đồ chơi thu nhỏ (`img_038.jpg`).
- **Hình in phẳng 2D:** Không gán box cho người in trên biển pano quảng cáo (`img_018.jpg`), áp phích hay tranh vẽ tường.
- **Bóng phản chiếu qua gương:** Không gán bounding box cho bất kỳ xe cộ hay cảnh vật ảo phản chiếu bên trong mặt gương chiếu hậu (`img_020.jpg`).
- **Xử lý ảnh không có đối tượng hợp lệ:** Các ảnh `img_017.jpg`, `img_020.jpg`, `img_027.jpg`, `img_033.jpg`, `img_038.jpg` vẫn giữ nguyên trong Task CVAT và xuất COCO JSON với 0 annotation.

### `R-02`: Phân tách độc lập Cặp người đi xe máy (`motorcycle` + `person`)
- Bắt buộc tách rời thực thể:
  - **1 Box `motorcycle`:** Ôm sát toàn bộ thân xe máy từ mép ngoài của bánh trước, bánh sau, yếm xe, pô xe và tay lái (không bao gồm đầu/thân người lái).
  - **1 Box `person`:** Bao trọn vẹn người điều khiển từ đỉnh mũ bảo hiểm / đầu xuống đến bàn chân (kể cả tay đang nắm tay lái và chân đặt trên bàn đạp).
  - *Xe chở nhiều người (`img_026.jpg`):* Gán 1 box `motorcycle` + $N$ box `person` riêng biệt cho từng người trên xe.
- *Xích lô / Xe đạp (`img_006.jpg`, `img_023.jpg`, `img_034.jpg`, `img_039.jpg`):* Không gán box cho xích lô/xe đạp; **chỉ gán box `person`** cho tài xế và hành khách ngồi trên xe.

### `R-03`: Xe chuyên dụng chở ô tô (`img_002.jpg`)
- Xe tải chở hàng: Gán 1 box lớn `truck` cho xe tải kéo bao trọn đầu cabin, rơ-moóc và giàn khung chở xe.
- Các ô tô con trên sàn xe: Bắt buộc gán nhãn riêng từng chiếc ô tô con là `car` (trên `img_002.jpg` có đủ 8 xe con trên 2 tầng sàn). Đặt thuộc tính `occluded_level = 1` hoặc `2` tùy theo mức độ bị khung giàn sắt che khuất.

### `R-04`: Ôm sát phần nhìn thấy (Visible Bounding Box)
- Bbox phải là hình chữ nhật nhỏ nhất ngoại tiếp các pixel nhìn thấy được của vật thể (tight visible box).
- **Tuyệt đối không amodal prediction:** Không tự ý phóng to box ra ngoài để phỏng đoán phần cơ thể hoặc thân xe bị che khuất ngầm phía sau vật cản khác.
- Trường hợp vật bị cột điện, thân cây hoặc dây mỏng che cắt ngang làm hai phần nhìn thấy, vẫn vẽ **1 box duy nhất** bao phủ từ biên ngoài bên này đến biên ngoài bên kia của vật.

### `R-05`: Ngưỡng kích thước vật nhỏ ($< 20\text{ px}$) và Vùng bỏ qua (`ignore_region`)
- Bbox riêng lẻ phải có chiều cao $\ge 20\text{ px}$.
- Đối với các phương tiện hoặc đám đông người ở hậu cảnh xa xôi, kích thước $< 20\text{ px}$, mờ nhòe, chen chúc không thể tách rời chính xác: Khoanh một vùng bằng hình chữ nhật hoặc đa giác gán nhãn `ignore_region`. Lỗi bỏ sót trong vùng `ignore_region` không tính vào lỗi QC.

### `R-06`: Xe chủ (Ego Vehicle)
- Bộ phận của chính xe mang camera (nắp capo, cần gạt nước mưa, mép gương chiếu hậu) lọt vào góc đáy khung hình **không được gán** nhãn xe.

---

## 4. Bảng ca khó và Cơ chế giải quyết bất đồng

| Mã ảnh | Hiện tượng biên | Mã quy tắc | Quyết định thống nhất của nhóm | Cơ sở lập luận kỹ thuật |
|---|---|---|---|---|
| `img_001.jpg` | Bán tải cũ cạnh quán ăn đêm; khách ngồi mờ tối | `R-04`, `R-05` | Gán xe bán tải là `truck`; gán `person` cho người phụ nữ đứng cạnh; đám đông khách ngồi xa dùng `ignore_region`. | Bán tải có khoang chở hàng riêng; người phụ nữ tiền cảnh rất rõ; khách ngồi xa lẫn bàn ghế đèn mờ khó phân tách. |
| `img_002.jpg` | Xe tải Renault chở 8 ô tô con trên 2 tầng sàn | `R-03` | 1 box lớn `truck` cho xe tải chở hàng + 8 box `car` cho 8 ô tô con trên 2 tầng sàn. | Cần học nhận diện cả hình khối xe tải lớn lẫn từng xe ô tô con trên giàn để hệ thống ADAS không bỏ sót vật thể va chạm. |
| `img_004.jpg` | 2 xe tuk-tuk 3 bánh đỗ vỉa hè ban đêm | Taxonomy v1.0 | Gán lớp `tuk_tuk`, `occluded_level=0`, `truncated=no`. | Nhóm đã chính thức bổ sung lớp `tuk_tuk` để phân biệt rõ ràng với xe máy 2 bánh và ô tô 4 bánh. |
| `img_006.jpg` | Xích lô du lịch kẹt xe cùng xe đạp, người đi bộ | `R-02` | **Không gán** phương tiện cho xích lô và xe đạp; **chỉ gán** `person` cho người lái và hành khách. | Xích lô và xe đạp chạy bằng sức người đạp, không thuộc phương tiện cơ giới đường bộ. Người trên xe vẫn là tác nhân sống cần bảo vệ. |
| `img_009.jpg` | Xích lô chở khách, phía sau có xe buýt du lịch lớn | `R-02`, v1.0 | Gán `bus` cho xe buýt phía sau; gán `person` cho người trên xích lô. | Xe buýt chở khách trên 16 chỗ được gán lớp `bus` mới trong taxonomy v1.0. |
| `img_011.jpg` | Tượng quái vật Predator đứng cạnh hàng mô tô độ | `R-01` | Gán `motorcycle` cho các xe mô tô; **tuyệt đối không gán** tượng Predator là `person`. | Tượng trang trí cosplay/kim loại không phải người thật, gán sẽ gây báo động giả nguy hiểm. |
| `img_014.jpg` | Người đi bộ qua đường giữa làn xe máy trong mưa | `R-02`, `R-04` | Gán `person` cho người đi bộ; gán `motorcycle` và `person` cho các xe máy cự ly gần; xe quá xa vẽ `ignore_region`. | Mưa và vệt nhòe chuyển động là điều kiện tự nhiên; các đối tượng cự ly gần vẫn phải nhận diện chính xác. |
| `img_017.jpg` | Tượng đồng Duke of Wellington cưỡi ngựa ở Glasgow | `R-01` | **Không gán bất kỳ box nào** (ảnh sạch 0 annotation). | Cả tượng người và ngựa đều là tác phẩm điêu khắc nghệ thuật kim loại cố định, không phải tác nhân tham gia giao thông. |
| `img_018.jpg` | Pano lớn in hình chân dung ứng viên Lukáš Zicha | `R-01` | **Không gán** box `person`. | Hình in phẳng 2D trên biển hiệu quảng cáo, không phải người thật đứng trên vỉa hè. |
| `img_020.jpg` | Cầu vồng và các xe ô tô phản chiếu qua gương chiếu hậu | `R-01` | **Không gán** box cho các xe ảo trong gương (0 annotation). | Hình ảnh phản chiếu không nằm trên mặt đường thực tế; gán box sẽ làm sai lệch bản đồ không gian 3D. |
| `img_024.jpg` | Xe cổ AMC Pacer gắn nửa thân vỏ xe phụ trên nóc | `R-04` | Gán 1 box `car` cho xe chính, **chỉ bao thân xe chính** (hoặc bao cả khối nóc nếu dính liền? Sẽ chốt tại Pha 5 nếu có lệch). | Thân vỏ phụ trên nóc là vật trang trí tĩnh tại bảo tàng, không phải phương tiện hoạt động. |
| `img_026.jpg` | Đôi nam nữ đi chung xe máy trong hầm Thủ Thiêm | `R-02` | Gán 1 box `motorcycle` + 2 box `person` (người lái và người ngồi sau). Lưu ý ảnh kích thước $784 \times 1024$. | Chuẩn hóa quy tắc đa người trên phương tiện cơ giới. Cần cẩn thận không để box vượt biên ảnh. |
| `img_027.jpg` | Bia mộ đá hoa cương tạc hình xe bán tải pickup | `R-01` | **Không gán bất kỳ box nào** (0 annotation). | Khối đá điêu khắc trong nghĩa trang, tuyệt đối không được nhận diện nhầm là xe cộ thật. |
| `img_029.jpg` | Xe máy chở bó ống nhựa dài cồng kềnh gấp nhiều lần xe | `R-02` | Gán 1 `person`, 1 `motorcycle` ôm thân xe và hàng hóa trong bán kính hợp lý, tick `can_review`. | Giữ tỉ lệ khung hình hợp lý cho `motorcycle`, tránh làm méo mó nghiêm trọng đặc trưng lớp. |
| `img_033.jpg` | Ma-nơ-canh người trong tủ kính tiệm thời trang | `R-01` | **Không gán** box `person` (0 annotation). | Búp bê ma-nơ-canh trưng bày, không phải người thật. |
| `img_035.jpg` | Xe tuk-tuk chở hàng hóa bao tải chất cao ngất trên nóc | Taxonomy v1.0 | Gán lớp `tuk_tuk`, tick `can_review` để theo dõi ranh giới khối hàng hóa tại Pha 5. | Bổ sung lớp `tuk_tuk`. Ranh giới hàng hóa cồng kềnh sẽ được calibration chi tiết nếu hai người gán lệch IoU. |
| `img_037.jpg` | Xe bán tải GO Transit gắn nắp thùng cao kín Master 75 | Taxonomy v1.0 | Gán lớp `truck` (hoặc `van`?), tick `can_review`. | Nhóm thống nhất xếp vào `truck` do nguyên bản là xe bán tải khung gầm rời (body-on-frame) có thùng sau riêng biệt. |
| `img_038.jpg` | Tủ kính lưu niệm bày bộ sưu tập búp bê và mô hình ô tô | `R-01` | **Không gán bất kỳ box nào** (0 annotation). | Toàn bộ là mô hình đồ chơi thu nhỏ kích thước vài cm sau tủ kính trưng bày. |

---

## 5. Tiêu chuẩn QC và Lịch sử phiên bản

### 5.1. Bộ chỉ số và Ngưỡng kiểm soát chất lượng (QC Metrics)
- **Độ phủ phân công (Coverage):** Bắt buộc đạt **$100\%$** số lượt gán theo `assignment.csv` mới được phép chạy phân tích IAA.
- **Ngưỡng ghép cặp đối tượng (Object Matching):** $\text{IoU} \ge 0.50$.
- **Độ trùng khớp hình học (IoU Threshold):**
  - Đối tượng lớn (chiều cao $\ge 50\text{ px}$): $\text{IoU} \ge 0.85$.
  - Đối tượng nhỏ (chiều cao $< 50\text{ px}$): $\text{IoU} \ge 0.70$.
- **Độ đồng thuận giữa các người gán (IAA Thresholds):**
  - $\text{IoU trung bình} \ge 0.85$ (tính trên các cặp box ghép đôi thành công).
  - Tỷ lệ trùng khớp cùng lớp $\ge 95\%$.
- **Ngưỡng nghiệm thu lô (Acceptance Error Rate):**
  - Tỷ lệ ảnh có lỗi $\le 2.0\%$ (với lô 40 ảnh, chỉ cần $1/40 = 2.5\%$ ảnh có lỗi là không đạt và bắt buộc chuyển sang quy trình **Rework**).

### 5.2. Lịch sử phiên bản đặc tả

| Phiên bản | Ngày cập nhật | Tác giả | Nội dung điều chỉnh và Căn cứ thực nghiệm |
|---|---|---|---|
| `v0` | Gốc | Giảng viên | Bản khởi đầu thô sơ gồm 5 lớp (`car`, `truck`, `van`, `motorcycle`, `person`), thiếu định nghĩa định lượng, bỏ trống các trường hợp xe buýt, tuk-tuk, tượng, phản chiếu. |
| `v1.0` | 16/11/2026 | Nhóm thống nhất | - Bổ sung 2 lớp mới: `bus` và `tuk_tuk` nâng tổng số lên 8 lớp; cập nhật `submission/taxonomy.json` và sinh `cvat/labels_generated.json`.<br/>- Thiết lập hệ thống mã quy tắc chuẩn `R-01` đến `R-06`.<br/>- Định lượng hóa ngưỡng % che khuất của `occluded_level` ($5\%, 30\%, 70\%$) và `truncated`.<br/>- Thống nhất xử lý triệt để 18 ca biên trên 40 ảnh thực tế.<br/>- Khóa cứng đặc tả để toàn bộ thành viên gán mù đôi độc lập ở Pha 3. |
