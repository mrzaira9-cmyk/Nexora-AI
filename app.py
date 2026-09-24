import os
import html
import gradio as gr
from google import genai

# ============================================================
# NEXORA AI — SINGLE FILE APP
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

TEXT_MODEL = "gemini-3.5-flash-lite"

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
तुम Nexora AI हो।

नियम:
1. यूज़र हिंदी में पूछे तो हिंदी देवनागरी में उत्तर दो।
2. यूज़र अंग्रेज़ी में पूछे तो अंग्रेज़ी में उत्तर दो।
3. बिना जरूरत Roman Hindi या Hinglish मत लिखो।
4. सीधे और साफ उत्तर दो।
5. तथ्यात्मक सवालों में सही और स्पष्ट जानकारी दो।
6. बहुत लंबी भूमिका मत दो।
7. कोड मांगा जाए तो पूरा और साफ code दो।
"""


# ============================================================
# HTML / CSS
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

body {
    background: #ffffff !important;
}

.gradio-container {
    max-width: none !important;
    background: #ffffff !important;
}

/* Remove Gradio default spacing */
#app-root {
    width: 100%;
    height: 100vh;
}

/* =========================================================
   APP
   ========================================================= */

#nexora-app {
    width: 100%;
    height: 100vh;
    display: flex;
    background: #ffffff;
    color: #202123;
}

/* =========================================================
   SIDEBAR
   ========================================================= */

#sidebar {
    width: 260px;
    height: 100vh;
    background: #f7f7f8;
    border-right: 1px solid #e5e5e5;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    transition: width 0.2s ease, transform 0.2s ease;
    z-index: 50;
}

#sidebar-header {
    height: 64px;
    padding: 12px;
    display: flex;
    align-items: center;
}

#new-chat-btn {
    width: 100%;
    height: 42px;
    border: 1px solid #d9d9e3;
    border-radius: 10px;
    background: #ffffff;
    color: #202123;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 0 14px;
    gap: 10px;
}

#new-chat-btn:hover {
    background: #ececf1;
}

.new-icon {
    font-size: 20px;
    line-height: 1;
}

#sidebar-history-title {
    padding: 12px 16px 8px;
    font-size: 12px;
    font-weight: 600;
    color: #8e8ea0;
}

#history-list {
    flex: 1;
    overflow-y: auto;
    padding: 4px 8px;
}

.history-empty {
    color: #8e8ea0;
    font-size: 13px;
    padding: 14px 10px;
}

.history-item {
    width: 100%;
    border: 0;
    background: transparent;
    padding: 10px;
    border-radius: 8px;
    text-align: left;
    color: #343541;
    font-size: 13px;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.history-item:hover {
    background: #ececf1;
}

#sidebar-bottom {
    border-top: 1px solid #e5e5e5;
    padding: 10px;
}

.profile-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px;
}

.profile-avatar {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #111827;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

.profile-name {
    font-size: 14px;
    font-weight: 600;
}

/* =========================================================
   MAIN
   ========================================================= */

#main-area {
    flex: 1;
    min-width: 0;
    height: 100vh;
    position: relative;
    display: flex;
    flex-direction: column;
    background: #ffffff;
}

/* =========================================================
   TOPBAR
   ========================================================= */

#topbar {
    height: 58px;
    min-height: 58px;
    border-bottom: 1px solid #eeeeee;
    display: flex;
    align-items: center;
    padding: 0 18px;
    background: rgba(255,255,255,0.96);
    z-index: 20;
}

#menu-btn {
    width: 38px !important;
    min-width: 38px !important;
    height: 38px !important;
    border: 0 !important;
    border-radius: 8px !important;
    background: transparent !important;
    color: #343541 !important;
    font-size: 20px !important;
    cursor: pointer !important;
    padding: 0 !important;
    box-shadow: none !important;
}

#menu-btn:hover {
    background: #f1f1f1 !important;
}

#brand-area {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-left: 7px;
}

.brand-logo {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: #111827;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
}

.brand-name {
    font-size: 16px;
    font-weight: 600;
    color: #202123;
}

/* =========================================================
   CHAT AREA
   ========================================================= */

#chat-wrap {
    position: absolute;
    top: 58px;
    left: 0;
    right: 0;
    bottom: 120px;
    overflow-y: auto;
    overflow-x: hidden;
    scroll-behavior: smooth;
}

#chat-content {
    width: 100%;
    min-height: 100%;
    padding-bottom: 30px;
}

/* =========================================================
   HOME SCREEN
   ========================================================= */

#home-screen {
    width: 100%;
    min-height: calc(100vh - 178px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 35px 20px 40px;
}

.home-inner {
    width: 100%;
    max-width: 760px;
    text-align: center;
}

.home-logo {
    width: 58px;
    height: 58px;
    border-radius: 16px;
    margin: 0 auto 18px;
    background: #111827;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 800;
}

.home-title {
    margin: 0;
    font-size: 32px;
    line-height: 1.2;
    font-weight: 600;
    color: #202123;
}

.home-subtitle {
    margin: 10px 0 28px;
    color: #6e6e80;
    font-size: 16px;
}

.suggestions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    text-align: left;
}

.suggestion {
    border: 1px solid #e5e5e5;
    background: #ffffff;
    border-radius: 12px;
    padding: 14px;
    cursor: pointer;
    transition: background 0.15s ease, border 0.15s ease;
}

.suggestion:hover {
    background: #f7f7f8;
    border-color: #d5d5d5;
}

.suggestion-title {
    font-size: 14px;
    color: #343541;
    font-weight: 500;
}

/* =========================================================
   MESSAGES
   ========================================================= */

.message-row {
    width: 100%;
    padding: 24px 20px;
}

.message-row.user {
    background: #ffffff;
}

.message-row.assistant {
    background: #f7f7f8;
}

.message-inner {
    max-width: 820px;
    margin: 0 auto;
    display: flex;
    gap: 15px;
}

.message-avatar {
    width: 32px;
    min-width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
}

.user-avatar {
    background: #ececf1;
    color: #343541;
}

.ai-avatar {
    background: #111827;
    color: #ffffff;
}

.message-body {
    flex: 1;
    min-width: 0;
}

.message-name {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #343541;
}

.message-text {
    font-size: 15px;
    line-height: 1.65;
    color: #343541;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

/* =========================================================
   SIX ACTION BUTTONS
   ========================================================= */

.answer-actions {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 13px;
    flex-wrap: wrap;
}

.answer-action {
    border: 0;
    background: transparent;
    color: #8e8ea0;
    border-radius: 7px;
    min-width: 32px;
    height: 30px;
    padding: 0 7px;
    cursor: pointer;
    font-size: 14px;
}

.answer-action:hover {
    background: #e9e9ee;
    color: #343541;
}

.action-status {
    display: inline-block;
    margin-left: 5px;
    color: #6e6e80;
    font-size: 12px;
}

/* =========================================================
   COMPOSER
   ========================================================= */

#composer {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    min-height: 120px;
    background: linear-gradient(
        to top,
        #ffffff 72%,
        rgba(255,255,255,0.95)
    );
    padding: 16px 20px 18px;
    z-index: 30;
}

#composer-inner {
    width: 100%;
    max-width: 820px;
    margin: 0 auto;
}

#input-box {
    width: 100%;
}

#input-box textarea {
    border: 1px solid #d9d9e3 !important;
    border-radius: 14px !important;
    background: #ffffff !important;
    color: #202123 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
    padding: 14px 52px 14px 16px !important;
    font-size: 15px !important;
    min-height: 58px !important;
    max-height: 160px !important;
}

#input-box textarea:focus {
    border-color: #b9b9c5 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
}

#composer-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 6px;
    margin-top: -48px;
    margin-right: 8px;
    position: relative;
    z-index: 5;
}

#send-btn,
#mic-btn {
    width: 36px !important;
    min-width: 36px !important;
    height: 36px !important;
    border-radius: 9px !important;
    border: 0 !important;
    padding: 0 !important;
    font-size: 17px !important;
    box-shadow: none !important;
}

#send-btn {
    background: #111827 !important;
    color: #ffffff !important;
}

#mic-btn {
    background: #f1f1f1 !important;
    color: #343541 !important;
}

#send-btn:hover {
    opacity: 0.88;
}

#mic-btn:hover {
    background: #e5e5e5 !important;
}

.composer-note {
    text-align: center;
    margin-top: 8px;
    color: #8e8ea0;
    font-size: 11px;
}

/* Hide Gradio button containers around our custom buttons */
#send-btn .wrap,
#mic-btn .wrap,
#menu-btn .wrap,
#new-chat-btn .wrap {
    border: 0 !important;
}

/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 700px) {

    #sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        transform: translateX(-100%);
        width: 270px;
        box-shadow: 5px 0 20px rgba(0,0,0,0.12);
    }

    #sidebar.open {
        transform: translateX(0);
    }

    #topbar {
        padding: 0 10px;
    }

    .brand-name {
        font-size: 15px;
    }

    #chat-wrap {
        bottom: 120px;
    }

    .message-row {
        padding: 20px 14px;
    }

    .message-inner {
        gap: 10px;
    }

    .message-avatar {
        width: 30px;
        min-width: 30px;
        height: 30px;
    }

    .message-text {
        font-size: 14px;
    }

    #composer {
        padding: 12px 10px 15px;
    }

    .suggestions {
        grid-template-columns: 1fr;
    }

    .home-title {
        font-size: 27px;
    }

    .home-subtitle {
        font-size: 14px;
    }

    #home-screen {
        padding-top: 20px;
    }
}
"""


