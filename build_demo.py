#!/usr/bin/env python3
"""Genera demo.html a partir de la última versión de la app (chatfake/index.html).

Uso: build_demo.py <app index.html> <salida demo.html>

La demo es la propia app con estas diferencias:
  - datos ficticios en memoria (nada se guarda),
  - límite de 5 clics, después se bloquea,
  - sin capturas, sin crear/editar, sin importar/exportar.
"""
import re
import sys

src_path, out_path = sys.argv[1], sys.argv[2]
s = open(src_path, encoding="utf-8").read()


def sub1(pattern, repl, text, flags=0):
    """Sustituye exactamente una vez; si no encuentra el patrón, falla en alto."""
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=flags)
    if n != 1:
        sys.exit(f"ERROR: no se encontró el patrón: {pattern[:70]}")
    return new


# 1) Cabecera: sin html2canvas (no hay capturas en la demo) y título propio
s = sub1(r'<script src="https://cdnjs[^"]*html2canvas[^"]*"></script>\n', "", s)
s = sub1(r"<title>ChatFake</title>", "<title>ChatFake · Demo</title>", s)

# 2) CSS de la pantalla "Demo finalizada"
DEMO_CSS = """#dlk{position:absolute;inset:0;background:#000b;backdrop-filter:blur(10px);display:flex;align-items:center;justify-content:center;text-align:center;padding:30px;z-index:99;color:#fff}
#dlk[hidden]{display:none}#dlk .ic{font-size:46px}#dlk h2{margin:8px 0}#dlk p{color:#d6d9e0;margin-bottom:18px}
#dlk a{display:inline-block;background:linear-gradient(45deg,#f9a03f,#e1306c,#8a3ab9);color:#fff;text-decoration:none;font-weight:600;padding:12px 20px;border-radius:12px}
"""
s = sub1(r"</style>", DEMO_CSS + "</style>", s)

# 3) Overlay dentro del móvil
OVERLAY = ('<div id=dlk hidden><div><div class=ic>🔒</div><h2>Demo finalizada</h2>'
           '<p>Para más información, contacta con la creadora.</p>'
           '<a href="https://instagram.com/maariaaledesmaa" target=_blank rel=noopener>'
           'Instagram: @maariaaledesmaa</a></div></div>')
s = sub1(r"<div id=phone><div id=screen></div></div>",
         f"<div id=phone><div id=screen></div>{OVERLAY}</div>", s)

# 4) Sin IndexedDB: nada persiste
s = sub1(r"const db=new Promise\(.*?\);\nconst idb=.*?;\n", "const idb=()=>Promise.resolve();\n", s, re.S)

# 5) Barra lateral de la demo (mismas opciones que la app; las de edición avisan)
TOOLS = r"""const LIM=5;let n=0;
function tools(){const p=P(),c=p&&ui.scr=='chat'?cur():null;$('#tools').innerHTML=(p?`<button id=cam data-a=cam>📷 Captura</button><button data-a=swp>👥 Cambiar perfil</button><button data-a=home>🏠 Pantalla de inicio</button><button data-a=lk>🔒 Pantalla de bloqueo</button><button data-a=view>🔄 Cambiar a ${p.v=='ios'?'WhatsApp':'iMessage'}</button><button data-a=wd>🧩 Widgets de bloqueo</button><button data-a=ap>📱 Añadir apps</button><button data-a=nn>🔔 Crear notificación</button><button data-a=cfc>📞 Simular llamada</button><button data-a=set>⚙ Ajustes de ${h(p.n)}</button>`:'')+(c?`<label class=sl>Escribir como<select id=snd>${c.m.map(i=>`<option value=${i} ${i==ui.snd?'selected':''}>${h(N(i))}${i==me(p.id).id?' (yo)':''}</option>`).join('')}</select></label><button data-a=ec>🎨 Personalizar chat</button>`:'')+`<button data-a=th>${document.body.classList.contains('dk')?'☀ Tema claro':'🌙 Tema oscuro'}</button><button data-a=dir>📁 Carpeta backup</button><button data-a=exp>💾 Exportar todo</button><button data-a=imp>📂 Importar</button><div class=sl>${Math.max(0,LIM-n)} clics restantes en la demo</div><a href="./" style="color:#ec4899;text-decoration:none;font-size:14px">← Volver al showcase</a>`}
"""
s = sub1(r"^function tools\(\)\{.*$\n", TOOLS, s, re.M)

