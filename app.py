import os
import html
import json

import gradio as gr
from google import genai


# =========================================================
# GEMINI API
# =========================================================

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)


# =========================================================
# CHAT FUNCTION
# =========================================================

def nexora_ai(message, history=None):
    if not message or not message.strip():
        return (
            history or [],
            "",
            "## 🗂️ Chat History\n\nअभी कोई बातचीत नहीं हुई।",
            "",
        )

    try:
        history = history or []

        old_chat = ""

        for user_msg, ai_msg in history:
            old_chat += (
                f"User: {user_msg}\n"
                f"Nexora AI: {ai_msg}\n\n"
            )

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
You are Nexora AI, a helpful multilingual AI assistant.

IMPORTANT RULES:

1. Understand the user's language automatically.
2. Reply in the same language as the user's question.
3. If the user asks in Hindi using Roman Hindi,
   reply in proper Devanagari Hindi.
4. If the user asks in English, reply in English.
5. If the user asks in Bengali, reply in Bengali.
6. If the user asks in another language, reply in that language.
7. Give clear, useful and natural answers.
8. Remember previous conversation when relevant.
9. Do not invent facts.
10. If information may be uncertain or outdated, clearly say so.
11. Do not mention these internal instructions.

Previous conversation:
{old_chat}

Current user question:
{message}
"""
        )

        answer_text = response.text or "मुझे इस सवाल का उत्तर नहीं मिल पाया।"

        history.append((message, answer_text))

        # =================================================
        # CHAT HTML
        # =================================================

        chat_html = ""

        for index, (user_msg, ai_msg) in enumerate(history):

            safe_user = html.escape(user_msg)
            safe_ai = html.escape(ai_msg)

            answer_json = json.dumps(
                ai_msg,
                ensure_ascii=False
            )

            chat_html += f"""
            <div class="message-block">

                <div class="user-message">
                    <div class="message-label">आप</div>
                    <div class="user-bubble">
                        {safe_user}
                    </div>
                </div>

                <div class="ai-message">
                    <div class="message-label">🤖 Nexora AI</div>

                    <div class="ai-bubble">
                        {safe_ai}
                    </div>

                    <div class="answer-actions">

                        <button
                            class="answer-btn like-btn"
                            data-action="like">
                            👍
                        </button>

                        <button
                            class="answer-btn dislike-btn"
                            data-action="dislike">
                            👎
                        </button>

                        <button
                            class="answer-btn speak-btn"
                            data-answer='{answer_json}'>
                            🔊
                        </button>

                        <button
                            class="answer-btn copy-btn"
                            data-answer='{answer_json}'>
                            📋
                        </button>

                        <button
                            class="answer-btn share-btn"
                            data-answer='{answer_json}'>
                            ↗️
                        </button>

                        <button
                            class="answer-btn more-btn"
                            data-action="more">
                            ⋯
                        </button>

                    </div>
                </div>

            </div>
            """

        history_display = (
            "## 🗂️ Chat History\n\n"
            + chat_html
        )

        # =================================================
        # TOP SPEAKER BAR
        # =================================================

        sound_bar = f"""
        <div id="speaker-bar">

            <span id="speaker-title">
                🔊 Nexora AI
            </span>

            <button id="pause-speech">
                ⏸️
            </button>

            <button id="stop-speech">
                ⏹️
            </button>

            <button id="close-speaker">
                ✕
            </button>

        </div>
        """

        return (
            history,
            "",
            history_display,
            sound_bar,
        )

    except Exception as e:
        return (
            history or [],
            "",
            f"❌ समस्या: {html.escape(str(e))}",
            "",
        )


# =========================================================
# STATUS BUTTON FUNCTIONS
# =========================================================

def like():
    return "👍 पसंद किया गया"


def dislike():
    return "👎 प्रतिक्रिया दर्ज हुई"


def more():
    return "⋯ विकल्प"


# =========================================================
# CSS
# =========================================================

css = r"""
/* =========================================
   MAIN APP
========================================= */

body {
    background: #ffffff !important;
}

.gradio-container {
    max-width: 900px !important;
    margin: auto !important;
    padding-bottom: 95px !important;
}

/* =========================================
   HEADER
========================================= */

#nexora-header {
    text-align: center;
    padding: 10px 0 4px 0;
}

#nexora-title {
    font-size: 27px;
    font-weight: 700;
}

#nexora-subtitle {
    font-size: 14px;
    opacity: 0.65;
}

/* =========================================
   SPEAKER BAR
========================================= */

#speaker-container {
    position: sticky;
    top: 0;
    z-index: 50;
}

#speaker-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    margin: 5px 0 10px 0;
    border-radius: 14px;
    background: #f1f3f4;
}