# ============================================================
# HTML BUILDERS
# ============================================================

def escape_text(value):
    return html.escape(str(value))


def make_home_html():
    return """
    <div id="home-screen">
        <div class="home-inner">
            <div class="home-logo">N</div>

            <h1 class="home-title">Nexora AI</h1>

            <div class="home-subtitle">
                मुझसे कुछ भी पूछिए
            </div>

            <div class="suggestions">

                <div class="suggestion"
                     onclick="useSuggestion('भारत की राजधानी क्या है?')">
                    <div class="suggestion-title">
                        भारत की राजधानी क्या है?
                    </div>
                </div>

                <div class="suggestion"
                     onclick="useSuggestion('एक छोटी और रोचक कहानी सुनाइए')">
                    <div class="suggestion-title">
                        एक छोटी और रोचक कहानी सुनाइए
                    </div>
                </div>

                <div class="suggestion"
                     onclick="useSuggestion('मैं Python सीखना चाहता हूँ, शुरुआत कैसे करूँ?')">
                    <div class="suggestion-title">
                        Python सीखना कैसे शुरू करूँ?
                    </div>
                </div>

                <div class="suggestion"
                     onclick="useSuggestion('मेरे लिए एक आसान daily productivity plan बनाइए')">
                    <div class="suggestion-title">
                        Daily productivity plan बनाइए
                    </div>
                </div>

            </div>
        </div>
    </div>
    """


