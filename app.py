import os
import datetime
import gradio as gr
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

TEXT_MODEL = "gemini-3.5-flash-lite"
LIVE_MODEL = "gemini-3.8-live"
client = genai.Client(api_key=API_KEY)
last_answer = {"text": ""}

SYSTEM_PROMPT = """
तुम Nexora AI हो।
हमेशा सरल, स्पष्ट और स्वाभाविक हिंदी में उत्तर दो।
हिंदी सवाल का उत्तर देवनागरी हिंदी में दो।
Roman Hindi या Hinglish में उत्तर मत दो, जब तक उपयोगकर्ता विशेष रूप से ऐसा न कहे।
तथात्मक प्रश्नों का सही और स्पष्ट उत्तर दो।
"""

def ask_nexora(question, history):
    question = (question or "").strip()
    history = history or []
    if not question:
        return history, ""
    context = []
    for m in history[-10:]:
        if isinstance(m, dict) and m.get("content"):
            context.append(f'{m.get("role","")}: {m["content"]}')
    prompt = SYSTEM_PROMPT
    if context:
        prompt += "\n\nपिछली बातचीत:\n" + "\n".join(context)
    prompt += f"\n\nनया सवाल:\n{question}"
    try:
        r = client.models.generate_content(model=TEXT_MODEL, contents=prompt)
        answer = (r.text or "मुझे अभी उत्तर नहीं मिला।").strip()
    except Exception as e:
        answer = f"⚠️ उत्तर देने में समस्या हुई:\n{e}"
    last_answer["text"] = answer
    history = list(history)
    history += [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
    return history, ""

def new_chat():
    last_answer["text"] = ""
    return []

def like_answer():
    return "👍 धन्यवाद! Feedback दर्ज हो गया।"

def dislike_answer():
    return "👎 धन्यवाद! Feedback दर्ज हो गया।"

def more_answer():
    return "⋯ Copy, Like, Dislike, Sound, Share और Live Voice उपलब्ध हैं।"

def create_live_token():
    now = datetime.datetime.now(datetime.timezone.utc)
    token = client.auth_tokens.create(config={
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
    })
    return token.name

CSS = """
#chat { border: none !important; }
#bottom { position: sticky; bottom: 0; background: white; padding-top: 8px; z-index: 20; }
#question textarea { font-size: 16px !important; }
.action-row button { min-width: 44px !important; }
"""

JS = r"""
() => {
const S={rec:null,live:null,ctx:null,proc:null,stream:null,next:0};
const box=()=>document.querySelector("#question textarea");
const put=t=>{
 const b=box(); if(!b)return;
 const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value").set;
 set.call(b,t); b.dispatchEvent(new Event("input",{bubbles:true}));
};
window.startNexoraMic=()=>{
 const R=window.SpeechRecognition||window.webkitSpeechRecognition;
 if(!R){alert("इस browser में Speech Recognition उपलब्ध नहीं है।");return;}
 const r=new R(); r.lang="hi-IN"; r.continuous=false; r.interimResults=false;
 r.onresult=e=>put(e.results[0][0].transcript||"");
 r.onerror=e=>console.log(e); S.rec=r; r.start();
};
window.copyLastAnswer=async()=>{
 const c=document.querySelector("#chat"); if(!c)return;
 try{await navigator.clipboard.writeText(c.innerText||"");}catch(e){alert("Copy नहीं हो पाया।");}
};
window.soundLastAnswer=()=>{
 const c=document.querySelector("#chat"); if(!c)return;
 speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(c.innerText||"");
 u.lang="hi-IN"; u.rate=.9; speechSynthesis.speak(u);
};
window.shareLastAnswer=async()=>{
 const c=document.querySelector("#chat"),t=c?c.innerText:""; if(!t)return;
 if(navigator.share){try{await navigator.share({title:"Nexora AI",text:t});return;}catch(e){}}
 try{await navigator.clipboard.writeText(t);alert("Share उपलब्ध नहीं है, उत्तर copy कर दिया गया है।");}catch(e){}
};
function b64bytes(s){const x=atob(s),o=new Uint8Array(x.length);for(let i=0;i<x.length;i++)o[i]=x.charCodeAt(i);return o;}
function play(s){
 if(!S.ctx)S.ctx=new(window.AudioContext||window.webkitAudioContext)();
 const a=b64bytes(s),v=new DataView(a.buffer,a.byteOffset,a.byteLength),f=new Float32Array(a.length/2);
 for(let i=0;i<f.length;i++)f[i]=v.getInt16(i*2,true)/32768;
 const b=S.ctx.createBuffer(1,f.length,24000);b.copyToChannel(f,0);
 const n=S.ctx.createBufferSource();n.buffer=b;n.connect(S.ctx.destination);
 const st=Math.max(S.ctx.currentTime,S.next);n.start(st);S.next=st+b.duration;
}
async function mic(){
 S.stream=await navigator.mediaDevices.getUserMedia({audio:true});
 const ac=new(window.AudioContext||window.webkitAudioContext)(),src=ac.createMediaStreamSource(S.stream);
 const p=ac.createScriptProcessor(4096,1,1);S.proc=p;
 p.onaudioprocess=e=>{
  if(!S.live)return;
  const x=e.inputBuffer.getChannelData(0),a=new Int16Array(x.length);
  for(let i=0;i<x.length;i++){let v=Math.max(-1,Math.min(1,x[i]));a[i]=v<0?v*32768:v*32767;}
  let u=new Uint8Array(a.buffer),z="",n=0x8000;
  for(let i=0;i<u.length;i+=n)z+=String.fromCharCode(...u.subarray(i,i+n));
  try{S.live.sendRealtimeInput({audio:{data:btoa(z),mimeType:"audio/pcm;rate=16000"}});}catch(e){}
 };
 src.connect(p);p.connect(ac.destination);
}
window.startNexoraLive=async token=>{
 if(!token){alert("Live token नहीं मिला।");return;}
 try{
  const m=await import("https://esm.sh/@google/genai");
  const ai=new m.GoogleGenAI({apiKey:token});
  S.live=await ai.live.connect({
   model:"gemini-3.8-live",
   config:{responseModalities:["AUDIO"],systemInstruction:"तुम Nexora AI हो। सरल और स्पष्ट हिंदी में बोलो।",sessionResumption:{}},
   callbacks:{
    onmessage:x=>{
     const p=x.serverContent&&x.serverContent.modelTurn&&x.serverContent.modelTurn.parts;
     if(p)for(const q of p)if(q.inlineData&&q.inlineData.data)play(q.inlineData.data);
    }
   }
  });
  await mic();
 }catch(e){console.error(e);alert("Live Voice शुरू नहीं हो पाया।");}
};
window.stopNexoraLive=async()=>{
 try{if(S.proc)S.proc.disconnect();if(S.stream)S.stream.getTracks().forEach(t=>t.stop());}catch(e){}
 try{if(S.live)S.live.close();}catch(e){}
 S.live=null;S.proc=null;S.stream=null;
};
}
"""

with gr.Blocks(title="Nexora AI") as app:
    gr.Markdown("# 🤖 Nexora AI")
    chat = gr.Chatbot(
        value=[], show_label=False, autoscroll=True,
        height="calc(100vh - 245px)", elem_id="chat",
        buttons=["copy"], feedback_options=["Like","Dislike"]
    )
    status = gr.Markdown("")
    with gr.Group(elem_id="bottom"):
        question = gr.Textbox(
            placeholder="यहाँ अपना सवाल लिखें या 🎤 बोलें...",
            show_label=False, lines=2, elem_id="question"
        )
        with gr.Row():
            send_btn = gr.Button("➤ भेजें", variant="primary")
            mic_btn = gr.Button("🎤")
            live_start = gr.Button("🔴 Live")
            live_stop = gr.Button("⏹️")
        with gr.Row(elem_classes=["action-row"]):
            like_btn=gr.Button("👍")
            dislike_btn=gr.Button("👎")
            sound_btn=gr.Button("🔊")
            copy_btn=gr.Button("📋")
            share_btn=gr.Button("↗️")
            more_btn=gr.Button("⋯")
        new_chat_btn=gr.Button("＋ नया चैट")

    live_token=gr.State("")

    send_btn.click(ask_nexora,[question,chat],[chat,question])
    question.submit(ask_nexora,[question,chat],[chat,question])
    new_chat_btn.click(new_chat,[],[chat])
    like_btn.click(like_answer,[],[status])
    dislike_btn.click(dislike_answer,[],[status])
    more_btn.click(more_answer,[],[status])
    mic_btn.click(None,[],[],js="() => { window.startNexoraMic(); }")
    copy_btn.click(None,[],[],js="() => { window.copyLastAnswer(); }")
    sound_btn.click(None,[],[],js="() => { window.soundLastAnswer(); }")
    share_btn.click(None,[],[],js="() => { window.shareLastAnswer(); }")
    live_start.click(create_live_token,[],[live_token])
    live_token.change(None,[live_token],[],js="token => { window.startNexoraLive(token); }")
    live_stop.click(None,[],[],js="() => { window.stopNexoraLive(); }")

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT","10000")),
    css=CSS,
    js=JS
    )
