import os
import json
import datetime
import html
import gradio as gr
from google import genai

# =========================================================
# GEMINI
# =========================================================

API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=API_KEY)

TEXT_MODEL = "gemini-3.5-flash-lite"
LIVE_MODEL = "gemini-3.8-live"

MAX_HISTORY = 10


# =========================================================
# TEXT CHAT
# =========================================================

def ask_nexora(message, history):

    history = history or []

    if not message or not message.strip():
        return history, history, ""

    # पिछली बातचीत
    previous = ""

    for item in history[-MAX_HISTORY * 2:]:
        if not isinstance(item, dict):
            continue

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
        "Do not invent facts.\n"
        "Remember previous conversation when relevant.\n\n"

        "Previous conversation:\n"
        + previous
        + "\nCurrent question:\n"
        + message
    )

    try:

        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )

        answer = response.text or "मुझे कोई उत्तर नहीं मिला।"

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


# =========================================================
# NEW CHAT
# =========================================================

def new_chat():
    return [], []


# =========================================================
# LIKE / DISLIKE
# =========================================================

def handle_like(data):
    print("Feedback:", data)


# =========================================================
# LIVE VOICE TOKEN
# =========================================================

def create_live_token():

    try:

        now = datetime.datetime.now(
            tz=datetime.timezone.utc
        )

        token = client.auth_tokens.create(
            config={
                "uses": 1,

                "expire_time": now + datetime.timedelta(
                    minutes=30
                ),

                "new_session_expire_time":
                    now + datetime.timedelta(
                        minutes=1
                    ),

                "live_connect_constraints": {
                    "model": LIVE_MODEL,

                    "config": {
                        "response_modalities": ["AUDIO"],

                        "system_instruction": {
                            "parts": [
                                {
                                    "text":
                                    "You are Nexora AI. "
                                    "Have a natural, friendly, "
                                    "real-time voice conversation. "
                                    "Understand Hindi and other languages. "
                                    "Reply in the same language the user speaks."
                                }
                            ]
                        }
                    }
                }
            }
        )

        return token.name

    except Exception as e:

        return "ERROR:" + str(e)


# =========================================================
# CSS
# =========================================================

CSS = """
html, body {
    margin: 0 !important;
    padding: 0 !important;
}

body {
    background: #ffffff !important;
}

.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
}

#topbar {
    height: 58px;
    border-bottom: 1px solid #eeeeee;
    align-items: center;
    padding: 0 10px;
}

#chat {
    height: calc(100vh - 160px) !important;
}

#bottom {
    position: fixed !important;
    left: 50%;
    bottom: 10px;
    transform: translateX(-50%);
    width: min(96%, 850px);
    z-index: 1000;
    background: white;
    border: 1px solid #dddddd;
    border-radius: 24px;
    padding: 5px;
    box-shadow: 0 5px 25px rgba(0,0,0,.12);
}

#question textarea {
    border: 0 !important;
    box-shadow: none !important;
    font-size: 16px !important;
    padding: 12px !important;
}

#send button,
#mic button,
#live button {
    min-height: 46px !important;
    min-width: 46px !important;
    border-radius: 20px !important;
    font-size: 19px !important;
}

#voice-panel {
    text-align: center;
    padding: 8px;
}

.live-status {
    font-size: 15px;
    color: #666;
}

.live-circle {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    margin: 12px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 42px;
    background: #eef2ff;
}

.voice-buttons {
    display: flex;
    justify-content: center;
    gap: 8px;
}

@media (max-width: 600px) {

    #chat {
        height: calc(100vh - 145px) !important;
    }

    #bottom {
        width: 97%;
    }
}
"""


# =========================================================
# LIVE VOICE JAVASCRIPT
# =========================================================

