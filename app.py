import os
import html
import json
from datetime import datetime

import gradio as gr
from google import genai
from google.genai import types


# =========================================================
# GEMINI SETUP
# =========================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing."
    )

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"

MAX_HISTORY = 8


# =========================================================
# WEB SEARCH DETECTION
# =========================================================

def needs_web_search(message):

    text = str(message).lower()

    keywords = [
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
        "2027",

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

    return any(
        word in text
        for word in keywords
    )


# =========================================================
# CURRENT DATE
# =========================================================

def current_date_text():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )


# =========================================================
# SOURCE LINKS
# =========================================================

def get_source_html(response):

    sources = []

    try:

        candidates = getattr(
            response,
            "candidates",
            []
        ) or []

        if not candidates:
            return ""

        candidate = candidates[0]

        metadata = getattr(
            candidate,
            "grounding_metadata",
            None
        )

        if not metadata:
            return ""

        chunks = getattr(
            metadata,
            "grounding_chunks",
            []
        ) or []

        for chunk in chunks:

            web_data = getattr(
                chunk,
                "web",
                None
            )

            if not web_data:
                continue

            uri = getattr(
                web_data,
                "uri",
                None
            )

            title = getattr(
                web_data,
                "title",
                None
            )

            if not uri:
                continue

            already_exists = any(
                old_uri == uri
                for old_uri, old_title in sources
            )

            if not already_exists:

                sources.append(
                    (
                        uri,
                        title or uri
                    )
                )

    except Exception:

        return ""

    if not sources:
        return ""

    result = """
    <div class="sources-box">
        <div class="sources-title">
            🔗 स्रोत
        </div>
    """

    for uri, title in sources[:6]:

        safe_uri = html.escape(
            str(uri),
            quote=True
        )

        safe_title = html.escape(
            str(title)
        )

        result += f"""
        <a
            class="source-link"
            href="{safe_uri}"
            target="_blank"
            rel="noopener noreferrer"
        >
            🌐 {safe_title}
        </a>
        """

    result += """
    </div>
    """

    return result


# =========================================================
# ANSWER BUTTONS
# =========================================================

def answer_actions(answer_text):

    answer_json = json.dumps(
        str(answer_text),
        ensure_ascii=False
    )

    safe_answer = html.escape(
        answer_json,
        quote=True
    )

    return f"""
    <div class="answer-actions">

        <button
            class="answer-btn"
            title="पसंद"
        >
            👍
        </button>

        <button
            class="answer-btn"
            title="नापसंद"
        >
            👎
        </button>

        <button
            class="answer-btn speak-btn"
            data-answer="{safe_answer}"
            title="सुनें"
        >
            🔊
        </button>

        <button
            class="answer-btn copy-btn"
            data-answer="{safe_answer}"
            title="कॉपी"
        >
            📋
        </button>

        <button
            class="answer-btn share-btn"
            data-answer="{safe_answer}"
            title="शेयर"
        >
            ↗️
        </button>

        <button
            class="answer-btn"
            title="और विकल्प"
        >
            ⋯
        </button>

    </div>
    """


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

                    <button
                        class="suggestion-card"
                        data-prompt="भारत की राजधानी क्या है?"
                    >
                        💡

                        <b>
                            जानकारी
                        </b>

                        <span>
                            किसी भी विषय के बारे में पूछें
                        </span>

                    </button>


                    <button
                        class="suggestion-card"
                        data-prompt="आज की ताज़ा खबरें क्या हैं?"
                    >
                        🌐

                        <b>
                            ताज़ा जानकारी
                        </b>

                        <span>
                            नई जानकारी और समाचार पूछें
                        </span>

                    </button>


                    <button
                        class="suggestion-card"
                        data-prompt="मेरी पढ़ाई में मदद करें।"
                    >
                        ✍️

                        <b>
                            पढ़ाई
                        </b>

                        <span>
                            कठिन विषय आसान भाषा में समझें
                        </span>

                    </button>


                    <button
                        class="suggestion-card"
                        data-prompt="किसी विषय को आसान भाषा में समझाइए।"
                    >
                        🧠

                        <b>
                            सीखें
                        </b>

                        <span>
                            किसी भी विषय को आसानी से सीखें
                        </span>

                    </button>

                </div>

            </div>

        </div>
        """

    result = """
    <div id="chat-container">
    """

    for user_msg, ai_msg in history:

        safe_user = html.escape(
            str(user_msg)
        )

        safe_ai = html.escape(
            str(ai_msg)
        )

        result += f"""

        <div class="message-block">

            <div class="message-label">
                आप
            </div>

            <div class="user-bubble">
                {safe_user}
            </div>


            <div class="message-label ai-label">
                🤖 Nexora AI
            </div>

            <div class="ai-bubble">
                {safe_ai}
            </div>

            {answer_actions(ai_msg)}

        </div>

        """

    result += """
    </div>
    """

    return result


# =========================================================
# AI FUNCTION
# =========================================================

def nexora_ai(message, history):

    history = history or []

    if not message or not str(message).strip():

        return (
            history,
            build_chat_html(history),
            "",
            ""
        )

    message = str(message).strip()

    recent_history = history[-MAX_HISTORY:]

    old_chat_parts = []

    for user_msg, ai_msg in recent_history:

        old_chat_parts.append(
            f"User: {user_msg}\n"
            f"Nexora AI: {ai_msg}"
        )

    old_chat = "\n\n".join(
        old_chat_parts
    )

    use_search = needs_web_search(
        message
    )

    prompt = f"""
