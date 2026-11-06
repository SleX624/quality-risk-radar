# Правила очистки данных

## Переименование
- "trade_name": "drug_name",
- "no_ru": "registration_number",
- "dt_ru": "registration_date",
- "series": "batch_series",
- "producer": "manufacturer",
- "country": "manufacturer_country",
- "status": "quality_status",
- "type": "action_type",
- "letter_number": "letter_number",
- "letter_date": "letter_date",

## Нормализация
- Текст приводится к нижнему регистру.
- Удаляются лишние пробелы и кавычки.
- Сохраняются исходные названия и создаются поля `_clean`.

## Даты
- `letter_date` и `registration_date` преобразуются в `datetime`.
- Формат: день сначала.
- Некорректные даты помечаются как NaT.

## Ключ события
- `event_key = letter_number + letter_date + drug_name_clean + batch_series + manufacturer_clean`.
- Полные дубликаты удаляются (их нет)

## Месячная гранулярность
- `event_month = YYYY-MM` на основе `letter_date`.