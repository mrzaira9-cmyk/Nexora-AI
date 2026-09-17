
import os
import datetime
import html
import gradio as gr
from google import genai

# ============================================================
# Nexora AI - Complete app.py
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

TEXT_MODEL = "gemini-3.5-flash-lite"
LIVE_MODEL = "gemini-3.8-live"

client = genai.Client(api_key=API_KEY)


SYSTEM_PROMPT = """
तुम Nexora AI हो।
हमेशा सरल, स्पष्ट और स्वाभाविक हिंदी में उत्तर दो।
हिंदी सवाल का उत्तर देवनागरी हिंदी में दो।
Roman Hindi या Hinglish में उत्तर मत दो, जब तक उपयोगकर्ता विशेष रूप से ऐसा न कहे।
तथात्मक प्रश्नों का सही और स्पष्ट उत्तर दो।
"""


def make_chat_html(history):
    """Build the visible ChatGPT-style conversation area."""
    if not history:
        return """
        <div class="nexora-empty">
            <div class="nexora-logo">🤖</div>
            <h2>Nexora AI</h2>
            <p>मुझसे अपना सवाल पूछिए</p>
        </div>
        """

    parts = ['<div class="nexora-chat-list">']

    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        safe = html.escape(str(content)).replace("\n", "<br>")

        if role == "user":
            parts.append(f"""
            <div class="nexora-message user-message">
                <div class="message-bubble user-bubble">{safe}</div>
            </div>
            """)
        elif role == "assistant":
            parts.append(f"""
            <div class="nexora-message assistant-message">
                <div class="assistant-name">🤖 Nexora AI</div>
                <div class="message-bubble assistant-bubble nexora-answer">{safe}</div>
                <div class="answer-actions">
                    <button class="answer-action" data-action="like" title="Like">👍</button>
                    <button class="answer-action" data-action="dislike" title="Dislike">👎</button>
                    <button class="answer-action" data-action="sound" title="Sound">🔊</button>
                    <button class="answer-action" data-action="copy" title="Copy">📋</button>
                    <button class="answer-action" data-action="share" title="Share">↗️</button>
                    <button class="answer-action" data-action="more" title="More">⋯</button>
                </div>
            </div>
            """)

    parts.append("</div>")
    return "".join(parts)


def ask_nexora(question, history):
    question = (question or "").strip()
    history = history or []

    if not question:
        return make_chat_html(history), history, ""

    context = []
    for item in history[-10:]:
        if isinstance(item, dict) and item.get("content"):
            role = item.get("role", "")
            content = item.get("content", "")
            context.append(f"{role}: {content}")

    prompt = SYSTEM_PROMPT

    if context:
        prompt += "\n\nपिछली बातचीत:\n" + "\n".join(context)

    prompt += f"\n\nनया सवाल:\n{question}"

    try:
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )
        answer = (response.text or "मुझे अभी उत्तर नहीं मिला।").strip()
    except Exception as exc:
        answer = f"⚠️ उत्तर देने में समस्या हुई:\n{exc}"

    new_history = list(history)
    new_history.append({"role": "user", "content": question})
    new_history.append({"role": "assistant", "content": answer})

    return make_chat_html(new_history), new_history, ""


def new_chat():
    return make_chat_html([]), []


def create_live_token():
    now = datetime.datetime.now(datetime.timezone.utc)

    token = client.auth_tokens.create(
        config={
            "uses": 1,
            "expire_time": now + datetime.timedelta(minutes=30),
            "new_session_expire_time": now + datetime.timedelta(minutes=1),
            "live_connect_constraints": {
                "model": LIVE_MODEL,
                "config": {
                    "response_modalities": ["AUDIO"],
                    "session_resumption": {}
                }
            }
        }
    )

    return token.name


