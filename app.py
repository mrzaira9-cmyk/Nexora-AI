import os
import datetime
import html
import gradio as gr
from google import genai

# ============================================================
# Nexora AI - Fast ChatGPT-style Gradio app
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

# सही और उपलब्ध मॉडल नाम सेट किए गए हैं
TEXT_MODEL = "gemini-2.5-flash"
LIVE_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
तुम Nexora AI हो।
हमेशा सरल, स्पष्ट और स्वाभाविक हिंदी में उत्तर दो।
हिंदी सवाल का उत्तर देवनागरी हिंदी में दो।
Roman Hindi या Hinglish में उत्तर मत दो, जब तक उपयोगकर्ता विशेष रूप से ऐसा न कहे।
तथात्मक प्रश्नों का सही और स्पष्ट उत्तर दो।
उत्तर सीधे सवाल पर दो और अनावश्यक लंबी भूमिका से बचो।
""".strip()


def make_chat_html(history):
if not history:
return """
<div class="home-screen">
<div class="home-logo">N</div>
<h1>Nexora AI</h1>
<p>मुझसे कुछ भी पूछिए</p>
<div class="suggestions">
<button class="suggestion" data-prompt="भारत की राजधानी क्या है?">
<span>💡</span><b>जानकारी पूछें</b><small>किसी भी विषय पर सवाल पूछें</small>
</button>
<button class="suggestion" data-prompt="एक आसान और मज़ेदार कहानी सुनाइए।">
<span>✍️</span><b>लिखने में मदद</b><small>कहानी, संदेश या लेख लिखें</small>
</button>
<button class="suggestion" data-prompt="मुझे Python सीखने की शुरुआत समझाइए।">
<span>💻</span><b>सीखने में मदद</b><small>कोड और पढ़ाई में सहायता</small>
</button>
<button class="suggestion" data-prompt="आज के लिए एक उपयोगी productivity plan बनाइए।">
<span>🧠</span><b>योजना बनाएं</b><small>काम को आसान तरीके से व्यवस्थित करें</small>
</button>
</div>
</div>
"""

parts = ['<div class="chat-list">']

for item in history:
role = item.get("role", "") if isinstance(item, dict) else ""
content = item.get("content", "") if isinstance(item, dict) else ""
safe = html.escape(str(content)).replace("\n", "<br>")

if role == "user":
parts.append(f"""
<div class="message-row user-row">
<div class="user-bubble">{safe}</div>
</div>
""")
elif role == "assistant":
parts.append(f"""
<div class="message-row assistant-row">
<div class="assistant-head">
<div class="assistant-avatar">N</div>
<span>Nexora AI</span>
</div>
<div class="assistant-answer nexora-answer">{safe}</div>
<div class="answer-actions" aria-label="उत्तर विकल्प">
<button class="answer-action" data-action="copy" title="Copy">▢</button>
<button class="answer-action" data-action="like" title="Like">♡</button>
<button class="answer-action" data-action="dislike" title="Dislike">♧</button>
<button class="answer-action" data-action="sound" title="Sound">◖))</button>
<button class="answer-action" data-action="share" title="Share">⌯</button>
<button class="answer-action" data-action="more" title="More">•••</button>
</div>
</div>
""")

parts.append("</div>")
return "".join(parts)


def build_prompt(question, history):
context = []
for item in (history or [])[-6:]:
if isinstance(item, dict) and item.get("content"):
role = item.get("role", "")
content = item.get("content", "")
context.append(f"{role}: {content}")

prompt = SYSTEM_PROMPT
if context:
prompt += "\n\nपिछली बातचीत:\n" + "\n".join(context)
prompt += f"\n\nनया सवाल:\n{question}"
return prompt


def ask_nexora(question, history):
question = (question or "").strip()
history = list(history or [])

if not question:
yield make_chat_html(history), history, ""
return

base_history = history + [{"role": "user", "content": question}]
working_history = base_history + [{"role": "assistant", "content": "▌"}]
yield make_chat_html(working_history), working_history, "⏳ Nexora AI लिख रहा है..."

prompt = build_prompt(question, history)
answer_parts = []

try:
stream = client.models.generate_content_stream(
model=TEXT_MODEL,
contents=prompt,
)

for chunk in stream:
piece = getattr(chunk, "text", None) or ""
if not piece:
continue
answer_parts.append(piece)
current_answer = "".join(answer_parts).strip()
working_history = base_history + [{
"role": "assistant",
"content": current_answer + "▌"
}]
yield make_chat_html(working_history), working_history, ""

answer = "".join(answer_parts).strip()
if not answer:
response = client.models.generate_content(
model=TEXT_MODEL,
contents=prompt,
)
answer = (getattr(response, "text", None) or "मुझे अभी उत्तर नहीं मिला।").strip()

except Exception as exc:
answer = f"⚠️ उत्तर देने में समस्या हुई:\n{exc}"

final_history = base_history + [{"role": "assistant", "content": answer}]
yield make_chat_html(final_history), final_history, ""


def new_chat():
return make_chat_html([]), []


def create_live_token():
# Gradio के लिए एक साधारण स्ट्रिंग टोकन रिटर्न किया गया है ताकि लाइव कॉल क्रैश न हो
return API_KEY


CSS = r"""
:root {
--bg: #ffffff;
--panel: #f7f7f8;
--text: #202123;
--muted: #6b7280;
--border: #e5e7eb;
--hover: #eeeeee;
--user: #e8f1ff;
--composer: #ffffff;
}

