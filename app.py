import os
import html
import json
import uuid
import gradio as gr
from google import genai

# ============================================================
# NEXORA AI
# Single-file ChatGPT-style interface
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=API_KEY)

DEFAULT_MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = """
You are Nexora AI.

Rules:
- Answer clearly and directly.
- If the user asks in Hindi, answer in Hindi Devanagari unless another style is requested.
- If the user asks in English, answer in English.
- Do not invent facts.
- Keep answers useful and reasonably concise.
- For code requests, provide complete and clean code.
"""


# ============================================================
# CSS
# ============================================================

CSS = r"""
* {
    box-sizing: border-box;
}

html,
body,
.gradio-container {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    overflow: hidden !important;
    font-family: Arial, Helvetica, sans-serif !important;
}

.gradio-container {
    max-width: none !important;
    background: #ffffff !important;
}

#app {
    width: 100%;
    height: 100vh;
    display: flex;
    background: #ffffff;
    color: #202123;
}

/* ================= SIDEBAR ================= */

#sidebar {
    width: 270px;
    height: 100vh;
    flex-shrink: 0;
    background: #f7f7f8;
    border-right: 1px solid #e5e5e5;
    display: flex;
    flex-direction: column;
    z-index: 100;
}

#new-chat-area {
    padding: 12px;
}

#new-chat-button {
    width: 100%;
    height: 44px;
    border: 1px solid #d9d9e3;
    border-radius: 10px;
    background: #ffffff;
    color: #202123;
    cursor: pointer;
    font-size: 14px;
}

#new-chat-button:hover {
    background: #ececf1;
}

.sidebar-title {
    padding: 12px 16px 7px;
    color: #8e8ea0;
    font-size: 12px;
    font-weight: 600;
}

#history-list {
    flex: 1;
    overflow-y: auto;
    padding: 4px 8px;
}

.history-item {
    padding: 10px;
    margin-bottom: 2px;
    border-radius: 8px;
    font-size: 13px;
    color: #343541;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.history-item:hover {
    background: #ececf1;
}

#sidebar-tools {
    border-top: 1px solid #e5e5e5;
    padding: 8px;
}

.sidebar-tool {
    width: 100%;
    text-align: left;
    border: 0;
    background: transparent;
    padding: 10px;
    border-radius: 8px;
    cursor: pointer;
    color: #343541;
}

.sidebar-tool:hover {
    background: #ececf1;
}

#profile {
    border-top: 1px solid #e5e5e5;
    padding: 12px;
}

.profile-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.profile-avatar {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: #111827;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

.profile-name {
    font-size: 14px;
    font-weight: 600;
}

/* ================= MAIN ================= */

#main {
    flex: 1;
    min-width: 0;
    height: 100vh;
    position: relative;
    background: #ffffff;
}

/* ================= TOP BAR ================= */

#topbar {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 58px;
    border-bottom: 1px solid #eeeeee;
    background: rgba(255, 255, 255, 0.96);
    display: flex;
    align-items: center;
    padding: 0 15px;
    gap: 9px;
    z-index: 20;
}

#menu-button {
    width: 38px !important;
    min-width: 38px !important;
    height: 38px !important;
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    color: #343541 !important;
    box-shadow: none !important;
}

#menu-button:hover {
    background: #f1f1f1 !important;
}

.nexora-logo-small {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: #111827;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}

.nexora-name {
    font-weight: 600;
    font-size: 16px;
}

/* ================= CHAT ================= */

#chat-scroll {
    position: absolute;
    top: 58px;
    left: 0;
    right: 0;
    bottom: 125px;
    overflow-y: auto;
    overflow-x: hidden;
}

#chat-content {
    width: 100%;
    max-width: 900px;
    margin: auto;
    padding: 20px 20px 40px;
}

/* ================= HOME ================= */

.home {
    min-height: calc(100vh - 205px);
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 25px 10px;
}

.home-inner {
    width: 100%;
    max-width: 760px;
}

.home-logo {
    width: 62px;
    height: 62px;
    border-radius: 17px;
    margin: 0 auto 18px;
    background: #111827;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 29px;
    font-weight: 800;
}

.home h1 {
    margin: 0;
    font-size: 32px;
    font-weight: 600;
}

.home-subtitle {
    margin: 10px 0 28px;
    color: #6e6e80;
    font-size: 16px;
}

.suggestion-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    text-align: left;
}

.suggestion {
    border: 1px solid #e5e5e5;
    border-radius: 12px;
    padding: 15px;
    cursor: pointer;
    background: #ffffff;
}

.suggestion:hover {
    background: #f7f7f8;
}

/* ================= MESSAGE ================= */

.message {
    display: flex;
    gap: 13px;
    padding: 22px 0;
}

.message.assistant {
    margin-left: -20px;
    margin-right: -20px;
    padding-left: 20px;
    padding-right: 20px;
    background: #f7f7f8;
}

.avatar {
    width: 32px;
    height: 32px;
    min-width: 32px;
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 700;
}

.avatar-user {
    background: #ececf1;
    color: #343541;
}

.avatar-ai {
    background: #111827;
    color: white;
}

.message-body {
    flex: 1;
    min-width: 0;
}

.message-name {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 7px;
}

.message-text {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.65;
    font-size: 15px;
    color: #343541;
}

/* ================= SIX ANSWER BUTTONS ================= */

.answer-actions {
    display: flex;
    align-items: center;
    gap: 3px;
    margin-top: 11px;
    flex-wrap: wrap;
}

.answer-actions button {
    border: 0;
    background: transparent;
    color: #8e8ea0;
    border-radius: 7px;
    padding: 6px 8px;
    cursor: pointer;
}

.answer-actions button:hover {
    background: #e9e9ee;
    color: #343541;
}

.action-status {
    color: #6e6e80;
    font-size: 12px;
}

/* ================= COMPOSER ================= */

#composer {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 125px;
    padding: 14px 20px;
    background: linear-gradient(
        to top,
        #ffffff 75%,
        rgba(255,255,255,0.92)
    );
    z-index: 30;
}

#composer-inner {
    max-width: 850px;
    margin: auto;
}

#message-input textarea {
    border: 1px solid #d9d9e3 !important;
    border-radius: 14px !important;
    padding: 14px 100px 14px 16px !important;
    font-size: 15px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
}

#composer-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 6px;
    margin-top: -47px;
    margin-right: 8px;
    position: relative;
    z-index: 10;
}

#send-button button,
#mic-button button {
    width: 36px !important;
    min-width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    border-radius: 9px !important;
}

#send-button button {
    background: #111827 !important;
    color: white !important;
}

#mic-button button {
    background: #eeeeef !important;
}

.composer-note {
    text-align: center;
    color: #999;
    font-size: 11px;
    margin-top: 8px;
}

/* ================= MODEL MENU ================= */

#model-selector {
    position: absolute;
    top: 62px;
    left: 55px;
    width: 220px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    padding: 7px;
    display: none;
    z-index: 80;
}

.model-option {
    padding: 10px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
}

.model-option:hover {
    background: #f1f1f1;
}

/* ================= MOBILE ================= */

@media (max-width: 700px) {

    #sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        transform: translateX(-100%);
        transition: transform .2s ease;
        box-shadow: 5px 0 25px rgba(0,0,0,.15);
    }

    #sidebar.open {
        transform: translateX(0);
    }

    #chat-content {
        padding-left: 14px;
        padding-right: 14px;
    }

    .message.assistant {
        margin-left: -14px;
        margin-right: -14px;
        padding-left: 14px;
        padding-right: 14px;
    }

    .suggestion-grid {
        grid-template-columns: 1fr;
    }

    .home h1 {
        font-size: 28px;
    }

    #composer {
        padding-left: 10px;
        padding-right: 10px;
    }
}
"""