CSS = r"""
:root {
    --nexora-border: #e5e7eb;
    --nexora-soft: #f7f7f8;
    --nexora-user: #eaf3ff;
}

body {
    margin: 0 !important;
}

.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
}

#nexora-app {
    min-height: 100vh;
}

#chat-wrap {
    height: calc(100vh - 178px);
    min-height: 430px;
    overflow-y: auto;
    padding: 18px 12px 12px 12px;
    box-sizing: border-box;
    scroll-behavior: smooth;
}

#chat-html {
    max-width: 900px;
    margin: 0 auto;
}

.nexora-empty {
    min-height: calc(100vh - 245px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #6b7280;
}

.nexora-empty .nexora-logo {
    font-size: 52px;
    margin-bottom: 4px;
}

.nexora-empty h2 {
    margin: 0;
    color: #222;
    font-size: 28px;
}

.nexora-empty p {
    margin-top: 8px;
    font-size: 16px;
}

.nexora-chat-list {
    display: flex;
    flex-direction: column;
    gap: 22px;
    padding-bottom: 12px;
}

.nexora-message {
    display: flex;
    flex-direction: column;
    max-width: 100%;
}

.user-message {
    align-items: flex-end;
}

.assistant-message {
    align-items: flex-start;
}

.message-bubble {
    max-width: min(82%, 760px);
    padding: 11px 14px;
    border-radius: 16px;
    line-height: 1.55;
    font-size: 16px;
    word-break: break-word;
}

.user-bubble {
    background: var(--nexora-user);
    border-bottom-right-radius: 5px;
}

.assistant-bubble {
    background: var(--nexora-soft);
    border: 1px solid var(--nexora-border);
    border-bottom-left-radius: 5px;
}

.assistant-name {
    font-size: 13px;
    font-weight: 600;
    margin: 0 0 5px 4px;
}

.answer-actions {
    display: flex;
    gap: 5px;
    margin: 6px 0 0 2px;
}

.answer-action {
    border: 0;
    background: transparent;
    border-radius: 8px;
    padding: 5px 8px;
    font-size: 17px;
    cursor: pointer;
}

.answer-action:hover {
    background: #eeeeee;
}

#bottom {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 50;
    background: rgba(255,255,255,.97);
    border-top: 1px solid var(--nexora-border);
    padding: 7px 10px 8px;
}

#bottom-inner {
    max-width: 900px;
    margin: 0 auto;
}

#question textarea {
    font-size: 16px !important;
    border-radius: 14px !important;
    min-height: 48px !important;
}

.main-row {
    gap: 7px !important;
    margin-top: 6px;
}

.main-row button {
    min-height: 42px !important;
}

.tool-row {
    gap: 4px !important;
    margin-top: 5px;
}

.tool-row button {
    min-height: 38px !important;
    font-size: 17px !important;
}

#new-chat button {
    margin-top: 4px;
    min-height: 34px !important;
}

#status {
    text-align: center;
    font-size: 13px;
    min-height: 0 !important;
}

@media (max-width: 600px) {
    #chat-wrap {
        height: calc(100vh - 190px);
        min-height: 360px;
        padding: 12px 8px 8px;
    }

    .message-bubble {
        max-width: 90%;
        font-size: 15px;
    }

    .answer-action {
        font-size: 16px;
        padding: 5px 7px;
    }

    #bottom {
        padding: 5px 7px 6px;
    }
}
"""


