"""Công cụ gộp bảng điểm từ nhiều file CSV/Excel thành một báo cáo Excel.

Ví dụ:
    python main.py                          # chạy với thư mục sample_data/
    python main.py --input D:/diem_cac_lop  # thư mục của bạn
    python main.py --dry-run                # chạy thử, không ghi file báo cáo
"""
import argparse
import logging
import sys
from pathlib import Path

from logger_setup import setup_logging
from processor import process_folder, write_report

BASE_DIR = Path(__file__).resolve().parent
log = logging.getLogger("bangdiem")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gộp bảng điểm từ nhiều file CSV/Excel thành báo cáo tổng.")
    parser.add_argument("--input", "-i", type=Path, default=BASE_DIR / "sample_data",
                        help="thư mục chứa file điểm (mặc định: sample_data/)")
    parser.add_argument("--output", "-o", type=Path, default=BASE_DIR / "output",
                        help="thư mục lưu báo cáo (mặc định: output/)")
    parser.add_argument("--log-dir", type=Path, default=BASE_DIR / "logs",
                        help="thư mục lưu file log (mặc định: logs/)")
    parser.add_argument("--pass-score", type=float, default=5.0,
                        help="điểm tối thiểu để đạt (mặc định: 5.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="chạy thử: đọc, kiểm tra, in thống kê nhưng KHÔNG ghi file báo cáo")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # để Windows hiển thị đúng tiếng Việt
    except Exception:
        pass

    log_file = setup_logging(args.log_dir)
    log.info("Bắt đầu. input=%s | output=%s | điểm đạt=%s | dry-run=%s",
             args.input, args.output, args.pass_score, args.dry_run)

    if not 0 <= args.pass_score <= 10:
        log.error("Điểm đạt (--pass-score) phải nằm trong khoảng 0 đến 10 (nhận được: %s)", args.pass_score)
        return 1

    if not args.input.is_dir():
        log.error("Thư mục đầu vào không tồn tại: %s", args.input)
        return 1

    result = process_folder(args.input, args.pass_score)

    if result.detail.empty and result.invalid.empty and result.files.empty:
        log.error("Không tìm thấy file nào trong thư mục %s", args.input)
        return 1

    if not result.detail.empty:
        print("\n=== TỔNG HỢP THEO LỚP ===")
        print(result.summary.to_string(index=False))
        print()
    else:
        log.warning("Không có dòng dữ liệu hợp lệ nào! Vẫn xuất báo cáo để xem chi tiết lỗi. Log: %s", log_file)

    if args.dry_run:
        log.info("--dry-run: không ghi file báo cáo.")
    else:
        report = write_report(result, args.output)
        log.info("Đã xuất báo cáo: %s", report)

    ok = int(result.files["Trạng thái"].str.startswith("OK").sum())
    err = int(result.files["Trạng thái"].str.startswith("LỖI").sum())
    log.info("Xong. %d file đọc được, %d file lỗi, %d dòng bị loại. Log: %s",
             ok, err, len(result.invalid), log_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
