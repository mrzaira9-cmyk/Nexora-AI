import os
import html
import json
import base64

import gradio as gr
from google import genai
from google.genai import types


# =========================================================
# SETTINGS
# =========================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY Render Environment Variables में सेट नहीं है।")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"
MAX_HISTORY = 10


# =========================================================
# WEB SEARCH DETECTION
# =========================================================

def needs_web_search(text):
    keywords = [
        "latest",
        "today",
        "current",
        "news",
        "recent",
        "now",
        "live",
        "price",
        "weather",
        "मौसम",
        "आज",
        "अभी",
        "वर्तमान",
        "ताज़ा",
        "समाचार",
        "न्यूज़",
        "कीमत",
        "लेटेस्ट",
        "2026",
        "2025"
    ]

    text = text.lower()

    for word in keywords:
        if word.lower() in text:
            return True

    return False


# =========================================================
# HISTORY TEXT
# =========================================================

def make_history(history):
    if not history:
        return "कोई पिछली बातचीत नहीं।"

    result = []

    for user_text, ai_text in history[-MAX_HISTORY:]:
        result.append("User: " + user_text)
        result.append("Nexora AI: " + ai_text)

    return "\n".join(result)


# =========================================================
# SOURCE EXTRACTION
# =========================================================

def get_sources(response):
    sources = []

    try:
        candidates = getattr(response, "candidates", None)

        if not candidates:
            return []

        metadata = getattr(
            candidates[0],
            "grounding_metadata",
            None
        )

        if not metadata:
            return []

        chunks = getattr(
            metadata,
            "grounding_chunks",
            None
        )

        if not chunks:
            return []

        for chunk in chunks:
            web_data = getattr(chunk, "web", None)

            if web_data:
                uri = getattr(web_data, "uri", None)
                title = getattr(web_data, "title", None)

                if uri:
                    found = False

                    for old_uri, old_title in sources:
                        if old_uri == uri:
                            found = True
                            break

                    if not found:
                        sources.append(
                            (
                                uri,
                                title or "वेब स्रोत"
                            )
                        )

    except Exception:
        return []

    return sources[:6]


# =========================================================
# SOURCE HTML
# =========================================================

def sources_html(response):
    sources = get_sources(response)

    if not sources:
        return ""

    result = [
        '<div class="sources">',
        '<div class="sources-title">🌐 वेब स्रोत</div>'
    ]

    for uri, title in sources:
        safe_uri = html.escape(uri, quote=True)
        safe_title = html.escape(title)

        result.append(
            '<a class="source-link" href="'
            + safe_uri
            + '" target="_blank" rel="noopener">'
            + safe_title
            + "</a>"
        )

    result.append("</div>")

    return "".join(result)


# =========================================================
# CHAT HTML
# =========================================================

def make_chat_html(history):
    if not history:
        return (
            '<div class="welcome">'
            '<div class="robot">🤖</div>'
            '<h1>Nexora AI</h1>'
            '<p>आप अपनी भाषा में कुछ भी पूछ सकते हैं।</p>'
            '<div class="suggestions">'
            '<button class="suggestion">भारत की राजधानी क्या है?</button>'
            '<button class="suggestion">आज की ताज़ा खबरें बताओ</button>'
            '<button class="suggestion">मुझे Python सिखाओ</button>'
            '<button class="suggestion">एक मजेदार कहानी सुनाओ</button>'
            '</div>'
            '</div>'
        )

    result = []

    for user_text, ai_text in history:
        safe_user = html.escape(user_text)
        safe_ai = html.escape(ai_text)

        answer_json = json.dumps(
            ai_text,
            ensure_ascii=False
        )

        result.append(
            '<div class="message-block">'

            '<div class="user-message">'
            '<div class="user-label">👤 आप</div>'
            '<div class="user-bubble">'
            + safe_user +
            '</div>'
            '</div>'

            '<div class="ai-message">'
            '<div class="ai-label">🤖 Nexora AI</div>'
            '<div class="ai-bubble">'
            + safe_ai.replace("\n", "<br>") +
            '</div>'

            '<div class="answer-actions">'

            '<button class="answer-btn like-btn">'
            '👍'
            '</button>'

            '<button class="answer-btn dislike-btn">'
            '👎'
            '</button>'

            '<button class="answer-btn speak-btn" data-answer='
            + html.escape(answer_json, quote=True) +
            '>'
            '🔊'
            '</button>'

            '<button class="answer-btn copy-btn" data-answer='
            + html.escape(answer_json, quote=True) +
            '>'
            '📋'
            '</button>'

            '<button class="answer-btn share-btn" data-answer='
            + html.escape(answer_json, quote=True) +
            '>'
            '↗️'
            '</button>'

            '<button class="answer-btn more-btn">'
            '⋯'
            '</button>'

            '</div>'
            '</div>'
            '</div>'
        )

    return "".join(result)


