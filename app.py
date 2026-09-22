import os
import html
import gradio as gr
from google import genai
from google.genai import types

# ============================================================
# Nexora AI - single-file Render app
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

TEXT_MODEL = os.environ.get("TEXT_MODEL", "gemini-3.8-flash")
client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
तुम Nexora AI के सहायक हो।
उपयोगकर्ता जिस भाषा और लहजे में बात करे, उसी के अनुसार स्वाभाविक जवाब दो।
हिंदी में सवाल हो तो साफ और स्वाभाविक देवनागरी हिंदी में जवाब दो।
हर उत्तर की शुरुआत नमस्ते या अपने नाम/परिचय से मत करो।
पिछली बातचीत को ध्यान में रखकर उसी विषय को आगे बढ़ाओ।
नया विषय हो तभी विषय बदलो।
सीधे सवाल का जवाब दो और अनावश्यक भूमिका मत दो।
""".strip()


def esc(value):
    return html.escape(str(value)).replace("\n", "<br>")


def home_html():
    return """
    <div class="home">
      <div class="home-logo">N</div>
      <h1>Nexora AI</h1>
      <p>मुझसे कुछ भी पूछिए</p>
      <div class="suggestions">
        <button class="suggestion" data-prompt="भारत की राजधानी क्या है?">
          <span class="sicon">💡</span><span><b>जानकारी पूछें</b><small>किसी भी विषय पर सवाल पूछें</small></span>
        </button>
        <button class="suggestion" data-prompt="एक आसान और मज़ेदार कहानी सुनाइए।">
          <span class="sicon">✍️</span><span><b>लिखने में मदद</b><small>कहानी, संदेश या लेख लिखें</small></span>
        </button>
        <button class="suggestion" data-prompt="मुझे Python सीखने की शुरुआत आसान भाषा में समझाइए।">
          <span class="sicon">💻</span><span><b>सीखने में मदद</b><small>कोड और पढ़ाई में सहायता</small></span>
        </button>
        <button class="suggestion" data-prompt="आज के लिए एक उपयोगी productivity plan बनाइए।">
          <span class="sicon">🧠</span><span><b>योजना बनाएं</b><small>काम को आसान तरीके से व्यवस्थित करें</small></span>
        </button>
      </div>
    </div>
    """


def actions_html():
    return """
    <div class="actions">
      <button class="action" data-action="copy" title="Copy">▢</button>
      <button class="action" data-action="like" title="Like">♡</button>
      <button class="action" data-action="dislike" title="Dislike">♧</button>
      <button class="action" data-action="sound" title="Sound">◖))</button>
      <button class="action" data-action="share" title="Share">⌯</button>
      <button class="action" data-action="more" title="More">⋮</button>
    </div>
    """


def chat_html(history):
    if not history:
        return home_html()

    out = ['<div class="chat-list">']
    for item in history:
        role = item.get("role", "") if isinstance(item, dict) else ""
        text = item.get("content", "") if isinstance(item, dict) else ""
        if role == "user":
            out.append(f'<div class="user-row"><div class="user-bubble">{esc(text)}</div></div>')
        elif role == "assistant":
            # No avatar/name above every answer.
            out.append(
                f'<div class="assistant-row"><div class="answer nexora-answer">'
                f'{esc(text)}</div>{actions_html()}</div>'
            )
    out.append("</div>")
    return "".join(out)


def sidebar_html(history):
    rows = []
    for item in history:
        if not isinstance(item, dict) or item.get("role") != "user":
            continue
        q = str(item.get("content", "")).strip()
        if not q:
            continue
        title = q.replace("\n", " ")
        if len(title) > 38:
            title = title[:38].rstrip() + "…"
        rows.append(
            f'<button class="history-item" title="{html.escape(q, quote=True)}">'
            f'<span>▢</span><span>{html.escape(title)}</span></button>'
        )

    history_block = "".join(rows) or '<div class="empty-history">अभी कोई पुरानी चैट नहीं है</div>'
    return f"""
    <div class="side-inner">
      <div class="side-brand"><div class="side-logo">N</div><b>Nexora AI</b></div>
      <button class="side-new" id="side-new">＋ <b>New Chat</b></button>
      <div class="side-title">History</div>
      <div class="history">{history_block}</div>
      <div class="side-bottom">
        <button class="side-link" id="side-settings">⚙️ <span>Settings</span></button>
        <button class="side-link" id="side-help">❔ <span>Help</span></button>
      </div>
    </div>
    """


def prompt_for(question, history):
    lines = []
    for item in (history or [])[-12:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        text = str(item.get("content", "")).strip()
        if not text:
            continue
        lines.append(("उपयोगकर्ता: " if role == "user" else "सहायक: ") + text)

    prompt = SYSTEM_PROMPT
    if lines:
        prompt += "\n\nपिछली बातचीत:\n" + "\n".join(lines)
    prompt += "\n\nनया संदेश:\n" + question
    return prompt


def ask(question, history):
    question = (question or "").strip()
    history = list(history or [])

    if not question:
        yield chat_html(history), sidebar_html(history), history, "", ""
        return

    base = history + [{"role": "user", "content": question}]
    working = base + [{"role": "assistant", "content": "▌"}]
    yield chat_html(working), sidebar_html(base), working, "⏳ लिख रहा हूँ…", ""

    parts = []
    try:
        stream = client.models.generate_content_stream(
            model=TEXT_MODEL,
            contents=prompt_for(question, history),
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1200,
            ),
        )
        for chunk in stream:
            piece = getattr(chunk, "text", None) or ""
            if not piece:
                continue
            parts.append(piece)
            current = "".join(parts).strip()
            working = base + [{"role": "assistant", "content": current + "▌"}]
            yield chat_html(working), sidebar_html(base), working, "", ""

        answer = "".join(parts).strip()
        if not answer:
            response = client.models.generate_content(
                model=TEXT_MODEL,
                contents=prompt_for(question, history),
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1200,
                ),
            )
            answer = (getattr(response, "text", None) or "").strip()
        if not answer:
            answer = "मुझे अभी उत्तर नहीं मिला। कृपया दोबारा पूछें।"
    except Exception as exc:
        answer = "⚠️ उत्तर देने में समस्या हुई। कृपया थोड़ी देर बाद फिर कोशिश करें।\n\nतकनीकी विवरण: " + str(exc)

    final = base + [{"role": "assistant", "content": answer}]
    yield chat_html(final), sidebar_html(final), final, "", ""


def new_chat():
    return home_html(), sidebar_html([]), [], "", ""


CSS = r"""
*{box-sizing:border-box}
html,body{margin:0!important;padding:0!important;height:100%;background:#fff!important}
body{overflow:hidden!important;color:#202123!important}
.gradio-container{max-width:none!important;width:100%!important;min-height:100vh!important;padding:0!important;margin:0!important}
footer{display:none!important}
#app{height:100vh;min-height:100vh;background:#fff}
#top{
 position:fixed!important;top:0;left:0;right:0;height:62px!important;z-index:100;
 display:flex!important;align-items:center!important;padding:7px 10px!important;
 background:rgba(255,255,255,.97)!important;border-bottom:1px solid #e5e7eb!important;
 backdrop-filter:blur(10px)
}
.topbtn button{width:44px!important;min-width:44px!important;height:44px!important;padding:0!important;
 border:0!important;border-radius:12px!important;background:transparent!important;color:#202123!important;font-size:22px!important}
.topbtn button:hover{background:#f3f4f6!important}
#title{flex:1!important;margin:0 8px!important}
#brand{display:flex;align-items:center;gap:10px}
#brandicon,.side-logo{display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;
 background:linear-gradient(135deg,#06b6d4,#6366f1,#a855f7)}
#brandicon{width:38px;height:38px;border-radius:11px}
#brandname{font-size:17px;font-weight:700}
#brandsub{font-size:11px;color:#6b7280}
#chat{
 position:fixed!important;top:62px;left:0;right:0;bottom:78px;overflow-y:auto!important;
 overflow-x:hidden!important;padding:18px 12px 30px!important;-webkit-overflow-scrolling:touch}
#chathtml{max-width:920px!important;margin:0 auto!important}
.home{min-height:calc(100vh - 150px);display:flex;flex-direction:column;align-items:center;
 justify-content:center;text-align:center;padding:35px 10px 80px}
.home-logo{width:108px;height:108px;border-radius:30px;display:flex;align-items:center;justify-content:center;
 color:#fff;font-size:54px;font-weight:800;background:linear-gradient(135deg,#06b6d4,#6366f1,#a855f7);
 box-shadow:0 18px 45px rgba(99,102,241,.2)}
.home h1{font-size:38px;margin:18px 0 5px;letter-spacing:-.7px}
.home>p{margin:0;color:#6b7280;font-size:17px}
.suggestions{width:min(760px,100%);display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:34px}
.suggestion{min-height:110px;display:flex;gap:12px;text-align:left;padding:16px;border:1px solid #e5e7eb;
 border-radius:16px;background:#fff;cursor:pointer;color:#202123}
.suggestion:hover{background:#fafafa}
.sicon{width:42px;height:42px;flex:0 0 42px;border-radius:13px;background:#eef4ff;
 display:flex;align-items:center;justify-content:center;font-size:21px}
.suggestion b{display:block;margin:3px 0 6px;font-size:15px}
.suggestion small{display:block;color:#6b7280;line-height:1.45}
.chat-list{max-width:860px;margin:0 auto;padding:8px 0 45px}
.user-row{display:flex;justify-content:flex-end;margin:0 0 27px}
.user-bubble{max-width:min(78%,700px);background:#e9f2ff;border-radius:20px 20px 5px 20px;
 padding:11px 15px;font-size:16px;line-height:1.6;overflow-wrap:anywhere}
.assistant-row{display:flex;flex-direction:column;align-items:flex-start;margin:0 0 28px}
.answer{max-width:94%;font-size:16px;line-height:1.7;overflow-wrap:anywhere}
.actions{display:flex;align-items:center;gap:3px;margin-top:7px}
.action{width:38px;min-width:38px;height:34px;border:0;background:transparent;color:#6b7280;
 border-radius:9px;cursor:pointer;font-size:18px}
.action:hover{background:#f3f4f6;color:#202123}
#status{position:fixed!important;left:50%;bottom:80px;transform:translateX(-50%);
 z-index:110;min-height:0!important;margin:0!important;padding:3px 8px!important;
 border-radius:8px;background:rgba(255,255,255,.9);color:#6b7280!important;font-size:12px!important}
#composer{position:fixed!important;left:0;right:0;bottom:0;height:78px!important;z-index:90;
 padding:8px 10px!important;background:rgba(255,255,255,.97)!important;border-top:1px solid #e5e7eb!important;
 backdrop-filter:blur(10px)}
#composerrow{max-width:920px!important;margin:0 auto!important;display:flex!important;align-items:center!important;gap:8px!important}
#question{flex:1!important;margin:0!important}
#question textarea{min-height:56px!important;max-height:130px!important;resize:none!important;
 border-radius:29px!important;border:1px solid #e5e7eb!important;background:#fff!important;
 font-size:16px!important;padding:16px 18px!important;box-shadow:0 1px 5px rgba(0,0,0,.06)!important}
.circle button{width:52px!important;min-width:52px!important;height:52px!important;padding:0!important;
 border-radius:50%!important;border:1px solid #e5e7eb!important;background:#fff!important;font-size:20px!important}
#send button{background:#111827!important;color:#fff!important;border-color:#111827!important}
#sidebar{position:fixed!important;z-index:140;top:0;bottom:0;left:-310px;width:300px!important;margin:0!important;
 padding:0!important;background:#111827!important;color:#fff!important;border-right:1px solid #263244!important;
 transition:left .2s ease;overflow:hidden!important}
#sidebar.open{left:0}
#overlay{position:fixed!important;inset:0;z-index:130;display:none;background:rgba(0,0,0,.28)}
#overlay.open{display:block}
.side-inner{height:100%;display:flex;flex-direction:column;padding:18px 12px}
.side-brand{display:flex;align-items:center;gap:11px;padding:5px 7px 20px;font-size:20px}
.side-logo{width:40px;height:40px;border-radius:12px}
.side-new{height:52px;width:100%;border:0;border-radius:13px;background:#26354b;color:#fff;
 display:flex;align-items:center;gap:10px;padding:0 15px;cursor:pointer;font-size:15px}
.side-title{margin:25px 8px 10px;color:#b8c0cc;font-size:13px;font-weight:700}
.history{overflow-y:auto}
.history-item{width:100%;display:flex;gap:10px;align-items:center;text-align:left;padding:10px 8px;
 margin-bottom:2px;border:0;border-radius:9px;background:transparent;color:#e5e7eb;cursor:pointer;font-size:14px}
.history-item:hover,.side-link:hover{background:#202b3e}
.empty-history{padding:10px 8px;color:#8993a3;font-size:13px}
.side-bottom{margin-top:auto;border-top:1px solid #283344;padding-top:10px}
.side-link{width:100%;border:0;background:transparent;color:#e5e7eb;text-align:left;padding:12px 8px;
 border-radius:9px;cursor:pointer;font-size:14px}
@media(max-width:650px){
 #top{height:57px!important}.topbtn button{width:42px!important;min-width:42px!important}
 #chat{top:57px;bottom:76px;padding:12px 8px 25px!important}
 #composer{height:76px!important;padding:7px!important}
 .circle button{width:49px!important;min-width:49px!important;height:49px!important}
 .home{padding-bottom:80px}.home-logo{width:82px;height:82px;border-radius:24px;font-size:40px}
 .home h1{font-size:29px}.home>p{font-size:15px}
 .suggestions{grid-template-columns:1fr;gap:10px;margin-top:24px}
 .suggestion{min-height:82px}.user-bubble{max-width:88%;font-size:15px}.answer{max-width:97%;font-size:15px}
 #sidebar{width:min(300px,86vw)!important;left:calc(-1 * min(310px,88vw))}
 #sidebar.open{left:0}
}
"""

JS = r"""
() => {
  const box=()=>document.querySelector("#question textarea");
  const status=t=>{const e=document.querySelector("#status");if(e)e.innerText=t||""};
  const scroll=()=>{const e=document.querySelector("#chat");if(e)e.scrollTop=e.scrollHeight};
  const openSide=()=>{document.querySelector("#sidebar")?.classList.add("open");document.querySelector("#overlay")?.classList.add("open")};
  const closeSide=()=>{document.querySelector("#sidebar")?.classList.remove("open");document.querySelector("#overlay")?.classList.remove("open")};
  const setText=t=>{
    const b=box(); if(!b)return;
    const p=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value");
    if(p&&p.set)p.set.call(b,t||"");else b.value=t||"";
    b.dispatchEvent(new Event("input",{bubbles:true}));b.dispatchEvent(new Event("change",{bubbles:true}));b.focus();
  };
  const observer=new MutationObserver(scroll);
  setTimeout(()=>{const e=document.querySelector("#chat");if(e)observer.observe(e,{childList:true,subtree:true,characterData:true});scroll()},300);
  setInterval(scroll,450);

  async function copy(t){
    if(!t)return;
    try{await navigator.clipboard.writeText(t)}catch(e){
      const a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();document.execCommand("copy");a.remove();
    }
    status("📋 उत्तर copy हो गया");setTimeout(()=>status(""),1400);
  }
  function speak(t){if(!t||!speechSynthesis)return;speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.lang="hi-IN";u.rate=.92;speechSynthesis.speak(u)}
  async function share(t){
    if(!t)return;
    if(navigator.share){try{await navigator.share({title:"Nexora AI",text:t});return}catch(e){}}
    copy(t);
  }
  let rec=null;
  function mic(){
    const R=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!R){status("⚠️ इस browser में voice typing उपलब्ध नहीं है");setTimeout(()=>status(""),1800);return}
    try{rec?.stop()}catch(e){}
    rec=new R();rec.lang="hi-IN";rec.continuous=false;rec.interimResults=true;
    rec.onstart=()=>status("🎤 सुन रहा हूँ…");
    rec.onresult=e=>{let t="";for(let i=0;i<e.results.length;i++)t+=e.results[i][0].transcript;setText(t)};
    rec.onerror=()=>{status("⚠️ आवाज़ समझ नहीं आई");setTimeout(()=>status(""),1800)};
    rec.onend=()=>setTimeout(()=>status(""),300);
    try{rec.start()}catch(e){status("⚠️ माइक्रोफोन शुरू नहीं हो पाया");setTimeout(()=>status(""),1800)}
  }

  document.addEventListener("click",async e=>{
    const s=e.target.closest(".suggestion");if(s){setText(s.dataset.prompt||"");return}
    if(e.target.closest("#menu")){openSide();return}
    if(e.target.closest("#overlay")){closeSide();return}
    if(e.target.closest("#search")){box()?.focus();return}
    if(e.target.closest("#top-more")){status("Nexora AI");setTimeout(()=>status(""),1000);return}
    if(e.target.closest("#mic")){mic();return}
    if(e.target.closest("#side-new")){document.querySelector("#new-chat")?.click();closeSide();return}
    if(e.target.closest("#side-settings")){status("⚙️ Settings अभी इस संस्करण में सीमित हैं");setTimeout(()=>status(""),1700);return}
    if(e.target.closest("#side-help")){status("❔ सवाल लिखें या 🎤 से बोलें, फिर ➤ दबाएँ");setTimeout(()=>status(""),1900);return}
    const b=e.target.closest(".action");if(!b)return;
    const row=b.closest(".assistant-row");const a=row?.querySelector(".nexora-answer");
    const t=(a?.innerText||"").replace(/▌$/,"").trim();const act=b.dataset.action;
    if(act==="copy")await copy(t);
    else if(act==="sound")speak(t);
    else if(act==="share")await share(t);
    else if(act==="like"){status("👍 Feedback दर्ज हो गया");setTimeout(()=>status(""),1300)}
    else if(act==="dislike"){status("👎 Feedback दर्ज हो गया");setTimeout(()=>status(""),1300)}
    else if(act==="more"){status("Copy, Like, Dislike, Sound और Share उपलब्ध हैं");setTimeout(()=>status(""),1600)}
  });
}
"""

with gr.Blocks(
    title="Nexora AI",
    css=CSS,
    js=JS,
    theme=gr.themes.Soft(primary_hue="indigo", neutral_hue="slate"),
) as app:
    with gr.Column(elem_id="app"):
        with gr.Row(elem_id="top"):
            with gr.Column(scale=0, elem_classes=["topbtn"]):
                gr.Button("☰", elem_id="menu", show_label=False)
            with gr.Column(elem_id="title"):
                gr.HTML("""
                <div id="brand">
                  <div id="brandicon">N</div>
                  <div><div id="brandname">Nexora AI</div><div id="brandsub">AI Assistant</div></div>
                </div>
                """)
            with gr.Column(scale=0, elem_classes=["topbtn"]):
                gr.Button("⌕", elem_id="search", show_label=False)
            with gr.Column(scale=0, elem_classes=["topbtn"]):
                gr.Button("⋮", elem_id="top-more", show_label=False)

        with gr.Column(elem_id="sidebar"):
            side = gr.HTML(sidebar_html([]), elem_id="sidebarhtml")
        gr.HTML('<div id="overlay"></div>')

        with gr.Column(elem_id="chat"):
            chat = gr.HTML(home_html(), elem_id="chathtml")

        status_box = gr.Markdown("", elem_id="status")

        with gr.Column(elem_id="composer"):
            with gr.Row(elem_id="composerrow"):
                question = gr.Textbox(
                    placeholder="यहाँ अपना सवाल लिखें...",
                    show_label=False,
                    lines=1,
                    max_lines=6,
                    elem_id="question",
                    scale=1,
                )
                with gr.Column(scale=0, min_width=52, elem_classes=["circle"]):
                    gr.Button("🎤", elem_id="mic", show_label=False)
                with gr.Column(scale=0, min_width=52, elem_classes=["circle"]):
                    send = gr.Button("➤", elem_id="send", show_label=False)

    state = gr.State([])

    hidden_new = gr.Button("New Chat", elem_id="new-chat", visible=False)

    send.click(
        ask,
        [question, state],
        [chat, side, state, status_box, question],
    )
    question.submit(
              ask,
        [question, state],
        [chat, side, state, status_box, question],
    )
    hidden_new.click(
        new_chat,
        [],
        [chat, side, state, status_box, question],
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        show_error=True,
    )
    