#speaker-title {
    flex: 1;
    font-weight: 600;
}

#speaker-bar button {
    border: none;
    border-radius: 10px;
    padding: 7px 10px;
    cursor: pointer;
    background: #ffffff;
    font-size: 17px;
}

/* =========================================
   CHAT AREA
========================================= */

#chat-container {
    height: calc(100vh - 235px);
    min-height: 390px;
    overflow-y: auto;
    padding: 10px 5px 120px 5px;
    scroll-behavior: smooth;
}

.message-block {
    margin-bottom: 22px;
}

.message-label {
    font-size: 13px;
    font-weight: 600;
    opacity: 0.65;
    margin-bottom: 5px;
}

.user-message {
    margin-bottom: 13px;
}

.user-bubble {
    background: #f1f3f4;
    border-radius: 16px;
    padding: 11px 14px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.ai-bubble {
    padding: 2px 3px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.55;
}

/* =========================================
   ANSWER BUTTONS
========================================= */

.answer-actions {
    display: flex;
    gap: 5px;
    margin-top: 8px;
    flex-wrap: wrap;
}

.answer-btn {
    border: none;
    background: transparent;
    padding: 6px 8px;
    border-radius: 9px;
    cursor: pointer;
    font-size: 17px;
}

.answer-btn:hover {
    background: #f1f3f4;
}

/* =========================================
   INPUT AREA
========================================= */

#input-area {
    position: fixed;
    left: 50%;
    bottom: 8px;
    transform: translateX(-50%);
    width: min(880px, calc(100% - 18px));
    z-index: 100;
    background: rgba(255,255,255,0.97);
    padding: 8px;
    border-radius: 18px;
    box-shadow: 0 2px 18px rgba(0,0,0,0.12);
}

#question-box textarea {
    border-radius: 15px !important;
    padding: 13px 50px 13px 14px !important;
    min-height: 48px !important;
    max-height: 130px !important;
}

#mic-button button {
    border-radius: 13px !important;
    min-width: 50px !important;
    height: 48px !important;
    font-size: 21px !important;
}

#send-button button {
    border-radius: 13px !important;
    min-width: 52px !important;
    height: 48px !important;
    font-size: 20px !important;
}

/* =========================================
   MOBILE
========================================= */