# =========================================================
# MAIN AI
# =========================================================

def nexora_ai(message, history=None, uploaded_file=None):
    history = history or []

    if not message or not message.strip():
        return (
            history,
            "",
            make_chat_html(history),
            "",
            ""
        )

    message = message.strip()

    try:
        old_chat = make_history(history)

        prompt_parts = [
            "You are Nexora AI, a helpful multilingual AI assistant.",
            "Understand the user's language automatically.",
            "Reply in the same language as the user.",
            "If the user writes Roman Hindi, reply in proper Devanagari Hindi.",
            "Give clear, useful and natural answers.",
            "Remember relevant previous conversation.",
            "Do not invent facts.",
            "If information is uncertain, say so.",
            "Current date: 2026-09-14.",
            "",
            "Previous conversation:",
            old_chat,
            "",
            "Current user question:",
            message
        ]

        prompt = "\n".join(prompt_parts)

        contents = [prompt]

        # -------------------------------------------------
        # FILE / IMAGE
        # -------------------------------------------------

        if uploaded_file:
            try:
                file_path = uploaded_file

                if hasattr(uploaded_file, "name"):
                    file_path = uploaded_file.name

                uploaded = client.files.upload(
                    file=file_path
                )

                contents.append(uploaded)

            except Exception as file_error:
                return (
                    history,
                    "",
                    make_chat_html(history),
                    "",
                    "⚠️ फ़ाइल पढ़ने में समस्या: "
                    + html.escape(str(file_error))
                )

        # -------------------------------------------------
        # CONFIG
        # -------------------------------------------------

        config_args = {
            "max_output_tokens": 1500
        }

        if needs_web_search(message):
            config_args["tools"] = [
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]

        config = types.GenerateContentConfig(
            **config_args
        )

        # -------------------------------------------------
        # GENERATE
        # -------------------------------------------------

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config
        )

        answer = response.text

        if not answer:
            answer = "मुझे अभी उत्तर नहीं मिला।"

        # -------------------------------------------------
        # SAVE HISTORY
        # -------------------------------------------------

        history = history[-(MAX_HISTORY - 1):]

        history.append(
            (
                message,
                answer
            )
        )

        # -------------------------------------------------
        # SPEAKER
        # -------------------------------------------------

        speaker_text = json.dumps(
            answer,
            ensure_ascii=False
        )

        speaker = (
            '<div id="speaker-bar" data-answer='
            + html.escape(speaker_text, quote=True)
            + '>'

            '<span class="speaker-name">'
            '🔊 Nexora AI'
            '</span>'

            '<button id="speaker-play">▶️</button>'
            '<button id="speaker-pause">⏸️</button>'
            '<button id="speaker-stop">⏹️</button>'
            '<button id="speaker-settings">⚙️</button>'
            '<button id="speaker-close">✕</button>'

            '</div>'
        )

        return (
            history,
            "",
            make_chat_html(history),
            sources_html(response),
            speaker
        )

    except Exception as e:
        return (
            history,
            "",
            make_chat_html(history),
            "",
            "❌ समस्या: "
            + html.escape(str(e))
        )


# =========================================================
# NEW CHAT
# =========================================================

def new_chat():
    return (
        [],
        make_chat_html([]),
        "",
        "",
        ""
    )


# =========================================================
# CSS
# =========================================================

