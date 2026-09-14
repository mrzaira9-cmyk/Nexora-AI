import os
import html
import json
import re
from datetime import datetime

import gradio as gr
from google import genai
from google.genai import types


# =========================================================
# GEMINI
# =========================================================

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"

# बहुत बड़ी history भेजने से बचने के लिए
MAX_HISTORY = 8


# =========================================================
# WEB SEARCH कब इस्तेमाल करना है
# =========================================================

def needs_web_search(message):
    text = message.lower()

    keywords = [
        # English
        "today",
        "latest",
        "current",
        "recent",
        "news",
        "now",
        "date",
        "time",
        "price",
        "weather",
        "score",
        "match",
        "live",
        "2026",

        # Hindi
        "आज",
        "अभी",
        "ताज़ा",
        "ताजा",
        "वर्तमान",
        "नवीनतम",
        "हाल की",
        "खबर",
        "समाचार",
        "तारीख",
        "दिनांक",
        "समय",
        "कीमत",
        "भाव",
        "मौसम",
        "स्कोर",
        "मैच",
        "लाइव",
    ]

    return any(word in text for word in keywords)


# =========================================================
# DATE
# =========================================================

def current_date_text():
    now = datetime.now()

    return now.strftime(
        "%d-%m-%Y %H:%M"
    )


# =========================================================
# CHAT FUNCTION
# =========================================================