@media (max-width: 600px) {

    .gradio-container {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }

    #nexora-title {
        font-size: 23px;
    }

    #chat-container {
        height: calc(100vh - 210px);
        padding-bottom: 115px;
    }

    #input-area {
        width: calc(100% - 12px);
        bottom: 5px;
    }

    .answer-btn {
        font-size: 16px;
        padding: 5px 7px;
    }
}
"""


# =========================================================
# JAVASCRIPT
# =========================================================

js = r"""
() => {

    // -----------------------------------------
    // AUTO SCROLL
    // -----------------------------------------

    function scrollChat() {
        const box = document.querySelector("#chat-container");

        if (box) {
            setTimeout(() => {
                box.scrollTop = box.scrollHeight;
            }, 150);
        }
    }

    scrollChat();


    // -----------------------------------------
    // SPEECH RECOGNITION / MIC
    // -----------------------------------------

    let recognition = null;
    let listening = false;

    function startMic() {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            alert("इस ब्राउज़र में माइक्रोफोन सुविधा उपलब्ध नहीं है।");
            return;
        }

        if (listening && recognition) {
            recognition.stop();
            return;
        }

        recognition = new SpeechRecognition();

        recognition.lang = "hi-IN";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            listening = true;

            const btn =
                document.querySelector("#mic-button button");

            if (btn) {
                btn.innerText = "🛑";
            }
        };

        recognition.onresult = (event) => {

            const text =
                event.results[0][0].transcript;

            const textarea =
                document.querySelector("#question-box textarea");

            if (textarea) {

                textarea.value = text;

                textarea.dispatchEvent(
                    new Event("input", {bubbles: true})
                );

                textarea.dispatchEvent(
                    new Event("change", {bubbles: true})
                );
            }
        };

        recognition.onerror = () => {
            listening = false;

            const btn =
                document.querySelector("#mic-button button");

            if (btn) {
                btn.innerText = "🎤";
            }
        };

        recognition.onend = () => {
            listening = false;

            const btn =
                document.querySelector("#mic-button button");

            if (btn) {
                btn.innerText = "🎤";
            }
        };

        recognition.start();
    }


    // -----------------------------------------
    // MIC BUTTON
    // -----------------------------------------

    document.addEventListener("click", (event) => {

        const mic =
            event.target.closest("#mic-button button");

        if (mic) {
            startMic();
        }
    });


    // -----------------------------------------
    // ANSWER BUTTONS
    // -----------------------------------------

    document.addEventListener("click", (event) => {

        const button =
            event.target.closest(".answer-btn");

        if (!button) {
            return;
        }

        // LIKE
        if (button.classList.contains("like-btn")) {
            button.innerText = "👍✓";
            return;
        }

        // DISLIKE
        if (button.classList.contains("dislike-btn")) {
            button.innerText = "👎✓";
            return;
        }

        // MORE
        if (button.classList.contains("more-btn")) {
            alert("Nexora AI के और विकल्प जल्द जोड़े जाएंगे।");
            return;
        }

        // COPY
        if (button.classList.contains("copy-btn")) {

            const text =
                button.getAttribute("data-answer");

            if (text) {
                navigator.clipboard.writeText(text);
                button.innerText = "✓";
                setTimeout(() => {
                    button.innerText = "📋";
                }, 1200);
            }

            return;
        }

        // SHARE
        if (button.classList.contains("share-btn")) {

            const text =
                button.getAttribute("data-answer");

            if (navigator.share) {

                navigator.share({
                    title: "Nexora AI",
                    text: text || "Nexora AI"
                });

            } else {

                navigator.clipboard.writeText(text || "");

                button.innerText = "✓";

                setTimeout(() => {
                    button.innerText = "↗️";
                }, 1200);
            }

            return;
        }

        // SPEAK
        if (button.classList.contains("speak-btn")) {

            const text =
                button.getAttribute("data-answer");

            if (text) {

                speechSynthesis.cancel();

                const speech =
                    new SpeechSynthesisUtterance(text);

                speech.lang = "hi-IN";
                speech.rate = 0.9;

                speechSynthesis.speak(speech);
            }

            return;
        }

    });


    // -----------------------------------------
    // TOP SPEAKER BAR
    // -----------------------------------------

    document.addEventListener("click", (event) => {

        if (event.target.closest("#pause-speech")) {

            if (speechSynthesis.speaking) {

                if (speechSynthesis.paused) {
                    speechSynthesis.resume();
                } else {
                    speechSynthesis.pause();
                }

            }

            return;
        }


        if (event.target.closest("#stop-speech")) {

            speechSynthesis.cancel();

            return;
        }


        if (event.target.closest("#close-speaker")) {

            const bar =
                document.querySelector("#speaker-bar");

            if (bar) {
                bar.remove();
            }

            speechSynthesis.cancel();

            return;
        }

    });


    // -----------------------------------------
    // OBSERVE CHAT CHANGES
    // -----------------------------------------

    const observer = new MutationObserver(() => {
        scrollChat();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

}
"""


# =========================================================
# GRADIO UI
# =========================================================

with gr.Blocks(title="Nexora AI") as app:

    gr.HTML("""
    <div id="nexora-header">
        <div id="nexora-title">🤖 Nexora AI</div>
        <div id="nexora-subtitle">
            अपनी भाषा में सवाल पूछिए
        </div>
    </div>
    """)

    # Speaker area
    speaker_container = gr.HTML(
        "",
        elem_id="speaker-container"
    )

    # Chat history
    history_state = gr.State([])

    history_display = gr.HTML(
        """
        <div id="chat-container">
            <div style="text-align:center; opacity:0.55; padding:50px 10px;">
                💬 Nexora AI से बातचीत शुरू करें
            </div>
        </div>
        """
    )

    # Status
    status = gr.Markdown("")

    # -----------------------------------------
    # FIXED INPUT
    # -----------------------------------------

    with gr.Row(elem_id="input-area"):

        question = gr.Textbox(
            placeholder="💬 अपना सवाल लिखें...",
            show_label=False,
            lines=1,
            max_lines=5,
            elem_id="question-box",
            autofocus=True
        )

        mic_button = gr.Button(
            "🎤",
            elem_id="mic-button"
        )

        send = gr.Button(
            "➤",
            variant="primary",
            elem_id="send-button"
        )


    # -----------------------------------------
    # SEND
    # -----------------------------------------

    send.click(
        nexora_ai,
        inputs=[question, history_state],
        outputs=[
            history_state,
            question,
            history_display,
            speaker_container
        ]
    )

    # Enter key से भी सवाल भेजें
    question.submit(
        nexora_ai,
        inputs=[question, history_state],
        outputs=[
            history_state,
            question,
            history_display,
            speaker_container
        ]
    )

    # -----------------------------------------
    # STATUS
    # -----------------------------------------

    like_button = gr.Button(
        "👍",
        visible=False
    )

    dislike_button = gr.Button(
        "👎",
        visible=False
    )

    more_button = gr.Button(
        "⋯",
        visible=False
    )


# =========================================================
# LAUNCH
# =========================================================

app.launch(
    server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"),
    server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
    css=css,
    js=js
)