# ============================================================
# HTML HELPERS
# ============================================================

def esc(value):
    return html.escape(str(value))


def home_html():
    return """
    <div class="home">
        <div class="home-inner">

            <div class="home-logo">N</div>

            <h1>Nexora AI</h1>

            <div class="home-subtitle">
                मुझसे कुछ भी पूछिए
            </div>

            <div class="suggestion-grid">

                <div class="suggestion"
                     onclick="setSuggestion('भारत की राजधानी क्या है?')">
                    भारत की राजधानी क्या है?
                </div>

                <div class="suggestion"
                     onclick="setSuggestion('एक छोटी और रोचक कहानी सुनाइए')">
                    एक छोटी और रोचक कहानी सुनाइए
                </div>

                <div class="suggestion"
                     onclick="setSuggestion('मैं Python सीखना चाहता हूँ, शुरुआत कैसे करूँ?')">
                    Python सीखना कैसे शुरू करूँ?
                </div>

                <div class="suggestion"
                     onclick="setSuggestion('मेरे लिए एक आसान daily productivity plan बनाइए')">
                    Daily productivity plan बनाइए
                </div>

            </div>
        </div>
    </div>
    """


def message_html(role, text):
    safe = esc(text)

    if role == "user":
        return f"""
        <div class="message user">
            <div class="avatar avatar-user">U</div>

            <div class="message-body">
                <div class="message-name">आप</div>
                <div class="message-text">{safe}</div>
            </div>
        </div>
        """

    return f"""
    <div class="message assistant">

        <div class="avatar avatar-ai">
            N
        </div>

        <div class="message-body">

            <div class="message-name">
                Nexora AI
            </div>

            <div class="message-text answer-text">
                {safe}
            </div>

            <div class="answer-actions">

                <button onclick="answerAction(this,'copy')"
                        title="Copy">
                    📋
                </button>

                <button onclick="answerAction(this,'like')"
                        title="Like">
                    👍
                </button>

                <button onclick="answerAction(this,'dislike')"
                        title="Dislike">
                    👎
                </button>

                <button onclick="answerAction(this,'sound')"
                        title="Read aloud">
                    🔊
                </button>

                <button onclick="answerAction(this,'share')"
                        title="Share">
                    ↗
                </button>

                <button onclick="answerAction(this,'more')"
                        title="More">
                    ⋯
                </button>

                <span class="action-status"></span>

            </div>

        </div>
    </div>
    """


