import os
import html
import datetime
import gradio as gr
from google import genai

# ============================================================
# Nexora AI - Gradio 6 / Render
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
            <button class="suggestion" data-prompt="भारत की राजधानी क्या है?"><span>💡</span><b>जानकारी पूछें</b><small>किसी भी विषय पर सवाल पूछें</small></button>
            <button class="suggestion" data-prompt="एक आसान और मज़ेदार कहानी सुनाइए।"><span>✍️</span><b>लिखने में मदद</b><small>कहानी, संदेश या लेख लिखें</small></button>
            <button class="suggestion" data-prompt="मुझे Python सीखने की शुरुआत समझाइए।"><span>💻</span><b>सीखने में मदद</b><small>कोड और पढ़ाई में सहायता</small></button>
            <button class="suggestion" data-prompt="आज के लिए एक उपयोगी productivity plan बनाइए।"><span>🧠</span><b>योजना बनाएं</b><small>काम को आसान तरीके से व्यवस्थित करें</small></button>
          </div>
        </div>
        """

    parts = ['<div class="chat-list">']
    for item in history:
        role = item.get("role", "") if isinstance(item, dict) else ""
        content = item.get("content", "") if isinstance(item, dict) else ""
        safe = html.escape(str(content)).replace("\n", "<br>")
        if role == "user":
            parts.append(f'<div class="message-row user-row"><div class="user-bubble">{safe}</div></div>')
        elif role == "assistant":
            parts.append(f"""
            <div class="message-row assistant-row">
              <div class="assistant-head"><div class="assistant-avatar">N</div><span>Nexora AI</span></div>
              <div class="assistant-answer nexora-answer">{safe}</div>
              <div class="answer-actions">
                <button class="answer-action" data-action="copy" title="Copy">📋</button>
                <button class="answer-action" data-action="like" title="Like">👍</button>
                <button class="answer-action" data-action="dislike" title="Dislike">👎</button>
                <button class="answer-action" data-action="sound" title="Sound">🔊</button>
                <button class="answer-action" data-action="share" title="Share">🔗</button>
                <button class="answer-action" data-action="more" title="More">⋮</button>
              </div>
            </div>
            """)
    parts.append('</div>')
    return ''.join(parts)


def build_prompt(question, history):
    context = []
    for item in (history or [])[-6:]:
        if isinstance(item, dict) and item.get("content"):
            context.append(f"{item.get('role', '')}: {item.get('content', '')}")
    prompt = SYSTEM_PROMPT
    if context:
        prompt += "\n\nपिछली बातचीत:\n" + "\n".join(context)
    return prompt + f"\n\nनया सवाल:\n{question}"


def ask_nexora(question, history):
    question = (question or "").strip()
    history = list(history or [])
    if not question:
        yield make_chat_html(history), history, "", ""
        return

    base = history + [{"role": "user", "content": question}]
    working = base + [{"role": "assistant", "content": "▌"}]
    yield make_chat_html(working), working, "", ""

    answer_parts = []
    try:
        stream = client.models.generate_content_stream(
            model=TEXT_MODEL,
            contents=build_prompt(question, history),
        )
        for chunk in stream:
            piece = getattr(chunk, "text", None) or ""
            if not piece:
                continue
            answer_parts.append(piece)
            current = "".join(answer_parts)
            working = base + [{"role": "assistant", "content": current + "▌"}]
            yield make_chat_html(working), working, "", ""

        answer = "".join(answer_parts).strip()
        if not answer:
            response = client.models.generate_content(model=TEXT_MODEL, contents=build_prompt(question, history))
            answer = (getattr(response, "text", None) or "मुझे अभी उत्तर नहीं मिला।").strip()
    except Exception as exc:
        answer = f"⚠️ उत्तर देने में समस्या हुई:\n{exc}"

    final = base + [{"role": "assistant", "content": answer}]
    yield make_chat_html(final), final, "", ""


def new_chat():
    return make_chat_html([]), [], ""


def create_live_token():
    now = datetime.datetime.now(datetime.timezone.utc)
    token = client.auth_tokens.create(
        config={
            "uses": 1,
            "expire_time": now + datetime.timedelta(minutes=30),
            "new_session_expire_time": now + datetime.timedelta(minutes=1),
            "live_connect_constraints": {
                "model": LIVE_MODEL,
                "config": {"response_modalities": ["AUDIO"], "session_resumption": {}},
            },
        }
    )
    return token.name


CSS = r"""
:root{--bg:#fff;--panel:#f7f7f8;--text:#202123;--muted:#6b7280;--border:#e5e7eb;--hover:#eeeeee;--user:#e8f1ff}
*{box-sizing:border-box}html,body{margin:0!important;padding:0!important;height:100%;background:var(--bg)!important;color:var(--text)!important}
.gradio-container{max-width:none!important;width:100%!important;padding:0!important;margin:0!important}footer{display:none!important}
#app-shell{min-height:100vh;background:var(--bg)}
#topbar{position:fixed;top:0;left:0;right:0;height:58px;z-index:100;display:flex;align-items:center;padding:7px 12px;background:rgba(255,255,255,.96);border-bottom:1px solid var(--border);backdrop-filter:blur(10px)}
#brand-box{display:flex;align-items:center;gap:9px}.top-button button{min-width:40px!important;height:40px!important;border:0!important;border-radius:10px!important;background:transparent!important;color:var(--text)!important;font-size:20px!important}.top-button button:hover{background:var(--hover)!important}
#brand-icon{width:34px;height:34px;border-radius:11px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;background:linear-gradient(135deg,#06b6d4,#6366f1,#a855f7)}#brand-name{font-weight:700;font-size:17px}#brand-sub{color:var(--muted);font-size:11px}
#top-title{flex:1;margin:0 12px}
#chat-wrap{position:fixed;top:58px;left:0;right:0;bottom:125px;overflow-y:auto!important;overflow-x:hidden!important;padding:18px 12px 35px!important;-webkit-overflow-scrolling:touch}
#chat-html{max-width:900px!important;margin:0 auto!important}.home-screen{min-height:calc(100vh - 220px);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:30px 12px 80px;text-align:center}.home-logo{width:64px;height:64px;border-radius:20px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:30px;font-weight:800;background:linear-gradient(135deg,#06b6d4,#6366f1,#a855f7)}.home-screen h1{font-size:30px;margin:18px 0 4px}.home-screen p{margin:0;color:var(--muted)}
.suggestions{width:min(760px,100%);margin-top:32px;display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.suggestion{text-align:left;padding:14px;border:1px solid var(--border);background:#fff;color:var(--text);border-radius:14px;cursor:pointer}.suggestion:hover{background:var(--hover)}.suggestion span{font-size:20px;margin-right:8px}.suggestion b{font-size:14px}.suggestion small{display:block;color:var(--muted);margin-top:6px;padding-left:29px}
.chat-list{max-width:900px;margin:0 auto;padding:5px 0 50px}.message-row{margin:0 0 28px}.user-row{display:flex;justify-content:flex-end}.user-bubble{max-width:min(78%,700px);background:var(--user);border-radius:20px 20px 5px 20px;padding:11px 15px;line-height:1.55;font-size:16px;overflow-wrap:anywhere}.assistant-row{display:flex;flex-direction:column;align-items:flex-start}.assistant-head{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;margin:0 0 7px 2px}.assistant-avatar{width:28px;height:28px;border-radius:9px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:800;background:linear-gradient(135deg,#06b6d4,#6366f1,#a855f7)}.assistant-answer{max-width:min(92%,760px);font-size:16px;line-height:1.65;padding:0 2px;overflow-wrap:anywhere}.answer-actions{display:flex;align-items:center;gap:2px;margin:7px 0 0}.answer-action{border:0;background:transparent;color:#6b7280;cursor:pointer;min-width:38px;height:36px;border-radius:9px;font-size:17px;touch-action:manipulation;-webkit-tap-highlight-color:transparent}.answer-action:hover,.answer-action.active{background:var(--hover);color:var(--text)}
#composer{position:fixed;left:0;right:0;bottom:0;z-index:90;background:rgba(255,255,255,.97);border-top:1px solid var(--border);padding:7px 10px 9px;backdrop-filter:blur(10px)}#composer-inner{max-width:900px!important;margin:0 auto!important}#question textarea{min-height:50px!important;max-height:150px!important;resize:none!important;border-radius:18px!important;border:1px solid var(--border)!important;font-size:16px!important;padding:14px 15px!important}#composer-buttons{margin-top:5px!important}.composer-button button{min-height:39px!important;border-radius:12px!important;border:1px solid var(--border)!important;background:#fff!important;color:var(--text)!important;font-size:15px!important;touch-action:manipulation}.composer-button button:hover{background:var(--hover)!important}#send button{background:#111827!important;color:#fff!important;border-color:#111827!important}#status{text-align:center!important;min-height:0!important;margin:0!important;font-size:12px!important;color:var(--muted)!important}
#side-panel{position:fixed;z-index:120;top:58px;bottom:0;left:-290px;width:280px;background:var(--panel);border-right:1px solid var(--border);transition:left .2s ease;padding:12px}#side-panel.open{left:0}.side-label{color:var(--muted);font-size:12px;margin:10px 6px}.side-card{padding:10px 12px;border-radius:10px;cursor:pointer}.side-card:hover{background:var(--hover)}
@media(max-width:600px){#topbar{height:54px;padding:6px 8px}#chat-wrap{top:54px;bottom:143px;padding:12px 8px 25px!important}#composer{padding:5px 7px 7px}.suggestions{grid-template-columns:1fr;margin-top:25px}.home-screen{padding-bottom:100px}.home-screen h1{font-size:27px}.user-bubble{max-width:88%;font-size:15px}.assistant-answer{max-width:96%;font-size:15px}.answer-action{min-width:36px;font-size:16px}#brand-sub{display:none}}
"""

JS = r"""
() => {
  const S={rec:null,live:null,audioCtx:null,liveCtx:null,processor:null,stream:null,source:null,nextAudioTime:0};
  const qbox=()=>document.querySelector('#question textarea');
  const wrap=()=>document.querySelector('#chat-wrap');
  const status=(t)=>{const e=document.querySelector('#status');if(e)e.innerText=t||''};
  function setQuestion(t){const b=qbox();if(!b)return;const s=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;s.call(b,t||'');b.dispatchEvent(new Event('input',{bubbles:true}));b.dispatchEvent(new Event('change',{bubbles:true}));b.focus()}
  function scrollFast(){const w=wrap();if(!w)return;w.scrollTop=w.scrollHeight}
  let queued=false;function queueScroll(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;scrollFast()})}
  const mo=new MutationObserver(queueScroll);setTimeout(()=>{const w=wrap();if(w)mo.observe(w,{childList:true,subtree:true,characterData:true});queueScroll()},250);setInterval(queueScroll,300);
  document.addEventListener('click',e=>{const s=e.target.closest('.suggestion');if(s)setQuestion(s.dataset.prompt||'')});
  function answerOf(btn){const row=btn.closest('.assistant-row');const a=row&&row.querySelector('.nexora-answer');return a?(a.innerText||'').replace(/▌$/,'').trim():''}
  async function copyText(t){if(!t)return;try{await navigator.clipboard.writeText(t)}catch(e){const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove()}status('📋 उत्तर copy हो गया।');setTimeout(()=>status(''),1200)}
  function speak(t){if(!t||!window.speechSynthesis)return;window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.lang='hi-IN';u.rate=.95;window.speechSynthesis.speak(u)}
  async function share(t){if(!t)return;if(navigator.share){try{await navigator.share({title:'Nexora AI',text:t});return}catch(e){}}await copyText(t)}
  document.addEventListener('click',async e=>{const b=e.target.closest('.answer-action');if(!b)return;e.preventDefault();const a=b.dataset.action,t=answerOf(b);b.classList.add('active');if(a==='copy')await copyText(t);else if(a==='sound')speak(t);else if(a==='share')await share(t);else if(a==='like'||a==='dislike'){status(a==='like'?'👍 Feedback दर्ज हो गया।':'👎 Feedback दर्ज हो गया।');setTimeout(()=>status(''),1200)}else if(a==='more'){status('⋮ Copy, Like, Dislike, Sound और Share उपलब्ध हैं।');setTimeout(()=>status(''),1500)}});
  window.startNexoraMic=()=>{const R=window.SpeechRecognition||window.webkitSpeechRecognition;if(!R){alert('इस browser में Speech Recognition उपलब्ध नहीं है।');return}try{if(S.rec)S.rec.stop()}catch(e){}const r=new R();r.lang='hi-IN';r.continuous=false;r.interimResults=true;r.onstart=()=>status('🎤 सुन रहा हूँ...');r.onresult=e=>{let t='';for(let i=0;i<e.results.length;i++)t+=e.results[i][0].transcript;setQuestion(t)};r.onerror=()=>{status('⚠️ आवाज़ पहचान नहीं हो पाई।');setTimeout(()=>status(''),1500)};r.onend=()=>setTimeout(()=>status(''),300);S.rec=r;r.start()};
  window.toggleNexoraSidebar=()=>{const p=document.querySelector('#side-panel');if(p)p.classList.toggle('open')};
  function b64(v){const r=atob(v),u=new Uint8Array(r.length);for(let i=0;i<r.length;i++)u[i]=r.charCodeAt(i);return u}
  function b64out(u){let x='';for(let i=0;i<u.length;i+=0x8000)x+=String.fromCharCode(...u.subarray(i,i+0x8000));return btoa(x)}
  function playPcm(v){try{if(!S.audioCtx)S.audioCtx=new(window.AudioContext||window.webkitAudioContext)();if(S.audioCtx.state==='suspended')S.audioCtx.resume();const u=b64(v),d=new DataView(u.buffer,u.byteOffset,u.byteLength),f=new Float32Array(Math.floor(u.length/2));for(let i=0;i<f.length;i++)f[i]=d.getInt16(i*2,true)/32768;const buf=S.audioCtx.createBuffer(1,f.length,24000);buf.copyToChannel(f,0);const n=S.audioCtx.createBufferSource();n.buffer=buf;n.connect(S.audioCtx.destination);const st=Math.max(S.audioCtx.currentTime,S.nextAudioTime);n.start(st);S.nextAudioTime=st+buf.duration}catch(e){console.error(e)}}
  async function startLiveMic(){S.stream=await navigator.mediaDevices.getUserMedia({audio:true});const c=new(window.AudioContext||window.webkitAudioContext)();S.liveCtx=c;const src=c.createMediaStreamSource(S.stream),p=c.createScriptProcessor(4096,1,1),g=c.createGain();g.gain.value=0;S.source=src;S.processor=p;p.onaudioprocess=e=>{if(!S.live)return;const input=e.inputBuffer.getChannelData(0),inRate=e.inputBuffer.sampleRate,outRate=16000,len=Math.max(1,Math.round(input.length*outRate/inRate)),pcm=new Int16Array(len);for(let i=0;i<len;i++){const pos=i*inRate/outRate,l=Math.min(Math.floor(pos),input.length-1),r=Math.min(l+1,input.length-1),f=pos-l,v=(input[l]||0)*(1-f)+(input[r]||0)*f;pcm[i]=Math.max(-1,Math.min(1,v))*(v<0?32768:32767)}try{S.live.sendRealtimeInput({audio:{data:b64out(new Uint8Array(pcm.buffer)),mimeType:'audio/pcm;rate=16000'}})}catch(x){}};src.connect(p);p.connect(g);g.connect(c.destination);if(c.state==='suspended')await c.resume()}
  window.startNexoraLive=async token=>{if(!token){alert('Live token नहीं मिला।');return}try{status('🔴 Live Voice शुरू हो रहा है...');const m=await import('https://esm.sh/@google/genai');const ai=new m.GoogleGenAI({apiKey:token});S.live=await ai.live.connect({model:'gemini-3.8-live',config:{responseModalities:['AUDIO'],systemInstruction:'तुम Nexora AI हो। सरल और स्पष्ट हिंदी में बोलो।',sessionResumption:{}},callbacks:{onmessage:x=>{const p=x?.serverContent?.modelTurn?.parts||[];for(const z of p)if(z.inlineData?.data)playPcm(z.inlineData.data)},onerror:()=>status('⚠️ Live Voice में समस्या हुई।'),onclose:()=>status('')}});await startLiveMic();status('🔴 Live Voice चालू है — बोलिए...')}catch(e){console.error(e);status('⚠️ Live Voice शुरू नहीं हो पाया।');await stopLive()}};
  async function stopLive(){try{if(S.processor)S.processor.disconnect()}catch(e){}try{if(S.source)S.source.disconnect()}catch(e){}try{if(S.stream)S.stream.getTracks().forEach(t=>t.stop())}catch(e){}try{if(S.live)S.live.close()}catch(e){}try{if(S.liveCtx)await S.liveCtx.close()}catch(e){}S.live=null;S.processor=null;S.source=null;S.stream=null;S.liveCtx=null;S.nextAudioTime=0;status('')};window.stopNexoraLive=stopLive;
}
"""

with gr.Blocks(title="Nexora AI") as app:
    with gr.Column(elem_id="app-shell"):
        with gr.Row(elem_id="topbar"):
            with gr.Column(scale=0, elem_classes=["top-button"]):
                menu_btn=gr.Button("☰",elem_id="menu")
            with gr.Column(elem_id="top-title"):
                gr.Markdown("<div id='brand-box'><div id='brand-icon'>N</div><div><div id='brand-name'>Nexora AI</div><div id='brand-sub'>AI Assistant</div></div></div>")
            with gr.Column(scale=0, elem_classes=["top-button"]):
                search_btn=gr.Button("⌕",elem_id="search")
            with gr.Column(scale=0, elem_classes=["top-button"]):
                more_top=gr.Button("⋮",elem_id="top-more")
        gr.HTML("""
        <div id="side-panel"><div class="side-label">Nexora AI</div><div class="side-card" onclick="document.getElementById('new-chat').click()">＋ नया चैट</div><div class="side-label">हाल की चैट</div><div class="side-card">💬 आपकी बातचीत यहाँ दिखेगी</div></div>
        """)
        with gr.Column(elem_id="chat-wrap"):
            chat_html=gr.HTML(make_chat_html([]),elem_id="chat-html")
        status_box=gr.Markdown("",elem_id="status")
        with gr.Column(elem_id="composer"):
            with gr.Column(elem_id="composer-inner"):
                question=gr.Textbox(placeholder="यहाँ अपना सवाल लिखें या 🎤 बोलें...",show_label=False,lines=1,max_lines=6,elem_id="question")
                with gr.Row(elem_id="composer-buttons"):
                    attach_btn=gr.Button("＋",elem_classes=["composer-button"],scale=1)
                    mic_btn=gr.Button("🎤",elem_classes=["composer-button"],scale=1)
                    live_start=gr.Button("🔵",elem_classes=["composer-button"],scale=1)
                    send_btn=gr.Button("➤",elem_id="send",elem_classes=["composer-button"],scale=2)
                    live_stop=gr.Button("■",elem_classes=["composer-button"],scale=1)
                    new_chat_btn=gr.Button("＋ नया चैट",elem_id="new-chat",elem_classes=["composer-button"],scale=2)
    history_state=gr.State([])
    send_btn.click(fn=ask_nexora,inputs=[question,history_state],outputs=[chat_html,history_state,status_box,question])
    question.submit(fn=ask_nexora,inputs=[question,history_state],outputs=[chat_html,history_state,status_box,question])
    new_chat_btn.click(fn=new_chat,inputs=[],outputs=[chat_html,history_state,question])
    mic_btn.click(fn=None,inputs=[],outputs=[],js="() => { window.startNexoraMic(); }")
    menu_btn.click(fn=None,inputs=[],outputs=[],js="() => { window.toggleNexoraSidebar(); }")
    search_btn.click(fn=None,inputs=[],outputs=[],js="() => { const e=document.querySelector('#question textarea'); if(e)e.focus(); }")
    more_top.click(fn=None,inputs=[],outputs=[],js="() => { alert('Nexora AI: नया चैट, टेक्स्ट चैट, माइक्रोफोन और Live Voice उपलब्ध हैं।'); }")
    attach_btn.click(fn=None,inputs=[],outputs=[],js="() => { alert('फ़ाइल अटैचमेंट अभी इस संस्करण में सक्रिय नहीं है।'); }")
    live_token=gr.State("")
    live_start.click(fn=create_live_token,inputs=[],outputs=[live_token])
    live_token.change(fn=None,inputs=[live_token],outputs=[],js="token => { window.startNexoraLive(token); }")
    live_stop.click(fn=None,inputs=[],outputs=[],js="() => { window.stopNexoraLive(); }")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0",server_port=int(os.environ.get("PORT","7860")),css=CSS,js=JS)
