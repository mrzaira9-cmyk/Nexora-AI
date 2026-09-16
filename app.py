import os
import json
import datetime
import gradio as gr
from google import genai


# =========================================================
# API
# =========================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable नहीं मिला।")


client = genai.Client(api_key=API_KEY)

TEXT_MODEL = "gemini-3.5-flash-lite"
LIVE_MODEL = "gemini-3.8-live"


# =========================================================
# MEMORY
# =========================================================

conversation_memory = []


# =========================================================
# TEXT AI
# =========================================================

def ask_nexora(question, history):

    question = (question or "").strip()

    if not question:
        return history, ""

    try:

        context = ""

        for item in history[-10:]:
            if isinstance(item, dict):
                role = item.get("role", "")
                content = item.get("content", "")

                if role in ["user", "assistant"]:
                    context += f"{role}: {content}\n"

        prompt = f"""
आप Nexora AI हैं।

नियम:
- उपयोगकर्ता जिस भाषा में पूछे, उसी भाषा में उत्तर दें।
- हिंदी में पूछा जाए तो देवनागरी हिंदी में उत्तर दें।
- उत्तर साफ, सरल और तथ्यात्मक रखें।
- बातचीत के पिछले संदेशों का संदर्भ रखें।
- अगर प्रश्न वर्तमान जानकारी मांगता है और आपके पास निश्चित जानकारी नहीं है,
  तो अनुमान न लगाएँ।

पिछली बातचीत:
{context}

नया प्रश्न:
{question}
"""

        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )

        answer = response.text or "मुझे अभी उत्तर नहीं मिला।"

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

    except Exception as e:

        new_history = list(history)

        new_history.append({
            "role": "user",
            "content": question
        })

        new_history.append({
            "role": "assistant",
            "content": "⚠️ उत्तर देते समय समस्या हुई। कृपया फिर कोशिश करें।"
        })

        print("ERROR:", e)

        return new_history, ""


# =========================================================
# NEW CHAT
# =========================================================

def new_chat():
    return []


# =========================================================
# LIKE / DISLIKE
# =========================================================

def like_answer():
    return "👍 धन्यवाद!"


def dislike_answer():
    return "👎 आपका feedback दर्ज किया गया।"


def more_answer():
    return "⋯ Nexora AI के और विकल्प जल्द जोड़े जाएँगे।"


# =========================================================
# LIVE TOKEN
# =========================================================

def create_live_token():

    try:

        now = datetime.datetime.now(
            tz=datetime.timezone.utc
        )

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

html, body {
    margin: 0 !important;
    padding: 0 !important;
}

.gradio-container {
    max-width: 100% !important;
    min-height: 100vh !important;
    padding: 0 !important;
}

#header {
    padding: 12px 16px 5px 16px;
}

#chat {
    height: calc(100vh - 190px) !important;
}

#input-area {
    position: sticky;
    bottom: 0;
    background: white;
    padding: 8px;
    z-index: 20;
}

#question textarea {
    min-height: 48px !important;
    max-height: 120px !important;
}

#bottom-buttons button {
    min-height: 42px !important;
}

#live-status {
    text-align: center;
    font-size: 14px;
    padding: 3px;
}

"""


# =========================================================
# JAVASCRIPT
# =========================================================

JS = r"""

// =======================================================
// GLOBAL
// =======================================================

window.nexoraLiveSocket = null;
window.nexoraAudioContext = null;
window.nexoraMicStream = null;
window.nexoraProcessor = null;


// =======================================================
// MICROPHONE → TEXT
// =======================================================

window.startNexoraMic = function() {

    const box =
        document.querySelector(
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

    recognition.onstart = function() {

        box.placeholder =
            "🎙️ सुन रहा हूँ... बोलिए";
    };

    recognition.onresult = function(event) {

        const text =
            event.results[0][0].transcript;

        box.value = text;

        box.dispatchEvent(
            new Event("input", {
                bubbles: true
            })
        );

        box.placeholder =
            "अपना सवाल लिखें...";
    };

    recognition.onerror = function() {

        box.placeholder =
            "अपना सवाल लिखें...";
    };

    recognition.onend = function() {

        box.placeholder =
            "अपना सवाल लिखें...";
    };

    recognition.start();
};


// =======================================================
// COPY
// =======================================================

window.copyLastAnswer = async function() {

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
        last.innerText || "";

    if (!text) {
        return;
    }

    try {

        await navigator.clipboard.writeText(text);

        alert("उत्तर कॉपी हो गया।");

    } catch(e) {

        alert("कॉपी नहीं हो पाया।");
    }
};


// =======================================================
// SOUND
// =======================================================

window.soundLastAnswer = function() {

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
        last.innerText || "";

    if (!text) {
        return;
    }

    speechSynthesis.cancel();

    const speech =
        new SpeechSynthesisUtterance(text);

    speech.lang = "hi-IN";

    speech.rate = 0.9;

    speechSynthesis.speak(speech);
};


// =======================================================
// SHARE
// =======================================================

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
        last.innerText || "";

    if (!text) {
        return;
    }

    if (navigator.share) {

        try {

            await navigator.share({

                title: "Nexora AI",

                text: text
            });

        } catch(e) {}

    } else {

        try {

            await navigator.clipboard.writeText(text);

            alert(
                "Share उपलब्ध नहीं है। उत्तर कॉपी कर दिया गया।"
            );

        } catch(e) {}
    }
};


// =======================================================
// LIVE AUDIO HELPERS
// =======================================================