def make_message(role, content):
    safe_content = escape_text(content)

    if role == "user":
        return f"""
        <div class="message-row user">
            <div class="message-inner">
                <div class="message-avatar user-avatar">U</div>
                <div class="message-body">
                    <div class="message-name">आप</div>
                    <div class="message-text">{safe_content}</div>
                </div>
            </div>
        </div>
        """

    return f"""
    <div class="message-row assistant">
        <div class="message-inner">
            <div class="message-avatar ai-avatar">N</div>

            <div class="message-body">

                <div class="message-name">Nexora AI</div>

                <div class="message-text nexora-answer">
                    {safe_content}
                </div>

                <div class="answer-actions">

                    <button class="answer-action"
                            onclick="answerAction(this, 'copy')"
                            title="Copy">
                        📋
                    </button>

                    <button class="answer-action"
                            onclick="answerAction(this, 'like')"
                            title="Like">
                        👍
                    </button>

                    <button class="answer-action"
                            onclick="answerAction(this, 'dislike')"
                            title="Dislike">
                        👎
                    </button>

                    <button class="answer-action"
                            onclick="answerAction(this, 'sound')"
                            title="Read aloud">
                        🔊
                    </button>

                    <button class="answer-action"
                            onclick="answerAction(this, 'share')"
                            title="Share">
                        ↗
                    </button>

                    <button class="answer-action"
                            onclick="answerAction(this, 'more')"
                            title="More">
                        ⋯
                    </button>

                    <span class="action-status"></span>

                </div>
            </div>
        </div>
    </div>
    """