* { box-sizing: border-box; }
html, body { margin: 0 !important; padding: 0 !important; height: 100%; }
body { background: var(--bg) !important; color: var(--text) !important; }
.gradio-container { max-width: none !important; width: 100% !important; padding: 0 !important; margin: 0 !important; }
footer { display: none !important; }

#app-shell { min-height: 100vh; background: var(--bg); }
#topbar {
position: fixed;
top: 0; left: 0; right: 0;
height: 58px;
z-index: 100;
display: flex;
align-items: center;
justify-content: space-between;
padding: 7px 12px;
background: rgba(255,255,255,.96);
border-bottom: 1px solid var(--border);
backdrop-filter: blur(10px);
}
#brand-box { display:flex; align-items:center; gap:9px; }
#brand-icon {
width: 34px; height:34px; border-radius: 11px;
display:flex; align-items:center; justify-content:center;
color:#fff; font-weight:800;
background: linear-gradient(135deg,#06b6d4,#6366f1,#a855f7);
}
#brand-name { font-weight:700; font-size:17px; }
#brand-sub { color:var(--muted); font-size:11px; margin-top:1px; }

.top-button button {
min-width: 40px !important; height: 40px !important;
border-radius: 10px !important;
border: 0 !important;
background: transparent !important;
color: var(--text) !important;
font-size: 20px !important;
padding: 0 9px !important;
}
.top-button button:hover { background: var(--hover) !important; }
#top-title { flex: 1; margin: 0 12px; }
#top-title button { font-weight:600 !important; font-size:15px !important; }

#chat-wrap {
position: fixed;
top: 58px;
left: 0; right: 0; bottom: 125px;
overflow-y: auto !important;
overflow-x: hidden !important;
padding: 18px 12px 35px !important;
scroll-behavior: auto !important;
-webkit-overflow-scrolling: touch;
}
#chat-html { max-width: 900px !important; margin: 0 auto !important; }