function base64FromArrayBuffer(buffer) {

    let binary = "";

    const bytes =
        new Uint8Array(buffer);

    const chunkSize = 0x8000;

    for (
        let i = 0;
        i < bytes.length;
        i += chunkSize
    ) {

        binary += String.fromCharCode(
            ...bytes.subarray(
                i,
                Math.min(
                    i + chunkSize,
                    bytes.length
                )
            )
        );
    }

    return btoa(binary);
}


function base64ToArrayBuffer(base64) {

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

    return bytes.buffer;
}


// =======================================================
// PLAY GEMINI AUDIO
// =======================================================

window.playNexoraPCM = async function(base64) {

    try {

        if (!window.nexoraAudioContext) {

            window.nexoraAudioContext =
                new AudioContext({
                    sampleRate: 24000
                });
        }

        const raw =
            new Int16Array(
                base64ToArrayBuffer(base64)
            );

        const audioBuffer =
            window.nexoraAudioContext.createBuffer(
                1,
                raw.length,
                24000
            );

        const channel =
            audioBuffer.getChannelData(0);

        for (
            let i = 0;
            i < raw.length;
            i++
        ) {

            channel[i] =
                raw[i] / 32768;
        }

        const source =
            window.nexoraAudioContext.createBufferSource();

        source.buffer =
            audioBuffer;

        source.connect(
            window.nexoraAudioContext.destination
        );

        source.start();

    } catch(e) {

        console.log(
            "Audio playback error:",
            e
        );
    }
};


// =======================================================
// START LIVE
// =======================================================

window.startNexoraLive = async function(token) {

    if (!token) {

        alert(
            "Live token नहीं मिला।"
        );

        return;
    }

    try {

        const status =
            document.querySelector(
                "#live-status"
            );

        if (status) {
            status.innerText =
                "🟢 Live चालू हो रहा है...";
        }


        const url =
            "wss://generativelanguage.googleapis.com/ws/" +
            "google.ai.generativelanguage.v1beta." +
            "GenerativeService.BidiGenerateContentConstrained" +
            "?access_token=" +
            encodeURIComponent(token);


        const socket =
            new WebSocket(url);

        window.nexoraLiveSocket =
            socket;


        socket.onopen = async function() {

            const setup = {

                setup: {

                    model:
                        "models/gemini-3.8-live",

                    generationConfig: {

                        responseModalities: [
                            "AUDIO"
                        ]
                    },

                    systemInstruction: {

                        parts: [

                            {
                                text:
                                    "You are Nexora AI. " +
                                    "Be helpful and concise. " +
                                    "Answer in the user's language."
                            }

                        ]
                    }
                }
            };


            socket.send(
                JSON.stringify(setup)
            );


            try {

                window.nexoraMicStream =
                    await navigator.mediaDevices
                        .getUserMedia({
                            audio: true
                        });


                window.nexoraAudioContext =
                    new AudioContext();


                const source =
                    window.nexoraAudioContext
                        .createMediaStreamSource(
                            window.nexoraMicStream
                        );


                const processor =
                    window.nexoraAudioContext
                        .createScriptProcessor(
                            4096,
                            1,
                            1
                        );


                window.nexoraProcessor =
                    processor;


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
                            new Int16Array(
                                input.length
                            );


                        for (
                            let i = 0;
                            i < input.length;
                            i++
                        ) {

                            let sample =
                                Math.max(
                                    -1,
                                    Math.min(
                                        1,
                                        input[i]
                                    )
                                );

                            pcm[i] =
                                sample < 0
                                    ? sample * 32768
                                    : sample * 32767;
                        }


                        socket.send(
                            JSON.stringify({

                                realtimeInput: {

                                    audio: {

                                        data:
                                            base64FromArrayBuffer(
                                                pcm.buffer
                                            ),

                                        mimeType:
                                            "audio/pcm;rate=" +
                                            window.nexoraAudioContext
                                                .sampleRate
                                    }
                                }
                            })
                        );
                    };


                source.connect(processor);

                processor.connect(
                    window.nexoraAudioContext.destination
                );


                if (status) {

                    status.innerText =
                        "🟢 Live चालू है — बोलिए...";
                }

            } catch(e) {

                console.log(
                    "Microphone error:",
                    e
                );

                if (status) {

                    status.innerText =
                        "⚠️ Microphone permission दें।";
                }
            }
        };


        socket.onmessage =
            async function(event) {

                try {

                    const data =
                        JSON.parse(
                            event.data
                        );


                    if (
                        data.serverContent &&
                        data.serverContent.modelTurn
                    ) {

                        const parts =
                            data.serverContent
                                .modelTurn.parts || [];


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
                    }


                    if (
                        data.serverContent &&
                        data.serverContent.outputTranscription
                    ) {

                        const text =
                            data.serverContent
                                .outputTranscription
                                .text;

                        console.log(
                            "Nexora:",
                            text
                        );
                    }

                } catch(e) {

                    console.log(
                        "Live message error:",
                        e
                    );
                }
            };


        socket.onerror =
            function(error) {

                console.log(
                    "Live WebSocket error:",
                    error
                );

                const status =
                    document.querySelector(
                        "#live-status"
                    );

                if (status) {

                    status.innerText =
                        "⚠️ Live connection में समस्या हुई।";
                }
            };


        socket.onclose =
            function() {

                const status =
                    document.querySelector(
                        "#live-status"
                    );

                if (status) {

                    status.innerText =
                        "⚪ Live बंद है";
                }
            };

    } catch(e) {

        console.log(
            "Live error:",
            e
        );

        alert(
            "Live शुरू नहीं हो पाया।"
        );
    }
};


// =======================================================
// STOP LIVE
// =======================================================

window.stopNexoraLive = function() {

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
                    track => track.stop()
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


        const status =
            document.querySelector(
                "#live-status"
            );

        if (status) {

            status.innerText =
  
