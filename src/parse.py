import re,glob,json
rows=[]
for f in sorted(glob.glob('IMLL*.txt')):
    t=open(f).read()
    inv=f[:-4]
    d=re.search(r'Data emitere:\s+(\d\d)\.(\d\d)\.(\d{4})',t)
    date=f"{d[3]}-{d[2]}"
    sect=None
    seen=set()
    for line in t.split('\n'):
        s=line.strip()
        if s in('SERVICII ADMINISTRATIVE','CHELTUIELI DE INTRETINERE') or (s.isupper() and len(s)>12 and not re.search(r'\d',s) and 'FACTURA' not in s and 'TOTAL' not in s and 'DENUM' not in s and 'LEGEA' not in s):
            sect=s
        m=re.match(r'^\s*(\d{1,2})\s+(.*?)\s{2,}(\S+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)\s*$',line)
        if m and (inv,m[1]) not in seen:
            seen.add((inv,m[1]))
            rows.append(dict(inv=inv,month=date,sect=sect,n=int(m[1]),desc=m[2],um=m[3],qty=float(m[4]),net=float(m[6]),vat=float(m[7]),gross=float(m[8])))
json.dump(rows,open('rows.json','w'),indent=0)
import collections
for inv in sorted({r['inv'] for r in rows}):
    rs=[r for r in rows if r['inv']==inv]
    print(inv,rs[0]['month'],len(rs),round(sum(r['net'] for r in rs),2),round(sum(r['gross'] for r in rs),2))
