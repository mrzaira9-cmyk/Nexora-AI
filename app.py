
import os
import gradio as gr
from google import genai

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"


def ask_nexora(message, history):
    history = history or []

    if not message or not message.strip():
        return history, history, ""

    # पुरानी बातचीत को Gemini के लिए तैयार करना
    previous = ""

    for item in history[-20:]:
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

        # Gradio messages format
        new_history = history + [
            {
                "role": "user",
                "content": message
            },
            {
                "role": "assistant",
                "content": answer
            }
        ]

        return new_history, new_history, ""

    except Exception as e:
        error = "❌ समस्या आ गई: " + str(e)

        new_history = history + [
            {
                "role": "user",
                "content": message
            },
            {
                "role": "assistant",
                "content": error
            }
        ]

        return new_history, new_history, ""


def new_chat():
    return [], []


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

#chat {
    height: calc(100vh - 150px) !important;
}

#bottom {
    position: fixed !important;
    left: 50% !important;
    bottom: 10px !important;
    transform: translateX(-50%) !important;
    width: min(94%, 850px) !important;
    z-index: 9999 !important;
    background: white !important;
    border: 1px solid #dddddd !important;
    border-radius: 25px !important;
    padding: 5px !important;
    box-shadow: 0 3px 18px rgba(0,0,0,0.12) !important;
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
        height: calc(100vh - 140px) !important;
    }

    #bottom {
        width: 96% !important;
    }
}
"""


with gr.Blocks(title="Nexora AI") as app:

    # ऊपर का Header
    with gr.Row():
        menu = gr.Button("☰", scale=0, min_width=45)
        gr.Markdown("## 🤖 Nexora AI")

    # बंद Sidebar
    with gr.Sidebar(
        label="Nexora AI",
        open=False,
        width=270
    ):
        gr.Markdown("# 🤖 Nexora AI")

        new_chat_btn = gr.Button("🆕 नया चैट")
        gr.Button("🗂️ Chat History")
        gr.Button("🌐 Web Search")
        gr.Button("🖼️ Create Image")
        gr.Button("✍️ Write / Edit")
        gr.Button("📁 Files")
        gr.Button("🎙️ Voice")
        gr.Button("⚙️ Settings")

    # बातचीत की memory
    history_state = gr.State([])

    # Chatbot
    chat = gr.Chatbot(
        value=[],
        show_label=False,
        autoscroll=True,
        height="calc(100vh - 150px)",
        elem_id="chat"
    )

    # नीचे हमेशा रहने वाला input
    with gr.Row(elem_id="bottom"):

        question = gr.Textbox(
            placeholder="Nexora AI से कुछ पूछें...",
            show_label=False,
            lines=1,
            max_lines=4,
            scale=8,
            elem_id="question"
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

    # Send
    send.click(
        ask_nexora,
        inputs=[question, history_state],
        outputs=[chat, history_state, question]
    )

    # Enter से Send
    question.submit(
        ask_nexora,
        inputs=[question, history_state],
        outputs=[chat, history_state, question]
    )

    # नया चैट
    new_chat_btn.click(
        new_chat,
        outputs=[chat, history_state]
    )


app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "10000")),
    css=CSS
            )
