import json,re
exec(open('build.py').read().split('data={}')[0])   # rows, months, cat
out=json.load(open('out.json'))
C={c['name']:c for c in out['cats']}
H='Consum apa calda'; U='Utilitati consumate pentru incalzirea apei (gaz; curent)'
old=H+' + '+U
C['Total apa calda']=C.pop(old); C['Total apa calda']['name']='Total apa calda'
C['Total apa calda']['items']=[[x for x in it if x[0].startswith('Cantitate')] for it in C['Total apa calda']['items']]
C['Total apa calda']['note']='cantitatea facturată pentru fiecare lună (suma celor două grafice)'
def total(name,parts):
    C[name]=dict(name=name,v=[round(sum(C[p]['v'][i] for p in parts),2) for i in range(len(months))])
total('Total lift',['Curent lift','Mentenanta lift','Responsabil cu Supravegherea si Verificarea Tehnica a Instalatiilor - ascensor','Autorizare anuala ascensor'])
total('Total curent comun',['Curent casa scarii','Consum energie electrica iluminat public'])
total('Total Diverse',['Reparatie','Refacturare servicii','Dezinsectie si deratizare spatii comune','Statii de intoxicare rozatoare spatii comune','Ingrasamant spatii verzi','Materiale nestocate','Servicii de deszapezire stradala sezon de iarna','Material antiderapant'])
total('Total statie dedurizare',['Mentenanta statie de dedurizare','Mentenanta centrala termica'])
total('Total servicii administrative',['Servicii administrative – suprafata utila','Servicii administrative – terasa'])
# lists: text after the last dash
def detail(r):
    lines=open(r['inv']+'.txt').read().split('\n'); d=r['desc']
    for i,l in enumerate(lines):
        if re.match(r'^\s*%d\s+'%r['n'],l) and r['desc'][:40] in l:
            if i+1<len(lines) and lines[i+1].strip() and not re.match(r'^\s*\d',lines[i+1]) and 'Subtotal' not in lines[i+1] and 'Observatii' not in lines[i+1]: d+=' '+lines[i+1].strip()
            break
    return re.split(r'\s[-–]\s',d)[-1].strip()
for nm in ['Dezinsectie si deratizare spatii comune','Statii de intoxicare rozatoare spatii comune','Ingrasamant spatii verzi','Materiale nestocate']:
    C[nm]['items']=[[] for _ in months]; C[nm]['note']='descrierea din factură pentru fiecare lună'
    for r in rows:
        if cat(r['desc'])==nm: C[nm]['items'][months.index(r['month'])].append([detail(r),r['gross']])
for nm,c in C.items():
    if c.get('items') and c['items'] and all(it and it[-1][0].startswith('Cantitate') for it in c['items']):
        c['qty']=[float(it[-1][0].split(':')[1].split()[0]) for it in c['items']]; c['unit']=c['items'][0][-1][0].split()[-1]
        del c['items']; c.pop('note',None)
# render kinds
for nm,c in C.items():
    if nm in('Reparatie','Refacturare servicii'): c['kind']='cells'
    elif c.get('items'): c['kind']='list'
    if nm.startswith('Consum apa') and 'items' in c or nm==U: c['grid2']=True
C['Total apa calda']['grid2']=True
C['Total factura']=dict(name='Total factura',v=out['tot'])
layout=[['Total factura'],
 ['Consum apa rece si canal menajer','Consum apa spatii verzi','Servicii supraveghere video spatii comune'],
 ['Consum apa calda',U,'Total apa calda'],
 ['Curent lift','Mentenanta lift','Responsabil cu Supravegherea si Verificarea Tehnica a Instalatiilor - ascensor','Autorizare anuala ascensor','Total lift'],
 ['Curent casa scarii','Consum energie electrica iluminat public','Total curent comun'],
 ['Servicii administrative – suprafata utila','Servicii administrative – terasa','Total servicii administrative'],
 ['Preluare apa pluviala','Abonament internet spatii comune','Gunoi menajer'],
 ['Mentenanta statie de dedurizare','Mentenanta centrala termica','Total statie dedurizare'],
 ['Reparatie'],['Refacturare servicii'],
 ['Dezinsectie si deratizare spatii comune','Statii de intoxicare rozatoare spatii comune','Ingrasamant spatii verzi','Materiale nestocate'],
 ['Servicii de deszapezire stradala sezon de iarna','Material antiderapant','Total Diverse']]