JS = r"""
() => {
    const S = {
        rec: null,
        live: null,
        audioCtx: null,
        processor: null,
        stream: null,
        source: null,
        nextAudioTime: 0
    };

    function questionBox() {
        return document.querySelector("#question textarea");
    }

    function setQuestion(text) {
        const box = questionBox();
        if (!box) return;

        const setter = Object.getOwnPropertyDescriptor(
            HTMLTextAreaElement.prototype,
            "value"
        ).set;

        setter.call(box, text || "");
        box.dispatchEvent(new Event("input", { bubbles: true }));
        box.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function getAnswer(button) {
        const message = button.closest(".assistant-message");
        if (!message) return "";
        const answer = message.querySelector(".nexora-answer");
        return answer ? (answer.innerText || "").trim() : "";
    }

    function showStatus(text) {
        const status = document.querySelector("#status");
        if (status) status.innerText = text;
    }

    window.startNexoraMic = () => {
        const Recognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!Recognition) {
            alert("इस browser में Speech Recognition उपलब्ध नहीं है।");
            return;
        }

        try {
            if (S.rec) S.rec.stop();
        } catch (e) {}

        const recognition = new Recognition();
        recognition.lang = "hi-IN";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => showStatus("🎤 सुन रहा हूँ...");
        recognition.onend = () => showStatus("");

        recognition.onresult = (event) => {
            const text =
                event.results &&
                event.results[0] &&
                event.results[0][0]
                    ? event.results[0][0].transcript
                    : "";

            setQuestion(text);
        };

        recognition.onerror = (event) => {
            console.log("Speech recognition:", event);
            showStatus("⚠️ आवाज़ पहचान नहीं हो पाई।");
            setTimeout(() => showStatus(""), 2500);
        };

        S.rec = recognition;
        recognition.start();
    };

    async function copyText(text) {
        if (!text) return;

        try {
            await navigator.clipboard.writeText(text);
            showStatus("📋 उत्तर copy हो गया।");
        } catch (e) {
            const area = document.createElement("textarea");
            area.value = text;
            document.body.appendChild(area);
            area.select();
            document.execCommand("copy");
            area.remove();
            showStatus("📋 उत्तर copy हो गया।");
        }

        setTimeout(() => showStatus(""), 1800);
    }

    function speakText(text) {
        if (!text) return;

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "hi-IN";
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    }

    async function shareText(text) {
        if (!text) return;

        if (navigator.share) {
            try {
                await navigator.share({
                    title: "Nexora AI",
                    text: text
                });
                return;
            } catch (e) {}
        }

        await copyText(text);
        showStatus("↗️ Share उपलब्ध नहीं है, उत्तर copy कर दिया गया।");
    }

    document.addEventListener("click", async (event) => {
        const button = event.target.closest(".answer-action");
        if (!button) return;

        const action = button.dataset.action;
        const text = getAnswer(button);

        if (action === "like") {
            showStatus("👍 धन्यवाद! Feedback दर्ज हो गया।");
        } else if (action === "dislike") {
            showStatus("👎 धन्यवाद! Feedback दर्ज हो गया।");
        } else if (action === "sound") {
            speakText(text);
        } else if (action === "copy") {
            await copyText(text);
        } else if (action === "share") {
            await shareText(text);
        } else if (action === "more") {
            showStatus("⋯ Copy, Like, Dislike, Sound, Share और Live Voice उपलब्ध हैं।");
        }

        if (action === "like" || action === "dislike" || action === "more") {
            setTimeout(() => showStatus(""), 2200);
        }
    });

    function scrollChatToBottom() {
        const wrap = document.querySelector("#chat-wrap");
        if (wrap) {
            setTimeout(() => {
                wrap.scrollTop = wrap.scrollHeight;
            }, 80);
        }
    }

    // Scroll whenever the chat HTML changes.
    const observer = new MutationObserver(() => scrollChatToBottom());

    function startObserver() {
        const target = document.querySelector("#chat-wrap");
        if (target) observer.observe(target, { childList: true, subtree: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", startObserver);
    } else {
        startObserver();
    }

    // ========================================================
    // Gemini Live Voice
    // ========================================================

    function base64ToBytes(value) {
        const raw = atob(value);
        const bytes = new Uint8Array(raw.length);

        for (let i = 0; i < raw.length; i++) {
            bytes[i] = raw.charCodeAt(i);
        }

        return bytes;
    }

    function playPcm24k(base64) {
        try {
            if (!S.audioCtx) {
                S.audioCtx = new (
                    window.AudioContext || window.webkitAudioContext
                )();
            }

            if (S.audioCtx.state === "suspended") {
                S.audioCtx.resume();
            }

            const bytes = base64ToBytes(base64);
            const view = new DataView(
                bytes.buffer,
                bytes.byteOffset,
                bytes.byteLength
            );

            const samples = new Float32Array(Math.floor(bytes.length / 2));

            for (let i = 0; i < samples.length; i++) {
                samples[i] =
                    view.getInt16(i * 2, true) / 32768.0;
            }

            const buffer = S.audioCtx.createBuffer(
                1,
                samples.length,
                24000
            );

            buffer.copyToChannel(samples, 0);

            const node = S.audioCtx.createBufferSource();
            node.buffer = buffer;
            node.connect(S.audioCtx.destination);

            const startAt = Math.max(
                S.audioCtx.currentTime,
                S.nextAudioTime
            );

            node.start(startAt);
            S.nextAudioTime = startAt + buffer.duration;
        } catch (e) {
            console.error("Live audio playback error:", e);
        }
    }

    function bytesToBase64(bytes) {
        let binary = "";
        const chunk = 0x8000;

        for (let i = 0; i < bytes.length; i += chunk) {
            binary += String.fromCharCode(
                ...bytes.subarray(i, i + chunk)
            );
        }

        return btoa(binary);
    }

    async function startLiveMicrophone() {
        S.stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        const audioContext = new (
            window.AudioContext || window.webkitAudioContext
        )();

        const source = audioContext.createMediaStreamSource(S.stream);

        // ScriptProcessor is widely supported in browsers and keeps
        // this client-side implementation simple.
        const processor = audioContext.createScriptProcessor(
            4096,
            1,
            1
        );

        S.processor = processor;
        S.source = source;

        processor.onaudioprocess = (event) => {
            if (!S.live) return;

            const input = event.inputBuffer.getChannelData(0);
            const pcm = new Int16Array(input.length);

            for (let i = 0; i < input.length; i++) {
                const value = Math.max(-1, Math.min(1, input[i]));
                pcm[i] = value < 0
                    ? value * 32768
                    : value * 32767;
            }

            const base64 = bytesToBase64(
                new Uint8Array(pcm.buffer)
            );

            try {
                S.live.sendRealtimeInput({
                    audio: {
                        data: base64,
                        mimeType: "audio/pcm;rate=16000"
                    }
                });
            } catch (e) {
                console.log("Live input error:", e);
            }
        };

        source.connect(processor);
        processor.connect(audioContext.destination);
    }

    window.startNexoraLive = async (token) => {
        if (!token) {
            alert("Live token नहीं मिला।");
            return;
        }

        try {
            showStatus("🔴 Live Voice शुरू हो रहा है...");

            const module = await import(
                "https://esm.sh/@google/genai"
            );

            const ai = new module.GoogleGenAI({
                apiKey: token
            });

            S.live = await ai.live.connect({
                model: "gemini-3.8-live",
                config: {
                    responseModalities: ["AUDIO"],
                    systemInstruction:
                        "तुम Nexora AI हो। सरल और स्पष्ट हिंदी में बोलो।",
                    sessionResumption: {}
                },
                callbacks: {
                    onmessage: (message) => {
                        const parts =
                            message &&
                            message.serverContent &&
                            message.serverContent.modelTurn &&
                            message.serverContent.modelTurn.parts;

                        if (!parts) return;

                        for (const part of parts) {
                            if (
                                part.inlineData &&
                                part.inlineData.data
                            ) {
                                playPcm24k(part.inlineData.data);
                            }
                        }
                    },
                    onerror: (error) => {
                        console.error("Live error:", error);
                        showStatus("⚠️ Live Voice में समस्या हुई।");
                    },
                    onclose: () => {
                        showStatus("");
                    }
                }
            });

            await startLiveMicrophone();
            showStatus("🔴 Live Voice चालू है — बोलिए...");
        } catch (error) {
            console.error("Live start error:", error);
            showStatus("⚠️ Live Voice शुरू नहीं हो पाया।");
            alert("Live Voice शुरू नहीं हो पाया।");
            await stopLive();
        }
    };

    async function stopLive() {
        try {
            if (S.processor) S.processor.disconnect();
        } catch (e) {}

        try {
            if (S.source) S.source.disconnect();
        } catch (e) {}

        try {
            if (S.stream) {
                S.stream.getTracks().forEach(
                    track => track.stop()
                );
            }
        } catch (e) {}

        try {
            if (S.live) S.live.close();
        } catch (e) {}

        S.live = null;
        S.processor = null;
        S.source = null;
        S.stream = null;

        showStatus("");
    }

    window.stopNexoraLive = stopLive;
}
"""

with gr.Blocks(
    title="Nexora AI",
    css=CSS,
    js=JS
) as app:

    with gr.Column(elem_id="nexora-app"):
        gr.Markdown(
            "<h2 style='text-align:center;margin:8px 0 4px;'>🤖 Nexora AI</h2>"
        )

        with gr.Column(elem_id="chat-wrap"):
            chat_html = gr.HTML(
                make_chat_html([]),
                elem_id="chat-html"
            )

        status = gr.Markdown("", elem_id="status")

        with gr.Column(elem_id="bottom"):
            with gr.Column(elem_id="bottom-inner"):
                question = gr.Textbox(
                    placeholder="यहाँ अपना सवाल लिखें या 🎤 बोलें...",
                    show_label=False,
                    lines=2,
                    elem_id="question"
                )

                with gr.Row(elem_classes=["main-row"]):
                    send_btn = gr.Button("➤ with gr.Row(elem_classes=["main-row"]):
    send_btn = gr.Button("➤ भेजें",
    variant="primary")
    mic_btn = gr.Button("🎤")
    live_start = gr.Button("🔴 Live")
    live_stop = gr.Button("⏹️")
                                         
