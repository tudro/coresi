import json,re
rows=json.load(open('rows.json'))
months=sorted({r['month'] for r in rows})
def cat(d):
    rules=[(r'^Servicii administrative.*terasa','Servicii administrative – terasa'),
    (r'^Servicii administrative','Servicii administrative – suprafata utila'),
    (r'iluminat public','Consum energie electrica iluminat public'),(r'supraveghere video','Servicii supraveghere video spatii comune'),
    (r'apa rece','Consum apa rece si canal menajer'),(r'apa calda','Consum apa calda'),(r'incalzirea apei','Utilitati consumate pentru incalzirea apei (gaz; curent)'),
    (r'^Gunoi','Gunoi menajer'),(r'^Curent lift','Curent lift'),(r'casa scarii','Curent casa scarii'),
    (r'^Mentenanta lift','Mentenanta lift'),(r'^Responsabil','Responsabil cu Supravegherea si Verificarea Tehnica a Instalatiilor - ascensor'),(r'^Autorizare','Autorizare anuala ascensor'),
    (r'pluviala','Preluare apa pluviala'),(r'^Consum apa spatii verzi','Consum apa spatii verzi'),(r'^Abonament internet','Abonament internet spatii comune'),
    (r'^Reparatie','Reparatie'),(r'^Refacturare','Refacturare servicii'),
    (r'deszapezire','Servicii de deszapezire stradala sezon de iarna'),
    (r'^Dezinsectie','Dezinsectie si deratizare spatii comune'),(r'intoxicare','Statii de intoxicare rozatoare spatii comune'),
    (r'centrala termica','Mentenanta centrala termica'),(r'dedurizare','Mentenanta statie de dedurizare'),
    (r'antiderapant','Material antiderapant'),(r'nestocate','Materiale nestocate'),(r'[Ii]ngrasamant','Ingrasamant spatii verzi')]
    for p,n in rules:
        if re.search(p,d): return n
    raise Exception(d)
data={}
for r in rows:
    c=cat(r['desc']); data.setdefault(c,{m:0 for m in months})
    data[c][r['month']]=round(data[c][r['month']]+r['gross'],2)
tot={m:round(sum(r['gross'] for r in rows if r['month']==m),2) for m in months}
cats=sorted(data,key=lambda c:-sum(data[c].values()))
out=dict(months=months,tot=[tot[m] for m in months],cats=[dict(name=c,v=[round(data[c][m],2) for m in months]) for c in cats])
import glob
det={'Reparatie':{m:[] for m in months},'Refacturare servicii':{m:[] for m in months}}
for r in rows:
    c=cat(r['desc'])
    if c in det:
        lines=open(r['inv']+'.txt').read().split('\n')
        for i,l in enumerate(lines):
            if re.match(r'^\s*%d\s+'%r['n'],l) and r['desc'][:40] in l:
                d=r['desc']
                if i+1<len(lines) and lines[i+1].strip() and not re.match(r'^\s*\d',lines[i+1]) and 'Subtotal' not in lines[i+1] and 'Observatii' not in lines[i+1]:
                    d+=' '+lines[i+1].strip()
                d=re.sub(r'^.*?Cost pe cota parte\s*-?\s*','',d)
                det[c][r['month']].append([d,r['gross']]);break
for c in out['cats']:
    if c['name'] in det: c['items']=[det[c['name']][m] for m in months]
qn={'Consum apa rece si canal menajer','Consum apa calda','Utilitati consumate pentru incalzirea apei (gaz; curent)'}
q={c:{m:0 for m in months} for c in qn}; um={}
for r in rows:
    c=cat(r['desc'])
    if c in qn: q[c][r['month']]=round(q[c][r['month']]+r['qty'],3); um[c]=r['um']
g=lambda x:('%g'%x)
for c in out['cats']:
    if c['name'] in qn:
        c['items']=[[['Cantitate: %.2f %s'%(q[c['name']][m],um[c['name']]),None]] for m in months]
        c['note']='cantitatea facturată pentru fiecare lună'
        c['qavg']='%.2f %s/lună'%(sum(q[c['name']].values())/len(months),um[c['name']])
    if c.get('items') and 'note' not in c: c['note']='descrierea din factura pentru fiecare luna'
H='Consum apa calda'; U='Utilitati consumate pentru incalzirea apei (gaz; curent)'
cv={c['name']:c['v'] for c in out['cats']}
out['cats'].append(dict(name=H+' + '+U,v=[round(a+b,2) for a,b in zip(cv[H],cv[U])],
  items=[[['Apa calda: %.2f RON'%cv[H][i],None],['Utilitati: %.2f RON'%cv[U][i],None],['Cantitate: %.2f %s'%(q[H][m],um[H]),None]] for i,m in enumerate(months)],
  note='suma celor două linii, cu detaliu pe lună',qavg='%.2f %s/lună'%(sum(q[H].values())/len(months),um[H])))
out['cats'].sort(key=lambda c:-sum(c['v']) if c['name']!=H+' + '+U else 0)
# keep combined chart right after the hot water / utilities charts
comb=[c for c in out['cats'] if c['name']==H+' + '+U][0]; out['cats'].remove(comb)
i=max(k for k,c in enumerate(out['cats']) if c['name'] in(H,U)); out['cats'].insert(i+1,comb)
json.dump(out,open('out.json','w'))
html=open('tpl.html').read().replace('__DATA__',json.dumps(out))
open('index.html','w').write(html)
print(len(cats),[ (c,round(sum(data[c].values()),2)) for c in cats][:5], sum(tot.values()))
