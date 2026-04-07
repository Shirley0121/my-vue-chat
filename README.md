# AI 考试系统 / AI Экзаменационная система

AI 自动出题、评分。一问一答，最后输出 JSON 结果。
AI автоматически генерирует вопросы, оценивает ответы и выводит результат в формате JSON.

---

## 安装 / Установка

### 1. 启动后端 / Запуск бэкенда
cd server-deepseek
python app.py

### 2. 启动前端 / Запуск фронтенда
cd my-chat-app
npm run dev

### 3. 打开浏览器 / Откройте браузер
`http://localhost:5173`

---

## 配置新考试 / Настройка нового экзамена

修改 `server-deepseek/.env` 文件：
Измените файл `server-deepseek/.env`:

EXAM_TOPIC=Basic Math and Logic
EXAM_QUESTIONS=
EXAM_SCORING=Generate 5 math/logic questions. Ask one question at a time. Each question 20 points, total 100 points. Give full points only for correct answers.

- `EXAM_TOPIC`：考试主题 / Тема экзамена
- `EXAM_QUESTIONS`：题目，用 `|` 隔开（不写则 AI 自己出5道题）/ Вопросы через `|` (если пусто, AI сам сгенерирует 5 вопросов)
- `EXAM_SCORING`：评分规则 / Правила оценки

---

## 使用 / Как использовать

1. 打开网页 / Откройте сайт
2. AI 一问一答 / AI задаёт вопросы по одному
3. 答完后自动评分，输出 JSON / После ответов AI выводит JSON с оценкой

---

## 需要的环境 / Требования

- Python 3.10+
- Node.js 16+
- DeepSeek API key

---

## 文件说明 / Структура проекта

- `server-deepseek/app.py`：后端 / бэкенд
- `server-deepseek/.env`：配置 / настройки
- `my-chat-app/src/App.vue`：前端 / фронтенд