def make_chat_html(history):
    if not history:
        return make_home_html()

    output = []

    for item in history:
        if isinstance(item, dict):
            role = item.get("role", "")
            content = item.get("content", "")
        else:
            role = item[0]
            content = item[1]

        if role == "user":
            output.append(make_message("user", content))
        elif role == "assistant":
            output.append(make_message("assistant", content))

    return "\n".join(output)


def make_history_html(history):
    if not history:
        return """
        <div class="history-empty">
            अभी कोई चैट नहीं है।
        </div>
        """

    items = []

    for item in history:
        if item.get("role") == "user":
            text = item.get("content", "").strip()

            if text:
                short_text = text[:42]
                if len(text) > 42:
                    short_text += "..."

                safe = escape_text(short_text)

                items.append(
                    f'<div class="history-item">{safe}</div>'
                )

    if not items:
        return """
        <div class="history-empty">
            अभी कोई चैट नहीं है।
        </div>
        """

    return "".join(items)


# ============================================================
# CHAT LOGIC
# ============================================================

def build_prompt(history, question):
    recent = history[-12:]

    conversation = []

    for item in recent:
        role = item.get("role")
        content = item.get("content", "")

        if role == "user":
            conversation.append("यूज़र: " + content)

        elif role == "assistant":
            conversation.append("Nexora AI: " + content)

    old_chat = "\n".join(conversation)

    return f"""
{SYSTEM_PROMPT}

पिछली बातचीत:
{old_chat}

नया सवाल:
{question}

अब यूज़र के सवाल का सीधा उत्तर दो।
"""


def ask_nexora(message, history):
    message = (message or "").strip()

    if not message:
        yield make_chat_html(history), history, make_history_html(history)
        return

    history = list(history or [])

    history.append({
        "role": "user",
        "content": message
    })

    # Show user's message immediately.
    yield make_chat_html(history), history, make_history_html(history)

    prompt = build_prompt(history[:-1], message)

    answer = ""

    try:
        stream = client.models.generate_content_stream(
            model=TEXT_MODEL,
            contents=prompt
        )

        for chunk in stream:
            text = getattr(chunk, "text", None)

            if text:
                answer += text

                temporary = list(history)

                temporary.append({
                    "role": "assistant",
                    "content": answer + "▌"
                })

                yield (
                    make_chat_html(temporary),
                    history,
                    make_history_html(history)
                )

    except Exception as first_error:
        try:
            response = client.models.generate_content(
                model=TEXT_MODEL,
                contents=prompt
            )

            answer = getattr(response, "text", "") or ""

        except Exception:
            answer = "⚠️ उत्तर देने में समस्या हुई। कृपया कुछ देर बाद फिर कोशिश करें।"

    if not answer:
        answer = "⚠️ कोई उत्तर प्राप्त नहीं हुआ।"

    history.append({
        "role": "assistant",
        "content": answer
    })

    yield (
        make_chat_html(history),
        history,
        make_history_html(history)
    )


def new_chat():
    return make_home_html(), [], make_history_html([])


# ============================================================
# JAVASCRIPT
# ============================================================

