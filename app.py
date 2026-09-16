import os
import datetime
import gradio as gr
from google import genai


# =========================================================
# GEMINI
# =========================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY नहीं मिला।")

client = genai.Client(api_key=API_KEY)

TEXT_MODEL = "gemini-3.5-flash-lite"
LIVE_MODEL = "gemini-3.8-live"


# =========================================================
# TEXT CHAT
# =========================================================

def ask_nexora(question, history):

    question = (question or "").strip()
    history = history or []

    if not question:
        return history, ""

    context = ""

    for item in history[-10:]:

        if isinstance(item, dict):

            role = item.get("role", "")
            content = item.get("content", "")

            if role in ("user", "assistant") and isinstance(content, str):
                context += f"{role}: {content}\n"

    prompt = f"""आप Nexora AI हैं।

नियम:
1. उपयोगकर्ता जिस भाषा में पूछे उसी भाषा में उत्तर दें।
2. हिंदी में पूछा जाए तो देवनागरी हिंदी में उत्तर दें।
3. उत्तर सरल, साफ और तथ्यात्मक रखें।
4. पिछली बातचीत का संदर्भ रखें।
5. जानकारी निश्चित न हो तो अनुमान न लगाएँ।

पिछली बातचीत:
{context}

नया सवाल:
{question}
"""

    try:

        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )

        answer = response.text or "मुझे अभी उत्तर नहीं मिला।"

    except Exception as e:

        print("TEXT ERROR:", e)

        answer = (
            "⚠️ उत्तर देते समय समस्या हुई। "
            "कृपया फिर कोशिश करें।"
        )

    new_history = list(history)

    new_history.append({
        "role": "user",
        "content": question
    })

    new_history.append({
        "role": "assistant",
        "content": answer
    })

    return new_history, ""


# =========================================================
# BUTTON FUNCTIONS
# =========================================================

def new_chat():
    return []


def like_answer():
    return "👍 धन्यवाद!"


def dislike_answer():
    return "👎 आपका feedback दर्ज किया गया।"


def more_answer():
    return "⋯ और सुविधाएँ जल्द जोड़ी जाएँगी।"


# =========================================================
# LIVE TOKEN
# =========================================================

def create_live_token():

    try:

        now = datetime.datetime.now(datetime.timezone.utc)

        token = client.auth_tokens.create(
            config={
                "uses": 1,

                "expire_time":
                    now + datetime.timedelta(minutes=30),

                "new_session_expire_time":
                    now + datetime.timedelta(minutes=1),

                "live_connect_constraints": {

                    "model": LIVE_MODEL,

                    "config": {

                        "response_modalities": [
                            "AUDIO"
                        ],

                        "input_audio_transcription": {},

                        "output_audio_transcription": {}
                    }
                }
            }
        )

        return token.name

    except Exception as e:

        print("LIVE TOKEN ERROR:", e)

        return ""


# =========================================================
# CSS
# =========================================================

CSS = """
html,
body {
    margin: 0 !important;
    padding: 0 !important;
}

.gradio-container {
    max-width: 100% !important;
    min-height: 100vh !important;
    padding: 0 !important;
}

#header {
    padding: 10px 14px 5px 14px;
}

#chat {
    height: calc(100vh - 240px) !important;
}

#input-area {
    position: sticky;
    bottom: 0;
    z-index: 20;
    background: white;
    padding: 6px 8px;
}

#question textarea {
    min-height: 48px !important;
    max-height: 120px !important;
}

#six-options button {
    min-height: 42px !important;
}

#live-status {
    text-align: center;
    font-size: 13px;
    padding: 2px;
}
"""


# =========================================================
# JAVASCRIPT
# =========================================================

