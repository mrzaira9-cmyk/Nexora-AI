import os
import json
import html
import gradio as gr
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY Render Environment Variables में सेट नहीं है।")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"
MAX_HISTORY = 8


def needs_web_search(text):
    words = [
        "latest", "today", "current", "news", "now", "recent",
        "आज", "अभी", "वर्तमान", "ताज़ा", "न्यूज़", "समाचार",
        "कौन है", "कितना है", "कीमत", "price", "weather",
        "मौसम", "2026", "2025"
    ]
    t = text.lower()
    return any(word.lower() in t for word in words)


def make_history_text(history):
    if not history:
        return "कोई पिछली बातचीत नहीं है।"

    parts = []
    for user_text, ai_text in history[-MAX_HISTORY:]:
        parts.append("User: " + user_text)
        parts.append("Nexora AI: " + ai_text)

    return "\n".join(parts)


def get_sources(response):
    links = []

    try:
        candidates = getattr(response, "candidates", None)

        if candidates:
            metadata = getattr(candidates[0], "grounding_metadata", None)

            if metadata:
                chunks = getattr(metadata, "grounding_chunks", None)

                if chunks:
                    for chunk in chunks:
                        web_data = getattr(chunk, "web", None)

                        if web_data:
                            uri = getattr(web_data, "uri", None)
                            title = getattr(web_data, "title", None)

                            if uri and uri not in [x[0] for x in links]:
                                links.append(
                                    (
                                        uri,
                                        title or "वेब स्रोत"
                                    )
                                )
    except Exception:
        pass

    return links[:5]


def build_chat_html(history):
    if not history:
        return (
            '<div id="welcome">'
            '<div class="welcome-icon">🤖</div>'
            '<h1>Nexora AI</h1>'
            '<p>आपका स्मार्ट AI सहायक</p>'
            '<div class="suggestions">'
            '<button class="suggestion">भारत की राजधानी क्या है?</button>'
            '<button class="suggestion">आज की ताज़ा खबरें बताओ</button>'
            '<button class="suggestion">मुझे कुछ नया सिखाओ</button>'
            '</div>'
            '</div>'
        )

    output = []

    for user_text, ai_text in history:
        u = html.escape(user_text)
        a = html.escape(ai_text)

        output.append(
            '<div class="message user-message">'
            '<div class="avatar">👤</div>'
            '<div class="bubble">' + u + '</div>'
            '</div>'
        )

        output.append(
            '<div class="message ai-message">'
            '<div class="avatar">🤖</div>'
            '<div class="answer-wrap">'
            '<div class="bubble">' + a.replace("\n", "<br>") + '</div>'
            '<div class="answer-actions">'
            '<button class="answer-btn" data-action="like">👍</button>'
            '<button class="answer-btn" data-action="dislike">👎</button>'
            '<button class="answer-btn" data-action="speak">🔊</button>'
            '<button class="answer-btn" data-action="copy">📋</button>'
            '<button class="answer-btn" data-action="share">↗️</button>'
            '<button class="answer-btn" data-action="more">⋯</button>'
            '</div>'
            '</div>'
            '</div>'
        )

    return "".join(output)


def nexora_ai(message, history=None):
    history = history or []

    if not message or not message.strip():
        return "", history, build_chat_html(history), "", ""

    message = message.strip()

    try:
        old_chat = make_history_text(history)

        system_text = "\n".join([
            "You are Nexora AI, a helpful multilingual AI assistant.",
            "Understand the user's language automatically.",
            "Reply in the same language as the user.",
            "Give clear, useful and accurate answers.",
            "Remember relevant previous conversation.",
            "Do not invent facts.",
            "If information may have changed recently, use web search when available.",
            "Current date: 2026-09-14.",
            "",
            "Previous conversation:",
            old_chat,
            "",
            "User question:",
            message
        ])

        use_search = needs_web_search(message)

        config_args = {
            "max_output_tokens": 1200
        }

        if use_search:
            config_args["tools"] = [
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]

        config = types.GenerateContentConfig(**config_args)

        response = client.models.generate_content(
            model=MODEL,
            contents=system_text,
            config=config
        )

        answer = response.text or "मुझे अभी उत्तर नहीं मिला।"

        history = history[-(MAX_HISTORY - 1):]
        history.append((message, answer))

        chat_html = build_chat_html(history)

        source_html = ""

        sources = get_sources(response)

        if sources:
            source_items = []

            for uri, title in sources:
                safe_title = html.escape(title)
                safe_uri = html.escape(uri, quote=True)

                source_items.append(
                    '<a class="source-link" href="'
                    + safe_uri
                    + '" target="_blank">'
                    + safe_title
                    + '</a>'
                )

            source_html = (
                '<div class="sources">'
                '<b>🌐 स्रोत</b>'
                + "".join(source_items)
                + '</div>'
            )

        speaker_text = json.dumps(
            answer,
            ensure_ascii=False
        )

        speaker_html = (
            '<div id="speaker-bar" data-text='
            + html.escape(speaker_text, quote=True)
            + '>'
            '🔊 उत्तर सुनने के लिए नीचे 🔊 दबाएँ'
            '<button onclick="speakCurrent()">🔊</button>'
            '<button onclick="stopSpeaking()">⏹️</button>'
            '<button onclick="openVoices()">⚙️</button>'
            '<button onclick="closeSpeaker()">✕</button>'
            '</div>'
        )

        return (
            "",
            history,
            chat_html,
            source_html,
            speaker_html
        )

    except Exception as e:
        error = "❌ समस्या आ गई: " + str(e)

        return (
            "",
            history,
            build_chat_html(history),
            "",
            '<div id="speaker-bar">' + html.escape(error) + '</div>'
        )


