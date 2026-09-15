import os
import html
import gradio as gr
from google import genai
from google.genai import types

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"
MAX_HISTORY = 10


def ask_nexora(message, history):
    history = history or []

    if not message or not message.strip():
        return "", history, render_chat(history)

    previous = ""

    for user_text, ai_text in history[-MAX_HISTORY:]:
        previous += "User: " + user_text + "\n"
        previous += "Nexora AI: " + ai_text + "\n"

    prompt = (
        "You are Nexora AI, a helpful multilingual AI assistant.\n"
        "Understand the user's language automatically.\n"
        "Reply in the same language as the user.\n"
        "Give clear, useful and honest answers.\n"
        "Do not invent facts.\n\n"
        "Previous conversation:\n"
        + previous
        + "\nCurrent question:\n"
        + message
    )

    try:
        search_words = [
            "latest", "today", "current", "news",
            "weather", "price", "2026",
            "आज", "अभी", "वर्तमान", "ताज़ा",
            "समाचार", "मौसम", "कीमत"
        ]

        use_search = any(
            word in message.lower()
            for word in search_words
        )

        if use_search:
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

        return "", history, render_chat(history)

    except Exception as e:
        error = "❌ समस्या: " + str(e)
        return "", history, render_chat(history) + (
            "<div class='error'>" +
            html.escape(error) +
            "</div>"
        )


def render_chat(history):
    if not history:
        return (
            "<div class='welcome'>"
            "<div class='logo-big'>🤖</div>"
            "<h1>Nexora AI</h1>"
            "<p>आपकी AI सहायता के लिए तैयार हूँ</p>"
            "</div>"
        )

    result = ""

    for user_text, ai_text in history:
        safe_user = html.escape(user_text)
        safe_ai = html.escape(ai_text).replace("\n", "<br>")

        result += (
            "<div class='message user-message'>"
            "<div class='user-bubble'>"
            + safe_user +
            "</div>"
            "</div>"
        )

        result += (
            "<div class='message ai-message'>"
            "<div class='ai-name'>🤖 Nexora AI</div>"
            "<div class='ai-bubble'>"
            + safe_ai +
            "</div>"
            "<div class='actions'>"
            "<button onclick='copyAnswer(this)'>📋</button>"
            "<button>👍</button>"
            "<button>👎</button>"
            "<button onclick='speakAnswer(this)'>🔊</button>"
            "<button onclick='shareAnswer(this)'>↗️</button>"
            "<button>⋯</button>"
            "</div>"
            "</div>"
        )

    return result


def clear_chat():
    return [], render_chat([])


CSS = (
    "html,body{margin:0!important;padding:0!important;}"
    "body{background:#fff!important;}"
    ".gradio-container{max-width:100%!important;"
    "padding:0!important;}"
    "#main-area{height:100vh;overflow:hidden;}"
    "#chat-area{height:calc(100vh - 145px);"
    "overflow-y:auto;padding:20px 18px 120px;"
    "scroll-behavior:smooth;}"
    ".welcome{text-align:center;padding-top:25vh;"
    "color:#444;}"
    ".logo-big{font-size:58px;}"
    ".welcome h1{font-size:30px;margin:10px;}"
    ".welcome p{font-size:17px;color:#777;}"
    ".message{margin:18px 0;}"
    ".user-message{display:flex;"
    "justify-content:flex-end;}"
    ".user-bubble{background:#e8f0fe;"
    "padding:11px 15px;border-radius:18px;"
    "max-width:78%;font-size:16px;}"
    ".ai-message{max-width:90%;}"
    ".ai-name{font-weight:700;margin-bottom:6px;"
    "font-size:16px;}"
    ".ai-bubble{background:#f5f5f5;"
    "padding:13px 15px;border-radius:17px;"
    "font-size:16px;line-height:1.55;}"
    ".actions{display:flex;gap:5px;margin-top:6px;}"
    ".actions button{border:0;background:transparent;"
    "padding:6px 8px;font-size:17px;cursor:pointer;}"
    "#input-area{position:fixed;left:50%;"
    "bottom:10px;transform:translateX(-50%);"
    "width:min(94%,850px);z-index:100;"
    "background:white;border:1px solid #ddd;"
    "border-radius:24px;padding:6px;"
    "box-shadow:0 4px 20px #0002;}"
    "#question textarea{border:0!important;"
    "box-shadow:none!important;font-size:16px!important;"
    "padding:13px!important;}"
    "#mic button,#send button{border:0!important;"
    "border-radius:18px!important;min-height:48px!important;"
    "font-size:20px!important;}"
    ".error{color:#b00020;padding:12px;}"
    "@media(max-width:600px){"
    "#chat-area{height:calc(100vh - 135px);"
    "padding-left:10px;padding-right:10px;}"
    ".ai-bubble,.user-bubble{font-size:15px;}"
    "#input-area{width:96%;}"
    "}"
)


