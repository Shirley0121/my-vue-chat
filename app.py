import os
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# 读取考试配置
EXAM_TOPIC = os.getenv("EXAM_TOPIC", "编程")
EXAM_QUESTIONS = os.getenv("EXAM_QUESTIONS", "")
EXAM_SCORING = os.getenv("EXAM_SCORING", "每题25分，共100分")

# 初始化 SQLite 数据库
def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

# 启动时创建数据库表
init_db()

# 获取最近的历史消息
def get_recent_history(session_id, limit=10):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM history WHERE session_id=? ORDER BY timestamp DESC LIMIT ?",
              (session_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

# 保存消息到数据库
def save_message(session_id, role, content):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (session_id, role, content, datetime.utcnow()))
    conn.commit()
    conn.close()

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))
LOG_PATH = os.getenv("LOG_PATH", "tutor_log.jsonl")

def language_instruction(lang: str) -> str:
    lang = (lang or "ru").lower().strip()
    if lang == "zh":
        return "Answer in Simplified Chinese."
    if lang == "en":
        return "Answer in English."
    return "Answer in Russian."

def build_tutor_prompt(code: str, lang: str) -> str:
    instr = language_instruction(lang)
    return (
        "You are a programming tutor helping students learn C. "
        f"{instr}\n"
        "When given code, respond with exactly the following format:\n\n"
        "1) A brief explanation of what the code does.\n"
        "2) One or Two specific hints to help student.\n"
        "(Do NOT rewrite the code or give a full solution.)\n\n"
        "Related code:\n"
        f"```c\n{code}\n```"
    )

def deepseek_chat_completions(messages: List[Dict[str, str]],
                             temperature: float = 0.5,
                             max_tokens: int = 500) -> str:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY is not set (put it into .env)")

    url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    r = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        },
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    if r.status_code != 200:
        raise RuntimeError(f"DeepSeek API error {r.status_code}: {r.text}")

    data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected DeepSeek response: {json.dumps(data, ensure_ascii=False)}")

def append_log(entry: Dict[str, Any]) -> None:
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/api/tutor")
def api_tutor():
    body = request.get_json(silent=True) or {}
    code = (body.get("code") or "").strip()
    lang = (body.get("lang") or "ru").strip()

    if not code:
        return jsonify({"error": "code is required"}), 400

    prompt = build_tutor_prompt(code, lang)
    try:
        answer = deepseek_chat_completions(
            messages=[{"role": "user", "content": prompt}],
            temperature=float(body.get("temperature", 0.5)),
            max_tokens=int(body.get("max_tokens", 500)),
        )
        append_log({"type": "tutor", "lang": lang, "code": code, "answer": answer})
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/api/chat")
def api_chat():
    body = request.get_json(silent=True) or {}
    messages = body.get("messages")
    session_id = body.get("session_id", "default")
    mode = body.get("mode", "chat")
    print(f"🔍 DEBUG: mode = {mode}")

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "messages[] is required"}), 400

    cleaned = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = (m.get("role") or "").strip()
        content = (m.get("content") or "").strip()
        if role in ("system", "user", "assistant") and content:
            cleaned.append({"role": role, "content": content})

    if not cleaned:
        return jsonify({"error": "messages[] has no valid items"}), 400

    history = get_recent_history(session_id)

    if mode == "exam":
        if EXAM_QUESTIONS:
            # 有预设题目就用预设的
            questions_list = EXAM_QUESTIONS.split("|")
            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions_list)])
        else:
            # 没有预设题目，让 AI 自己出题
            questions_text = "Generate appropriate questions based on the topic. Make sure they are clear and suitable for the student's level."
    
        exam_prompt = f"""You are a tutor. You need to conduct an exam on the topic: {EXAM_TOPIC}.

{questions_text}

Scoring rule: {EXAM_SCORING}

You must ask **one question at a time** until all questions are answered.
After all questions are answered, output **exactly one line** in this JSON format:
{{"topic": "{EXAM_TOPIC}", "answers": ["answer1", "answer2", ...], "score": computed_score}}

Then end the conversation.
"""

        exam_system = {
            "role": "system",
            "content": exam_prompt
        }
        full_messages = [exam_system] + history + cleaned
    else:
        full_messages = history + cleaned

    try:
        answer = deepseek_chat_completions(
            messages=full_messages,
            temperature=float(body.get("temperature", 0.7)),
            max_tokens=int(body.get("max_tokens", 600)),
        )

        for msg in cleaned:
            save_message(session_id, msg["role"], msg["content"])
        save_message(session_id, "assistant", answer)

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 管理后台 ====================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def update_env_file(key, value):
    """更新 .env 文件"""
    env_path = ".env"
    lines = []
    updated = False
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"{key}={value}\n")
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    os.environ[key] = value

@app.post("/admin/login")
def admin_login():
    body = request.get_json(silent=True) or {}
    password = body.get("password")
    if password == ADMIN_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"error": "密码错误"}), 401

@app.get("/admin/config")
def admin_get_config():
    auth = request.headers.get("Authorization")
    if auth != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({
        "EXAM_TOPIC": EXAM_TOPIC,
        "EXAM_QUESTIONS": EXAM_QUESTIONS,
        "EXAM_SCORING": EXAM_SCORING
    })

@app.post("/admin/config")
def admin_save_config():
    body = request.get_json(silent=True) or {}
    password = body.get("password")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "密码错误"}), 401
    
    if "EXAM_TOPIC" in body:
        update_env_file("EXAM_TOPIC", body["EXAM_TOPIC"])
        global EXAM_TOPIC
        EXAM_TOPIC = body["EXAM_TOPIC"]
    if "EXAM_QUESTIONS" in body:
        update_env_file("EXAM_QUESTIONS", body["EXAM_QUESTIONS"])
        global EXAM_QUESTIONS
        EXAM_QUESTIONS = body["EXAM_QUESTIONS"]
    if "EXAM_SCORING" in body:
        update_env_file("EXAM_SCORING", body["EXAM_SCORING"])
        global EXAM_SCORING
        EXAM_SCORING = body["EXAM_SCORING"]
    
    return jsonify({"success": True, "message": "配置已保存，请重启后端"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)