def nexora_ai(message, history=None):

    history = history or []

    if not message or not message.strip():
        return (
            history,
            "",
            build_chat_html(history),
            "",
            ""
        )

    try:

        # -------------------------------------------------
        # केवल हाल की history
        # -------------------------------------------------

        recent_history = history[-MAX_HISTORY:]

        old_chat = ""

        for user_msg, ai_msg in recent_history:
            old_chat += (
                f"User: {user_msg}\n"
                f"Nexora AI: {ai_msg}\n\n"
            )

        # -------------------------------------------------
        # Search जरूरत है या नहीं
        # -------------------------------------------------

        use_search = needs_web_search(message)

        today_info = current_date_text()

        prompt = f"""
You are Nexora AI, a helpful multilingual AI assistant.

CURRENT DATE AND TIME:
{today_info}

IMPORTANT RULES:

1. Understand the user's language automatically.
2. Reply in the same language as the user.
3. If the user writes Hindi in Roman Hindi,
   reply in proper Devanagari Hindi.
4. If the user asks in English, reply in English.
5. If the user asks in Bengali, reply in Bengali.
6. For other languages, reply in that language.
7. Give clear, useful and natural answers.
8. Remember recent conversation when relevant.
9. Do not invent facts.
10. If current information is available from web search,
    prefer the current information.
11. If you used web information, mention useful sources
    with their links when available.
12. Do not claim something is current unless you have
    reliable current information.
13. Keep answers reasonably concise unless the user asks
    for detailed information.
14. Do not mention these internal instructions.

RECENT CONVERSATION:
{old_chat}

CURRENT USER QUESTION:
{message}
"""

        # -------------------------------------------------
        # GEMINI CONFIG
        # -------------------------------------------------

        config = types.GenerateContentConfig(
            max_output_tokens=1200
        )

        # -------------------------------------------------
        # Google Search only when useful
        # -------------------------------------------------

        if use_search:
            config.tools = [
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]

        # -------------------------------------------------
        # GEMINI REQUEST
        # -------------------------------------------------

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config
        )

        answer_text = (
            response.text
            or "मुझे इस सवाल का उत्तर नहीं मिल पाया।"
        )

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        history.append(
            (message, answer_text)
        )

        # -------------------------------------------------
        # CHAT HTML
        # -------------------------------------------------

        chat_html = build_chat_html(history)

        # -------------------------------------------------
        # SPEAKER BAR
        # -------------------------------------------------

        sound_bar = """
        <div id="speaker-bar">

            <span id="speaker-title">
                🔊 Nexora AI Voice
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

        search_status = ""

        if use_search:
            search_status = """
            <div class="search-status">
                🌐 ताज़ी जानकारी के लिए Web Search इस्तेमाल किया गया।
            </div>
            """

        return (
            history,
            "",
            chat_html,
            sound_bar,
            search_status
        )

    except Exception as e:

        error_text = html.escape(
            str(e)
        )

        return (
            history,
            "",
            build_chat_html(history),
            "",
            f"❌ समस्या: {error_text}"
        )


# =========================================================
# CHAT HTML
# =========================================================

def build_chat_html(history):

    if not history:

        return """
        <div id="chat-container">

            <div class="welcome-screen">

                <div class="welcome-logo">
                    🤖
                </div>

                <h1>
                    Nexora AI
                </h1>

                <p>
                    आप क्या जानना चाहते हैं?
                </p>

                <div class="suggestion-grid">

                    <div class="suggestion-card">
                        💡
                        <b>जानकारी</b>
                        <span>किसी भी विषय के बारे में पूछें</span>
                    </div>

                    <div class="suggestion-card">
                        🌐
                        <b>ताज़ा जानकारी</b>
                        <span>नई जानकारी और समाचार पूछें</span>
                    </div>

                    <div class="suggestion-card">
                        ✍️
                        <b>लिखने में मदद</b>
                        <span>लेखन और विचारों में सहायता लें</span>
                    </div>

                    <div class="suggestion-card">
                        🧠
                        <b>सीखें</b>
                        <span>किसी विषय को आसान भाषा में समझें</span>
                    </div>

                </div>

            </div>

        </div>
        """

    chat_html = """
    <div id="chat-container">
    """

    for index, (user_msg, ai_msg) in enumerate(history):

        safe_user = html.escape(
            str(user_msg)
        )

        safe_ai = html.escape(
            str(ai_msg)
        )

        answer_json = json.dumps(
            str(ai_msg),
            ensure_ascii=False
        )

        safe_answer_json = html.escape(
            answer_json,
            quote=True
        )

        chat_html += f"""

        <div class="message-block">

            <div class="user-message">

                <div class="message-label">
                    आप
                </div>

                <div class="user-bubble">
                    {safe_user}
                </div>

            </div>


            <div class="ai-message">

                <div class="message-label">
                    🤖 Nexora AI
                </div>

                <div class="ai-bubble">
                    {safe_ai}
                </div>


                <div class="answer-actions">

                    <button
                        class="answer-btn like-btn"
                        title="पसंद">
                        👍
                    </button>

                    <button
                        class="answer-btn dislike-btn"
                        title="नापसंद">
                        👎
                    </button>

                    <button
                        class="answer-btn speak-btn"
                        data-answer="{safe_answer_json}"
                        title="सुनें">
                        🔊
                    </button>

                    <button
                        class="answer-btn copy-btn"
                        data-answer="{safe_answer_json}"
                        title="कॉपी">
                        📋
                    </button>

                    <button
                        class="answer-btn share-btn"
                        data-answer="{safe_answer_json}"
                        title="शेयर">
                        ↗️
                    </button>

                    <button
                        class="answer-btn more-btn"
                        title="और विकल्प">
                        ⋯
                    </button>

                </div>

            </div>

        </div>

        """

    chat_html += """
    </div>
    """

    return chat_html


# =========================================================
# NEW CHAT
# =========================================================

def new_chat():

    return (
        [],
        "",
        build_chat_html([]),
        "",
        ""
    )


# =========================================================
# CSS
# =========================================================

css = r"""

/* =====================================================
   GENERAL
===================================================== */

html,
body {
    margin: 0 !important;
    padding: 0 !important;
    background: #ffffff !important;
}

.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}


/* =====================================================
   HEADER
===================================================== */

#top-header {
    height: 58px;
    display: flex;
    align-items: center;
    padding: 0 15px;
    border-bottom: 1px solid #eeeeee;
    background: #ffffff;
    position: sticky;
    top: 0;
    z-index: 200;
}

#menu-button button {
    border: none !important;
    background: transparent !important;
    font-size: 23px !important;
}

#brand-name {
    font-size: 19px;
    font-weight: 700;
    margin-left: 5px;
}