def new_chat():
    return [], build_chat_html([]), "", ""


css = "\n".join([
    "html, body { margin:0; padding:0; }",

    "body {",
    "  background:#ffffff;",
    "  font-family:Arial, sans-serif;",
    "}",

    "#app-container {",
    "  max-width:900px;",
    "  margin:auto;",
    "}",

    ".header {",
    "  position:sticky;",
    "  top:0;",
    "  z-index:20;",
    "  background:white;",
    "  border-bottom:1px solid #eee;",
    "  padding:12px 16px;",
    "  display:flex;",
    "  justify-content:space-between;",
    "  align-items:center;",
    "}",

    ".brand {",
    "  font-size:22px;",
    "  font-weight:bold;",
    "}",

    ".new-chat {",
    "  border-radius:20px !important;",
    "}",

    "#chat-area {",
    "  min-height:65vh;",
    "  max-height:calc(100vh - 250px);",
    "  overflow-y:auto;",
    "  padding:20px 12px 130px;",
    "}",

    "#welcome {",
    "  text-align:center;",
    "  padding-top:70px;",
    "}",

    ".welcome-icon {",
    "  font-size:60px;",
    "}",

    "#welcome h1 {",
    "  font-size:34px;",
    "  margin:10px 0;",
    "}",

    "#welcome p {",
    "  color:#777;",
    "}",

    ".suggestions {",
    "  display:flex;",
    "  flex-wrap:wrap;",
    "  justify-content:center;",
    "  gap:10px;",
    "  margin-top:25px;",
    "}",

    ".suggestion {",
    "  padding:12px 16px;",
    "  border:1px solid #ddd;",
    "  border-radius:18px;",
    "  background:white;",
    "  cursor:pointer;",
    "}",

    ".message {",
    "  display:flex;",
    "  gap:10px;",
    "  margin:18px 0;",
    "}",

    ".user-message {",
    "  justify-content:flex-end;",
    "}",

    ".ai-message {",
    "  justify-content:flex-start;",
    "}",

    ".avatar {",
    "  width:34px;",
    "  height:34px;",
    "  border-radius:50%;",
    "  display:flex;",
    "  justify-content:center;",
    "  align-items:center;",
    "  background:#f0f0f0;",
    "  flex-shrink:0;",
    "}",

    ".bubble {",
    "  max-width:75%;",
    "  padding:12px 15px;",
    "  border-radius:18px;",
    "  line-height:1.55;",
    "  white-space:normal;",
    "  word-wrap:break-word;",
    "}",

    ".user-message .bubble {",
    "  background:#e9f3ff;",
    "}",

    ".ai-message .bubble {",
    "  background:#f5f5f5;",
    "}",

    ".answer-wrap {",
    "  max-width:80%;",
    "}",

    ".answer-wrap .bubble {",
    "  max-width:100%;",
    "}",

    ".answer-actions {",
    "  display:flex;",
    "  gap:5px;",
    "  margin-top:6px;",
    "}",

    ".answer-btn {",
    "  border:0;",
    "  background:transparent;",
    "  padding:6px;",
    "  border-radius:8px;",
    "  cursor:pointer;",
    "}",

    ".answer-btn:hover {",
    "  background:#eee;",
    "}",

    "#speaker-bar {",
    "  position:fixed;",
    "  bottom:88px;",
    "  left:50%;",
    "  transform:translateX(-50%);",
    "  z-index:50;",
    "  background:white;",
    "  border:1px solid #ddd;",
    "  border-radius:18px;",
    "  padding:8px 12px;",
    "  box-shadow:0 3px 15px rgba(0,0,0,.12);",
    "}",

    "#speaker-bar button {",
    "  border:0;",
    "  background:transparent;",
    "  cursor:pointer;",
    "  font-size:17px;",
    "}",

    "#source-area {",
    "  padding:0 15px 10px;",
    "}",

    ".sources {",
    "  font-size:13px;",
    "  border-top:1px solid #eee;",
    "  padding-top:8px;",
    "}",

    ".source-link {",
    "  display:block;",
    "  padding:4px 0;",
    "  text-decoration:none;",
    "}",

    "#input-row {",
    "  position:fixed;",
    "  bottom:0;",
    "  left:50%;",
    "  transform:translateX(-50%);",
    "  width:min(900px,100%);",
    "  z-index:40;",
    "  background:white;",
    "  padding:10px;",
    "  border-top:1px solid #ddd;",
    "  box-sizing:border-box;",
    "}",

    "#question textarea {",
    "  border-radius:22px !important;",
    "  padding:13px 16px !important;",
    "}",

    "#send-btn button, #mic-btn button {",
    "  min-width:50px !important;",
    "  min-height:50px !important;",
    "  border-radius:50% !important;",
    "}",

    "#voice-panel {",
    "  display:none;",
    "  position:fixed;",
    "  z-index:100;",
    "  left:50%;",
    "  top:50%;",
    "  transform:translate(-50%,-50%);",
    "  width:min(420px,90%);",
    "  max-height:70vh;",
    "  overflow:auto;",
    "  background:white;",
    "  border:1px solid #ddd;",
    "  border-radius:20px;",
    "  padding:20px;",
    "  box-shadow:0 5px 30px rgba(0,0,0,.25);",
    "}",

    "#voice-panel select {",
    "  width:100%;",
    "  padding:10px;",
    "  margin-top:10px;",
    "}",

    "#voice-panel button {",
    "  margin-top:12px;",
    "  padding:9px 14px;",
    "  border-radius:12px;",
    "  border:1px solid #ddd;",
    "  background:white;",
    "}",

    "@media(max-width:600px) {",
    "  #welcome { padding-top:40px; }",
    "  #welcome h1 { font-size:28px; }",
    "  .bubble { max-width:85%; }",
    "  .answer-wrap { max-width:88%; }",
    "  #chat-area { max-height:calc(100vh - 220px); }",
    "}"
])


