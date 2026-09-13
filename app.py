import os

import gradio as gr
from google import genai

# API key Hugging Face Secret से ली जाएगी
API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

def nexora_ai(message, history=None):
    if not message or not message.strip():
        return "कृपया अपना सवाल लिखिए।"

    try:
        old_chat = ""

        if history:
            for item in history:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    old_chat += f"User: {item[0]}\nNexora AI: {item[1]}\n"

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
You are Nexora AI, a helpful multilingual AI assistant.

Rules:
- Understand the user's language automatically.
- Reply in the same language as the user.
- Give clear and useful answers.
- Remember previous conversation when relevant.

Previous conversation:
{old_chat}

User question:
{message}
"""
        )

        return response.text

    except Exception as e:
     return "ERROR: " + repr(e)   


def like():
    return "👍"


def dislike():
    return "👎"


def more():
    return "⋯"


css = """
#app {
    max-width: 850px;
    margin: auto;
}

#icons button {
    min-width: 48px !important;
    height: 42px !important;
    font-size: 19px !important;
    border-radius: 12px !important;
}
"""

with gr.Blocks(css=css, title="Nexora AI") as app:

    gr.Markdown("# 🤖 Nexora AI")
    gr.Markdown("🌍 अपनी पसंद की भाषा में सवाल पूछिए।")

    question = gr.Textbox(
        placeholder="💬 यहाँ अपना सवाल लिखें...",
        label="",
        lines=3
    )

    send = gr.Button("➤", variant="primary")

    answer = gr.Textbox(
        label="Nexora AI",
        lines=10,
        interactive=False
    )

    status = gr.Markdown("")

    with gr.Row(elem_id="icons"):
        like_btn = gr.Button("👍")
        dislike_btn = gr.Button("👎")
        sound_btn = gr.Button("🔊")
        copy_btn = gr.Button("📋")
        share_btn = gr.Button("↗️")
        more_btn = gr.Button("⋯")

    send.click(
        nexora_ai,
        inputs=question,
        outputs=answer
    )

    like_btn.click(like, outputs=status)
    dislike_btn.click(dislike, outputs=status)
    more_btn.click(more, outputs=status)

    copy_btn.click(
        None,
        inputs=answer,
        js="""
        (text) => {
            if (text) navigator.clipboard.writeText(text);
            return [];
        }
        """
    )

    sound_btn.click(
        None,
        inputs=answer,
        js="""
        (text) => {
            if (text) {
                speechSynthesis.cancel();
                const speech = new SpeechSynthesisUtterance(text);
                speech.lang = "hi-IN";
                speech.rate = 0.9;
                speechSynthesis.speak(speech);
            }
            return [];
        }
        """
    )

    share_btn.click(
        None,
        inputs=answer,
        js="""
        (text) => {
            if (navigator.share) {
                navigator.share({
                    title: "Nexora AI",
                    text: text || "Nexora AI"
                });
            }
            return [];
        }
        """
    )

app.launch()
