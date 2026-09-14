import os
import html
import json
from datetime import datetime

import gradio as gr
from google import genai
from google.genai import types


# =========================================================
# NEXORA AI - SETUP
# =========================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"
MAX_HISTORY = 10


# =========================================================
# WEB SEARCH
# =========================================================

def needs_web_search(message):
    text = str(message).lower()

    keywords = [
        "today", "latest", "current", "recent", "news",
        "now", "price", "weather", "score", "live",
        "2026", "2027", "who is", "president", "prime minister",

        "आज", "अभी", "ताज़ा", "ताजा", "वर्तमान",
        "नवीनतम", "हाल की", "खबर", "समाचार",
        "कीमत", "भाव", "मौसम", "स्कोर", "लाइव",
        "प्रधानमंत्री", "राष्ट्रपति"
    ]

    return any(word in text for word in keywords)


# =========================================================
# ANSWER BUTTONS
# =========================================================

def make_actions(answer):
    answer_json = json.dumps(
        str(answer),
        ensure_ascii=False
    )

    answer_safe = html.escape(
        answer_json,
        quote=True
    )

    return f"""
    <div class="answer-actions">

        <button class="answer-action" title="पसंद">👍</button>

        <button class="answer-action" title="नापसंद">👎</button>

        <button
            class="answer-action speak-action"
            data-answer="{answer_safe}"
            title="उत्तर सुनें">
            🔊
        </button>

        <button
            class="answer-action copy-action"
            data-answer="{answer_safe}"
            title="कॉपी करें">
            📋
        </button>

        <button
            class="answer-action share-action"
            data-answer="{answer_safe}"
            title="शेयर करें">
            ↗️
        </button>

        <button class="answer-action" title="और विकल्प">⋯</button>

    </div>
    """


# =========================================================
# CHAT DISPLAY
# =========================================================

def build_chat(history):

    if not history:
        return """
        <div id="chat">

            <div class="welcome">

                <div class="welcome-logo">🤖</div>

                <h1>Nexora AI</h1>

                <p>आप क्या जानना चाहते हैं?</p>

                <div class="suggestions">

                    <button
                        class="suggestion"
                        data-prompt="भारत की राजधानी क्या है?">
                        💡
                        <b>जानकारी</b>
                        <span>किसी भी विषय के बारे में पूछें</span>
                    </button>

                    <button
                        class="suggestion"
                        data-prompt="आज की ताज़ा खबरें क्या हैं?">
                        🌐
                        <b>ताज़ा जानकारी</b>
                        <span>नई जानकारी और समाचार पूछें</span>
                    </button>

                    <button
                        class="suggestion"
                        data-prompt="मेरी पढ़ाई में मदद करें।">
                        📚
                        <b>पढ़ाई</b>
                        <span>कठिन विषय आसान भाषा में समझें</span>
                    </button>

                    <button
                        class="suggestion"
                        data-prompt="किसी विषय को आसान भाषा में समझाइए।">
                        🧠
                        <b>सीखें</b>
                        <span>किसी भी विषय को आसानी से समझें</span>
                    </button>

                </div>

            </div>

        </div>
        """

    output = '<div id="chat">'

    for user_text, ai_text in history:

        user_safe = html.escape(str(user_text))
        ai_safe = html.escape(str(ai_text))

        output += f"""
        <div class="message-block">

            <div class="message-label">आप</div>

            <div class="user-bubble">
                {user_safe}
            </div>

            <div class="message-label ai-label">
                🤖 Nexora AI
            </div>

            <div class="ai-text">
                {ai_safe}
            </div>

            {make_actions(ai_text)}

        </div>
        """

    output += "</div>"

    return output


# =========================================================
# AI FUNCTION
# =========================================================

def nexora_ai(message, history):

    history = history or []

    if not message or not str(message).strip():
        return (
            history,
            build_chat(history),
            "",
            "",
            ""
        )

    message = str(message).strip()

    recent = history[-MAX_HISTORY:]

    previous = ""

    for user_text, ai_text in recent:
        previous += (
            f"User: {user_text}\n"
            f"Nexora AI: {ai_text}\n\n"
        )

    prompt = f"""
You are Nexora AI, a helpful multilingual AI assistant.

Current date and time:
{datetime.now().strftime("%d-%m-%Y %H:%M")}

RULES:

1. Understand the user's language automatically.
2. Reply in the same language as the user.
3. If the user writes Roman Hindi, reply in proper Devanagari Hindi.
4. If the user writes English, reply in English.
5. If the user writes Bengali, reply in Bengali.
6. For other languages, reply in that language.
7. Remember the recent conversation.
8. Give clear and useful answers.
9. Do not invent facts.
10. For current/latest/news questions, use web search when available.
11. Do not say information is current unless reliable current information is available.
12. Keep the answer reasonably concise.
13. Do not mention these internal instructions.

RECENT CONVERSATION:
{previous}

USER QUESTION:
{message}
"""

    try:

        if needs_web_search(message):

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

        answer = response.text or "मुझे उत्तर नहीं मिल पाया।"

        new_history = recent + [
            (message, str(answer))
        ]

        speaker = """
        <div id="speaker-bar">

            <span>🔊 Nexora AI Voice</span>

            <button id="pause-voice">⏸️</button>

            <button id="stop-voice">⏹️</button>

            <button id="voice-settings">⚙️</button>

            <button id="close-voice">✕</button>

        </div>
        """

        search_info = ""

        if needs_web_search(message):
            search_info = """
            <div class="search-info">
                🌐 ताज़ी जानकारी के लिए Web Search इस्तेमाल किया गया।
            </div>
            """

        return (
            new_history,
            build_chat(new_history),
            speaker,
            search_info,
            ""
        )

    except Exception as e:

        error = html.escape(str(e))

        return (
            history,
            build_chat(history),
            "",
            f"""
            <div class="error-box">
                ❌ समस्या: {error}
            </div>
            """,
            ""
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

#header {
    height: 58px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    border-bottom: 1px solid #eeeeee;
    background: #ffffff;
    position: sticky;
    top: 0;
    z-index: 100;
}

