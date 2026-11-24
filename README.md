# Công cụ gộp bảng điểm từ nhiều file CSV / Excel

Bài A6 – Xử lý file và tự động hóa dữ liệu (COMP1804).

Mỗi lớp thường nộp bảng điểm riêng, mỗi nơi một kiểu (CSV hoặc Excel, tên cột khác nhau, có dòng lỗi).
Công cụ này tự động duyệt thư mục, đọc hết các file, kiểm tra dữ liệu, tổng hợp theo lớp và xuất **một báo cáo Excel**
thay cho việc mở từng file rồi copy tay.

## Tính năng

- Duyệt tự động cả thư mục con, đọc file `.csv` (hỗ trợ cả dấu phân cách `,` và `;`) và `.xlsx`
- Nhận nhiều cách đặt tên cột (`MSSV` / `Mã SV`, `Họ tên` / `Họ và tên`, `Điểm` / `Điểm TB`, ...)
- Kiểm tra từng dòng: thiếu MSSV / họ tên / điểm, điểm không phải số, điểm ngoài khoảng 0–10, trùng MSSV (trong cùng file và giữa các file khác nhau)
- Chấp nhận điểm dạng `7,5` (dấu phẩy)
- File lỗi (hỏng, rỗng, thiếu cột) chỉ bị ghi log rồi bỏ qua, chương trình vẫn chạy tiếp
- Không ghi đè: file báo cáo có timestamp trong tên, nếu trùng sẽ thêm `_1`, `_2`...; file đầu vào chỉ đọc, không bị sửa
- Ghi log ra màn hình và vào `logs/run_<thời gian>.log`
- Chế độ `--dry-run`: chạy thử, không ghi file báo cáo

## Cài đặt

Cần Python 3.9 trở lên.

```bash
pip install -r requirements.txt
```

## Cách dùng

```bash
# 1. (tuỳ chọn) tạo dữ liệu mẫu có cả file lỗi trong sample_data/
python make_sample_data.py

# 2. chạy thử, chưa ghi file
python main.py --dry-run

# 3. chạy thật với dữ liệu mẫu
python main.py

# 4. chạy với thư mục điểm của bạn
python main.py --input "D:/diem_cac_lop" --output "D:/bao_cao" --pass-score 5
```

| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `--input`, `-i` | Thư mục chứa các file điểm | `sample_data/` |
| `--output`, `-o` | Thư mục lưu báo cáo | `output/` |
| `--log-dir` | Thư mục lưu log | `logs/` |
| `--pass-score` | Điểm tối thiểu để tính là đạt | `5.0` |
| `--dry-run` | Chỉ đọc, kiểm tra, in thống kê, không ghi báo cáo | tắt |

## Đầu vào

Mỗi file là bảng điểm của **một lớp**; tên lớp lấy từ tên file (`CNTT1.csv` → lớp `CNTT1`).
Dòng đầu là tiêu đề, cần có đủ 3 cột (tên cột không phân biệt hoa/thường, có dấu hay không đều được):

| Cột chuẩn | Các tên được nhận |
|---|---|
| MSSV | `MSSV`, `Mã SV`, `Mã số sinh viên`, `Student ID`, `ID` |
| Họ tên | `Họ tên`, `Họ và tên`, `Tên`, `Name`, `Full name` |
| Điểm | `Điểm`, `Điểm TB`, `Điểm tổng kết`, `Score`, `Grade` |

Muốn thêm tên cột khác thì sửa `COLUMN_ALIASES` trong `processor.py`.

## Đầu ra

File `output/bao_cao_diem_YYYYMMDD_HHMMSS.xlsx` gồm 4 sheet:

| Sheet | Nội dung |
|---|---|
| `TongHop` | Mỗi lớp: số SV, điểm TB, cao nhất, thấp nhất, số đạt / không đạt, tỉ lệ đạt; thêm dòng `TẤT CẢ` |
| `ChiTiet` | Toàn bộ sinh viên hợp lệ, kèm kết quả Đạt / Không đạt và file nguồn |
| `DongLoi` | Các dòng bị loại: file nào, dòng số mấy, lý do |
| `TrangThaiFile` | Trạng thái từng file: OK, OK (có dòng lỗi), LỖI, BỎ QUA |

## Cấu trúc project

```
gop_bang_diem/
├── main.py              # điểm vào, đọc tham số dòng lệnh
├── processor.py         # đọc, kiểm tra, tổng hợp, xuất báo cáo
├── logger_setup.py      # cấu hình log
├── make_sample_data.py  # tạo dữ liệu mẫu (có file lỗi)
├── sample_data/         # dữ liệu demo
├── output/              # báo cáo xuất ra
├── logs/                # file log mỗi lần chạy
├── requirements.txt
└── README.md
```

## Dữ liệu mẫu và kết quả mong đợi

`sample_data/` có 8 file, cố ý chứa đủ các tình huống:

| File | Tình huống | Kết quả |
|---|---|---|
| `CNTT1.csv` | 4 dòng lỗi: thiếu điểm, điểm là chữ, điểm 11.5, trùng MSSV | OK, loại 4 dòng |
| `CNTT2.xlsx` | Tên cột khác, điểm `7,5`, 1 dòng thiếu họ tên | OK, loại 1 dòng |
| `CNTT3.csv` | File sạch, UTF-8 có BOM | OK |
| `hoc_ky_2/CNTT4.xlsx` | File sạch trong thư mục con | OK |
| `CNTT5_thieu_cot.csv` | Thiếu cột điểm | LỖI, bỏ qua |
| `CNTT6_hong.xlsx` | Đuôi `.xlsx` nhưng là file hỏng | LỖI, bỏ qua |
| `CNTT7_rong.csv` | File rỗng | LỖI, bỏ qua |
| `ghi_chu.txt` | Định dạng không hỗ trợ | BỎ QUA |

## Hạn chế

- Mỗi file được coi là một lớp, chưa hỗ trợ file nhiều sheet
- Chỉ đọc `.csv` và `.xlsx` (chưa hỗ trợ `.xls` cũ)