JS = r"""
function getInput() {
    return document.querySelector("#input-box textarea");
}

function setInput(value) {
    const input = getInput();

    if (!input) {
        return;
    }

    input.value = value;

    input.dispatchEvent(
        new Event("input", { bubbles: true })
    );

    input.dispatchEvent(
        new Event("change", { bubbles: true })
    );

    input.focus();
}


window.useSuggestion = function(text) {
    setInput(text);
};


function scrollChat() {
    const box = document.querySelector("#chat-wrap");

    if (box) {
        box.scrollTop = box.scrollHeight;
    }
}


function fastScroll() {
    requestAnimationFrame(() => {
        scrollChat();
    });

    setTimeout(scrollChat, 20);
    setTimeout(scrollChat, 80);
    setTimeout(scrollChat, 160);
}


function sendMessage() {
    const btn = document.querySelector("#send-btn button");

    if (btn) {
        btn.click();
    }
}


function setupInput() {
    const input = getInput();

    if (!input || input.dataset.nexoraReady === "1") {
        return;
    }

    input.dataset.nexoraReady = "1";

    input.addEventListener("keydown", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
}


function observeChat() {
    const chat = document.querySelector("#chat-content");

    if (!chat || chat.dataset.observerReady === "1") {
        return;
    }

    chat.dataset.observerReady = "1";

    const observer = new MutationObserver(function() {
        fastScroll();
        setupInput();
    });

    observer.observe(chat, {
        childList: true,
        subtree: true,
        characterData: true
    });
}


window.answerAction = async function(button, action) {

    const container = button.closest(".message-body");

    if (!container) {
        return;
    }

    const answer = container.querySelector(".nexora-answer");
    const status = container.querySelector(".action-status");

    if (!answer) {
        return;
    }

    const text = answer.innerText.trim();

    if (action === "copy") {
        try {
            await navigator.clipboard.writeText(text);

            if (status) {
                status.textContent = "कॉपी हो गया";
                setTimeout(() => {
                    status.textContent = "";
                }, 1600);
            }

        } catch (error) {
            if (status) {
                status.textContent = "कॉपी नहीं हुआ";
            }
        }
    }

    else if (action === "like") {
        if (status) {
            status.textContent = "धन्यवाद";
            setTimeout(() => {
                status.textContent = "";
            }, 1200);
        }
    }

    else if (action === "dislike") {
        if (status) {
            status.textContent = "Feedback दर्ज";
            setTimeout(() => {
                status.textContent = "";
            }, 1200);
        }
    }

    else if (action === "sound") {

        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "hi-IN";
            utterance.rate = 0.92;

            window.speechSynthesis.speak(utterance);

            if (status) {
                status.textContent = "पढ़ रहा हूँ...";
                setTimeout(() => {
                    status.textContent = "";
                }, 1800);
            }
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
                // User cancelled share.
            }
        } else {
            try {
                await navigator.clipboard.writeText(text);

                if (status) {
                    status.textContent = "कॉपी करके शेयर करें";
                    setTimeout(() => {
                        status.textContent = "";
                    }, 1800);
                }
            } catch (error) {
                // Ignore.
            }
        }
    }

    else if (action === "more") {

        if (status) {
            status.textContent = "Nexora AI";
            setTimeout(() => {
                status.textContent = "";
            }, 1200);
        }
    }
};


function setupMic() {

    const mic = document.querySelector("#mic-btn button");

    if (!mic || mic.dataset.ready === "1") {
        return;
    }

    mic.dataset.ready = "1";

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        mic.style.display = "none";
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "hi-IN";
    recognition.continuous = false;
    recognition.interimResults = true;

    mic.addEventListener("click", function() {

        try {
            recognition.start();
        } catch (error) {
            // Already running.
        }
    });

    recognition.onresult = function(event) {

        let finalText = "";

        for (
            let i = event.resultIndex;
            i < event.results.length;
            i++
        ) {
            finalText += event.results[i][0].transcript;
        }

        setInput(finalText);
    };

    recognition.onerror = function() {
        // Ignore browser speech errors.
    };
}


function setupMenu() {

    const menu = document.querySelector("#menu-btn button");
    const sidebar = document.querySelector("#sidebar");

    if (!menu || !sidebar || menu.dataset.ready === "1") {
        return;
    }

    menu.dataset.ready = "1";

    menu.addEventListener("click", function() {
        sidebar.classList.toggle("open");
    });
}


function setupAll() {
    setupInput();
    setupMic();
    setupMenu();
    observeChat();
    fastScroll();
}


setInterval(setupAll, 500);

window.addEventListener("load", function() {
    setTimeout(setupAll, 300);
    setTimeout(setupAll, 1000);
});
"""