LIVE_JS = r"""
() => {

    window.nexoraLive = {
        socket: null,
        audioContext: null,
        processor: null,
        source: null,
        stream: null,
        playing: false
    };

    function base64FromArrayBuffer(buffer) {
        let binary = "";
        const bytes = new Uint8Array(buffer);

        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }

        return btoa(binary);
    }

    function arrayBufferFromBase64(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);

        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }

        return bytes.buffer;
    }

    function downsampleTo16k(buffer, inputRate) {

        if (inputRate === 16000) {
            return buffer;
        }

        const ratio = inputRate / 16000;
        const newLength = Math.round(buffer.length / ratio);
        const result = new Int16Array(newLength);

        let offsetResult = 0;
        let offsetBuffer = 0;

        while (offsetResult < result.length) {

            const nextOffsetBuffer =
                Math.round((offsetResult + 1) * ratio);

            let accum = 0;
            let count = 0;

            for (
                let i = offsetBuffer;
                i < nextOffsetBuffer &&
                i < buffer.length;
                i++
            ) {
                accum += buffer[i];
                count++;
            }

            result[offsetResult] =
                Math.max(
                    -1,
                    Math.min(
                        1,
                        accum / Math.max(1, count)
                    )
                ) * 32767;

            offsetResult++;
            offsetBuffer = nextOffsetBuffer;
        }

        return result;
    }

    async function playPCM16(base64) {

        const data =
            new Int16Array(
                arrayBufferFromBase64(base64)
            );

        if (!window.nexoraLive.audioContext) {

            window.nexoraLive.audioContext =
                new AudioContext({
                    sampleRate: 24000
                });
        }

        const ctx =
            window.nexoraLive.audioContext;

        const audioBuffer =
            ctx.createBuffer(
                1,
                data.length,
                24000
            );

        const channel =
            audioBuffer.getChannelData(0);

        for (let i = 0; i < data.length; i++) {
            channel[i] = data[i] / 32768;
        }

        const source =
            ctx.createBufferSource();

        source.buffer = audioBuffer;

        source.connect(ctx.destination);

        source.start();
    }


    window.startNexoraLive = async function(token) {

        try {

            if (!token || token.startsWith("ERROR:")) {

                alert(
                    "Live Voice token नहीं बन पाया।"
                );

                return;
            }

            const wsUrl =
                "wss://generativelanguage.googleapis.com/"
                + "ws/google.ai.generativelanguage.v1beta."
                + "GenerativeService."
                + "BidiGenerateContentConstrained"
                + "?access_token="
                + encodeURIComponent(token);

            const socket =
                new WebSocket(wsUrl);

            window.nexoraLive.socket = socket;

            socket.onopen = async function() {

                document
                    .getElementById("live-status")
                    .innerText =
                    "🟢 Live चालू है — बोलिए...";

                const setup = {
                    setup: {
                        model:
                            "models/gemini-3.8-live",

                        generationConfig: {
                            responseModalities: [
                                "AUDIO"
                            ]
                        },

                        inputAudioTranscription: {},

                        outputAudioTranscription: {}
                    }
                };

                socket.send(
                    JSON.stringify(setup)
                );

                try {

                    const stream =
                        await navigator
                            .mediaDevices
                            .getUserMedia({
                                audio: true
                            });

                    window.nexoraLive.stream =
                        stream;

                    const audioContext =
                        new AudioContext();

                    window.nexoraLive.audioContext =
                        audioContext;

                    const source =
                        audioContext
                            .createMediaStreamSource(
                                stream
                            );

                    const processor =
                        audioContext
                            .createScriptProcessor(
                                4096,
                                1,
                                1
                            );

                    window.nexoraLive.source =
                        source;

                    window.nexoraLive.processor =
                        processor;

                    source.connect(processor);

                    processor.connect(
                        audioContext.destination
                    );

                    processor.onaudioprocess =
                        function(event) {

                            if (
                                socket.readyState !==
                                WebSocket.OPEN
                            ) {
                                return;
                            }

                            const input =
                                event.inputBuffer
                                    .getChannelData(0);

                            const pcm =
                                downsampleTo16k(
                                    input,
                                    audioContext.sampleRate
                                );

                            const bytes =
                                new Uint8Array(
                                    pcm.buffer
                                );

                            socket.send(
                                JSON.stringify({
                                    realtimeInput: {
                                        audio: {
                                            data:
                                                base64FromArrayBuffer(
                                                    bytes.buffer
                                                ),
                                            mimeType:
                                                "audio/pcm;rate=16000"
                                        }
                                    }
                                })
                            );
                        };

                } catch (error) {

                    document
                        .getElementById("live-status")
                        .innerText =
                        "❌ Microphone की अनुमति नहीं मिली।";
                }
            };


            socket.onmessage = async function(event) {

                try {

                    const message =
                        JSON.parse(event.data);

                    const content =
                        message.serverContent;

                    if (!content) {
                        return;
                    }

                    if (
                        content.modelTurn &&
                        content.modelTurn.parts
                    ) {

                        for (
                            const part
                            of content.modelTurn.parts
                        ) {

                            if (
                                part.inlineData &&
                                part.inlineData.data
                            ) {

                                await playPCM16(
                                    part.inlineData.data
                                );
                            }
                        }
                    }

                    if (
                        content.outputTranscription &&
                        content.outputTranscription.text
                    ) {

                        console.log(
                            "Gemini:",
                            content.outputTranscription.text
                        );
                    }

                } catch (error) {

                    console.log(
                        "Live message error:",
                        error
                    );
                }
            };


            socket.onerror = function() {

                document
                    .getElementById("live-status")
                    .innerText =
                    "❌ Live Voice में समस्या हुई।";
            };


            socket.onclose = function() {

                document
                    .getElementById("live-status")
                    .innerText =
                    "⚪ Live बंद है";
            };

        } catch (error) {

            alert(
                "Live Voice शुरू नहीं हो पाया: "
                + error
            );
        }
    };


    window.stopNexoraLive = function() {

        const live =
            window.nexoraLive;

        if (live.processor) {
            live.processor.disconnect();
        }

        if (live.source) {
            live.source.disconnect();
        }

        if (live.stream) {

            live.stream
                .getTracks()
                .forEach(
                    track => track.stop()
                );
        }

        if (live.socket) {
            live.socket.close();
        }

        document
            .getElementById("live-status")
            .innerText =
            "⚪ Live बंद है";
    };


    window.copyLastAnswer = function() {

        const messages =
            document.querySelectorAll(
                "#chat .message"
            );

        if (!messages.length) {
            return;
        }

        const last =
            messages[messages.length - 1];

        navigator.clipboard.writeText(
            last.innerText
        );
    };


    window.shareLastAnswer = async function() {

        const messages =
            document.querySelectorAll(
                "#chat .message"
            );

        if (!messages.length) {
            return;
        }

        const last =
            messages[messages.length - 1];

        const text =
            last.innerText;

        if (navigator.share) {

            await navigator.share({
                title: "Nexora AI",
                text: text
            });

        } else {

            await navigator.clipboard.writeText(
                text
            );

            alert(
                "उत्तर कॉपी हो गया।"
            );
        }
    };
}
"""


