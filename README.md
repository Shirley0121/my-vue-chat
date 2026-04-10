# DeepSeek + Flask backend (пример для Vue-чата)

Это учебный пример бэкенда на **Flask**, который:
- принимает запросы от фронтенда (Vue),
- формирует `prompt` (режим “tutor” для проверки/подсказок по C-коду),
- или принимает `messages[]` (режим обычного чата),
- отправляет запрос в **DeepSeek Chat API**,
- возвращает ответ в JSON.

> Важно: **API-ключ хранится только на сервере** (в `.env`), во Vue его класть нельзя.

---

## 1) Требования

- macOS / Linux / Windows
- Python **3.10+** (желательно)
- Интернет-доступ
- API key от DeepSeek

Проверка Python:
```bash
python3 --version
````

---

## 2) Структура проекта

Пример структуры (минимум):

```
server-deepseek-example/
  app.py
  requirements.txt
  .env.example
  (создастся) .env
  (создастся) tutor_log.jsonl
```

---

## 3) Установка и запуск

### 3.1) Создать виртуальное окружение (venv)

Перейди в папку проекта:

```bash
cd "/Users/..."   # укажи путь до server-deepseek-example
```

Создай и активируй окружение:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Проверь, что используешь Python из venv:

```bash
which python
python --version
```

---

### 3.2) Установить зависимости

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Если видишь ошибку вида `ModuleNotFoundError: No module named 'requests'`, значит зависимости не поставились в текущее окружение. Сделай:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3.3) Настроить переменные окружения (.env)

Скопируй шаблон:

```bash
cp .env.example .env
```

Открой `.env` и вставь свой ключ:

```env
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
PORT=5000
REQUEST_TIMEOUT=30
LOG_PATH=tutor_log.jsonl
```

> Если у тебя API работает только с `/v1/...`, поменяй:
> `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`

---

### 3.4) Запуск сервера

```bash
python app.py
```

По умолчанию сервер поднимется на:

* `http://localhost:5000`

---

## 4) Эндпоинты API

### 4.1) Healthcheck

**GET** `/health`

Возвращает:

```json
{ "ok": true }
```

---

### 4.2) Tutor-режим (code + lang)

**POST** `/api/tutor`

Тело запроса:

```json
{
  "code": "ваш C-код",
  "lang": "ru",
  "temperature": 0.5,
  "max_tokens": 500
}
```

Ответ:

```json
{ "answer": "..." }
```

Если ошибка:

```json
{ "error": "..." }
```

---

### 4.3) Обычный чат (messages[])

**POST** `/api/chat`

Тело запроса:

```json
{
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "Привет! Объясни указатели в C." }
  ],
  "temperature": 0.7,
  "max_tokens": 600
}
```

Ответ:

```json
{ "answer": "..." }
```

---

## 5) Проверка через curl

### 5.1) Проверка, что сервер жив

```bash
curl -i http://localhost:5000/health
```

---

### 5.2) Проверка /api/tutor

```bash
curl -i -X POST http://localhost:5000/api/tutor \
  -H "Content-Type: application/json" \
  -d '{
    "lang": "ru",
    "code": "#include <stdio.h>\n\nint main() {\n  int a = 2;\n  int b = 3;\n  printf(\"%d\\n\", a + b);\n  return 0;\n}\n",
    "temperature": 0.5,
    "max_tokens": 300
  }'
```

---

### 5.3) Проверка /api/chat

```bash
curl -i -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Привет! Объясни простыми словами, что такое указатель в C."}
    ],
    "temperature": 0.7,
    "max_tokens": 300
  }'
```

---

## 6) Пример вызова из Vue (fetch)

### 6.1) Tutor режим

```js
async function tutorRequest(code, lang = "ru") {
  const r = await fetch("http://localhost:5000/api/tutor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, lang, temperature: 0.5, max_tokens: 500 }),
  });
  return await r.json();
}
```

### 6.2) Чат режим

```js
async function chatRequest(messages) {
  const r = await fetch("http://localhost:5000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, temperature: 0.7, max_tokens: 600 }),
  });
  return await r.json();
}
```

---

## 7) Логи

Сервер пишет лог в файл `tutor_log.jsonl` (по умолчанию).
Формат: одна JSON-строка на запрос (удобно для анализа).

---

## 8) Частые проблемы и решения

### 8.1) `ModuleNotFoundError: No module named 'requests'`

Зависимости не установлены в активное окружение:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 8.2) `DEEPSEEK_API_KEY is not set`

Ты не создал `.env` или не вставил ключ. Сделай:

```bash
cp .env.example .env
# открой .env и вставь ключ
```

---

### 8.3) DeepSeek API возвращает ошибку 401/403

Проверь, что ключ правильный, и что он имеет доступ к нужной модели.

---

### 8.4) DeepSeek API возвращает 404

Проверь `DEEPSEEK_BASE_URL`:

* обычно `https://api.deepseek.com`
* если нужно `/v1`, тогда `https://api.deepseek.com/v1`

---

## 9) Что можно улучшить (для следующего шага)

* Ограничить CORS только доменом фронта (не оставлять “разрешить всем”).
* Добавить rate limit (защита от спама).
* Добавить streaming (SSE), чтобы чат показывал генерацию “по токенам”.
* Добавить хранение истории диалога на сервере (если нужно).

---

Готово: теперь можно подключать Vue-чат к `/api/chat` или к `/api/tutor`.

