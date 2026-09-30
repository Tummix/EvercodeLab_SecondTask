"""Разовая проверка CSV: очищенные операции и список проблем в одном XLSX."""

from datetime import date

from file_io import read_csv, write_excel
from rows import validate_rows
from settings import INPUT_PATH, OUTPUT_PATH


def main() -> None:
    headers, rows = read_csv(INPUT_PATH)
    today = date.today()
    clean_rows, error_rows, rejected_count, corrected_count = validate_rows(rows, today)
    write_excel(OUTPUT_PATH, headers, clean_rows, error_rows)

    print(f"Готово: {OUTPUT_PATH}")
    print(f"Проверено исходных строк: {len(rows)}")
    print(f"Корректных строк: {len(clean_rows)}")
    print(f"Отклонённых строк: {rejected_count}")
    print(f"Исправлено дат: {corrected_count}")
    print(f"Записей на листе ошибок: {len(error_rows)}")


if __name__ == "__main__":
    main()