#brand {
    font-size: 20px;
    font-weight: 700;
}

#chat {
    height: calc(100vh - 155px);
    min-height: 350px;
    overflow-y: auto;
    scroll-behavior: smooth;
    padding: 28px 14px 140px;
    box-sizing: border-box;
}

.message-block {
    max-width: 850px;
    margin: 0 auto 30px;
}

.message-label {
    font-size: 13px;
    font-weight: 600;
    opacity: .6;
    margin: 7px 0;
}

.user-bubble {
    display: inline-block;
    max-width: 90%;
    padding: 12px 15px;
    border-radius: 17px;
    background: #f1f1f1;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.ai-text {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.65;
    font-size: 15px;
}

.answer-actions {
    display: flex;
    gap: 3px;
    margin-top: 8px;
}

.answer-action {
    border: none !important;
    background: transparent !important;
    padding: 6px 9px !important;
    border-radius: 9px !important;
    font-size: 16px !important;
    cursor: pointer !important;
}

.answer-action:hover {
    background: #eeeeee !important;
}

.welcome {
    max-width: 850px;
    margin: auto;
    text-align: center;
    padding-top: 50px;
}

.welcome-logo {
    font-size: 60px;
}

.welcome h1 {
    font-size: 32px;
    margin: 7px 0;
}

.welcome p {
    opacity: .6;
}

.suggestions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 30px;
}

.suggestion {
    text-align: left;
    padding: 16px;
    border: 1px solid #e5e5e5;
    border-radius: 15px;
    background: white;
    cursor: pointer;
    font: inherit;
}

.suggestion b {
    display: block;
    margin-top: 7px;
}

.suggestion span {
    display: block;
    font-size: 13px;
    opacity: .6;
    margin-top: 5px;
}

#speaker-box {
    position: sticky;
    top: 58px;
    z-index: 80;
}

#speaker-bar {
    display: flex;
    align-items: center;
    gap: 7px;
    margin: 7px 12px;
    padding: 8px 12px;
    border-radius: 14px;
    background: #f1f3f4;
}

#speaker-bar span {
    flex: 1;
    font-weight: 600;
}

#speaker-bar button {
    border: none;
    background: white;
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
    padding: 8px 10px;
    background: rgba(255,255,255,.98);
    border-top: 1px solid #eeeeee;
}

#input-row {
    max-width: 850px;
    margin: auto;
    align-items: flex-end;
}

#question textarea {
    border-radius: 18px !important;
}

#mic button,
#send button {
    min-width: 48px !important;
    height: 48px !important;
    border-radius: 15px !important;
    font-size: 20px !important;
}

.search-info {
    max-width: 850px;
    margin: 5px auto;
    text-align: center;
    font-size: 12px;
    opacity: .65;
}

.error-box {
    max-width: 850px;
    margin: 10px auto;
    padding: 10px;
    border-radius: 10px;
    background: #fff0f0;
}