def chat_html(history):
    if not history:
        return home_html()

    parts = []

    for item in history:
        parts.append(
            message_html(
                item["role"],
                item["content"]
            )
        )

    return "".join(parts)


def history_html(history):
    items = []

    for item in history:
        if item["role"] == "user":
            title = item["content"].strip()

            if title:
                title = title[:50]

                if len(item["content"]) > 50:
                    title += "..."

                items.append(
                    f'<div class="history-item">{esc(title)}</div>'
                )

    if not items:
        return '<div class="history-item">अभी कोई चैट नहीं है।</div>'

    return "".join(items)


# ============================================================
# MODEL
# ============================================================

def build_prompt(history, question):
    conversation = []

    for item in history[-12:]:
        role = item["role"]
        text = item["content"]

        if role == "user":
            conversation.append(
                "User: " + text
            )
        else:
            conversation.append(
                "Assistant: " + text
            )

    previous = "\n".join(conversation)

    return f"""
{SYSTEM_PROMPT}

Previous conversation:
{previous}

Latest user message:
{question}

Answer the latest user message directly.
"""


def ask_nexora(message, history, model):
    message = (message or "").strip()
    history = list(history or [])

    if not message:
        yield (
            chat_html(history),
            history,
            history_html(history),
            ""
        )
        return

    history.append(
        {
            "role": "user",
            "content": message
        }
    )

    yield (
        chat_html(history),
        history,
        history_html(history),
        ""
    )

    prompt = build_prompt(
        history[:-1],
        message
    )

    answer = ""

    try:

        stream = client.models.generate_content_stream(
            model=model,
            contents=prompt
        )

        for chunk in stream:

            chunk_text = getattr(
                chunk,
                "text",
                None
            )

            if chunk_text:

                answer += chunk_text

                temporary = list(history)

                temporary.append(
                    {
                        "role": "assistant",
                        "content": answer + "▌"
                    }
                )

                yield (
                    chat_html(temporary),
                    history,
                    history_html(history),
                    ""
                )

    except Exception:

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            answer = (
                getattr(response, "text", "")
                or ""
            )

        except Exception:

            answer = (
                "⚠️ उत्तर देने में समस्या हुई। "
                "कृपया कुछ देर बाद फिर कोशिश करें।"
            )

    if not answer:
        answer = "⚠️ कोई उत्तर प्राप्त नहीं हुआ।"

    history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    yield (
        chat_html(history),
        history,
        history_html(history),
        ""
    )


# ============================================================
# NEW CHAT
# ============================================================

def new_chat():
    return (
        home_html(),
        [],
        history_html([]),
        ""
    )


# ============================================================
# SIMPLE OPTION ACTIONS
# ============================================================

def option_message(name):
    return f"{name} option चुना गया।"


# ============================================================
# JAVASCRIPT
# ============================================================