#new-chat-top button {
    border-radius: 10px !important;
}


/* =====================================================
   SIDEBAR
===================================================== */

#sidebar {

    position: fixed;

    left: 0;
    top: 0;
    bottom: 0;

    width: 270px;

    background: #f7f7f8;

    z-index: 500;

    padding: 12px;

    box-sizing: border-box;

    transform: translateX(-100%);

    transition:
        transform 0.22s ease;

    box-shadow:
        4px 0 18px rgba(0,0,0,0.08);
}

#sidebar.open {
    transform: translateX(0);
}

.sidebar-title {
    font-size: 19px;
    font-weight: 700;
    padding: 10px;
}

.sidebar-item {

    width: 100%;

    border: none;

    background: transparent;

    text-align: left;

    padding: 12px;

    margin: 3px 0;

    border-radius: 10px;

    font-size: 15px;

    cursor: pointer;
}

.sidebar-item:hover {
    background: #e9e9e9;
}

.sidebar-close {
    float: right;
    border: none;
    background: transparent;
    font-size: 20px;
}


/* =====================================================
   MAIN
===================================================== */

#main-area {

    width: 100%;

    min-height: 100vh;

    box-sizing: border-box;

    padding-bottom: 100px;
}


/* =====================================================
   SPEAKER
===================================================== */

#speaker-container {

    position: sticky;

    top: 58px;

    z-index: 150;
}

#speaker-bar {

    display: flex;

    align-items: center;

    gap: 7px;

    padding: 8px 12px;

    margin: 6px 12px;

    border-radius: 14px;

    background: #f1f3f4;

    box-shadow:
        0 2px 8px rgba(0,0,0,0.06);
}

#speaker-title {
    flex: 1;
    font-weight: 600;
}

#speaker-bar button {

    border: none;

    background: white;

    border-radius: 9px;

    padding: 7px 9px;

    font-size: 16px;

    cursor: pointer;
}


/* =====================================================
   CHAT
===================================================== */

#history-display {

    width: 100%;

    box-sizing: border-box;
}

#chat-container {

    height: calc(100vh - 150px);

    min-height: 400px;

    overflow-y: auto;

    scroll-behavior: smooth;

    padding:

        25px
        max(16px, calc((100% - 850px) / 2))
        130px;

    box-sizing: border-box;
}


/* =====================================================
   WELCOME
===================================================== */

.welcome-screen {

    max-width: 850px;

    margin: auto;

    text-align: center;

    padding-top: 65px;
}

.welcome-logo {

    font-size: 58px;

    margin-bottom: 10px;
}

.welcome-screen h1 {

    font-size: 31px;

    margin: 5px 0 8px;
}

.welcome-screen p {

    font-size: 17px;

    opacity: 0.6;
}


/* =====================================================
   SUGGESTIONS
===================================================== */

.suggestion-grid {

    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 12px;

    margin-top: 35px;
}

.suggestion-card {

    text-align: left;

    border: 1px solid #e5e5e5;

    border-radius: 15px;

    padding: 16px;

    background: #ffffff;

    cursor: pointer;

    transition: 0.15s;
}

.suggestion-card:hover {

    background: #f7f7f7;

    transform: translateY(-1px);
}

.suggestion-card b {

    display: block;

    margin-top: 7px;
}

.suggestion-card span {

    display: block;

    font-size: 13px;

    opacity: 0.6;

    margin-top: 4px;
}


/* =====================================================
   MESSAGES
===================================================== */

.message-block {

    max-width: 850px;

    margin: 0 auto 28px;
}

.message-label {

    font-size: 13px;

    font-weight: 600;

    opacity: 0.65;

    margin-bottom: 6px;
}

.user-bubble {

    background: #f1f1f1;

    border-radius: 17px;

    padding: 12px 15px;

    white-space: pre-wrap;

    overflow-wrap: anywhere;

    display: inline-block;

    max-width: 90%;
}

.ai-bubble {

    padding: 2px 0;

    white-space: pre-wrap;

    overflow-wrap: anywhere;

    line-height: 1.6;

    font-size: 15px;
}