css = "\n".join([
    "body {",
    "    margin: 0;",
    "    background: #ffffff !important;",
    "}",

    ".gradio-container {",
    "    max-width: 920px !important;",
    "    margin: auto !important;",
    "    padding-bottom: 110px !important;",
    "}",

    "#header {",
    "    text-align: center;",
    "    padding: 12px 0;",
    "}",

    "#title {",
    "    font-size: 28px;",
    "    font-weight: 700;",
    "}",

    "#subtitle {",
    "    opacity: .6;",
    "    font-size: 14px;",
    "}",

    "#chat-container {",
    "    height: calc(100vh - 245px);",
    "    min-height: 400px;",
    "    overflow-y: auto;",
    "    padding: 15px 8px 130px 8px;",
    "    scroll-behavior: smooth;",
    "}",

    ".welcome {",
    "    text-align: center;",
    "    padding-top: 55px;",
    "}",

    ".robot {",
    "    font-size: 60px;",
    "}",

    ".welcome h1 {",
    "    font-size: 34px;",
    "    margin: 8px;",
    "}",

    ".welcome p {",
    "    opacity: .6;",
    "}",

    ".suggestions {",
    "    display: flex;",
    "    flex-wrap: wrap;",
    "    justify-content: center;",
    "    gap: 9px;",
    "    margin-top: 25px;",
    "}",

    ".suggestion {",
    "    border: 1px solid #ddd;",
    "    background: white;",
    "    border-radius: 18px;",
    "    padding: 10px 14px;",
    "    cursor: pointer;",
    "}",

    ".message-block {",
    "    margin-bottom: 28px;",
    "}",

    ".user-label, .ai-label {",
    "    font-size: 13px;",
    "    font-weight: 600;",
    "    opacity: .65;",
    "    margin-bottom: 5px;",
    "}",

    ".user-bubble {",
    "    background: #f1f3f4;",
    "    border-radius: 17px;",
    "    padding: 12px 15px;",
    "    white-space: pre-wrap;",
    "    overflow-wrap: anywhere;",
    "}",

    ".ai-bubble {",
    "    padding: 4px 2px;",
    "    line-height: 1.6;",
    "    white-space: normal;",
    "    overflow-wrap: anywhere;",
    "}",

    ".answer-actions {",
    "    display: flex;",
    "    gap: 4px;",
    "    margin-top: 8px;",
    "}",

    ".answer-btn {",
    "    border: 0;",
    "    background: transparent;",
    "    padding: 6px 8px;",
    "    border-radius: 9px;",
    "    cursor: pointer;",
    "    font-size: 17px;",
    "}",

    ".answer-btn:hover {",
    "    background: #f1f3f4;",
    "}",

    "#speaker-container {",
    "    position: sticky;",
    "    top: 0;",
    "    z-index: 60;",
    "}",

    "#speaker-bar {",
    "    display: flex;",
    "    align-items: center;",
    "    gap: 6px;",
    "    background: #f1f3f4;",
    "    padding: 8px 10px;",
    "    border-radius: 14px;",
    "    margin-bottom: 8px;",
    "}",

    ".speaker-name {",
    "    flex: 1;",
    "    font-weight: 600;",
    "}",

    "#speaker-bar button {",
    "    border: 0;",
    "    background: white;",
    "    border-radius: 9px;",
    "    padding: 7px 9px;",
    "    cursor: pointer;",
    "}",

    ".sources {",
    "    margin: 8px 5px;",
    "    padding: 10px;",
    "    border-top: 1px solid #eee;",
    "}",

    ".sources-title {",
    "    font-weight: 600;",
    "    margin-bottom: 5px;",
    "}",

    ".source-link {",
    "    display: block;",
    "    padding: 4px 0;",
    "    text-decoration: none;",
    "    overflow-wrap: anywhere;",
    "}",

    "#input-area {",
    "    position: fixed;",
    "    z-index: 100;",
    "    left: 50%;",
    "    bottom: 7px;",
    "    transform: translateX(-50%);",
    "    width: min(900px, calc(100% - 12px));",
    "    background: rgba(255,255,255,.98);",
    "    padding: 8px;",
    "    border-radius: 18px;",
    "    box-shadow: 0 2px 18px rgba(0,0,0,.14);",
    "}",

    "#question textarea {",
    "    min-height: 48px !important;",
    "    max-height: 130px !important;",
    "    border-radius: 17px !important;",
    "    padding: 12px 14px !important;",
    "}",

    "#mic button, #send button {",
    "    min-width: 50px !important;",
    "    height: 48px !important;",
    "    border-radius: 14px !important;",
    "    font-size: 20px !important;",
    "}",

    "#voice-panel {",
    "    display: none;",
    "    position: fixed;",
    "    z-index: 200;",
    "    left: 50%;",
    "    top: 50%;",
    "    transform: translate(-50%,-50%);",
    "    width: min(400px, 90%);",
    "    background: white;",
    "    border: 1px solid #ddd;",
    "    border-radius: 20px;",
    "    padding: 20px;",
    "    box-shadow: 0 5px 30px rgba(0,0,0,.25);",
    "}",

    "#voice-select {",
    "    width: 100%;",
    "    padding: 10px;",
    "    margin-top: 10px;",
    "}",

    "#new-chat button {",
    "    border-radius: 18px !important;",
    "}",

    "@media(max-width:600px) {",
    "    #title { font-size: 23px; }",
    "    #chat-container {",
    "        height: calc(100vh - 220px);",
    "    }",
    "    .welcome { padding-top: 35px; }",
    "    .welcome h1 { font-size: 28px; }",
    "    #input-area {",
    "        width: calc(100% - 8px);",
    "        bottom: 4px;",
    "    }",
    "}"
])


