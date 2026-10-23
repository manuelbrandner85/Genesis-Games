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
for r in out: r[17]=r[17].replace('Zeitcode offen','Zeitcode vorläufig/geschätzt')
# Entscheidung 23.10.2026: Shot 20-B = 7,5 s Übergang rein + volle 60 s aus 00-B/00-C (alle 8 C00-Zeilen, Originalton) + 7,5 s Übergang raus
c00={r[0]:r for r in out if r[2]=='C00'}
OFF=60+7.5-12  # C00-Zeit 00:12 entspricht C20-Zeit 01:07,5
def s2(x):h,m,se,f=map(int,x.split(':'));return h*3600+m*60+se+f/24
new=[];done=False
for r in out:
    if r[2]=='C20' and r[4]=='20-B':
        if done: continue
        done=True
        for k in range(1,9):
            o=c00[f'VO_C00_{k:03d}']
            n=list(o);n[2]='C20';n[3]='20-B (Shot-Bereich 01:00–02:15, Reprise 01:07:12–02:07:12)';n[4]='20-B';n[5]=tc(60);n[6]=tc(135)
            n[7]=tc(s2(o[7])+OFF);n[8]=tc(s2(o[8])+OFF)
            n[10]='vorläufig/geschätzt; folgt 1:1 aus C00 (+55,5 s)'
            n[11]=o[11]+', AUS C00 (ORIGINAL-O-TON)'
            n[17]=f'Zeitcode vorläufig/geschätzt; Reprise aus C00, Originalton – keine Neuaufnahme (Quelle {o[0]}, Zeile {o[16]}); Entscheidung 23.10.2026: volle 60 s, alle 8 Zeilen'
            n[16]=o[16]
            new.append(n)
    else: new.append(r)
# C20 neu nummerieren
k=0
for r in new:
    if r[2]=='C20':
        k+=1;r[0]=f'VO_C20_{k:03d}';r[1]=f'SUB_C20_{k:03d}'
out=new
with open('genesis_sprachzeilen_C00-C21_timing.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(H2);w.writerows(out)
from openpyxl import Workbook
wb=Workbook();ws=wb.active;ws.append(H2)
for r in out: ws.append(r)
ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions;wb.save('genesis_sprachzeilen_C00-C21_timing.xlsx')
print(len(out),'est',sum(1 for r in out if r[7]),'over',over)
for r in out[:8]: print(r[0],r[4],r[7],r[8],r[9])
