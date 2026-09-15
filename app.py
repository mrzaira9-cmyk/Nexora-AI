import os
import html
import gradio as gr
from google import genai
from google.genai import types

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"
MAX_HISTORY = 10


def web_needed(text):
    words = [
        "latest", "today", "current", "news", "weather",
        "price", "2026", "search", "who is",
        "आज", "अभी", "वर्तमान", "ताज़ा", "समाचार",
        "मौसम", "कीमत", "खोज", "कौन है"
    ]
    text = (text or "").lower()
    return any(x in text for x in words)


def make_history(history):
    if not history:
        return (
            '<div class="welcome">'
            '<div class="robot">🤖</div>'
            '<h1>Nexora AI</h1>'
            '<p>नमस्ते! मैं Nexora AI हूँ।</p>'
            '<p>नीचे अपना सवाल लिखें।</p>'
            '</div>'
        )

    out = ""

    for user_text, ai_text in history:
        u = html.escape(user_text)
        a = html.escape(ai_text).replace("\n", "<br>")

        out += (
            '<div class="user-row">'
            '<div class="user-bubble">'
            + u +
            '</div></div>'
        )

        out += (
            '<div class="ai-row">'
            '<div class="ai-bubble">'
            '<div class="ai-name">🤖 Nexora AI</div>'
            '<div class="answer-text">'
            + a +
            '</div>'
            '</div>'
            '<div class="answer-actions">'
            '<button onclick="copyAnswer(this)">📋</button>'
            '<button>👍</button>'
            '<button>👎</button>'
            '<button onclick="speakAnswer(this)">🔊</button>'
            '<button onclick="shareAnswer(this)">↗️</button>'
            '<button>⋯</button>'
            '</div>'
            '</div>'
        )

    return out


def ask_ai(message, history):
    history = history or []

    if not message or not message.strip():
        return "", history, make_history(history)

    old = ""

    for u, a in history[-MAX_HISTORY:]:
        old += "User: " + u + "\n"
        old += "Nexora AI: " + a + "\n"

    prompt = (
        "You are Nexora AI, a helpful multilingual AI assistant.\n"
        "Understand the user's language automatically.\n"
        "Reply in the same language as the user.\n"
        "Give clear and useful answers.\n"
        "Do not invent facts.\n"
        "If you are unsure, say so.\n\n"
        "Previous conversation:\n"
        + old +
        "\nCurrent user question:\n"
        + message
    )

    try:
        if web_needed(message):
            tool = types.Tool(
                google_search=types.GoogleSearch()
            )

            config = types.GenerateContentConfig(
                tools=[tool],
                max_output_tokens=1200
            )
        else:
            config = types.GenerateContentConfig(
                max_output_tokens=1200
            )

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config
        )

        answer = response.text or "मुझे कोई उत्तर नहीं मिला।"

        history = history[-MAX_HISTORY:] + [
            (message, answer)
        ]

        return "", history, make_history(history)

    except Exception as e:
        error = "❌ समस्या: " + str(e)
        return "", history, make_history(history) + (
            '<div class="error">' +
            html.escape(error) +
            '</div>'
        )


def new_chat_action():
    return [], make_history([])


CSS = (
    "html,body{margin:0;padding:0;}"
    "body{background:#fff;font-family:Arial,sans-serif;}"
    ".app{max-width:1000px;margin:auto;}"
    ".top{height:60px;display:flex;align-items:center;"
    "justify-content:space-between;padding:0 15px;"
    "border-bottom:1px solid #eee;}"
    ".brand{font-size:22px;font-weight:700;}"
    ".top-right{font-size:18px;}"
    ".welcome{text-align:center;padding-top:18vh;}"
    ".robot{font-size:55px;}"
    ".welcome h1{font-size:30px;margin:8px;}"
    ".welcome p{font-size:18px;margin:7px;color:#555;}"
    "#chatarea{height:68vh;overflow-y:auto;"
    "padding:10px 12px 150px;scroll-behavior:smooth;}"
    ".user-row{display:flex;justify-content:flex-end;margin:14px 0;}"
    ".user-bubble{background:#e8f0fe;padding:12px 16px;"
    "border-radius:18px;max-width:80%;font-size:16px;}"
    ".ai-row{margin:18px 0;}"
    ".ai-bubble{background:#f5f5f5;padding:14px 16px;"
    "border-radius:18px;max-width:88%;font-size:16px;"
    "line-height:1.55;}"
    ".ai-name{font-weight:700;margin-bottom:8px;}"
    ".answer-actions{display:flex;gap:6px;margin-top:6px;}"
    ".answer-actions button{border:0;background:#f1f1f1;"
    "border-radius:10px;padding:7px 10px;font-size:16px;}"
    ".error{color:#b00020;padding:10px;}"
    "#inputbar{position:fixed;left:50%;bottom:12px;"
    "transform:translateX(-50%);width:min(94%,950px);"
    "background:#fff;padding:8px;border-radius:22px;"
    "box-shadow:0 2px 20px #0002;z-index:100;}"
    "#question textarea{border-radius:18px!important;"
    "font-size:16px!important;}"
    "#mic button,#send button{min-width:52px!important;"
    "height:52px!important;border-radius:18px!important;"
    "font-size:22px!important;}"
    ".menu-title{font-size:21px;font-weight:700;"
    "padding:10px 5px;}"
    ".menu-info{color:#666;padding:5px;}"
)