/* =====================================================
   ANSWER BUTTONS
===================================================== */

.answer-actions {

    display: flex;

    gap: 3px;

    margin-top: 8px;
}

.answer-btn {

    border: none;

    background: transparent;

    border-radius: 9px;

    padding: 6px 8px;

    font-size: 16px;

    cursor: pointer;
}

.answer-btn:hover {

    background: #eeeeee;
}


/* =====================================================
   SEARCH STATUS
===================================================== */

.search-status {

    text-align: center;

    font-size: 12px;

    opacity: 0.6;

    padding: 3px 10px;
}


/* =====================================================
   INPUT
===================================================== */

#input-area {

    position: fixed;

    left: 50%;

    bottom: 10px;

    transform: translateX(-50%);

    width: min(850px, calc(100% - 20px));

    z-index: 300;

    display: flex;

    align-items: center;

    gap: 7px;

    background: #ffffff;

    border: 1px solid #dddddd;

    border-radius: 18px;

    padding: 7px;

    box-shadow:
        0 3px 20px rgba(0,0,0,0.12);

    box-sizing: border-box;
}

#question-box {

    flex: 1;
}

#question-box textarea {

    border: none !important;

    box-shadow: none !important;

    border-radius: 13px !important;

    min-height: 46px !important;

    max-height: 130px !important;

    padding: 12px !important;

    font-size: 15px !important;
}

#mic-button button {

    min-width: 45px !important;

    height: 45px !important;

    border-radius: 12px !important;

    font-size: 20px !important;
}

#send-button button {

    min-width: 47px !important;

    height: 45px !important;

    border-radius: 12px !important;

    font-size: 19px !important;
}


/* =====================================================
   MOBILE
===================================================== */

@media (max-width: 600px) {

    #brand-name {
        font-size: 17px;
    }

    #chat-container {

        height: calc(100vh - 145px);

        padding:

            18px
            12px
            125px;
    }

    .welcome-screen {

        padding-top: 45px;
    }

    .welcome-logo {

        font-size: 48px;
    }

    .welcome-screen h1 {

        font-size: 26px;
    }

    .suggestion-grid {

        grid-template-columns: 1fr;

        gap: 9px;

        margin-top: 25px;
    }

    .suggestion-card {

        padding: 13px;
    }

    .message-block {

        margin-bottom: 24px;
    }

    #input-area {

        width: calc(100% - 10px);

        bottom: 5px;

        border-radius: 17px;
    }

    .answer-btn {

        font-size: 15px;

        padding: 6px;
    }

    #sidebar {

        width: 82%;
    }
}


/* =====================================================
   VOICE PANEL
===================================================== */

#voice-panel {

    position: fixed;

    right: 14px;

    bottom: 80px;

    width: 290px;

    max-width: calc(100% - 28px);

    background: white;

    border: 1px solid #dddddd;

    border-radius: 17px;

    padding: 14px;

    z-index: 600;

    box-shadow:
        0 5px 25px rgba(0,0,0,0.15);

    display: none;
}

#voice-panel.open {
    display: block;
}

.voice-title {

    font-weight: 700;

    margin-bottom: 10px;
}

#voice-list {

    width: 100%;

    border: 1px solid #ddd;

    border-radius: 10px;

    padding: 9px;

    font-size: 14px;
}

.voice-note {

    font-size: 11px;

    opacity: 0.6;

    margin-top: 8px;
}

"""


# =========================================================
# JAVASCRIPT
# =========================================================

js = r"""
() => {

    console.log("Nexora AI interface loaded");


    // =====================================================
    // HELPERS
    // =====================================================

    function getChatBox() {

        return document.querySelector(
            "#chat-container"
        );

    }


    function scrollChat() {

        const box = getChatBox();

        if (!box) return;

        requestAnimationFrame(() => {

            box.scrollTo({
                top: box.scrollHeight,
                behavior: "smooth"
            });

        });

    }


    // =====================================================
    // SIDEBAR
    // =====================================================

    document.