# ============================================================
# GRADIO UI
# ============================================================

with gr.Blocks(
    title="Nexora AI",
    css=CSS,
    js=JS
) as demo:

    history_state = gr.State([])

    with gr.HTML():
        print(
            """
            <div id="nexora-app">

                <aside id="sidebar">

                    <div id="sidebar-header">
                        <button id="new-chat-btn">
                            <span class="new-icon">＋</span>
                            <span>New chat</span>
                        </button>
                    </div>

                    <div id="sidebar-history-title">
                        Chat history
                    </div>

                    <div id="history-list">
                        <div class="history-empty">
                            अभी कोई चैट नहीं है।
                        </div>
                    </div>

                    <div id="sidebar-bottom">
                        <div class="profile-row">
                            <div class="profile-avatar">N</div>
                            <div class="profile-name">
                                Nexora AI
                            </div>
                        </div>
                    </div>

                </aside>

                <main id="main-area">

                    <div id="topbar">

                        <button id="menu-btn">
                            ☰
                        </button>

                        <div id="brand-area">
                            <div class="brand-logo">N</div>
                            <div class="brand-name">
                                Nexora AI
                            </div>
                        </div>

                    </div>

                    <div id="chat-wrap">
                        <div id="chat-content">
                        </div>
                    </div>

                    <div id="composer">

                        <div id="composer-inner">

                            <div id="input-box"></div>

                            <div id="composer-buttons">
                                <div id="mic-btn"></div>
                                <div id="send-btn"></div>
                            </div>

                            <div class="composer-note">
                                Nexora AI गलतियाँ कर सकता है। महत्वपूर्ण जानकारी जाँच लें।
                            </div>

                        </div>

                    </div>

                </main>

            </div>
            """
        )

    # Invisible Gradio components used by the UI.
    chat_html = gr.HTML(
        value=make_home_html(),
        elem_id="chat-content"
    )

    history_html = gr.HTML(
        value=make_history_html([]),
        elem_id="history-list"
    )

    message_input = gr.Textbox(
        show_label=False,
        placeholder="Nexora AI से कुछ भी पूछें...",
        lines=1,
        max_lines=6,
        elem_id="input-box",
        container=False
    )

    mic_button = gr.Button(
        "🎙️",
        elem_id="mic-btn",
        size="sm"
    )

    send_button = gr.Button(
        "➤",
        elem_id="send-btn",
        variant="primary",
        size="sm"
    )

    new_chat_button = gr.Button(
        "＋ New chat",
        elem_id="new-chat-btn",
        size="sm"
    )

    # Send
    send_button.click(
        fn=ask_nexora,
        inputs=[message_input, history_state],
        outputs=[chat_html, history_state, history_html]
    ).then(
        fn=lambda: "",
        inputs=None,
        outputs=message_input
    )

    # Enter key
    message_input.submit(
        fn=ask_nexora,
        inputs=[message_input, history_state],
        outputs=[chat_html, history_state, history_html]
    ).then(
        fn=lambda: "",
        inputs=None,
        outputs=message_input
    )

    # New chat
    new_chat_button.click(
        fn=new_chat,
        inputs=None,
        outputs=[chat_html, history_state, history_html]
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860"))
    )