JS = r"""
window.nexoraLiveSocket = null;
window.nexoraAudioContext = null;
window.nexoraMicStream = null;
window.nexoraProcessor = null;


// =======================================================
// MIC → TEXT
// =======================================================

window.startNexoraMic = function () {

    const box = document.querySelector(
        "#question textarea"
    );

    if (!box) {

        alert("Chat box नहीं मिला।");

        return;
    }

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        alert(
            "इस browser में Voice Input उपलब्ध नहीं है।"
        );

        return;
    }

    const recognition =
        new SpeechRecognition();

    recognition.lang = "hi-IN";

    recognition.interimResults = false;

    recognition.continuous = false;

    recognition.onstart = function () {

        box.placeholder =
            "🎙️ सुन रहा हूँ...";
    };

    recognition.onresult = function (event) {

        box.value =
            event.results[0][0].transcript;

        box.dispatchEvent(
            new Event(
                "input",
                {
                    bubbles: true
                }
            )
        );
    };

    recognition.onerror = function () {

        box.placeholder =
            "अपना सवाल लिखें...";
    };

    recognition.onend = function () {

        box.placeholder =
            "अपना सवाल लिखें...";
    };

    recognition.start();
};


// =======================================================
// LAST ANSWER
// =======================================================

function getLastAnswer() {

    const messages =
        document.querySelectorAll(
            "#chat .message"
        );

    if (!messages.length) {

        return "";
    }

    return (
        messages[messages.length - 1]
            .innerText || ""
    );
}


// =======================================================
// COPY
// =======================================================

window.copyLastAnswer = async function () {

    const text =
        getLastAnswer();

    if (!text) {

        return;
    }

    try {

        await navigator.clipboard.writeText(
            text
        );

        alert(
            "उत्तर कॉपी हो गया।"
        );

    } catch (e) {

        alert(
            "कॉपी नहीं हो पाया।"
        );
    }
};


// =======================================================
// SOUND
// =======================================================

window.soundLastAnswer = function () {

    const text =
        getLastAnswer();

    if (!text) {

        return;
    }

    speechSynthesis.cancel();

    const speech =
        new SpeechSynthesisUtterance(
            text
        );

    speech.lang = "hi-IN";

    speech.rate = 0.9;

    speechSynthesis.speak(
        speech
    );
};


// =======================================================
// SHARE
// =======================================================

window.shareLastAnswer = async function () {

    const text =
        getLastAnswer();

    if (!text) {

        return;
    }

    if (navigator.share) {

        try {

            await navigator.share({

                title: "Nexora AI",

                text: text
            });

        } catch (e) {}

    } else {

        try {

            await navigator.clipboard.writeText(
                text
            );

            alert(
                "Share उपलब्ध नहीं है। "
                + "उत्तर कॉपी कर दिया गया।"
            );

        } catch (e) {}
    }
};


// =======================================================
// PCM → BASE64
// =======================================================

function pcmToBase64(floatData) {

    const pcm =
        new Int16Array(
            floatData.length
        );

    for (
        let i = 0;
        i < floatData.length;
        i++
    ) {

        const sample =
            Math.max(
                -1,
                Math.min(
                    1,
                    floatData[i]
                )
            );

        pcm[i] =
            sample < 0
                ? sample * 32768
                : sample * 32767;
    }

    const bytes =
        new Uint8Array(
            pcm.buffer
        );

    let binary = "";

    const size = 0x8000;

    for (
        let i = 0;
        i < bytes.length;
        i += size
    ) {

        binary += String.fromCharCode(
            ...bytes.subarray(
                i,
                Math.min(
                    i + size,
                    bytes.length
                )
            )
        );
    }

    return btoa(binary);
}


// =======================================================
// BASE64 → PCM
// =======================================================

function base64ToPCM(base64) {

    const binary =
        atob(base64);

    const bytes =
        new Uint8Array(
            binary.length
        );

    for (
        let i = 0;
        i < binary.length;
        i++
    ) {

        bytes[i] =
            binary.charCodeAt(i);
    }

    return new Int16Array(
        bytes.buffer
    );
}


// =======================================================
// PLAY GEMINI AUDIO
// =======================================================

window.playNexoraPCM = async function (
    base64
) {

    try {

        if (
            !window.nexoraAudioContext
        ) {

            window.nexoraAudioContext =
                new AudioContext({
                    sampleRate: 24000
                });
        }

        const pcm =
            base64ToPCM(base64);

        const audio =
            window.nexoraAudioContext
                .createBuffer(
                    1,
                    pcm.length,
                    24000
                );

        const channel =
            audio.getChannelData(0);

        for (
            let i = 0;
            i < pcm.length;
            i++
        ) {

            channel[i] =
                pcm[i] / 32768;
        }

        const source =
            window.nexoraAudioContext
                .createBufferSource();

        source.buffer = audio;

        source.connect(
            window.nexoraAudioContext.destination
        );

        source.start();

    } catch (e) {

        console.log(
            "AUDIO ERROR:",
            e
        );
    }
};


// =======================================================
// START GEMINI LIVE
// =======================================================

window.startNexoraLive = async function (
    token
) {

    if (!token) {

        alert(
            "Live token नहीं मिला।"
        );

        return;
    }

    const status =
        document.querySelector(
            "#live-status"
        );

    if (status) {

        status.innerText =
            "🟢 Live शुरू हो रहा है...";
    }

    const url =
        "wss://generativelanguage.googleapis.com/ws/" +
        "google.ai.generativelanguage.v1beta." +
        "GenerativeService." +
        "BidiGenerateContentConstrained" +
        "?access_token=" +
        encodeURIComponent(token);

    const socket =
        new WebSocket(url);

    window.nexoraLiveSocket =
        socket;


    socket.onopen = async function () {

        socket.send(
            JSON.stringify({

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
            })
        );


        try {

            const stream =
                await navigator.mediaDevices
                    .getUserMedia({
                        audio: true
                    });

            window.nexoraMicStream =
                stream;


            const context =
                new AudioContext();

            window.nexoraAudioContext =
                context;


            const source =
                context.createMediaStreamSource(
                    stream
                );


            const processor =
                context.createScriptProcessor(
                    4096,
                    1,
                    1
                );

            window.nexoraProcessor =
                processor;


            processor.onaudioprocess =
                function (event) {

                    if (
                        socket.readyState !==
                        WebSocket.OPEN
                    ) {

                        return;
                    }

                    const input =
                        event.inputBuffer
                            .getChannelData(0);

                    socket.send(
                        JSON.stringify({

                            realtimeInput: {

                                audio: {

                                    data:
                                        pcmToBase64(
                                            input
                                        ),

                                    mimeType:
                                        "audio/pcm;rate=" +
                                        context.sampleRate
                                }
                            }
                        })
                    );
                };


            source.connect(
                processor
            );

            processor.connect(
                context.destination
            );


            if (status) {

                status.innerText =
                    "🟢 Live चालू है — बोलिए...";
            }

        } catch (e) {

            console.log(
                "MIC ERROR:",
                e
            );

            if (status) {

                status.innerText =
                    "⚠️ Microphone permission दें।";
            }
        }
    };


    socket.onmessage =
        async function (event) {

            try {

                const data =
                    JSON.parse(
                        event.data
                    );

                const parts =
                    data.serverContent
                        ?.modelTurn
                        ?.parts || [];


                for (
                    const part of parts
                ) {

                    if (
                        part.inlineData &&
                        part.inlineData.data
                    ) {

                        await
                        window.playNexoraPCM(
                            part.inlineData.data
                        );
                    }
                }

            } catch (e) {

                console.log(
                    "LIVE MESSAGE ERROR:",
                    e
                );
            }
        };


    socket.onerror =
        function (e) {

            console.log(
                "LIVE ERROR:",
                e
            );

            if (status) {

                status.innerText =
                    "⚠️ Live connection में समस्या हुई।";
            }
        };


    socket.onclose =
        function () {

            if (status) {

                status.innerText =
                    "⚪ Live बंद है";
            }
        };
};


// =======================================================
// STOP LIVE
// =======================================================

window.stopNexoraLive = function () {

    try {

        if (
            window.nexoraProcessor
        ) {

            window.nexoraProcessor.disconnect();

            window.nexoraProcessor =
                null;
        }


        if (
            window.nexoraMicStream
        ) {

            window.nexoraMicStream
                .getTracks()
                .forEach(
                    function (track) {

                        track.stop();
                    }
                );

            window.nexoraMicStream =
                null;
        }


        if (
            window.nexoraLiveSocket
        ) {

            window.nexoraLiveSocket.close();

            window.nexoraLiveSocket =
                null;
        }


        if (
            window.nexoraAudioContext
        ) {

            window.nexoraAudioContext
                .close()
                .catch(
                    function () {}
                );

            window.nexoraAudioContext =
                null;
        }


        const status =
            document.querySelector(
                "#live-status"
            );

        if (status) {

            status.innerText =
                "⚪ Live बंद है";
        }

    } catch (e) {

        console.log(
            "STOP LIVE ERROR:",
            e
        );
    }
};
"""