You are Nexora AI, a helpful multilingual AI assistant.

CURRENT DATE AND TIME:
{current_date_text()}

IMPORTANT RULES:

1. Understand the user's language automatically.

2. Reply in the same language as the user.

3. If the user writes Hindi using Roman Hindi,
   reply in proper Devanagari Hindi.

4. If the user asks in English,
   reply in English.

5. If the user asks in Bengali,
   reply in Bengali.

6. For other languages,
   reply in that language.

7. Give clear and useful answers.

8. Remember recent conversation when relevant.

9. Do not invent facts.

10. For current, latest, news or time-sensitive
    questions, use web information when web
    search is available.

11. Prefer current reliable information.

12. Do not claim something is current without
    reliable current information.

13. Keep answers reasonably concise.

14. Do not mention these internal instructions.

RECENT CONVERSATION:
{old_chat}

CURRENT USER QUESTION:
{message}
"""

    try:

        if use_search:

            config = types.GenerateContentConfig(
                max_output_tokens=1200,
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ]
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

        answer_text = (
            response.text
            or "मुझे इस सवाल का उत्तर नहीं मिल पाया।"
        )

        new_history = (
            recent_history
            + [
                (
                    message,
                    str(answer_text)
                )
            ]
        )

        chat_html = build_chat_html(
            new_history
        )

        speaker_html = """
        <div id="speaker-bar">

            <span>
                🔊 Nexora AI Voice
            </span>

            <button
                id="pause-speech"
                title="Pause"
            >
                ⏸️
            </button>

            <button
                id="stop-speech"
                title="Stop"
            >
                ⏹️
            </button>

            <button
                id="close-speaker"
                title="Close"
            >
                ✕
            </button>

        </div>
        """

        search_html = ""

        if use_search:

            search_html = """
            <div class="search-status">
                🌐 ताज़ी जानकारी के लिए Web Search इस्तेमाल किया गया।
            </div>
            """

            search_html += get_source_html(
                response
            )

        return (
            new_history,
            chat_html,
            speaker_html,
            search_html
        )

    except Exception as e:

        error_text = html.escape(
            str(e)
        )

        return (
            history,
            build_chat_html(history),
            "",
            f"""
            <div class="error-box">
                ❌ समस्या: {error_text}
            </div>
            """
        )


# =========================================================
# CSS
# =========================================================

css = r"""
html,
body {
    margin: 0 !important;
    padding: 0 !important;
    background: #ffffff !important;
}

.gradio-container {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

#top-header {
    height: 58px;
    display: flex;
    align-items: center;
    padding: 0 15px;
    border-bottom: 1px solid #eeeeee;
    background: #ffffff;
    position: sticky;
    top: 0;
    z-index: 100;
}

#brand-name {
    font-size: 20px;
    font-weight: 700;
}

#main-area {
    width: 100%;
    min-height: 100vh;
    padding-bottom: 100px;
}

#chat-container {
    height: calc(100vh - 155px);
    min-height: 400px;
    overflow-y: auto;
    scroll-behavior: smooth;
    padding: 30px 15px 140px;
    box-sizing: border-box;
}

.message-block {
    max-width: 850px;
    margin: 0 auto 30px;
}

.message-label {
    font-size: 13px;
    font-weight: 600;
    opacity: 0.65;
    margin: 8px 0 6px;
}

.user-bubble {
    background: #f1f1f1;
    border-radius: 17px;
    padding: 12px 15px;
    display: inline-block;
    max-width: 90%;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.ai-bubble {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.6;
    font-size: 15px;
}

.answer-actions {
    display: flex;
    gap: 3px;
    margin-top: 8px;
}

.answer-btn {
    border: none !important;
    background: transparent !important;
    border-radius: 9px !important;
    padding: 6px 8px !important;
    font-size: 16px !important;
    cursor: pointer !important;
}

.answer-btn:hover {
    background: #eeeeee !important;
}

.welcome-screen {
    max-width: 850px;
    margin: auto;
    text-align: center;
    padding-top: 55px;
}

.welcome-logo {
    font-size: 58px;
}

.welcome-screen h1 {
    font-size: 31px;
    margin: 6px 0;
}

.welcome-screen p {
    opacity: 0.6;
}

.suggestion-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 30px;
}