.home-screen {
min-height: calc(100vh - 220px);
display:flex; flex-direction:column; align-items:center; justify-content:center;
padding: 30px 12px 80px; text-align:center;
}
.home-logo {
width: 64px; height:64px; border-radius:20px;
display:flex; align-items:center; justify-content:center;
color:#fff; font-size:30px; font-weight:800;
background:linear-gradient(135deg,#06b6d4,#6366f1,#a855f7);
box-shadow:0 12px 35px rgba(99,102,241,.20);
}
.home-screen h1 { font-size:30px; margin:18px 0 4px; }
.home-screen p { margin:0; color:var(--muted); font-size:15px; }
.suggestions {
width:min(760px,100%); margin-top:32px;
display:grid; grid-template-columns:repeat(2,1fr); gap:10px;
}
.suggestion {
text-align:left; padding:14px; border:1px solid var(--border);
background:var(--bg); color:var(--text); border-radius:14px; cursor:pointer;
}
.suggestion:hover { background:var(--hover); }
.suggestion span { font-size:20px; margin-right:8px; }
.suggestion b { font-size:14px; }
.suggestion small { display:block; color:var(--muted); margin-top:6px; padding-left:29px; }

.chat-list { max-width: 900px; margin:0 auto; padding:5px 0 50px; }
.message-row { margin: 0 0 28px; }
.user-row { display:flex; justify-content:flex-end; }
.user-bubble {
max-width:min(78%,700px); background:var(--user);
border-radius:20px 20px 5px 20px; padding:11px 15px;
line-height:1.55; font-size:16px; overflow-wrap:anywhere;
}
.assistant-row { display:flex; flex-direction:column; align-items:flex-start; }
.assistant-head { display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; margin:0 0 7px 2px; }
.assistant-avatar {
width:28px; height:28px; border-radius:9px; display:flex; align-items:center; justify-content:center;
color:#fff; font-size:12px; font-weight:800;
background:linear-gradient(135deg,#06b6d4,#6366f1,#a855f7);
}
.assistant-answer {
max-width:min(90%,760px); font-size:16px; line-height:1.65;
padding:0 2px; overflow-wrap:anywhere;
}
.answer-actions { display:flex; align-items:center; gap:2px; margin:7px 0 0 0; }
.answer-action {
border:0; background:transparent; color:#6b7280; cursor:pointer;
min-width:35px; height:34px; border-radius:9px; font-size:17px;
}
.answer-action:hover { background:var(--hover); color:var(--text); }

#composer {
position:fixed; left:0; right:0; bottom:0; z-index:90;
background:rgba(255,255,255,.97); border-top:1px solid var(--border);
padding:7px 10px 9px; backdrop-filter:blur(10px);
}
#composer-inner { max-width:900px !important; margin:0 auto !important; }
#question textarea {
min-height:50px !important; max-height:150px !important; resize:none !important;
border-radius:18px !important; border:1px solid var(--border) !important;
background:var(--composer) !important; color:var(--text) !important;
box-shadow:0 1px 4px rgba(0,0,0,.05) !important;
font-size:16px !important; padding:14px 48px 12px 15px !important;
}
#composer-buttons { margin-top:5px !important; }
.composer-button button {
min-height:39px !important; border-radius:12px !important;
border:1px solid var(--border) !important; background:var(--bg) !important;
color:var(--text) !important; font-size:15px !important;
}
#send button { background:#111827 !important; color:#fff !important; border-color:#111827 !important; }
#send button:hover { opacity:.9; }
#new-chat button { background:var(--bg) !important; }
#status { text-align:center !important; min-height:0 !important; margin:0 !important; font-size:12px !important; color:var(--muted) !important; }

#side-panel {
position:fixed; z-index:120; top:58px; bottom:0; left:-290px; width:280px;
background:var(--panel); border-right:1px solid var(--border);
transition:left .2s ease; padding:12px;
}
#side-panel.open { left:0; }
.side-label { color:var(--muted); font-size:12px; margin:10px 6px; }
.side-card { padding:10px 12px; border-radius:10px; cursor:pointer; }
.side-card:hover { background:var(--hover); }