# =========================================================
# NEXORA APP
# =========================================================

with gr.Blocks(
    title="Nexora AI"
) as app:


    # =====================================================
    # HEADER
    # =====================================================

    with gr.Row(
        elem_id="header"
    ):

        gr.Markdown(
            "# 🤖 Nexora AI"
        )

        new_chat_btn = gr.Button(
            "＋ नया चैट",
            scale=0
        )


    # =====================================================
    # CHAT
    # =====================================================

    chat = gr.Chatbot(
        value=[],
        show_label=False,
        autoscroll=True,
        height="calc(100vh - 240px)",
        elem_id="chat"
    )


    # =====================================================
    # INPUT
    # =====================================================

    with gr.Row(
        elem_id="input-area"
    ):

        question = gr.Textbox(
            placeholder="अपना सवाल लिखें...",
            show_label=False,
            lines=1,
            scale=8,
            elem_id="question"
        )

        mic_btn = gr.Button(
            "🎙️",
            scale=0
        )

        send_btn = gr.Button(
            "➤",
            variant="primary",
            scale=0
        )


    # =====================================================
    # GEMINI LIVE
    # =====================================================

    with gr.Row():

        live_status = gr.Markdown(
            "⚪ Live बंद है",
            elem_id="live-status"
        )

        live_start = gr.Button(
            "🎧 Gemini Live",
            scale=0
        )

        live_stop = gr.Button(
            "✕",
            scale=0
        )


    live_token = gr.Textbox(
        visible=False
    )


    # =====================================================
    # SIX OPTIONS
    # =====================================================

    with gr.Row(
        elem_id="six-options"
    ):

        like_btn = gr.Button(
            "👍 Like"
        )

        dislike_btn = gr.Button(
            "👎 Dislike"
        )

        sound_btn = gr.Button(
            "🔊 Sound"
        )

        copy_btn = gr.Button(
            "📋 Copy"
        )

        share_btn = gr.Button(
            "↗️ Share"
        )

        more_btn = gr.Button(
            "⋯ More"
        )


    feedback = gr.Markdown(
        ""
    )


    # =====================================================
    # SEND
    # =====================================================

    send_btn.click(
        fn=ask_nexora,
        inputs=[
            question,
            chat
        ],
        outputs=[
            chat,
            question
       