js_lines = [
    "let selectedVoice = null;",
    "let speaking = false;",

    "function getQuestionBox() {",
    "  return document.querySelector('#question textarea');",
    "}",

    "function putQuestion(text) {",
    "  const box = getQuestionBox();",
    "  if (!box) return;",
    "  box.value = text;",
    "  box.dispatchEvent(new Event('input', {bubbles:true}));",
    "  box.focus();",
    "}",

    "function stopSpeaking() {",
    "  if ('speechSynthesis' in window) speechSynthesis.cancel();",
    "  speaking = false;",
    "}",

    "function speakText(text) {",
    "  if (!('speechSynthesis' in window)) return;",
    "  stopSpeaking();",
    "  const u = new SpeechSynthesisUtterance(text);",
    "  if (selectedVoice) u.voice = selectedVoice;",
    "  u.rate = 0.9;",
    "  u.onend = function(){ speaking=false; };",
    "  speaking = true;",
    "  speechSynthesis.speak(u);",
    "}",

    "function speakCurrent() {",
    "  const bar = document.querySelector('#speaker-bar');",
    "  if (!bar) return;",
    "  let text = bar.getAttribute('data-text');",
    "  if (!text) return;",
    "  try { text = JSON.parse(text); } catch(e) {}",
    "  speakText(text);",
    "}",

    "function closeSpeaker() {",
    "  const bar = document.querySelector('#speaker-bar');",
    "  if (bar) bar.remove();",
    "  stopSpeaking();",
    "}",

    "function loadVoices() {",
    "  const select = document.querySelector('#voice-select');",
    "  if (!select || !('speechSynthesis' in window)) return;",
    "  const voices = speechSynthesis.getVoices();",
    "  select.innerHTML = '';",
    "  voices.slice(0,25).forEach(function(v){",
    "    const option = document.createElement('option');",
    "    option.value = v.name;",
    "    option.textContent = v.name + ' — ' + v.lang;",
    "    select.appendChild(option);",
    "  });",
    "}",

    "function openVoices() {",
    "  const panel = document.querySelector('#voice-panel');",
    "  if (!panel) return;",
    "  panel.style.display = 'block';",
    "  loadVoices();",
    "}",

    "function closeVoices() {",
    "  const panel = document.querySelector('#voice-panel');",
    "  if (panel) panel.style.display = 'none';",
    "}",

    "function startMic() {",
    "  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;",
    "  if (!Recognition) {",
    "    alert('इस ब्राउज़र में Voice Input उपलब्ध नहीं है।');",
    "    return;",
    "  }",
    "  const recognition = new Recognition();",
    "  recognition.lang = 'hi-IN';",
    "  recognition.interimResults = false;",
    "  recognition.maxAlternatives = 1;",
    "  recognition.start();",
    "  recognition.onresult = function(event) {",
    "    const text = event.results[0][0].transcript;",
    "    putQuestion(text);",
    "  };",
    "}",

    "function scrollChat() {",
    "  const area = document.querySelector('#chat-area');",
    "  if (area) area.scrollTop = area.scrollHeight;",
    "}",

    "document.addEventListener('click', function(e) {",
    "  const suggestion = e.target.closest('.suggestion');",
    "  if (suggestion) putQuestion(suggestion.textContent);",

    "  const action = e.target.closest('.answer-btn');",
    "  if (action) {",
    "    const wrap = action.closest('.answer-wrap');",
    "    const bubble = wrap ? wrap.querySelector('.bubble') : null;",
    "    const text = bubble ? bubble.innerText : '';",
    "    const type = action.getAttribute('data-action');",

    "    if (type === 'speak') speakText(text);",

    "    if (type === 'copy') {",
    "      navigator.clipboard.writeText(text);",
    "      action.textContent = '✅';",
    "      setTimeout(function(){ action.textContent='📋'; },1000);",
    "    }",

    "    if (type === 'share') {",
    "      if (navigator.share) {",
    "        navigator.share({text:text}).catch(function(){});",
    "      } else {",
    "        navigator.clipboard.writeText(text);",
    "        alert('उत्तर कॉपी हो गया।');",
    "      }",
    "    }",

    "    if (type === 'like') action.textContent = '✅';",
    "    if (type === 'dislike') action.textContent = '❌';",
    "    if (type === 'more') alert('Nexora AI विकल्प');",
    "  }",
    "});",

    "document.addEventListener('change', function(e){",
    "  if (e.target.id === 'voice-select') {",
    "    const name = e.target.value;",
    "    const voices = speechSynthesis.getVoices();",
    "    selectedVoice = voices.find(function(v){ return v.name === name; }) || null;",
    "  }",
    "});",

    "if ('speechSynthesis' in window) {",
    "  speechSynthesis.onvoiceschanged = loadVoices;",
    "}",

    "setInterval(scrollChat, 500);",

    "setTimeout(function(){ scrollChat(); }, 800);"
]