JS = (
    "() => {"

    "window.copyAnswer=function(btn){"
    "var b=btn.closest('.ai-row').querySelector('.ai-bubble');"
    "if(b&&navigator.clipboard){"
    "navigator.clipboard.writeText(b.innerText);"
    "}"
    "};"

    "window.speakAnswer=function(btn){"
    "var b=btn.closest('.ai-row').querySelector('.ai-bubble');"
    "if(!b)return;"
    "speechSynthesis.cancel();"
    "var u=new SpeechSynthesisUtterance(b.innerText);"
    "u.lang='hi-IN';"
    "u.rate=0.9;"
    "speechSynthesis.speak(u);"
    "};"

    "window.shareAnswer=function(btn){"
    "var b=btn.closest('.ai-row').querySelector('.ai-bubble');"
    "if(!b)return;"
    "if(navigator.share){"
    "navigator.share({text:b.innerText});"
    "}else if(navigator.clipboard){"
    "navigator.clipboard.writeText(b.innerText);"
    "}"
    "};"

    "document.addEventListener('click',function(e){"
    "var mic=e.target.closest('#mic');"
    "if(mic){"
    "var R=window.SpeechRecognition||window.webkitSpeechRecognition;"
    "if(!R){alert('इस ब्राउज़र में माइक्रोफोन उपलब्ध नहीं है।');return;}"
    "var r=new R();"
    "r.lang='hi-IN';"
    "r.interimResults=false;"
    "r.onresult=function(ev){"
    "var box=document.querySelector('#question textarea');"
    "if(box){"
    "box.value=ev.results[0][0].transcript;"
    "box.dispatchEvent(new Event('input',{bubbles:true}));"
    "}"
    "};"
    "r.start();"
    "}"
    "});"

    "setInterval(function(){"
    "var c=document.querySelector('#chatarea');"
    "if(c)c.scrollTop=c.scrollHeight;"
    "},1000);"

    "}"
)


with gr.Blocks(title="Nexora AI") as app:

    gr.HTML(
        '<div class="app">'
        '<div class="top">'
        '<div class="brand">🤖 Nexora AI</div>'
        '<div class="top-right">🔊 Nexora AI</div>'
        '</div>'
        '</div>'
    )

    with gr.Row():
        with gr.Column(scale=1, visible=True):
            gr.HTML(
                '<div class="menu-title">☰ Nexora AI</div>'
                '<div class="menu-info">✨ Nexora AI Assistant</div>'
            )

            new_chat = gr.Button("🆕 नया चैट")
            web_button = gr.Button("🌐 Web Search")
            image_button = gr.Button("🖼️ Create Image")
            write_button = gr.Button("✍️ Write / Edit")
            files_button = gr.Button("📁 Files")
            voice_button = gr.Button("🎙️ Voice")
            settings_button = gr.Button("⚙️ Settings")

        with gr.Column(scale=4):
            history_state = gr.State([])

            chat = gr.HTML(
                make_history([]),
                elem_id="chatarea"
            )

    with gr.Row(elem_id="inputbar"):

        question = gr.Textbox(
            placeholder="Ask Nexora AI...",
            show_label=False,
            lines=1,
            elem_id="question",
            scale=8
        )

        mic = gr.Button(
            "🎤",
            elem_id="mic",
            scale=0
        )

        send = gr.Button(
            "➤",
            elem_id="send",
            scale=0
        )

    send.click(
        ask_ai,
        inputs=[question, history_state],
        outputs=[question, history_state, chat]
    )

    question.submit(
        ask_ai,
        inputs=[question, history_state],
        outputs=[question, history_state, chat]
    )

    new_chat.click(
        new_chat_action,
        outputs=[history_state, chat]
    )


app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "10000")),
    css=CSS,
    js=JS
    )