@media (max-width:600px) {
#topbar { height:54px; padding:6px 8px; }
#chat-wrap { top:54px; bottom:143px; padding:12px 8px 25px !important; }
#composer { padding:5px 7px 7px; }
#question textarea { min-height:48px !important; font-size:16px !important; border-radius:17px !important; }
.suggestions { grid-template-columns:1fr; margin-top:25px; }
.home-screen { padding-bottom:100px; }
.home-screen h1 { font-size:27px; }
.user-bubble { max-width:88%; font-size:15px; }
.assistant-answer { max-width:96%; font-size:15px; }
.answer-action { min-width:34px; font-size:16px; }
#brand-sub { display:none; }
}
"""


JS = r"""
() => {
const S = { rec:null, live:null, audioCtx:null, processor:null, stream:null, source:null, nextAudioTime:0 };

const qbox = () => document.querySelector("#question textarea");
const chatWrap = () => document.querySelector("#chat-wrap");

function setQuestion(text) {
const box = qbox();
if (!box) return;
const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value").set;
setter.call(box, text || "");
box.dispatchEvent(new Event("input", {bubbles:true}));
box.dispatchEvent(new Event("change", {bubbles:true}));
box.focus();
}

function showStatus(text) {
const el = document.querySelector("#status");
if (el) el.innerText = text || "";
}

function fastScroll() {
const wrap = chatWrap();
if (!wrap) return;
wrap.scrollTop = wrap.scrollHeight;
const last = wrap.querySelector(".message-row:last-child");
if (last) last.scrollIntoView({block:"end", behavior:"auto"});
}

let scrollQueued = false;
function queueScroll() {
if (scrollQueued) return;
scrollQueued = true;
requestAnimationFrame(() => {
scrollQueued = false;
fastScroll();
});
}

const observer = new MutationObserver(queueScroll);
function watchChat() {
const target = chatWrap();
if (target) observer.observe(target, {childList:true, subtree:true, characterData:true});
queueScroll();
}
setTimeout(watchChat, 300);
setInterval(() => {
if (!document.querySelector("#chat-wrap")) return;
queueScroll();
}, 350);

document.addEventListener("click", (event) => {
const suggestion = event.target.closest(".suggestion");
if (suggestion) {
setQuestion(suggestion.dataset.prompt || "");
return;
}
});

function getAnswer(button) {
const row = button.closest(".assistant-row");
const answer = row ? row.querySelector(".nexora-answer") : null;
return answer ? (answer.innerText || "").replace(/▌$/,"" ).trim() : "";
}

async function copyText(text) {
if (!text) return;
try { await navigator.clipboard.writeText(text); }
catch(e) {
const area = document.createElement("textarea");
area.value = text; document.body.appendChild(area); area.select();
document.execCommand("copy"); area.remove();
}
showStatus("📋 उत्तर copy हो गया।");
setTimeout(() => showStatus(""), 1600);
}

function speakText(text) {
if (!text || !window.speechSynthesis) return;
window.speechSynthesis.cancel();
const u = new SpeechSynthesisUtterance(text);
u.lang = "hi-IN"; u.rate = 0.92;
window.speechSynthesis.speak(u);
}

async function shareText(text) {
if (!text) return;
if (navigator.share) {
try { await navigator.share({title:"Nexora AI", text}); return; } catch(e) {}
}
await copyText(text);
}

document.addEventListener("click", async (event) => {
const button = event.target.closest(".answer-action");
if (!button) return;
const action = button.dataset.action;
const text = getAnswer(button);
if (action === "copy") await copyText(text);
else if (action === "sound") speakText(text);
else if (action === "share") await shareText(text);
else if (action === "like") showStatus("👍 Feedback दर्ज हो गया।");
else if (action === "dislike") showStatus("👎 Feedback दर्ज हो गया।");
else if (action === "more") showStatus("⋯ Copy, Like, Dislike, Sound और Share उपलब्ध हैं।");
if (["like","dislike","more"].includes(action)) setTimeout(() => showStatus(""), 1800);
});

window.startNexoraMic = () => {
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!Recognition) { alert("इस browser में Speech Recognition उपलब्ध नहीं है।"); return; }
try { if (S.rec) S.rec.stop(); } catch(e) {}
const recognition = new Recognition();
recognition.lang = "hi-IN";
recognition.continuous = false;
recognition.interimResults = true;
recognition.onstart = () => showStatus("🎤 सुन रहा हूँ...");
recognition.onresult = (event) => {
let text = "";
for (let i=0; i<event.results.length; i++) text += event.results[i][0].transcript;
setQuestion(text);
};
recognition.onerror = () => { showStatus("⚠️ आवाज़ पहचान नहीं हो पाई।"); setTimeout(()=>showStatus(""),1800); };
recognition.onend = () => setTimeout(()=>showStatus(""),300);
S.rec = recognition;
recognition.start();
};