# 6) Clics: lista blanca + contador + bloqueo
CLICK = r"""const CNT=new Set('sel unlock lk swp bk oc dn qs snd view go home app cv ctb oc2 call ca cans ch1 tab'.split(' ')),FREE=new Set('mb th cf2 nx'.split(' '));
A.snd=()=>{const i=$('#inp'),v=i&&i.value.trim();if(!v)return false;send(v)};
document.addEventListener('click',async e=>{if(lpT)return;if(!e.target.closest('#cm'))$('#cm')?.remove();if(!e.target.closest('#tools,#mb'))document.body.classList.remove('op');if(e.target.closest('.qr input'))return;const t=e.target.closest('[data-a]');if(!t)return;const a=t.dataset.a;if(!A[a]||a=='hmenu')return;if(a!='mb'&&t.closest('#tools'))document.body.classList.remove('op');
if(!CNT.has(a)&&!FREE.has(a))return toast('No disponible en la demo · contacta con la creadora para la app completa');
if(n>=LIM)return;if(await A[a](t.dataset,e)===false)return;if(CNT.has(a))n++;if(!NR.split(' ').includes(a))render();$('#inp')?.focus();if(a!='mb'&&a!='th')tools();
if(n>=LIM)setTimeout(()=>$('#dlk').hidden=false,900)});
document.addEventListener('contextmenu',e=>{if(e.target.closest('.m,.row,.home')){e.preventDefault();e.stopPropagation();toast('No disponible en la demo')}},true);
"""
s = sub1(r"^document\.addEventListener\('click',async e=>\{if\(lpT\).*$\n", CLICK, s, re.M)

# 7) Enter para enviar pasa por el contador de clics
s = sub1(r"if\(e\.target\.id=='inp'&&e\.key=='Enter'\)doSend\(\)",
         "if(e.target.id=='inp'&&e.key=='Enter')$('.sn')?.click()", s)

# 8) Datos ficticios en lugar de leer IndexedDB
SEED = r"""const T=m=>Date.now()-m*6e4,M=(f,x,m,o)=>({id:id(),f,x,t:T(m),...o});
S={p:[
{id:'p1',n:'Emma Clarke',v:'ios',hu:330,bat:87,ha:['ig','sp','mp','ft','nt','cm','sf','aj','yt','tt'],ct:['c4'],
 wg:{bat:{on:1},mus:{on:1,ti:'Late Night Drive',ar:'The Neon Hearts'},cal:{on:1,ti:'Dinner with Liam',tm:'20:00'},wx:{on:1,v:'21° Sunny'}},
 calls:[{id:'k1',c:'c2',dir:'out',t:T(95),d:312},{id:'k2',c:'c3',dir:'miss',t:T(410),d:0},{id:'k3',c:null,num:'+1 555 010 4417',dir:'in',t:T(1600),d:48}],
 o:{c3:{n:'Sophie Hayes',n1:'Sophie',n2:'Hayes',co:'Hayes Studio',ph:'+1 555 010 2290',em:'sophie@example.com',bd:'1996-05-14',nt:'Best friend 💛'}}},
{id:'p2',n:'Liam Parker',v:'wa',hu:200,bat:64,ha:['gm','x','rj','mu','nf','dc'],ct:['c3','c4'],
 wg:{bat:{on:1},wx:{on:1,v:'18° Cloudy'}},
 calls:[{id:'k4',c:'c1',dir:'in',t:T(95),d:312},{id:'k5',c:'c4',dir:'miss',t:T(700),d:0}]}],
c:[{id:'c1',n:'Emma Clarke',col:'hsl(330 60% 45%)',pid:'p1'},{id:'c2',n:'Liam Parker',col:'hsl(200 60% 40%)',pid:'p2'},{id:'c3',n:'Sophie Hayes',col:'hsl(20 70% 42%)'},{id:'c4',n:'Jack Moore',col:'hsl(150 55% 34%)'}],
h:[{id:'h1',g:0,m:['c1','c2'],t:T(300),s:[M('c2','Are we still on for tonight? 🍕',62,{rb:['p1']}),M('c1',"Yes! Table's booked for 8",60,{rb:['p2']}),M('c2','Perfect, see you there ❤️',58,{e:'❤️',rb:['p1']}),M('c1','Running 5 min late 😅',3)]},
{id:'h2',g:0,m:['c1','c3'],t:T(300),s:[M('c1','Just got home, so tired',190),M('c3','Same 😴',185),M('c3','Did you see the photos from the party?!',8)]},
{id:'h3',g:1,n:'Weekend Trip',m:['c1','c2','c3','c4'],t:T(300),s:[M('c3','Cabin is booked! 🏔️',300),M('c4','Amazing!',290),M('c2',"I'll bring the speaker 🔊",280),M('c1','Count me in ✨',270),M('c4',"Who's driving?",4)]}],
n:[{id:id(),pid:'p1',cid:'h2',ti:'Sophie Hayes',x:'Did you see the photos from the party?!',t:T(8)},{id:id(),pid:'p1',cid:'h3',ti:'Weekend Trip',x:"Jack Moore: Who's driving?",t:T(4)},{id:id(),pid:'p2',cid:'h1',ti:'Emma Clarke',x:'Running 5 min late 😅',t:T(3)},{id:id(),pid:'p2',cid:'h3',ti:'Weekend Trip',x:"Jack Moore: Who's driving?",t:T(4)}]};
render();
"""
s = sub1(r"^\(async\(\)=>\{S=\(await idb\('get','s'\)\).*$\n", SEED, s, re.M)

open(out_path, "w", encoding="utf-8").write(s)
print(f"OK -> {out_path} ({len(s):,} bytes)")