JS = (
    "() => {"
    "window.copyAnswer=function(btn){"
    "var row=btn.closest('.ai-message');"
    "var box=row.querySelector('.ai-bubble');"
    "if(box&&navigator.clipboard){"
    "navigator.clipboard.writeText(box.innerText);"
    "}"
    "};"

    "window.speakAnswer=function(btn){"
    "var row=btn.closest('.ai-message');"
    "var box=row.querySelector('.ai-bubble');"
    "if(!box)return;"
    "speechSynthesis.cancel();"
    "var speech=new SpeechSynthesisUtterance(box.innerText);"
    "speech.lang='hi-IN';"
    "speech.rate=0.9;"
    "speechSynthesis.speak(speech);"
    "};"

    "window.shareAnswer=function(btn){"
    "var row=btn.closest('.ai-message');"
    "var box=row.querySelector('.ai-bubble');"
    "if(!box)return;"
    "if(navigator.share){"
    "navigator.share({text:box.innerText});"
    "}else if(navigator.clipboard){"
    "navigator.clipboard.writeText(box.innerText);"
    "}"
    "};"

    "setInterval(function(){"
    "var area=document.querySelector('#chat-area');"
    "if(area){area.scrollTop=area.scrollHeight;}"
    "},700);"

    "}"
)


with gr.Blocks(
    title="Nexora AI"
) as app:

    with gr.Sidebar(
        label="Nexora AI",
        open=False,
        width=280
    ):

        gr.Markdown("# 🤖 Nexora AI")

        new_chat = gr.Button("🆕 नया चैट")
        history_button = gr.Button("🗂️ Chat History")
        web_button = gr.Button("🌐 Web Search")
        image_button = gr.Button("🖼️ Create Image")
        write_button = gr.Button("✍️ Write / Edit")
        files_button = gr.Button("📁 Files")
        voice_button = gr.Button("🎙️ Voice")
        settings_button = gr.Button("⚙️ Settings")

    with gr.Column(elem_id="main-area"):

        gr.Markdown(
            "## 🤖 Nexora AI"
        )

        history_state = gr.State([])

        chat = gr.HTML(
            render_chat([]),
            elem_id="chat-area"
        )

        with gr.Row(elem_id="input-area"):

            question = gr.Textbox(
                placeholder="Nexora AI से कुछ पूछें...",
                show_label=False,
                lines=1,
                scale=8,
                elem_id="question"
            )

            mic = gr.Button(
                "🎤",
                scale=0,
                elem_id="mic"
            )

            send = gr.Button(
                "➤",
                scale=0,
                elem_id="send"
            )

    send.click(
        ask_nexora,
        inputs=[question, history_state],
        outputs=[question, history_state, chat]
    )

    question.submit(
        ask_nexora,
        inputs=[question, history_state],
        outputs=[question, history_state, chat]
    )

    new_chat.click(
        clear_chat,
        outputs=[history_state, chat]
    )


app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "10000")),
    css=CSS,
    js=JS
)
