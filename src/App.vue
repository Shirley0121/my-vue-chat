<template>
  <article id="contact" class="panel">
    <h2>Type your question here</h2>
<div class="page-title">🚀 Vue 聊天应用 v1.0</div>
    <main>
      <!-- List of messages -->
      <div class="chat-container">
        <div
          v-for="(user_message, index) in user_messages"
          :key="index"
          class="d-flex chat-message mb-3"
          :class="user_message.from === 11 ? 'outcoming' : 'incoming'"
        >
          <div v-if="user_message.from !== 11">
            <i class="fas fa-robot" style="margin-right: .5rem;"></i>
          </div>

          <div
            class="bubble markdown-body text-break"
            v-html="renderMd(user_message.message)"
          ></div>

          <div v-if="user_message.from === 11">
            <i class="fas fa-user" style="margin-left: .5rem;"></i>
          </div>
        </div>

        <div v-if="is_sending" class="typing-dots text-secondary my-3">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- Input form -->
      <form class="flex-form" @submit.prevent="sendMessage">
        <input
          type="text"
          v-model="message"
          class="form-control send-pole"
          placeholder="Write message..."
          style="max-width: 800px; height: 50px;"
        />

        <button
          type="submit"
          @click="sendMessage"
          class="send-button"
          :disabled="!message || is_sending"
          style="max-width: 100px; height: 50px;"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="currentColor"
            class="bi bi-arrow-up-circle-fill"
            viewBox="0 0 16 16"
          >
            <path
              fill-rule="evenodd"
              d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8m15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707z"
            />
          </svg>
        </button>
      </form>
      <button @click="clearChat" class="clear-btn" style="margin-top: 1rem; padding: 0.5rem 1rem; background-color: #ff6b6b; color: white; border: none; border-radius: 6px; cursor: pointer;">
  clearChat
</button>
    </main>
  </article>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

// 1. Настраиваем Markdown
const md = new MarkdownIt({
  html: false,    // запрещаем сырой HTML
  linkify: true,  // превращаем ссылки в <a>
  breaks: true,   // переносы строк = <br>
})

// Все ссылки открываем в новой вкладке
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const i = tokens[idx].attrIndex('target')
  if (i < 0) tokens[idx].attrPush(['target', '_blank'])
  else tokens[idx].attrs[i][1] = '_blank'
  return self.renderToken(tokens, idx, options)
}

// функция рендера Markdown с очисткой
const renderMd = (text) => {
  const s = String(text ?? '')
  const hasParagraphs = /\n\s*\n/.test(s)
  const html = hasParagraphs ? md.render(s) : md.renderInline(s)
  return DOMPurify.sanitize(html)
}

// 2. РЕАКТИВНЫЕ ПЕРЕМЕННЫЕ (состояние)
const message = ref('')          // строка ввода
const user_messages = ref([])    // массив сообщений
const is_sending = ref(false)    // флаг "бот печатает"
const error_messages = ref('')   // можно использовать для отображения ошибок

// 3. При загрузке – подтягиваем историю из sessionStorage
onMounted(() => {
  const raw = sessionStorage.getItem('user_messages')
  if (raw) {
    try {
      user_messages.value = JSON.parse(raw)
    } catch {
      user_messages.value = []
      sessionStorage.removeItem('user_messages')
    }
  }
})
// 4. Отправка сообщения
async function sendMessage() {
  // защита от пустых строк и двойных кликов
  if (message.value === '' || is_sending.value) {
    return
  }

  // добавляем сообщение пользователя в чат
  user_messages.value.push({ from: 11, to: 1, message: message.value })
  saveToSession()

  const message_priv = message.value
  message.value = ''            // очищаем поле ввода
  is_sending.value = true       // показываем "печатает..."

  const response_message = await getServerResponse(message_priv)

  is_sending.value = false

  // добавляем ответ бота
  user_messages.value.push({ from: 1, to: 11, message: response_message })
  saveToSession()
}

// 5. ВРЕМЕННАЯ ЗАГЛУШКА "СЕРВЕРА" В БРАУЗЕРЕ
// На этом этапе можно тестировать весь чат без реального backend
async function getServerResponse(message_priv) {
  // Имитируем задержку сети (~0.5 сек)
  await new Promise(resolve => setTimeout(resolve, 500))

  // Возвращаем тестовый ответ
  return 'Тестовый ответ сервера на: **' + message_priv + '**'
}

// 6. Сохранение истории чата
function saveToSession() {
  sessionStorage.setItem('user_messages', JSON.stringify(user_messages.value))
}
// 7.清空聊天记录
function clearChat() {
  user_messages.value = []
  sessionStorage.removeItem('user_messages')
}
</script>


.panel {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #ddd;
}

.chat-container {
  max-height: 60vh;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.chat-message {
  display: flex;
  align-items: flex-start;
}

.chat-message.incoming {
  justify-content: flex-start;
}

.chat-message.outcoming {
  justify-content: flex-end;
}

.bubble {
  padding: 0.6rem 0.9rem;
  border-radius: 12px;
  border: 1px solid #ddd;
  max-width: 70%;
}

.incoming .bubble {
  background: #f5f5f5;
}

.outcoming .bubble {
  background: #d1f0ff;
}

/* анимация "печатает..." */
.typing-dots span {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin: 0 2px;
  border-radius: 50%;
  background: #999;
  animation: blink 1s infinite alternate;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  from {
    opacity: 0.2;
  }
  to {
    opacity: 1;
  }
}

.flex-form {
  display: flex;
  gap: 0.5rem;
}
.clear-btn {
  padding: 0.5rem 1rem;
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.clear-btn:hover {
  background-color: #ff5252;
}
.page-title {
  text-align: center;
  color: #4a6fa5;
  font-weight: bold;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: #f0f8ff;
  border-radius: 8px;
}