"""Tạo dữ liệu mẫu trong sample_data/ (có cả file lỗi) để demo công cụ.

Chạy:  python make_sample_data.py
"""
import random
from pathlib import Path

import pandas as pd

random.seed(42)
OUT = Path(__file__).resolve().parent / "sample_data"

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Võ", "Đặng", "Bùi", "Đỗ"]
DEM = ["Văn", "Thị", "Minh", "Hoài", "Quốc", "Ngọc", "Thanh", "Gia"]
TEN = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Hùng", "Khoa", "Lan", "Linh",
       "Mai", "Nam", "Phát", "Quân", "Thảo", "Trang", "Tuấn", "Vy"]


def students(prefix: str, n: int) -> list[list]:
    """Trả về danh sách [mssv, họ tên, điểm]."""
    return [[f"{prefix}{i:03d}",
             f"{random.choice(HO)} {random.choice(DEM)} {random.choice(TEN)}",
             round(random.uniform(2.5, 10), 1)] for i in range(1, n + 1)]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "hoc_ky_2").mkdir(exist_ok=True)

    # 1) CSV có nhiều loại dòng lỗi: thiếu điểm, điểm là chữ, điểm > 10, trùng MSSV
    rows = students("21CT1", 12)
    rows[2][2] = ""            # thiếu điểm
    rows[4][2] = "vắng"        # không phải số
    rows[6][2] = 11.5          # ngoài khoảng 0-10
    rows[8][0] = rows[1][0]    # trùng MSSV
    pd.DataFrame(rows, columns=["MSSV", "Họ tên", "Điểm"]).to_csv(OUT / "CNTT1.csv", index=False, encoding="utf-8")

    # 2) Excel, tên cột khác kiểu, có điểm dạng "7,5" và 1 dòng thiếu họ tên
    rows = students("21CT2", 10)
    rows[1][2] = str(rows[1][2]).replace(".", ",")
    rows[5][1] = ""
    pd.DataFrame(rows, columns=["Mã SV", "Họ và tên", "Điểm TB"]).to_excel(OUT / "CNTT2.xlsx", index=False)

    # 3) CSV sạch, UTF-8 có BOM (kiểu Excel "CSV UTF-8" xuất ra)
    pd.DataFrame(students("21CT3", 15), columns=["mssv", "ho_ten", "diem"]).to_csv(
        OUT / "CNTT3.csv", index=False, encoding="utf-8-sig")

    # 4) Excel sạch nằm trong thư mục con (để thấy công cụ duyệt đệ quy)
    pd.DataFrame(students("21CT4", 8), columns=["MSSV", "Họ tên", "Điểm"]).to_excel(
        OUT / "hoc_ky_2" / "CNTT4.xlsx", index=False)

    # 5) File lỗi: thiếu cột điểm
    pd.DataFrame([r[:2] for r in students("21CT5", 5)], columns=["MSSV", "Họ tên"]).to_csv(
        OUT / "CNTT5_thieu_cot.csv", index=False, encoding="utf-8")

    # 6) File lỗi: đuôi .xlsx nhưng thực ra là file hỏng
    (OUT / "CNTT6_hong.xlsx").write_bytes(b"day khong phai la file excel that su")

    # 7) File lỗi: CSV rỗng
    (OUT / "CNTT7_rong.csv").write_bytes(b"")

    # 8) File không hỗ trợ (sẽ bị bỏ qua)
    (OUT / "ghi_chu.txt").write_text("File ghi chú, công cụ sẽ bỏ qua.\n", encoding="utf-8")

    print(f"Đã tạo dữ liệu mẫu trong {OUT}")


if __name__ == "__main__":
    main()