js = "\n".join(js_lines)


with gr.Blocks(title="Nexora AI") as app:

    gr.HTML(
        '<div class="header">'
        '<div class="brand">🤖 Nexora AI</div>'
        '</div>'
    )

    history_state = gr.State([])

    chat_area = gr.HTML(
        build_chat_html([]),
        elem_id="chat-area"
    )

    source_area = gr.HTML(
        "",
        elem_id="source-area"
    )

    speaker_area = gr.HTML(
        "",
        elem_id="speaker-area"
    )

    gr.HTML(
        '<div id="voice-panel">'
        '<h3>🎙️ Voice Settings</h3>'
        '<p>अपने डिवाइस की उपलब्ध आवाज़ चुनें:</p>'
        '<select id="voice-select"></select>'
        '<br>'
        '<button onclick="closeVoices()">बंद करें</button>'
        '</div>'
    )

    with gr.Row(elem_id="input-row"):

        question = gr.Textbox(
            placeholder="यहाँ अपना सवाल लिखें...",
            show_label=False,
            lines=1,
            elem_id="question",
            scale=8
        )

        mic = gr.Button(
            "🎤",
            elem_id="mic-btn",
            scale=1
        )

        send = gr.Button(
            "➤",
            elem_id="send-btn",
            scale=1
        )

    new_chat_btn = gr.Button(
        "＋ नया चैट",
        elem_id="new-chat-btn"
    )

    send.click(
        nexora_ai,
        inputs=[question, history_state],
        outputs=[
            question,
            history_state,
            chat_area,
            source_area,
            speaker_area
        ]
    )

    question.submit(
        nexora_ai,
        inputs=[question, history_state],
        outputs=[
            question,
            history_state,
            chat_area,
            source_area,
            speaker_area
        ]
    )

    new_chat_btn.click(
        new_chat,
        inputs=[],
        outputs=[
            history_state,
            chat_area,
            source_area,
            speaker_area
        ]
    )

    mic.click(
        None,
        inputs=[],
        outputs=[],
        js="startMic"
    )


app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "7860")),
    css=css,
    js=js
)            