used=[n for r in layout for n in r]
missing=[n for n in C if n not in used]; print('missing',missing)
assert len(used)==len(set(used)),'dup'
C['Preluare apa pluviala']['legend']='<b>Cum se calculează</b> (Compania Apa Brașov, Regulament – Anexa 2, pct. 3)<br>\n<code>Qpt = C1 × ST × 0,6</code> și se facturează la tariful de canalizare-epurare.<br>\n• <b>Qpt</b> – apa pluvială evacuată în canalizare, în mc/lună<br>\n• <b>C1</b> – precipitația medie (media anului precedent, date ANM); 1 mm = 0,001 mc/mp<br>\n• <b>ST</b> – suprafața totală construită și neconstruită declarată (mp)<br>\n• <b>0,6</b> – coeficient mediu de scurgere<br>\n<b>Preț în Brașov</b> (din 01.01.2026): canalizare-epurare <b>6,69 lei/mc fără TVA</b> (≈ 7,43 cu TVA 11%). Apă + canal cumulat: 17,03 lei/mc cu TVA.<br>\n<b>Exemplu (ilustrativ):</b> ST = 1.000 mp, C1 = 60 mm/lună → Qpt = 0,060 × 1.000 × 0,6 = 36 mc → 36 × 6,69 = 240,84 lei fără TVA → cu TVA 11% = 267,33 lei.<br>\n<b>Exemplu din factura ta:</b> 11,63 lei fără TVA ÷ 6,69 lei/mc ≈ 1,74 mc revenind pe cota ta parte; TVA 11% = 1,28 lei → 12,91 lei (cât apare pe facturi începând cu cea din aprilie 2026, adică luna martie).<br>\n<span class="lg">Notă: regulamentul scutește gospodăriile de taxa de apă pluvială; ea se aplică suprafețelor non-casnice/comune, iar factura îți repartizează doar o cotă parte. Valoarea C1 pentru Brașov nu e publicată în regulament, deci exemplul cu 60 mm e orientativ. Sume de 5,95 și 8,50 lei (fără TVA) înainte de aprilie nu sunt explicate în factură. Surse: Regulament Apa Brașov (ed. 2023), Capital.ro (17,03 lei/mc), clasament ANRSC la 1.02.2026 (Alba24).</span>'
for nm,c in C.items():
    c['shift']=not(nm.startswith('Servicii administrative') or nm=='Total servicii administrative' or nm=='Total factura')
