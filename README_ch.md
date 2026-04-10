# DeepSeek + Flask 后端示例（给 Vue 聊天项目用）

这是一个教学用的 **Flask** 后端示例，它可以：
- 接收来自前端（Vue）的请求
- 生成 `prompt`（“tutor/辅导”模式：给 C 代码解释 + 提示）
- 或接收 `messages[]`（普通聊天模式）
- 调用 **DeepSeek Chat API**
- 以 JSON 返回 AI 的回答

> 重要：**API Key 必须只放在服务器端**（`.env` 里），不要放到 Vue 前端代码中，否则会被别人从浏览器里拿走。

---

## 1) 环境要求

- macOS / Linux / Windows
- Python **3.10+**（推荐）
- 可以联网
- DeepSeek API Key

检查 Python 版本：
```bash
python3 --version
````

---

## 2) 项目目录结构

最小结构如下：

```
server-deepseek-example/
  app.py
  requirements.txt
  .env.example
  (运行后生成) .env
  (运行后生成) tutor_log.jsonl
```

---

## 3) 安装与运行

### 3.1 创建虚拟环境（venv）

先进入项目目录：

```bash
cd "/Users/..."   # 改成你自己的 server-deepseek-example 路径
```

创建并激活虚拟环境：

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

确认你正在使用 venv 的 Python：

```bash
which python
python --version
```

---

### 3.2 安装依赖

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

如果出现：
`ModuleNotFoundError: No module named 'requests'`

说明依赖没有安装到当前环境里。请确认激活 venv 后再执行：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3.3 配置环境变量（.env）

复制模板文件：

```bash
cp .env.example .env
```

打开 `.env` 并填入你的 API Key：

```env
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
PORT=8080
REQUEST_TIMEOUT=30
LOG_PATH=tutor_log.jsonl
```

> 如果你的接口必须用 `/v1/...`，请改成：
> `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`

---

### 3.4 运行服务器

```bash
python app.py
```

默认服务器地址：

* `http://localhost:8080`

---

## 4) API 接口说明

### 4.1 健康检查

**GET** `/health`

返回：

```json
{ "ok": true }
```

---

### 4.2 Tutor（辅导）模式：code + lang

**POST** `/api/tutor`

请求体示例：

```json
{
  "code": "你的 C 代码",
  "lang": "zh",
  "temperature": 0.5,
  "max_tokens": 500
}
```

返回：

```json
{ "answer": "..." }
```

如果报错：

```json
{ "error": "..." }
```

---

### 4.3 普通聊天模式：messages[]

**POST** `/api/chat`

请求体示例：

```json
{
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "你好！请解释一下 C 语言中的指针。" }
  ],
  "temperature": 0.7,
  "max_tokens": 600
}
```

返回：

```json
{ "answer": "..." }
```

---

## 5) 用 curl 测试接口

### 5.1 测试服务器是否启动成功

```bash
curl -i http://localhost:8080/health
```

---

### 5.2 测试 /api/tutor

```bash
curl -i -X POST http://localhost:8080/api/tutor \
  -H "Content-Type: application/json" \
  -d '{
    "lang": "zh",
    "code": "#include <stdio.h>\n\nint main() {\n  int a = 2;\n  int b = 3;\n  printf(\"%d\\n\", a + b);\n  return 0;\n}\n",
    "temperature": 0.5,
    "max_tokens": 300
  }'
```

---

### 5.3 测试 /api/chat

```bash
curl -i -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "你好！请用简单的方式解释 C 语言中的指针是什么？"}
    ],
    "temperature": 0.7,
    "max_tokens": 300
  }'
```

---

## 6) Vue 前端调用示例（fetch）

### 6.1 Tutor 模式

```js
async function tutorRequest(code, lang = "zh") {
  const r = await fetch("http://localhost:8080/api/tutor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, lang, temperature: 0.5, max_tokens: 500 }),
  });
  return await r.json();
}
```

### 6.2 聊天模式

```js
async function chatRequest(messages) {
  const r = await fetch("http://localhost:8080/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, temperature: 0.7, max_tokens: 600 }),
  });
  return await r.json();
}
```

---

## 7) 日志（log）

服务器会把请求和回答写到 `tutor_log.jsonl`（默认）。
每一行都是一条 JSON，方便后续查看和分析。

---

## 8) 常见问题（FAQ）

### 8.1 `ModuleNotFoundError: No module named 'requests'`

依赖没有装到当前环境里：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 8.2 `DEEPSEEK_API_KEY is not set`

你没有创建 `.env` 或没有填 API Key：

```bash
cp .env.example .env
# 打开 .env，填入你的 key
```

---

### 8.3 DeepSeek API 返回 401/403

Key 不正确，或者 Key 没有权限访问该模型。请检查 Key。

---

### 8.4 DeepSeek API 返回 404

检查 `DEEPSEEK_BASE_URL`：

* 通常是 `https://api.deepseek.com`
* 如果需要 `/v1`：`https://api.deepseek.com/v1`

---

## 9) 下一步可改进（进阶）

* 把 CORS 限制到你的前端域名（不要默认允许所有）
* 加 rate limit（防刷接口）
* 做 streaming（SSE），实现“逐字输出”效果
* 如果需要：把聊天历史存到服务器端

---

完成！现在 Vue 前端可以连接：

* `/api/chat`（普通聊天）
* `/api/tutor`（C 语言辅导模式）
