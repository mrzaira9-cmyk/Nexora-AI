import os
import gradio as gr
from google import genai

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"


def ask_nexora(message, history):
    history = history or []

    if not message or not message.strip():
        return history, ""

    # पुरानी बातचीत Gemini को भेजना
    previous = ""
    for item in history[-10:]:
        if isinstance(item, dict):
            role = item.get("role", "")
            content = item.get("content", "")
            if role == "user":
                previous += "User: " + str(content) + "\n"
            elif role == "assistant":
                previous += "Nexora AI: " + str(content) + "\n"

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
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        answer = response.text or "मुझे कोई उत्तर नहीं मिला।"

        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer}
        ]

        # खाली input box + updated chat
        return history, ""

    except Exception as e:
        error = "❌ समस्या आ गई: " + str(e)

        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error}
        ]

        return history, ""


def new_chat():
    return [], ""


CSS = """
html, body {
    margin: 0 !important;
    padding: 0 !important;
}

body {
    background: white !important;
}

.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
}

#header {
    height: 55px;
    display: flex;
    align-items: center;
    padding: 0 14px;
    border-bottom: 1px solid #eeeeee;
}

#chat {
    height: calc(100vh - 145px) !important;
    min-height: 400px !important;
}

#bottom {
    position: fixed !important;
    left: 50%;
    bottom: 10px;
    transform: translateX(-50%);
    width: min(94%, 850px);
    z-index: 1000;
    background: white;
    border: 1px solid #dddddd;
    border-radius: 25px;
    padding: 5px;
    box-shadow: 0 3px 18px rgba(0,0,0,0.12);
}

#question textarea {
    border: 0 !important;
    box-shadow: none !important;
    font-size: 16px !important;
    padding: 12px !important;
}

#mic button,
#send button {
    min-width: 48px !important;
    min-height: 48px !important;
    border-radius: 20px !important;
    font-size: 20px !important;
}

@media (max-width: 600px) {
    #chat {
        height: calc(100vh - 135px) !important;
    }

    #bottom {
        width: 96%;
        bottom: 8px;
    }
}
"""


with gr.Blocks(title="Nexora AI") as app:

    # ऊपर का छोटा Header
    with gr.Row(elem_id="header"):
        menu = gr.Button("☰", scale=0, min_width=45)
        gr.Markdown("### 🤖 Nexora AI")

    # Sidebar
    with gr.Sidebar(
        label="Nexora AI",
        open=False,
        width=270
    ):
        gr.Markdown("## 🤖 Nexora AI")

        new_chat_btn = gr.Button("🆕 नया चैट")
        gr.Button("🗂️ Chat History")
        gr.Button("🌐 Web Search")
        gr.Button("🖼️ Create Image")
        gr.Button("✍️ Write / Edit")
        gr.Button("📁 Files")
        gr.Button("🎙️ Voice")
        gr.Button("⚙️ Settings")

    # Chat area
    history = gr.State([])

    chat = gr.Chatbot(
        value=[],
        type="messages",
        autoscroll=True,
        height="calc(100vh - 145px)",
        show_label=False,
        elem_id="chat",
        placeholder=(
            "<div style='text-align:center;"
            "padding-top:20vh;'>"
            "<h1>🤖 Nexora AI</h1>"
            "<p>आपकी AI सहायता के लिए तैयार हूँ</p>"
            "</div>"
        )
    )

    # नीचे हमेशा रहने वाला Input
    with gr.Row(elem_id="bottom"):

        question = gr.Textbox(
            placeholder="Nexora AI से कुछ पूछें...",
            show_label=False,
            lines=1,
            max_lines=4,
            scale=8,
            elem_id="question",
            autofocus=True
        )

        mic = gr.Button(
            "🎤",
            scale=0,
            min_width=50,
            elem_id="mic"
        )

        send = gr.Button(
            "➤",
            scale=0,
            min_width=50,
            elem_id="send"
        )

    # Send button
    send.click(
        ask_nexora,
        inputs=[question, history],
        outputs=[chat, history, question]
    )

    # Enter दबाने पर भी भेजे
    question.submit(
        ask_nexora,
        inputs=[question, history],
        outputs=[chat, history, question]
    )

    # New Chat
    new_chat_btn.click(
        new_chat,
        outputs=[history, question]
    ).then(
        lambda: [],
        outputs=chat
    )


app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "10000")),
    css=CSS
            )
