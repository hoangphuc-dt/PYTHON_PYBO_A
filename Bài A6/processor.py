"""Đọc, kiểm tra, tổng hợp bảng điểm từ nhiều file CSV / Excel và xuất báo cáo."""
from __future__ import annotations

import logging
import math
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

log = logging.getLogger("bangdiem")

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}

# Tên cột chuẩn -> các cách đặt tên cột mà mỗi lớp/giảng viên có thể dùng
# (đã chuẩn hóa: chữ thường, không dấu, "_" thành khoảng trắng)
COLUMN_ALIASES = {
    "mssv": {"mssv", "ma sv", "masv", "ma so sinh vien", "student id", "id"},
    "hoten": {"ho ten", "hoten", "ho va ten", "ten", "name", "full name"},
    "diem": {"diem", "diem tb", "diem tong ket", "score", "grade"},
}


@dataclass
class Result:
    detail: pd.DataFrame    # từng sinh viên hợp lệ
    summary: pd.DataFrame   # thống kê theo lớp
    invalid: pd.DataFrame   # các dòng bị loại + lý do
    files: pd.DataFrame     # trạng thái xử lý từng file


# ---------------------------------------------------------------- đọc file
def _normalize(text: str) -> str:
    """'Điểm_TB ' -> 'diem tb' để so khớp tên cột linh hoạt."""
    text = str(text).strip().lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.replace("_", " ").split())


