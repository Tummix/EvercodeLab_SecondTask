from collections import Counter
from datetime import date

from checks import (
    check_amount,
    check_category,
    check_credit_currency,
    check_currency,
    check_date,
    check_description,
    check_id,
    check_payment,
    check_project,
    operation_key,
)

# Сбор проверок и исправлений для одной строки
def validate_row(row, id_counts, operation_counts, today):
    fields = (row + [""] * 9)[:9]
    problems = []

    if len(row) != 9:
        problems.append(f"Количество столбцов: {len(row)} вместо 9")
    elif operation_counts[operation_key(row, today)] > 1:
        problems.append("Повтор операции: совпадают столбцы 2–9")

    problems.extend(check_id(fields[0], id_counts))

    corrected_date, date_error = check_date(fields[1], today)
    if date_error:
        problems.append(date_error)

    for error in (
        check_project(fields[2]),
        check_category(fields[3]),
        check_currency(fields[6]),
        check_credit_currency(fields[7]),
    ):
        if error:
            problems.append(error)

    # Сохраняем порядок причин: 3, 4, 7, 8, затем 5, 6 и 9.
    description_error = check_description(fields[4])
    if description_error:
        problems.append(description_error)

    amount, amount_error = check_amount(fields[5])
    if amount_error:
        problems.append(amount_error)

    payment_error = check_payment(fields[8], fields[6])
    if payment_error:
        problems.append(payment_error)

    return problems, corrected_date, amount

# Возврат очищенных строк, ошибок и числа исправленных дат.
def validate_rows(rows: list[tuple[int, list[str]]], today: date):
    id_counts = Counter(row[0].strip() for _, row in rows if row and row[0].strip())
    operation_counts = Counter(
        operation_key(row, today) for _, row in rows if len(row) == 9
    )

    clean_rows = []
    error_rows = []
    corrected_dates_count = 0
    rejected_rows_count = 0

    for line_number, row in rows:
        fields = (row + [""] * 9)[:9]
        extra_fields = row[9:]

        if not any(value.strip() for value in row):
            error_rows.append(fields + ["Пустая строка", line_number, ""])
            rejected_rows_count += 1
            continue

        problems, corrected_date, amount = validate_row(
            row, id_counts, operation_counts, today
        )
        date_was_corrected = (
            corrected_date is not None and fields[1] != corrected_date.isoformat()
        )

        if problems:
            rejected_rows_count += 1
            if date_was_corrected:
                problems.append(
                    f"Столбец 2: дату можно привести к {corrected_date.isoformat()}"
                )
            error_rows.append(
                fields + ["; ".join(problems), line_number, ", ".join(extra_fields)]
            )
            continue

        corrected_fields = [value.strip() for value in fields]
        corrected_fields[1] = corrected_date
        corrected_fields[5] = float(amount) 
        clean_rows.append(corrected_fields)

        if date_was_corrected:
            corrected_dates_count += 1
            error_rows.append(
                fields + [f"Столбец 2: дата исправлена на {corrected_date.isoformat()}",
                          line_number, ""]
            )

    return clean_rows, error_rows, rejected_rows_count, corrected_dates_count
