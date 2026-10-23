import re,csv
L=open('drehbuch.md',encoding='utf-8').read().split('\n')
EXCL={94,102,112,116,121,123,125,131,149,151,180,197,199,232,252,291,318,393,406,430,434,448,463,479,485,515,525,538,607,628,683,684,707,708,709,710,714}
INLINE={220,222,280,338,566}
scene=shot=None; rows=[]
q=re.compile(r'„([^“]*)“')
for i,l in enumerate(L,1):
    if i>=724: break
    m=re.match(r'^## (C\d\d) ',l)
    if m: scene=m.group(1); shot=''; continue
    m=re.match(r'^\*\*SHOT (\d\d-[A-Z]) · ([0-9:]+)–([0-9:]+)',l)
    if m: shot=f"{m.group(1)} (Shot-Bereich {m.group(2)}–{m.group(3)})"
    if not scene or '„' not in l or i in EXCL: continue
    if i in INLINE:
        if i==220: spk='SPIELER';opts=re.findall(r'\*\*([A-D])\*\* „([^“]*)“',l)
        elif i==222: spk='NEUES KIND';opts=re.findall(r'\*\*(\w+)\*\* „([^“]*)“',l)
        elif i==280: spk='SPIELER';opts=re.findall(r'\*\*([A-E])\*\* „([^“]*)“',l)
        elif i==338: spk='SPIELER';opts=[(chr(65+k),t) for k,t in enumerate(q.findall(l))]
        else: spk='ANDERE PERSON';opts=[(chr(65+k),t) for k,t in enumerate(q.findall(l))]
        for v,t in opts: rows.append([scene,shot,spk,f'Option {v}',t,'Wahl-/Reaktionsoption aus Shot-Beschreibung',i])
        continue
    if i==365:
        rows.append([scene,shot,'BEZUGSPERSON','optional',q.findall(l)[0],'(Wenn passend); Sprecher nicht genannt, aus Kontext (Zeile 364)',i]);continue
    m=re.match(r'^\*\*([^*]+?):?\*\*\s*(\*\(([^)]*)\)\*)?:?\s*(.*)$',l)
    spk=m.group(1).rstrip(':').strip(); hint=m.group(3) or ''
    rest=m.group(4); texts=q.findall(rest)
    tail=re.sub(r'„[^“]*“','',rest).strip(' /')
    extra=re.findall(r'\*\(([^)]*)\)\*',rest)
    hint='; '.join([h for h in [hint]+extra if h])
    if len(texts)>1:
        for k,t in enumerate(texts): rows.append([scene,shot,spk,f'Option {chr(65+k)}',t,hint,i])
    else:
        rows.append([scene,shot,spk,'Standard',texts[0],hint,i])
G={83:'„so viel, das ich nie …“: nach „viel“ verlangt die Standardsprache „was“ (so viel, was …). Mögliche Absicht der Sprechweise – nicht geändert.',
595:'„Etwas, das …“: nach „etwas“ ist „was“ üblicher; „das“ ist umgangssprachlich verbreitet.',
212:'„Zeigt bitte, wo alles ist“: Dativobjekt fehlt (ihm/ihr); Name muss bei zwei Vorkommen gleich und flektionsneutral sein.',
250:'{{AKTUELLER_WUNSCH}} muss eine Infinitivgruppe sein (z. B. „… werden“), sonst ungrammatisch.',
371:'{{KONKRETE_HILFE}} muss eine Infinitivgruppe sein („… kann + Infinitiv“).',
422:'„Weißt du noch, {{…}}?“: Variable muss Nebensatz sein (wie/als/dass …), sonst ungrammatisch.',
286:'Umgangssprachlich Indikativ („bist“ statt „wärst“) – zulässig. „mein Freund“ abhängig vom Geschlecht des Spielers (Freund/Freundin).',
370:'„Bis Freitag ja.“: Komma empfohlen („Bis Freitag, ja.“).',
651:'„die gleiche Frage“ – gemeint ist dieselbe Frage; stilistisch, in Alltagssprache akzeptiert.',
355:'„bis {{FRIST}}“: Variable muss mit „bis“ passen (Datum/Wochentag ohne Artikel, sonst „bis zum …“).',
220:'Variable {{SPIELERNAME}}/{{NAME_FREUND}}: keine Flexionsprobleme (Nominativ/nach „auf“ Akkusativ, Name unverändert).',
}
for k in (165,239,272,282,285,335,441,564): G.setdefault(k,'Umgangssprachliche Verkürzung/Apostroph (’s, hab, mein’s, enttäusch) – bewusst, Schreibweise einheitlich halten.')
out=[];cnt={}
REP={81,82,86}; REPC20={636,637,638}
for sc,sh,spk,var,t,hint,ln in rows:
    cnt[sc]=cnt.get(sc,0)+1; n=cnt[sc]
    st=['Zeitcode offen']
    if ln in REP: st.append('Reprise C20, Originalton')
    if ln in REPC20: st.append('Reprise aus C00, Originalton – keine Neuaufnahme (Quelle '+{636:'VO_C00_001, Zeile 81',637:'VO_C00_002, Zeile 82',638:'VO_C00_006, Zeile 86'}[ln]+')')
    vars_=re.findall(r'\{\{(\w+)\}\}',t)
    if vars_:
        st.append('Variable offen: '+', '.join(sorted(set(vars_)))+' – Drehbuch nennt keine konkreten Werte (aus Spielstand)')
        if var=='Standard': var='Variablen-Platzhalter'
    if '/' in spk: st.append('Sprecher-Genusvariante (m/w) offen')
    if var.startswith('Option') or 'optional' in var or 'nur' in hint or 'falls' in hint or 'wenn' in hint.lower(): st.append('bedingt')
    out.append([f'VO_{sc}_{n:03d}',f'SUB_{sc}_{n:03d}',sc,sh,'','',spk,'de-DE',var,t,hint,ln,'; '.join(st),G.get(ln,'')])
H=['AudioCueID','SubtitleID','Szene','Shot','Start-Zeitcode','End-Zeitcode','Sprecher','Sprache','Variante','Text','Klangregie/Hinweis','Quelle (Zeilennummer im Drehbuch)','Status','Grammatik-Fund']
with open('genesis_sprachzeilen_C00-C21.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(H);w.writerows(out)
from openpyxl import Workbook
from openpyxl.styles import Font
wb=Workbook();ws=wb.active;ws.title='Sprachzeilen';ws.append(H)
for r in out: ws.append(r)
for c in ws[1]: c.font=Font(bold=True)
ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
for col,wd in zip('ABCDEFGHIJKLMN',[13,14,6,30,10,10,26,7,18,60,40,10,50,50]): ws.column_dimensions[col].width=wd
wb.save('genesis_sprachzeilen_C00-C21.xlsx')
from collections import Counter
print(len(out)); print(sorted(Counter(r[2] for r in out).items()))
print(Counter(r[6] for r in out).most_common())
print(sum(1 for r in out if r[13]))
for r in out:
  if '„' in r[9] or '**' in r[6] or len(r[6])>45: print('CHK',r)