def read_file(path: Path) -> pd.DataFrame:
    """Đọc 1 file CSV hoặc XLSX, mọi ô đọc dạng chuỗi để tự kiểm tra sau."""
    if path.suffix.lower() == ".csv":
        for encoding in ("utf-8-sig", "cp1258"):  # UTF-8 (có/không BOM) rồi tới Windows tiếng Việt
            try:
                df = pd.read_csv(path, dtype=str, encoding=encoding)
                # Nếu file CSV dùng dấu chấm phẩy ';'
                if len(df.columns) == 1 and ";" in str(df.columns[0]):
                    df = pd.read_csv(path, dtype=str, encoding=encoding, sep=";")
                return df
            except UnicodeDecodeError:
                continue
        raise ValueError("không đoán được encoding của file CSV")
    return pd.read_excel(path, dtype=str, engine="openpyxl")


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Đổi tên cột về mssv / hoten / diem. Thiếu cột nào thì báo lỗi cả file."""
    rename = {}
    for col in df.columns:
        key = _normalize(col)
        for std_name, aliases in COLUMN_ALIASES.items():
            if key in aliases and std_name not in rename.values():
                rename[col] = std_name
    df = df.rename(columns=rename)
    missing = [c for c in COLUMN_ALIASES if c not in df.columns]
    if missing:
        raise ValueError(f"thiếu cột: {', '.join(missing)} (file có cột: {list(df.columns)})")
    return df[list(COLUMN_ALIASES)]


# ---------------------------------------------------------------- kiểm tra
def _is_blank(value) -> bool:
    return value is None or pd.isna(value) or str(value).strip() == ""


def validate_rows(
    df: pd.DataFrame,
    current_file: str = "",
    seen_global: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, list[dict]]:
    """Tách dòng hợp lệ và dòng lỗi (kèm số dòng trong file + lý do)."""
    good, bad = [], []
    seen_in_file: set[str] = set()

    for idx, row in df.iterrows():
        line_no = idx + 2  # +1 vì đánh số từ 1, +1 vì dòng đầu là tiêu đề
        mssv, name, raw_score = row["mssv"], row["hoten"], row["diem"]
        reason, score = None, None

        if _is_blank(mssv):
            reason = "thiếu MSSV"
        elif _is_blank(name):
            reason = "thiếu họ tên"
        elif _is_blank(raw_score):
            reason = "thiếu điểm"
        else:
            mssv_clean = str(mssv).strip()
            try:
                score = float(str(raw_score).strip().replace(",", "."))  # chấp nhận "7,5"
            except ValueError:
                reason = f"điểm không phải số: {raw_score!r}"
            else:
                if not math.isfinite(score) or not 0 <= score <= 10:
                    reason = f"điểm ngoài khoảng 0-10: {raw_score!r}"
                elif mssv_clean in seen_in_file:
                    reason = f"trùng MSSV trong cùng file: {mssv_clean}"
                elif seen_global is not None and mssv_clean in seen_global:
                    reason = f"trùng MSSV với file {seen_global[mssv_clean]}: {mssv_clean}"

        if reason:
            bad.append({"Dòng": line_no, "MSSV": mssv, "Họ tên": name,
                        "Điểm gốc": raw_score, "Lý do": reason})
        else:
            mssv_clean = str(mssv).strip()
            seen_in_file.add(mssv_clean)
            if seen_global is not None:
                seen_global[mssv_clean] = current_file
            good.append({"MSSV": mssv_clean, "Họ tên": str(name).strip(), "Điểm": score})

    return pd.DataFrame(good, columns=["MSSV", "Họ tên", "Điểm"]), bad


# ---------------------------------------------------------------- tổng hợp
def build_summary(detail: pd.DataFrame) -> pd.DataFrame:
    columns = ["Lớp", "Số SV", "Điểm TB", "Cao nhất", "Thấp nhất", "Đạt", "Không đạt", "Tỉ lệ đạt (%)"]
    if detail.empty:
        return pd.DataFrame(columns=columns)

    def stats(group: pd.DataFrame, name: str) -> dict:
        total = len(group)
        passed = int((group["Kết quả"] == "Đạt").sum())
        return {"Lớp": name, "Số SV": total, "Điểm TB": round(group["Điểm"].mean(), 2),
                "Cao nhất": group["Điểm"].max(), "Thấp nhất": group["Điểm"].min(),
                "Đạt": passed, "Không đạt": total - passed,
                "Tỉ lệ đạt (%)": round(passed / total * 100, 1)}

    rows = [stats(group, name) for name, group in detail.groupby("Lớp")]
    rows.append(stats(detail, "TẤT CẢ"))
    return pd.DataFrame(rows, columns=columns)


def process_folder(input_dir: Path, pass_score: float = 5.0) -> Result:
    """Duyệt toàn bộ thư mục (kể cả thư mục con), xử lý từng file, không dừng khi gặp file lỗi."""
    details, invalid_rows, file_log = [], [], []
    seen_global: dict[str, str] = {}

    all_files = sorted(p for p in input_dir.rglob("*") if p.is_file() and not p.name.startswith("~$"))
    log.info("Tìm thấy %d file trong %s", len(all_files), input_dir)

    for path in all_files:
        rel = str(path.relative_to(input_dir))

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            log.info("BỎ QUA  %s (định dạng %s không hỗ trợ)", rel, path.suffix or "không có")
            file_log.append({"File": rel, "Trạng thái": "BỎ QUA", "Dòng hợp lệ": 0,
                             "Dòng lỗi": 0, "Ghi chú": "định dạng không hỗ trợ"})
            continue

        try:
            raw = read_file(path)
            df = standardize_columns(raw)
            if df.empty:
                raise ValueError("file không có dòng dữ liệu nào")
            valid, bad = validate_rows(df, current_file=rel, seen_global=seen_global)
        except Exception as exc:  # file hỏng / thiếu cột / rỗng: ghi log rồi làm tiếp file khác
            log.error("LỖI     %s -> %s: %s", rel, type(exc).__name__, exc)
            file_log.append({"File": rel, "Trạng thái": "LỖI", "Dòng hợp lệ": 0,
                             "Dòng lỗi": 0, "Ghi chú": f"{type(exc).__name__}: {exc}"})
            continue

        class_name = path.stem
        for item in bad:
            log.warning("DÒNG LỖI %s dòng %s: %s", rel, item["Dòng"], item["Lý do"])
            invalid_rows.append({"File": rel, "Lớp": class_name, **item})

        if not valid.empty:
            valid.insert(0, "Lớp", class_name)
            valid["Kết quả"] = valid["Điểm"].apply(lambda s: "Đạt" if s >= pass_score else "Không đạt")
            valid["File nguồn"] = rel
            details.append(valid)
            status = "OK" if not bad else "OK (có dòng lỗi)"
        else:
            status = "LỖI (0 dòng hợp lệ)"

        log.info("%-7s %s: %d dòng hợp lệ, %d dòng lỗi", status, rel, len(valid), len(bad))
        file_log.append({"File": rel, "Trạng thái": status,
                         "Dòng hợp lệ": len(valid), "Dòng lỗi": len(bad), "Ghi chú": ""})

    detail = (pd.concat(details, ignore_index=True) if details else
              pd.DataFrame(columns=["Lớp", "MSSV", "Họ tên", "Điểm", "Kết quả", "File nguồn"]))
    invalid = pd.DataFrame(invalid_rows, columns=["File", "Lớp", "Dòng", "MSSV", "Họ tên", "Điểm gốc", "Lý do"])
    files = pd.DataFrame(file_log, columns=["File", "Trạng thái", "Dòng hợp lệ", "Dòng lỗi", "Ghi chú"])
    return Result(detail, build_summary(detail), invalid, files)


# ---------------------------------------------------------------- xuất kết quả
def unique_path(path: Path) -> Path:
    """Nếu file đã tồn tại thì thêm _1, _2... để KHÔNG ghi đè."""
    if not path.exists():
        return path
    n = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def write_report(result: Result, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = unique_path(output_dir / f"bao_cao_diem_{datetime.now():%Y%m%d_%H%M%S}.xlsx")

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        result.summary.to_excel(writer, sheet_name="TongHop", index=False)
        result.detail.to_excel(writer, sheet_name="ChiTiet", index=False)
        result.invalid.to_excel(writer, sheet_name="DongLoi", index=False)
        result.files.to_excel(writer, sheet_name="TrangThaiFile", index=False)
        for sheet in writer.book.worksheets:  # giãn cột cho dễ đọc
            for column in sheet.columns:
                width = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
                sheet.column_dimensions[column[0].column_letter].width = min(width + 2, 60)
    return path