JS = r"""
function getInput() {
    return document.querySelector("#message-input textarea");
}

function setSuggestion(text) {

    const input = getInput();

    if (!input) {
        return;
    }

    input.value = text;

    input.dispatchEvent(
        new Event("input", {
            bubbles: true
        })
    );

    input.focus();
}

window.setSuggestion = setSuggestion;


function scrollChat() {

    const box = document.querySelector("#chat-scroll");

    if (box) {
        box.scrollTop = box.scrollHeight;
    }
}


function setupEnter() {

    const input = getInput();

    if (!input || input.dataset.ready === "1") {
        return;
    }

    input.dataset.ready = "1";

    input.addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                const button =
                    document.querySelector(
                        "#send-button button"
                    );

                if (button) {
                    button.click();
                }
            }
        }
    );
}


window.answerAction = async function(
    button,
    action
) {

    const body =
        button.closest(".message-body");

    if (!body) {
        return;
    }

    const answer =
        body.querySelector(".answer-text");

    const status =
        body.querySelector(".action-status");

    if (!answer) {
        return;
    }

    const text =
        answer.innerText.trim();


    if (action === "copy") {

        try {

            await navigator.clipboard.writeText(text);

            status.textContent =
                " कॉपी हो गया";

        } catch (error) {

            status.textContent =
                " कॉपी नहीं हुआ";
        }
    }


    else if (action === "like") {

        status.textContent =
            " धन्यवाद";
    }


    else if (action === "dislike") {

        status.textContent =
            " Feedback दर्ज";
    }


    else if (action === "sound") {

        if ("speechSynthesis" in window) {

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(text);

            speech.lang = "hi-IN";
            speech.rate = 0.92;

            window.speechSynthesis.speak(speech);

            status.textContent =
                " पढ़ रहा हूँ";
        }
    }


    else if (action === "share") {

        if (navigator.share) {

            try {

                await navigator.share({
                    title: "Nexora AI",
                    text: text
                });

            } catch (error) {
                // User cancelled.
            }

        } else {

            try {

                await navigator.clipboard.writeText(text);

                status.textContent =
                    " कॉपी हो गया";

            } catch (error) {

                status.textContent =
                    " Share उपलब्ध नहीं";
            }
        }
    }


    else if (action === "more") {

        status.textContent =
            " More options";
    }


    setTimeout(
        function() {
            status.textContent = "";
        },
        1800
    );
};


function setupMic() {

    const button =
        document.querySelector(
            "#mic-button button"
        );

    if (!button || button.dataset.ready === "1") {
        return;
    }

    button.dataset.ready = "1";


    const Recognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!Recognition) {
        button.style.display = "none";
        return;
    }


    const recognition =
        new Recognition();

    recognition.lang = "hi-IN";
    recognition.continuous = false;
    recognition.interimResults = true;


    button.addEventListener(
        "click",
        function() {

            try {
                recognition.start();
            } catch (error) {
                // Already running.
            }
        }
    );


    recognition.onresult =
        function(event) {

            let text = "";

            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                text +=
                    event.results[i][0].transcript;
            }

            setSuggestion(text);
        };
}


function setupMenu() {

    const button =
        document.querySelector(
            "#menu-button button"
        );

    const sidebar =
        document.querySelector(
            "#sidebar"
        );

    if (
        !button ||
        !sidebar ||
        button.dataset.ready === "1"
    ) {
        return;
    }

    button.dataset.ready = "1";

    button.addEventListener(
        "click",
        function() {

            sidebar.classList.toggle(
                "open"
            );
        }
    );
}


function setupNewChat() {

    const customButton =
        document.querySelector(
            "#new-chat-button"
        );

    const realButton =
        document.querySelector(
            "#hidden-new-chat button"
        );

    if (
        !customButton ||
        !realButton ||
        customButton.dataset.ready === "1"
    ) {
        return;
    }

    customButton.dataset.ready = "1";

    customButton.addEventListener(
        "click",
        function() {
            realButton.click();
        }
    );
}


function watchChat() {

    const target =
        document.querySelector(
            "#chat-content"
        );

    if (!target || target.dataset.ready === "1") {
        return;
    }

    target.dataset.ready = "1";

    const observer =
        new MutationObserver(
            function() {

                scrollChat();
                setupEnter();
                setupMic();
                setupMenu();
                setupNewChat();
            }
        );

    observer.observe(
        target,
        {
            childList: true,
            subtree: true,
            characterData: true
        }
    );
}


function setupAll() {

    setupEnter();
    setupMic();
    setupMenu();
    setupNewChat();
    watchChat();
    scrollChat();
}


setInterval(
    setupAll,
    500
);


window.addEventListener(
    "load",
    function() {

        setTimeout(
            setupAll,
            300
        );

        setTimeout(
            setupAll,
            1000
        );
    }
);
"""


# ============================================================
# GRADIO APP
# ============================================================

