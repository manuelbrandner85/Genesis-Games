import csv,re
L=open('drehbuch.md',encoding='utf-8').read().split('\n')
rows=list(csv.reader(open('genesis_sprachzeilen_C00-C21.csv',encoding='utf-8'),delimiter=';'))
H=rows[0];R=rows[1:]
WPS=2.3; GAP=0.6; LEAD=1.0
def pause_between(a,b):
    p=0
    for i in range(a+1,b):
        l=L[i-1].strip()
        if l.startswith('*(') and '„' not in l:
            if 'Acht Sekunden' in l:p+=8
            elif 'Drei Sekunden' in l or 'Längere Pause' in l:p+=3
            else:p+=1.5
    return p
def tc(s):
    f=round(s*24); return f"{f//86400:02d}:{f//1440%60:02d}:{f//24%60:02d}:{f%24:02d}"
def sec(x):m,s=x.split(':');return int(m)*60+int(s)
H2=H[:4]+['Shot-ID','Shot-Start','Shot-Ende']+H[4:6]+['Geschätzte Dauer (s)','Zeitcode-Status']+H[6:]
out=[];over=[]
from itertools import groupby
for (sc,sh),grp in groupby(R,key=lambda r:(r[2],r[3])):
    grp=list(grp)
    m=re.match(r'(\d\d-[A-Z]) \(Shot-Bereich ([0-9:]+)–([0-9:]+)\)',sh)
    sid,s0,s1=m.group(1),sec(m.group(2)),sec(m.group(3))
    t=s0+LEAD; prevln=None; slot_end=t; slot_start=t
    for r in grp:
        ln=int(r[11]); w=len(r[9].split()); d=round(w/WPS+0.4,1)
        if sc in('C15','C16'):
            out.append(r[:4]+[sid,tc(s0),tc(s1),'','','', 'zurückgestellt, Kanon-Entscheidung CON33-01 offen']+r[4:6][:0]+r[6:]);continue
        if ln!=prevln:
            if prevln is not None: slot_start=slot_end+GAP+pause_between(prevln,ln)
            prevln=ln
            cur=slot_start; slot_end=cur+d
        else:
            slot_end=max(slot_end,slot_start+d)
        st='vorläufig/geschätzt'
        e=slot_start+d
        if e>s1: st+='; ÜBERLÄUFT Shot-Ende'; over.append(r[0])
        out.append(r[:4]+[sid,tc(s0),tc(s1),tc(slot_start),tc(e),d,st]+r[6:])
for r in out: r[17]=r[17].replace('Zeitcode offen','Zeitcode vorläufig/geschätzt') if r[2] not in('C15','C16') else r[17].replace('Zeitcode offen','zurückgestellt (CON33-01)')
with open('genesis_sprachzeilen_C00-C21_timing.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(H2);w.writerows(out)
from openpyxl import Workbook
wb=Workbook();ws=wb.active;ws.append(H2)
for r in out: ws.append(r)
ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions;wb.save('genesis_sprachzeilen_C00-C21_timing.xlsx')
print(len(out),'est',sum(1 for r in out if r[7]),'zurück',sum(1 for r in out if r[2] in('C15','C16')),'over',over)
for r in out[:8]: print(r[0],r[4],r[7],r[8],r[9])
