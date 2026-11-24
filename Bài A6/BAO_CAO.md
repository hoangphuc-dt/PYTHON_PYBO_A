# Báo cáo ngắn – Bài A6: Xử lý file và tự động hóa dữ liệu

**Nhóm:** …  **Thành viên:** …  **Môn:** Python (COMP1804)

## 1. Bài toán

Cuối kỳ, giảng viên nhận bảng điểm từ nhiều lớp dưới dạng CSV và Excel, mỗi nơi một kiểu cột, có dòng thiếu hoặc sai.
Gộp thủ công tốn thời gian và dễ sót lỗi. Nhóm xây dựng công cụ Python tự động đọc cả thư mục, kiểm tra dữ liệu,
tổng hợp theo lớp và xuất một báo cáo Excel.

## 2. Thiết kế

- `main.py`: nhận tham số dòng lệnh (`argparse`), điều phối các bước.
- `processor.py`: duyệt thư mục (`pathlib.rglob`), đọc file (`pandas`), chuẩn hóa tên cột, kiểm tra từng dòng, thống kê theo lớp, xuất Excel.
- `logger_setup.py`: ghi log ra màn hình và file (`logging`).

Luồng xử lý: duyệt file → đọc → chuẩn hóa cột → kiểm tra dòng → gộp → thống kê → xuất báo cáo.

## 3. Đối chiếu yêu cầu đề bài

| Yêu cầu | Cách thực hiện |
|---|---|
| Làm việc với thư mục và file | `pathlib`, duyệt đệ quy thư mục con |
| Đọc ≥ 2 loại file | `.csv` và `.xlsx` |
| Tự động duyệt file | `rglob("*")`, không cần chỉ từng file |
| Kiểm tra dữ liệu | Thiếu trường, điểm không phải số, ngoài 0–10, trùng MSSV (trong file và giữa các file) |
| Xử lý / tổng hợp | `groupby` theo lớp: số SV, TB, cao nhất, thấp nhất, đạt / không đạt |
| Xuất kết quả | Excel 4 sheet |
| Ghi log | File `logs/run_*.log` mỗi lần chạy |
| Không ghi đè | Timestamp + hậu tố `_n`; file đầu vào chỉ đọc |
| Xử lý file lỗi | `try/except` từng file, ghi log rồi chạy tiếp |
| README | Có, kèm ví dụ lệnh |

## 4. Kết quả

Chạy trên 8 file mẫu: 4 file đọc được (40 sinh viên hợp lệ, 5 dòng bị loại), 3 file lỗi bị bỏ qua đúng cách, 1 file `.txt` bị bỏ qua.
Chương trình không dừng giữa chừng. (Dán thêm ảnh chụp màn hình bảng thống kê và file Excel vào đây.)

## 5. Hạn chế và hướng phát triển

- Chưa hỗ trợ file nhiều sheet và `.xls`.
- Có thể thêm biểu đồ phân bố điểm hoặc giao diện đơn giản.

## 6. Phân công

| Thành viên | Công việc |
|---|---|
| … | … |
