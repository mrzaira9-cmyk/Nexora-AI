import os
import html
import gradio as gr
from google import genai
from google.genai import types

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"
MAX_HISTORY = 10


def needs_web_search(text):
    words = [
        "latest", "today", "current", "news", "weather",
        "price", "2026", "who is", "what happened",
        "आज", "अभी", "वर्तमान", "ताज़ा", "समाचार",
        "मौसम", "कीमत", "कौन है", "क्या हुआ"
    ]
    text = (text or "").lower()
    return any(word in text for word in words)


def make_chat_html(history):
    if not history:
        return (
            '<div id="emptychat">'
            '👋 नमस्ते! मैं <b>Nexora AI</b> हूँ।<br>'
            'नीचे अपना सवाल लिखें।'
            '</div>'
        )

    result = ""

    for user_text, ai_text in history:
        safe_user = html.escape(user_text)
        safe_ai = html.escape(ai_text).replace("\n", "<br>")

        result += (
            '<div class="user-message">'
            '<div class="bubble user-bubble">'
            '<b>आप</b><br>'
            + safe_user +
            '</div></div>'
        )

        result += (
            '<div class="ai-message">'
            '<div class="bubble ai-bubble">'
            '<b>🤖 Nexora AI</b><br>'
            + safe_ai +
            '</div>'
            '<div class="actions">'
            '<button onclick="copyAnswer(this)">📋</button>'
            '<button>👍</button>'
            '<button>👎</button>'
            '<button onclick="speakAnswer(this)">🔊</button>'
            '<button onclick="shareAnswer(this)">↗️</button>'
            '<button>⋯</button>'
            '</div>'
            '</div>'
        )

    return result


def nexora_ai(message, history):
    history = history or []

    if not message or not message.strip():
        return "", history, make_chat_html(history)

    prompt = (
        "You are Nexora AI, a helpful multilingual AI assistant.\n"
        "Understand the user's language automatically.\n"
        "Reply in the same language as the user.\n"
        "Give clear, useful and honest answers.\n"
        "Do not invent facts.\n\n"
    )

    if history:
        prompt += "Previous conversation:\n"

        for user_text, ai_text in history[-MAX_HISTORY:]:
            prompt += "User: " + user_text + "\n"
            prompt += "Nexora AI: " + ai_text + "\n"

    prompt += "\nUser question:\n" + message

    try:
        if needs_web_search(message):
            search_tool = types.Tool(
                google_search=types.GoogleSearch()
            )

            config = types.GenerateContentConfig(
                tools=[search_tool],
                max_output_tokens=1200
            )

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=config
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

        answer = response.text or "मुझे अभी कोई उत्तर नहीं मिला।"

        history = history[-MAX_HISTORY:] + [
            (message, answer)
        ]

        return "", history, make_chat_html(history)

    except Exception as e:
        error_text = "❌ समस्या: " + str(e)

        return (
            "",
            history,
            make_chat_html(history)
            + '<div class="error">'
            + html.escape(error_text)
            + '</div>'
        )


def clear_chat():
    return [], make_chat_html([])


CSS = (
    "*{box-sizing:border-box;}"
    "body{margin:0;}"
    "#appbox{max-width:1000px;margin:auto;}"
    ".topbar{display:flex;align-items:center;"
    "justify-content:space-between;padding:12px 8px;}"
    ".logo{font-size:22px;font-weight:700;}"
    ".chatbox{height:68vh;overflow-y:auto;"
    "padding:15px 8px 130px;scroll-behavior:smooth;}"
    ".user-message{display:flex;justify-content:flex-end;"
    "margin:12px 0;}"
    ".ai-message{display:block;margin:14px 0;}"
    ".bubble{max-width:82%;padding:12px 15px;"
    "border-radius:16px;line-height:1.5;}"
    ".user-bubble{background:#e8f0fe;}"
    ".ai-bubble{background:#f3f3f3;}"
    ".actions{display:flex;gap:6px;margin-top:5px;}"
    ".actions button{min-width:38px;height:34px;"
    "border:0;border-radius:10px;cursor:pointer;}"
    "#inputrow{position:fixed;left:50%;bottom:10px;"
    "transform:translateX(-50%);width:min(96%,980px);"
    "z-index:50;background:white;padding:8px;"
    "border-radius:18px;box-shadow:0 2px 18px #9995;}"
    "#question textarea{border-radius:14px!important;}"
    "#emptychat{text-align:center;padding-top:18vh;"
    "font-size:18px;line-height:2;}"
    ".error{color:#b00020;padding:10px;}"
    "#voicepanel{padding:10px;margin:5px 0;"
    "border:1px solid #ddd;border-radius:12px;}"
)


JS = (
    "() => {"
    "window.copyAnswer = function(btn) {"
    " const box=btn.closest('.ai-message').querySelector('.bubble');"
    " if(box) navigator.clipboard.writeText(box.innerText);"
    "};"

    "window.speakAnswer = function(btn) {"
    " const box=btn.closest('.ai-message').querySelector('.bubble');"
    " if(!box)return;"
    " speechSynthesis.cancel();"
    " const u=new SpeechSynthesisUtterance(box.innerText);"
    " u.lang='hi-IN';"
    " u.rate=0.9;"
    " speechSynthesis.speak(u);"
    "};"

    "window.shareAnswer = function(btn) {"
    " const box=btn.closest('.ai-message').querySelector('.bubble');"
    " if(!box)return;"
    " if(navigator.share){"
    "  navigator.share({text:box.innerText});"
    " }else{"
    "  navigator.clipboard.writeText(box.innerText);"
    " }"
    "};"

    "document.addEventListener('click',function(e){"
    " const mic=e.target.closest('#micbtn');"
    " if(mic){"
    "  const R=window.SpeechRecognition||window.webkitSpeechRecognition;"
    "  if(!R){alert('इस ब्राउज़र में माइक्रोफोन उपलब्ध नहीं है।');return;}"
    "  const r=new R();"
    "  r.lang='hi-IN';"
    "  r.interimResults=false;"
    "  r.onresult=function(ev){"
    "   const box=document.querySelector('#question textarea');"
    "   if(box){"
    "    box.value=ev.results[0][0].transcript;"
    "    box.dispatchEvent(new Event('input',{bubbles:true}));"
    "   }"
    "  };"
    "  r.start();"
    " }"
    "});"

    "setInterval(function(){"
    " const c=document.querySelector('#chatbox');"
    " if(c)c.scrollTop=c.scrollHeight;"
    "},800);"
    "}"
)


with gr.Blocks(title="Nexora AI") as app:

    gr.HTML(
        '<div id="appbox">'
        '<div class="topbar">'
        '<div class="logo">🤖 Nexora AI</div>'
        '<div>🔊 Nexora AI</div>'
        '</div>'
        '</div>'
    )

    history_state = gr.State([])

    chat = gr.HTML(
        make_chat_html([]),
        elem_id="chatbox"
    )

    with gr.Row(elem_id="inputrow"):

        question = gr.Textbox(
            placeholder="यहाँ अपना सवाल लिखें...",
            show_label=False,
            lines=1,
            elem_id="question"
        )

        mic = gr.Button(
            "🎤",
            elem_id="micbtn",
            scale=0
        )

        send = gr.Button(
            "➤",
            elem_id="sendbtn",
            scale=0
        )

    new_chat = gr.Button(
        "🆕 नया चैट",
        elem_id="newchat"
    )

    send.click(
        nexora_ai,
        inputs=[question, history_state],
        outputs=[question, history_state, chat]
    )

    question.submit(
        nexora_ai,
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