# =========================================================
# JAVASCRIPT
# =========================================================

js_lines = [

    "let recognition = null;",
    "let listening = false;",
    "let selectedVoice = null;",

    "",

    "function scrollChat() {",
    "    const box = document.querySelector('#chat-container');",
    "    if (box) {",
    "        setTimeout(function() {",
    "            box.scrollTop = box.scrollHeight;",
    "        }, 150);",
    "    }",
    "}",

    "",

    "function setQuestion(text) {",
    "    const box = document.querySelector('#question textarea');",
    "    if (!box) return;",
    "    box.value = text;",
    "    box.dispatchEvent(new Event('input', {bubbles:true}));",
    "    box.dispatchEvent(new Event('change', {bubbles:true}));",
    "    box.focus();",
    "}",

    "",

    "function stopSpeech() {",
    "    if ('speechSynthesis' in window) {",
    "        speechSynthesis.cancel();",
    "    }",
    "}",

    "",

    "function speakText(text) {",
    "    if (!('speechSynthesis' in window)) {",
    "        alert('इस ब्राउज़र में आवाज़ सुविधा उपलब्ध नहीं है।');",
    "        return;",
    "    }",

    "    stopSpeech();",

    "    const utterance = new SpeechSynthesisUtterance(text);",

    "    if (selectedVoice) {",
    "        utterance.voice = selectedVoice;",
    "    }",

    "    utterance.rate = 0.9;",
    "    speechSynthesis.speak(utterance);",
    "}",

    "",

    "function loadVoices() {",
    "    const select = document.querySelector('#voice-select');",
    "    if (!select || !('speechSynthesis' in window)) return;",

    "    const voices = speechSynthesis.getVoices();",

    "    select.innerHTML = '';",

    "    voices.slice(0, 25).forEach(function(voice) {",
    "        const option = document.createElement('option');",
    "        option.value = voice.name;",
    "        option.textContent = voice.name + ' — ' + voice.lang;",
    "        select.appendChild(option);",
    "    });",
    "}",

    "",

    "function openVoiceSettings() {",
    "    const panel = document.querySelector('#voice-panel');",
    "    if (!panel) return;",
    "    panel.style.display = 'block';",
    "    loadVoices();",
    "}",

    "",

    "function closeVoiceSettings() {",
    "    const panel = document.querySelector('#voice-panel');",
    "    if (panel) panel.style.display = 'none';",
    "}",

    "",

    "function startMic() {",

    "    const SpeechRecognition =",
    "        window.SpeechRecognition ||",
    "        window.webkitSpeechRecognition;",

    "    if (!SpeechRecognition) {",
    "        alert('इस ब्राउज़र में Voice Input उपलब्ध नहीं है।');",
    "        return;",
    "    }",

    "    if (listening && recognition) {",
    "        recognition.stop();",
    "        return;",
    "    }",

    "    recognition = new SpeechRecognition();",

    "    recognition.lang = 'hi-IN';",
    "    recognition.continuous = false;",
    "    recognition.interimResults = false;",

    "    recognition.onstart = function() {",
    "        listening = true;",
    "        const btn = document.querySelector('#mic button');",
    "        if (btn) btn.innerText = '🛑';",
    "    };",

    "    recognition.onresult = function(event) {",
    "        const text = event.results[0][0].transcript;",
    "        setQuestion(text);",
    "    };",

    "    recognition.onerror = function() {",
    "        listening = false;",
    "        const btn = document.querySelector('#mic button');",
    "        if (btn) btn.innerText = '🎤';",
    "    };",

    "    recognition.onend = function() {",
    "        listening = false;",
    "        const btn = document.querySelector('#mic button');",
    "        if (btn) btn.innerText = '🎤';",
    "    };",

    "    recognition.start();",
    "}",

    "",

    "document.addEventListener('click', function(event) {",

    "    const suggestion = event.target.closest('.suggestion');",

    "    if (suggestion) {",
    "        setQuestion(suggestion.innerText);",
    "        return;",
    "    }",

    "    const mic = event.target.closest