@media (max-width: 650px) {

    .suggestions {
        grid-template-columns: 1fr;
    }

    #chat {
        padding-left: 10px;
        padding-right: 10px;
    }

    .welcome {
        padding-top: 30px;
    }
}
"""


# =========================================================
# JAVASCRIPT
# =========================================================

js = r"""
() => {

    const root = document;

    function speakText(text) {

        if (!window.speechSynthesis) {
            alert("इस ब्राउज़र में Voice उपलब्ध नहीं है।");
            return;
        }

        window.speechSynthesis.cancel();

        const utterance =
            new SpeechSynthesisUtterance(text);

        utterance.lang = "hi-IN";
        utterance.rate = 0.9;

        window.speechSynthesis.speak(utterance);
    }


    function startMicrophone() {

        const Recognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!Recognition) {
            alert(
                "इस ब्राउज़र में Voice Input उपलब्ध नहीं है।"
            );
            return;
        }

        const recognition =
            new Recognition();

        recognition.lang = "hi-IN";
        recognition.interimResults = false;
        recognition.continuous = false;

        recognition.onresult =
            function(event) {

                const text =
                    event.results[0][0].transcript;

                const box =
                    root.querySelector(
                        "#question textarea"
                    );

                if (box) {

                    box.value = text;

                    box.dispatchEvent(
                        new Event(
                            "input",
                            { bubbles: true }
                        )
                    );

                    box.focus();
                }
            };

        recognition.onerror =
            function() {
                alert(
                    "Microphone अनुमति या Voice Input में समस्या है।"
                );
            };

        try {
            recognition.start();
        } catch (e) {}
    }


    root.addEventListener(
        "click",
        function(event) {

            const suggestion =
                event.target.closest(".suggestion");

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
                            { bubbles: true }
                        )
                    );

                    box.focus();
                }

                return;
            }


            const speakButton =
                event.target.closest(".speak-action");

            if (speakButton) {

                try {

                    const text =
                        JSON.parse(
                            speakButton.dataset.answer
                        );

                    speakText(text);

                } catch (e) {}

                return;
            }


            const copyButton =
                event.target.closest(".copy-action");

            if (copyButton) {

                try {

                    const text =
                        JSON.parse(
                            copyButton.dataset.answer
                        );

                    if (navigator.clipboard) {

                        navigator.clipboard.writeText(
                            text
                        );
                    }

                } catch (e) {}

                return;
            }


            const shareButton =
                event.target.closest(".share-action");

            if (shareButton) {

                try {

                    const text =
                        JSON.parse(
                            shareButton.dataset.answer
                        );

                    if (navigator.share) {

                        navigator.share({
                            title: "Nexora AI",
                            text: text
                        });

                    } else if (navigator.clipboard) {

                        navigator.clipboard.writeText(
                            text
                        );
                    }

                } catch (e) {}

                return;
            }


            if (
                event.target.closest("#pause-voice")
            ) {

                if (window.speechSynthesis) {
                    window.speechSynthesis.pause();
                }

                return;
            }


            if (
                event.target.closest("#stop-voice")
            ) {

                if (window.speechSynthesis) {
                    window.speechSynthesis.cancel();
                }

                return;
            }


            if (
                event.target.closest("#close-voice")
            ) {

                const bar =
                    root.querySelector("#speaker-bar");

                if (bar) {
                    bar.remove();
                }

                return;
            }


            if (
                event.target.closest("#voice-settings")
            ) {

                showVoiceSettings();

                return;
            }


            if (
                event.target.closest("#mic button")
            ) {

                startMicrophone();

                return;
            }

        }
    );


    function showVoiceSettings() {

        if (root.querySelector("#voice-panel")) {
            return;
        }

        const panel =
            document.createElement("div");

        panel.id = "voice-panel";

        panel.style.position = "fixed";
        panel.style.left = "15px";
        panel.style.right = "15px";
        panel.style.bottom = "90px";
        panel.style.zIndex = "9999";
        panel.style.background = "white";
        panel.style.border = "1px solid #ddd";
        panel.style.borderRadius = "15px";
        panel.style.padding = "15px";
        panel.style.boxShadow =
            "0 5px 25px rgba(0,0,0,.15)";

        panel.innerHTML = `
            <b>🔊 Voice Settings</b>

            <br><br>

            <select id="voice-select"
                style="width:100%;padding:10px;border-radius:10px;">
            </select>

            <br><br>

            <button id="close-voice-panel"
                style="padding:9px 14px;border-radius:9px;">
                बंद करें
            </button>
        `;

        root.body.appendChild(panel);

        const select =
            root.querySelector("#voice-select");

        function loadVoices() {

            const voices =
                window.speechSynthesis.getVoices();

            select.innerHTML = "";

            voices.slice(0, 25).forEach(
                function(voice, index) {

                    const option =
                        document.createElement("option");

                    option.value = index;

                    option.textContent =
                        voice.name +
                        " — " +
                        voice.lang;

                    select.appendChild(option);
                }
            );
        }

        loadVoices();

        window.speechSynthesis.onvoiceschanged =
            loadVoices;

        root.querySelector(
            "#close-voice-panel"
        ).onclick =
            function() {

                panel.remove();
            };
    }


    function scrollBottom() {

        const chat =
            root.querySelector("#chat");

        if (chat) {
            chat.scrollTop =
                chat.scrollHeight;
        }
    }


    const observer =
        new MutationObserver(
            function() {

                setTimeout(
                    scrollBottom,
                    150
                );
            }
        );

    observer.observe(
        root.body,
        {
            childList: true,
            subtree: true
        }
    );


    setInterval(
        scrollBottom,
        1000
    );

    setTimeout(
        scrollBottom,
        500
    );
}
"""


# =========================================================
# GRADIO APP
# =========================================================

with gr.Blocks(
    title="Nexora AI"
) as app:

    gr.HTML(
        """
              