window.toggleNexoraSidebar = () => {
const panel = document.querySelector("#side-panel");
if (panel) panel.classList.toggle("open");
};

window.startNexoraLive = async (token) => {
if(!token){alert("API Key नहीं मिला।");return;}
showStatus("🔴 लाइव वॉइस सुविधा वर्तमान में अक्षम है।");
setTimeout(() => showStatus(""), 2000);
};

async function stopLive(){
showStatus("");
}
window.stopNexoraLive=stopLive;
}
"""


with gr.Blocks(title="Nexora AI", css=CSS, js=JS) as app:
with gr.Column(elem_id="app-shell"):
with gr.Row(elem_id="topbar"):
with gr.Column(scale=0, elem_classes=["top-button"]):
menu_btn = gr.Button("☰", elem_id="menu", show_label=False)
with gr.Column(elem_id="top-title"):
gr.Markdown("<div id='brand-box'><div id='brand-icon'>N</div><div><div id='brand-name'>Nexora AI</div><div id='brand-sub'>AI Assistant</div></div></div>")
with gr.Column(scale=0, elem_classes=["top-button"]):
search_btn = gr.Button("⌕", elem_id="search", show_label=False)
with gr.Column(scale=0, elem_classes=["top-button"]):
more_top = gr.Button("⋮", elem_id="top-more", show_label=False)

gr.HTML("""
<div id="side-panel">
<div class="side-label">Nexora AI</div>
<div class="side-card" onclick="document.getElementById('new-chat').click()">＋ नया चैट</div>
<div class="side-label">हाल की चैट</div>
<div class="side-card">💬 आपकी बातचीत यहाँ दिखेगी</div>
</div>
""")

with gr.Column(elem_id="chat-wrap"):
chat_html = gr.HTML(make_chat_html([]), elem_id="chat-html")

status = gr.Markdown("", elem_id="status")

with gr.Column(elem_id="composer"):
with gr.Column(elem_id="composer-inner"):
question = gr.Textbox(
placeholder="यहाँ अपना सवाल लिखें या 🎤 बोलें...",
show_label=False,
lines=1,
max_lines=6,
elem_id="question",
)
with gr.Row(elem_id="composer-buttons"):
attach_btn = gr.Button("＋", elem_classes=["composer-button"], scale=1)
mic_btn = gr.Button("🎤", elem_classes=["composer-button"], scale=1)
live_start = gr.Button("🔵", elem_classes=["composer-button"], scale=1)
send_btn = gr.Button("➤", elem_id="send", elem_classes=["composer-button"], scale=2)
live_stop = gr.Button("■", elem_classes=["composer-button"], scale=1)
new_chat_btn = gr.Button("＋ नया चैट", elem_id="new-chat", elem_classes=["composer-button"], scale=2)

history_state = gr.State([])

send_btn.click(
fn=ask_nexora,
inputs=[question, history_state],
outputs=[chat_html, history_state, status],
)
question.submit(
fn=ask_nexora,
inputs=[question, history_state],
outputs=[chat_html, history_state, status],
)
new_chat_btn.click(fn=new_chat, inputs=[], outputs=[chat_html, history_state])
mic_btn.click(fn=None, inputs=[], outputs=[], js="() => { window.startNexoraMic(); }")
menu_btn.click(fn=None, inputs=[], outputs=[], js="() => { window.toggleNexoraSidebar(); }")

live_token = gr.State("")
live_start.click(fn=create_live_token, inputs=[], outputs=[live_token])
live_token.change(fn=None, inputs=[live_token], outputs=[], js="token => { window.startNexoraLive(token); }")
live_stop.click(fn=None, inputs=[], outputs=[], js="() => { window.stopNexoraLive(); }")


if __name__ == "__main__":
app.launch(
server_name="0.0.0.0",
server_port=int(os.environ.get("PORT", "10000")),
)
```