with gr.Blocks(
    title="Nexora AI",
    css=CSS,
    js=JS
) as demo:

    history_state = gr.State([])


    with gr.Row(
        elem_id="app"
    ):


        # ====================================================
        # SIDEBAR
        # ====================================================

        with gr.Column(
            elem_id="sidebar",
            scale=0,
            min_width=270
        ):

            gr.HTML(
                """
                <div id="new-chat-area">

                    <button id="new-chat-button">
                        ＋ New chat
                    </button>

                </div>

                <div class="sidebar-title">
                    Chat History
                </div>
                """
            )

            history_view = gr.HTML(
                value=history_html([]),
                elem_id="history-list"
            )


            gr.HTML(
                """
                <div id="sidebar-tools">

                    <button class="sidebar-tool">
                        🔎 Search chats
                    </button>

                    <button class="sidebar-tool">
                        📌 Pinned chats
                    </button>

                    <button class="sidebar-tool">
                        🗂️ Archived chats
                    </button>

                    <button class="sidebar-tool">
                        ⚙️ Settings
                    </button>

                </div>

                <div id="profile">

                    <div class="profile-row">

                        <div class="profile-avatar">
                            N
                        </div>

                        <div class="profile-name">
                            Nexora AI
                        </div>

                    </div>

                </div>
                """
            )


        # ====================================================
        # MAIN
        # ====================================================

        with gr.Column(
            elem_id="main",
            scale=1
        ):

            gr.HTML(
                """
                <div id="topbar">

                    <button id="menu-button">
                        ☰
                    </button>

                    <div class="nexora-logo-small">
                        N
                    </div>

                    <div class="nexora-name">
                        Nexora AI
                    </div>

                </div>

                <div id="model-selector">

                    <div class="model-option">
                        ⚡ Fast Model
                    </div>

                    <div class="model-option">
                        🧠 Reasoning Model
                    </div>

                    <div class="model-option">
                        🎨 Image Model
                    </div>

                </div>
                """)


            with gr.Column(
                elem_id="chat-scroll"
            ):

                chat_view = gr.HTML(
                    value=home_html(),
                    elem_id="chat-content"
                )


            # =================================================
            # COMPOSER
            # =================================================

            with gr.Column(
                elem_id="composer"
            ):

                with gr.Column(
                    elem_id="composer-inner"
                ):

                    model_dropdown = gr.Dropdown(
                        choices=[
                            (
                                "⚡ Fast — Gemini 3.8 Flash",
                                "gemini-3.8-flash"
                            ),
                            (
                                "🪶 Lite — Gemini 3.5 Flash-Lite",
                                "gemini-3.5-flash-lite"
                            )
                        ],
                        value=DEFAULT_MODEL,
                        show_label=False,
                        container=False,
                        visible=False
                    )


                    message_input = gr.Textbox(
                        placeholder=(
                            "Nexora AI से कुछ भी पूछें..."
                        ),
                        show_label=False,
                        lines=1,
                        max_lines=7,
                        elem_id="message-input",
                        container=False
                    )


                    with gr.Row(
                        elem_id="composer-buttons"
                    ):

                        mic_button = gr.Button(
                            "🎙️",
                            elem_id="mic-button",
                            size="sm"
                        )

                        send_button = gr.Button(
                            "➤",
                            elem_id="send-button",
                            variant="primary",
                            size="sm"
                        )


                    gr.HTML(
                        """
                        <div class="composer-note">
                            Nexora AI गलतियाँ कर सकता है।
                            महत्वपूर्ण जानकारी जाँच लें।
                        </div>
                        """
                    )


    # ========================================================
    # HIDDEN NEW CHAT BUTTON
    # ========================================================

    hidden_new_chat = gr.Button(
        "New Chat",
        elem_id="hidden-new-chat",
        visible=False
    )


    # ========================================================
    # SEND
    # ========================================================

    send_event = send_button.click(
        fn=ask_nexora,
        inputs=[
            message_input,
            history_state,
            model_dropdown
        ],
        outputs=[
            chat_view,
            history_state,
            history_view,
            message_input
        ]
    )


    message_input.submit(
        fn=ask_nexora,
        inputs=[
            message_input,
            history_state,
            model_dropdown
        ],
        outputs=[
            chat_view,
            history_state,
            history_view,
            message_input
        ]
    )


    # ========================================================
    # NEW CHAT
    # ========================================================

    hidden_new_chat.click(
        fn=new_chat,
        inputs=None,
        outputs=[
            chat_view,
            history_state,
            history_view,
            message_input
        ]
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "7860"
        )
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=port
)
      