# =========================================================
# APP
# =========================================================

with gr.Blocks(
    title="Nexora AI"
) as app:

    # ---------------- TOP ----------------

    with gr.Row(elem_id="topbar"):

        menu = gr.Button(
            "☰",
            scale=0,
            min_width=45
        )

        gr.Markdown(
            "## 🤖 Nexora AI"
        )


    # ---------------- SIDEBAR ----------------

    with gr.Sidebar(
        label="Nexora AI",
        open=False,
        width=270
    ):

        gr.Markdown(
            "# 🤖 Nexora AI"
        )

        new_chat_btn = gr.Button(
            "🆕 नया चैट"
        )

        gr.Button(
            "🗂️ Chat History"
        )

        gr.Button(
            "🌐 Web Search"
        )

        gr.Button(
            "🖼️ Create Image"
        )

        gr.Button(
            "✍️ Write / Edit"
        )

        gr.Button(
            "📁 Files"
        )

        gr.Button(
            "🎙️ Live Voice"
        )

        gr.Button(
            "⚙️ Settings"
        )


    # ---------------- STATE ----------------

    history_state = gr.State([])


    # ---------------- CHAT ----------------

    chat = gr.Chatbot(
        value=[],
        show_label=False,
        autoscroll=True,
        height="calc(100vh - 160px)",
        elem_id="chat",
        buttons=["copy"],
        feedback_options=[
            "Like",
            "Dislike"
        ]
    )


    chat.like(
        handle_like,
        None,
        None
    )


    # =====================================================
    # EXTRA ANSWER OPTIONS
    # =====================================================

    with gr.Row():

        copy_btn = gr.Button(
            "📋 Copy"
        )

        sound_btn = gr.Button(
            "🔊 Sound"
        )

        share_btn = gr.Button(
            "↗️ Share"
        )

        more_btn = gr.Button(
            "⋯ More"
        )


    # =====================================================
    # LIVE VOICE PANEL
    # =====================================================

    with gr.Group(
        visible=True,
        elem_id="voice-panel"
    ):

        gr.HTML(
            """
            <div class="live-circle">
                🎙️
            </div>

            <div
                id="live-status"
                class="live-status"
            >
                ⚪ Live Voice बंद है
            </div>
            """
        )

        live_token = gr.Textbox(
            visible=False
        )

        with gr.Row(
            elem_id="voice-buttons"
  
