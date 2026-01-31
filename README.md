# Async Site Parser

Асинхронный парсер сайта одного домена, который обходит страницы сайта и извлекает контактные данные (email и телефонные номера).


---

## Возможности

- Асинхронный обход сайта (`asyncio`, `aiohttp`)
- Обход **только одного домена**
- Защита от бесконечного обхода сайта
- Вывод результата:
  - в консоль (JSON)
  - в файл `results/<domain>.json`

---

## Стек технологий

- Python 3.10+
- asyncio
- aiohttp
- BeautifulSoup4

---

## Установка

```bash
python -m venv venv
source venv/bin/activate  # Linux / MacOS
venv\\Scripts\\activate     # Windows

pip install -r requirements.txt
```

---

## Использование

Запуск из корня проекта:

```bash
python -m parser.crawler https://example.com
```

После выполнения:
- результат будет напечатан в консоль в формате JSON
- файл с результатом сохранится в директории:

```text
results/example.com.json
```

Формат результата:

```json
{
  "url": "https://example.com",
  "emails": ["info@example.com"],
  "phones": ["+79991234567"]
}
```

---

