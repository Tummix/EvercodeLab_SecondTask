import re
from datetime import date
from pathlib import Path


# Настройки путей
INPUT_PATH = Path(r"C:\Users\Михаил\Desktop\Evercode\task2.csv")
OUTPUT_PATH = INPUT_PATH.with_name("task2_проверенный.xlsx")

# Настройки даты
MIN_DATE = date(2024, 12, 31)
MAX_DATE = date.today()

# Настройки регулярных выражений, для проверки формата данных
ID_PATTERN = re.compile(r"TX-[0-9]{4}")
DATE_YEAR_FIRST = re.compile(r"([0-9]{4})([./-])([0-9]{1,2})\2([0-9]{1,2})")
DATE_YEAR_LAST = re.compile(r"([0-9]{1,2})([./-])([0-9]{1,2})\2([0-9]{4})")

# Ключевые слова для проверки значений в столбцах с 3, 4, 7 и 8
WORDS = {
    3: {"FNN", "ABDM", "PRT", "AM", "KLP", "CS"},
    4: {
        "Office expenses", "Team happiness", "Salary", "Taxes",
        "Marketing", "Business trips", "Overtimes", "Banking fees",
        "Recruiting", "Salary Bonuses",
    },
    7: {"EUR", "USD", "RUB"},
    8: {"EUR", "USD", "RUB"},
}