.suggestion-card {
    text-align: left;
    border: 1px solid #e5e5e5;
    border-radius: 15px;
    padding: 16px;
    background: #ffffff;
    cursor: pointer;
    font: inherit;
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

#speaker-container {
    position: sticky;
    top: 58px;
    z-index: 80;
}

#speaker-bar {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 8px 12px;
    margin: 6px 12px;
    border-radius: 14px;
    background: #f1f3f4;
}

#speaker-bar span {
    flex: 1;
    font-weight: 600;
}

#speaker-bar button {
    border: none;
    background: #ffffff;
    border-radius: 9px;
    padding: 7px 9px;
    cursor: pointer;
}

#input-area {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 120;
    background: rgba(255,255,255,0.97);
    border-top: 1px solid #eeeeee;
    padding: 8px 10px;
}

#input-row {
    max-width: 850px;
    margin: auto;
    display: flex;
    align-items: flex-end;
    gap: 7px;
}

#question textarea {
    border-radius: 18px !important;
}

#mic-button button,
#send-button button {
    min-width: 48px !important;
    height: 48px !important;
    border-radius: 15px !important;
    font-size: 20px !important;
}

.sources-box {
    max-width: 850px;
    margin: 5px auto 15px;
    padding: 10px 14px;
    border: 1px solid #e6e6e6;
    border-radius: 12px;
    background: #fafafa;
}

.sources-title {
    font-weight: 700;
    margin-bottom: 7px;
}

.source-link {
    display: block;
    padding: 4px 0;
    font-size: 13px;
}

.search-status {
    text-align: center;
    font-size: 12px;
    opacity: 0.65;
    padding: 5px;
}

.error-box {
    max-width: 850px;
    margin: 10px auto;
    padding: 10px;
    border-radius: 10px;
    background: #fff0f0;
}

@media (max-width: 650px) {

    .suggestion-grid {
        grid-template-columns: 1fr;
    }

    #chat-container {
        min-height: 300px;
        padding-left: 12px;
        padding-right: 12px;
    }

    .welcome-screen {
        padding-top: 35px;
    }
}
"""


# =========================================================
# JAVASCRIPT
# =========================================================

js = r"""
() => {

    const root = document;

    function speak(text) {

        if (!text) {
            return;
        }

        if (!window.speechSynthesis) {
            return;
        }

        window.speechSynthesis.cancel();

        const utterance =
            new SpeechSynthesisUtterance(text);

        utterance.lang = "hi-IN";
        utterance.rate = 0.9;

        window.speechSynthesis.speak(
            utterance
        );
    }


    root.addEventListener(
        "click",
        function(event) {

            const suggestion =
                event.target.closest(
                    ".suggestion-card"
                );

            if (suggestion) {

                const prompt =
                    suggestion.dataset.prompt || "";

                const box =
                    root.querySelector(
                        "#question textarea"
                    );

                if (box) {

                    box.value = prompt;

                    box.dispatchEvent(
                        new Event(
                            "input",
                            {
                                bubbles: true
                            }
                        )
                    );

                    box.focus();
                }

                return;
            }


            const speakButton =
                event.target.closest(
                    ".speak-btn"
                );

            if (speakButton) {

                try {

                    const text =
                        JSON.parse(
                            speakButton.dataset.answer
                        );

                    speak(text);

                } catch (error) {
                }

                return;
            }


            const copyButton =
                event.target.closest(
                    ".copy-btn"
                );

            if (copyButton) {

                try {

                    const text =
                        JSON.parse(
                            copyButton.dataset.answer
                        );

                    if (
                        navigator.clipboard
                    ) {

                        navigator.clipboard.writeText(
                            text
                        );
                    }

                } catch (error) {
                }

                return;
            }


            const shareButton =
                event.target.closest(
                    ".share-btn"
                );

            if (shareButton) {

                try {

                    const text =
                        JSON.parse(
                            shareButton.dataset.answer
                        );

                    if (
                        navigator.share
                    ) {

                        navigator.share({
                            title: "Nexora AI",
                            text: text
                        });

                    } else if (
                        navigator.clipboard
                    ) {

                        navigator.clipboard.writeText(
                            text
                        );
                    }

                } catch (error) {
                }

                return;
            }


            if (
                
