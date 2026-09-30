from datetime import date
from decimal import Decimal, InvalidOperation

from settings import DATE_YEAR_FIRST, DATE_YEAR_LAST, ID_PATTERN, MAX_DATE, MIN_DATE, WORDS

# Удаление пробелов и замена запятой на точку, чтобы Decimal мог распознать число.
def parse_number(value):
    text = (
        value.strip()
        .replace(" ", "")
        .replace("\u00a0", "")
        .replace("\u202f", "")
        .replace(",", ".")
    )

    try:
        number = Decimal(text)
        return number if number.is_finite() else None
    except InvalidOperation:
        return None

# Распознаем дату и проверка диапазона
def parse_date(value: str, today: date) -> tuple[date | None, str | None]:
    """Возвращает календарную дату или причину отказа."""
    text = value.strip()
    match = DATE_YEAR_FIRST.fullmatch(text)
    if match:
        year, month, day = int(match[1]), int(match[3]), int(match[4])
    else:
        match = DATE_YEAR_LAST.fullmatch(text)
        if not match:
            return None, "Дата не распознана или год не из четырёх цифр"

        first, second, year = int(match[1]), int(match[3]), int(match[4])
        if first > 12 and second <= 12:
            day, month = first, second
        elif second > 12 and first <= 12:
            month, day = first, second
        elif first == second and first <= 12:
            day, month = first, second
        elif first <= 12 and second <= 12:
            return None, "Непонятно, где день, а где месяц"
        else:
            return None, "Неверные день и месяц"

    try:
        result = date(year, month, day)  # Проверка дни месяца и високосный год.
    except ValueError:
        return None, "Дата не существует"

    if not MIN_DATE <= result <= MAX_DATE:
        return None, f"Дата {result.isoformat()} вне допустимого диапазона"

    return result, None

# Приводин дату и сумму к стандартному виду
def operation_key(fields: list[str], today: date) -> tuple[str, ...]:
    values = [value.strip() for value in fields[1:9]]
    corrected_date, date_error = parse_date(fields[1], today)
    if date_error is None:
        values[0] = corrected_date.isoformat()
    amount = parse_number(fields[5])
    if amount is not None:
        values[4] = str(amount.normalize())
    return tuple(values)

#Проверка первого столбца на соответствие формату и уникальность ID
def check_id(value: str, id_counts) -> list[str]:
    """Столбец 1: формат и уникальность ID во всём CSV."""
    transaction_id = value.strip()
    problems = []
    if not ID_PATTERN.fullmatch(transaction_id):
        problems.append("Столбец 1: требуется формат TX-0001")
    if transaction_id and id_counts[transaction_id] > 1:
        problems.append("Столбец 1: дублирующееся значение")
    return problems

#Проверка второго столбца на корректность даты и диапазон
def check_date(value: str, today: date) -> tuple[date | None, str | None]:
    """Столбец 2: календарная дата и допустимый диапазон."""
    corrected, error = parse_date(value, today)
    return corrected, f"Столбец 2: {error}" if error else None

#Проверка значений в столбцах 3, 4, 7 и 8
def _check_list_value(value: str, column_number: int) -> str | None:
    if value.strip() not in WORDS[column_number]:
        return f"Столбец {column_number}: значение не из списка"
    return None

#Проверка значений в столбце 3
def check_project(value: str) -> str | None:
    return _check_list_value(value, 3)

#Проверка значений в столбце 4
def check_category(value: str) -> str | None:
    return _check_list_value(value, 4)

#Проверка значений в столбце 5
def check_description(value: str) -> str | None:
    if not value.strip():
        return "Столбец 5: пустое значение"
    return None

#Проверка значений в столбце 6
def check_amount(value: str) -> tuple[Decimal | None, str | None]:
    amount = parse_number(value)
    if amount is None or amount <= 0:
        return amount, "Столбец 6: требуется число больше 0"
    return amount, None

#Проверка значений в столбце 7
def check_currency(value: str) -> str | None:
    return _check_list_value(value, 7)

#Проверка значений в столбце 8
def check_credit_currency(value: str) -> str | None:
    return _check_list_value(value, 8)

#Проверка значений в столбце 9
def check_payment(value: str, currency: str) -> str | None: 
    currency = currency.strip()
    expected_payment = f"CARD_{currency}"
    if not currency or value.strip() != expected_payment:
        return f"Столбец 9: ожидается {expected_payment!r}"
    return None