Z={2:('Apă caldă','#f47230'),3:('Lift','#6a4ce2'),4:('Curent comun','#f2a600'),5:('Servicii administrative','#00b894'),7:('Stație dedurizare','#ee7fac')}
for i in range(8,12): Z[i]=('Diverse','#8a8a8a')
zones=[Z.get(i) for i in range(len(layout))]
data=dict(months=months,cats=C,layout=layout,zones=zones)
t=open('tpl.html').read()
# --- template changes
t=t.replace("document.getElementById('tot').innerHTML=card('Total factura',D.tot,200,true);\n","")
a=t.index("function itemCard"); b=t.index("document.addEventListener")
js='''const aggr=c=>{const sum=c.v.reduce((a,b)=>a+b,0),k=c.v.filter(x=>x>0).length;return {sum,k,avg:f(sum/c.v.length)+' RON/lună (12 luni)'+(k<c.v.length?' · '+f(sum/k)+' RON pe lunile facturate':'')}};
function build(c,cols){ML=D.months.map(m=>lab(m,c.shift?1:0));const G=document.getElementById('g').clientWidth,W0=Math.max(220,Math.floor((G-14*(cols-1))/cols-26));const wide=c.kind==='cells'||c.name==='Total factura',a=aggr(c);
 let h=`<div class="card${wide?' wide':''}"><h2>${c.name}</h2><div class="meta">Total ${f(a.sum)} RON · facturat în ${a.k} din ${c.v.length} luni<br>Medie (linia punctată): ${a.avg}${c.qavg?`<br>Cantitate medie: ${c.qavg}`:''}${c.note?`<br>${c.note}`:''}</div>${c.legend?(()=>{const i=c.legend.indexOf('<br>');return `<details class="legend"><summary>${c.legend.slice(0,i)}</summary><div class="lb">${c.legend.slice(i+4)}</div></details>`})():''}${chart(c.name,c.v,wide?(c.name==='Total factura'?200:170):190,wide,wide?G-26:W0,c.qty,c.unit)}`;
 if(c.kind==='cells')h+=`<div class="cells">${c.items.map((it,i)=>`<div class="cell"><b>${ML[i]}</b>${it.map(x=>`<div class="it">${x[0]}${x[1]==null?'':`<br><span>${f(x[1])} RON</span>`}</div>`).join('')||'<div class="it none">–</div>'}</div>`).join('')}</div>`;
 else if(c.kind==='list')h+=`<div class="list${c.grid2?' g2':''}">${c.items.map((it,i)=>it.length?`<div class="li"><b>${ML[i]}</b> ${it.map(x=>x[0]+(x[1]==null?'':` <span>${f(x[1])} RON</span>`)).join('; ')}</div>`:'').join('')}</div>`;
 return h+'</div>'}
function render(){const narrow=innerWidth<900;let out='',i=0;const L=D.layout;
 const rowHtml=r=>{const cols=narrow?1:(r.length==1?1:Math.max(3,r.length));return `<div class="row" style="grid-template-columns:repeat(${cols},minmax(0,1fr))">${r.map(n=>build(D.cats[n],cols)).join('')}</div>`};
 while(i<L.length){const z=D.zones[i];if(!z){out+=rowHtml(L[i]);i++;continue}
  let j=i,inner='';while(j<L.length&&D.zones[j]&&D.zones[j][0]===z[0]){inner+=rowHtml(L[j]);j++}
  out+=`<section class="zone" style="--zc:${z[1]}"><div class="zl">${z[0]}</div>${inner}</section>`;i=j}
 document.getElementById('g').innerHTML=out}
render();let rt;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(render,150)});
'''
t=t[:a]+js+t[b:]
t=t.replace('<div id="tot"></div><div class="grid" id="g"></div>','<div id="g"></div>')
t=t.replace(".grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}",".row{display:grid;gap:14px;margin-bottom:14px}")
t=t.replace("@media(max-width:900px){.grid{grid-template-columns:1fr}}","@media(max-width:900px){.row{grid-template-columns:1fr!important}}")
t=t.replace(".card.wide{grid-column:1/-1;margin-bottom:14px}",".card.wide{grid-column:1/-1}")
t=t.replace("</style>",".zone{border-left:5px solid var(--zc);background:color-mix(in srgb,var(--zc) 9%,transparent);border-radius:8px;padding:8px 10px 0;margin-bottom:14px}.zone .row:last-child{margin-bottom:10px}.zl{font-weight:700;font-size:13px;margin:0 0 8px;color:var(--tx)}.zl::before{content:'';display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--zc);margin-right:6px}.legend{font-size:12px;line-height:1.5;margin:6px 0 8px;padding:8px 10px;border:1px solid var(--bd);border-radius:6px;background:rgba(127,127,127,.07)}.legend summary{cursor:pointer;list-style:none;display:block;position:relative;padding-right:24px}.legend summary::-webkit-details-marker{display:none}.legend summary::after{content:'▾';position:absolute;right:2px;top:-2px;font-size:18px;color:var(--tx2);transition:transform .15s}.legend[open] summary::after{transform:rotate(180deg)}.legend .lb{margin-top:6px}.legend code{font-weight:700}.legend .lg{display:block;margin-top:4px;color:var(--tx2);font-size:11px}.list{margin-top:6px;font-size:11px;line-height:1.35}.list .li{padding:2px 0;border-top:1px solid var(--grid)}.list b{color:var(--tx2);font-weight:600}.list span{color:var(--tx2)}.list.g2{display:grid;grid-template-columns:1fr 1fr;column-gap:10px}</style>",1)
t=t.replace("h2{min-height:2.8em;","h2{min-height:0;")
open('tpl2.html','w').write(t)
open('index.html','w').write(t.replace('__DATA__',json.dumps(data)))
