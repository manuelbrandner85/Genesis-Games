# Erzeugt Bildschirmtext-Liste und Geräusch-/UI-Klang-Liste.
# Aufruf: python3 paket2.py --drehbuch PFAD/GENESIS_ScriptLock_11_Drehbuch_v1.1.md --v62 PFAD/zum/entpackten/V62 [--out ZIELORDNER]
# Standard für --out: der Ordner über diesem Skript (docs/audio_cinematics/).
import csv,glob,re,argparse,hashlib,os,sys
SCRIPTLOCK_SHA256='b23a047b13c1a7d77d00679c757f4fbcaa6cfc3e736305a7f77152c072ce732d'
ap=argparse.ArgumentParser()
ap.add_argument('--drehbuch',required=True);ap.add_argument('--v62',required=True)
ap.add_argument('--out',default=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
a=ap.parse_args()
h=hashlib.sha256(open(a.drehbuch,'rb').read()).hexdigest()
if h!=SCRIPTLOCK_SHA256: sys.exit(f'ScriptLock-SHA256 falsch: {h}')
OUT=os.path.join(a.out,'')
D=open(a.drehbuch,encoding='utf-8').read().split('\n')
def tc(s):
    f=round(s*24);return f"{f//86400:02d}:{f//1440%60:02d}:{f//24%60:02d}:{f%24:02d}"
# --- 1) Bildschirmtexte: (Szene, Shot, Shot-Start s, Typ, Text, Zeile, Hinweis)
T=[
('C01','01-D',65,'Titel','GENESIS – DER KREISLAUF DES LEBENS',112,'schwarzes Titelbild'),
('C01','01-D',65,'Titel-Unterzeile','Jede Entscheidung hinterlässt ein Echo.',112,'unter dem Titel'),
('C01','01-D',65,'Aufforderung','Beliebige Taste drücken',112,'nach kurzer Stille'),
('C01','Übergabe',None,'Menüpunkt','Neues Leben',116,''),
('C01','Übergabe',None,'Menüpunkt','Fortsetzen',116,''),
('C01','Übergabe',None,'Menüpunkt','Lebensarchiv',116,'je nach Fortschritt; spoilerfrei'),
('C01','Übergabe',None,'Menüpunkt','Einstellungen',116,''),
('C01','Übergabe',None,'Menüpunkt','Barrierefreiheit',116,''),
('C01','Übergabe',None,'Menüpunkt','Mitwirkende',116,''),
('C01','Übergabe',None,'Menüpunkt','Beenden',116,''),
('C01','Übergabe',None,'Kapitelkarte','KAPITEL I – DER ANFANG',116,'nach „Neues Leben“'),
('C02','02-C',55,'Erklärtext (optional)','Befruchtung',131,'nur Dokumentationsmodus/bei Bedarf; Zeit Annahme'),
('C02','02-D',None,'Erklärtext (optional)','Zygote',131,'nur Dokumentationsmodus/bei Bedarf; Shot-Zuordnung offen'),
('C02','02-E',108,'Erklärtext (optional)','Erste Teilung',131,'nur Dokumentationsmodus/bei Bedarf; Zeit Annahme'),
('C09','09-B',28,'Nachricht (Smartphone)','Alles klar für morgen?',302,'falls passend; auch in Sprachliste (VO_C09)'),
('C09','09-B',28,'Antwortoption (Nachricht)','Ja. Bin aufgeregt.',303,'auch in Sprachliste'),
('C09','09-B',28,'Antwortoption (Nachricht)','Ich geb dir Bescheid.',303,'auch in Sprachliste'),
('C09','09-B',28,'Antwortoption (Nachricht)','[keine Nachricht senden]',303,'Aktion, Wortlaut der UI offen'),
('C11','11-A',0,'Nachricht/Gespräch','Wir können Ihnen den Platz anbieten. Bitte geben Sie uns bis {{FRIST}} Bescheid.',355,'Text oder Anruf – offen; auch in Sprachliste'),
('C16','16-E',213,'Auswahlpunkt','Weiter betrachten',515,'keine Punktewertung'),
('C16','16-E',213,'Auswahlpunkt','Zum nächsten Leben',515,''),
('C16','16-E',213,'Auswahlpunkt','Hier verweilen',515,''),
('C17','17-A',0,'Auswahlpunkt','Neues Leben beginnen',525,'Auswahl in der Bibliothek'),
('C21','21-F',225,'Titelzeile 1','Wir erben eine Welt, die andere vor uns geformt haben.',707,'nacheinander; Zeiten Annahme'),
('C21','21-F',233,'Titelzeile 2','Wir verändern sie durch unser Leben.',708,''),
('C21','21-F',241,'Titelzeile 3','Und wir hinterlassen eine Welt, in der andere weiterleben.',709,''),
('C21','21-F',249,'Titel','GENESIS – Jede Entscheidung hinterlässt ein Echo.',710,''),
('C21','Nachfilm-Wahl',None,'Auswahlpunkt A','In der neuen Welt leben',714,'nur wenn bewohnbar'),
('C21','Nachfilm-Wahl',None,'Auswahlpunkt A (Ersatz)','Weiterentwickeln lassen',714,'wenn nicht bewohnbar'),
('C21','Nachfilm-Wahl',None,'Auswahlpunkt B','Zur Bibliothek zurückkehren',714,''),
('C21','Nachfilm-Wahl',None,'Auswahlpunkt C','Den Kreislauf loslassen',714,''),
('MENÜ','Ingame-Pause',None,'Menüpunkt','Fortsetzen',788,''),
('MENÜ','Ingame-Pause',None,'Menüpunkt','Speichern',788,'nur wenn konsistent'),
('MENÜ','Ingame-Pause',None,'Menüpunkt','Laden',788,''),
('MENÜ','Ingame-Pause',None,'Menüpunkt','Einstellungen',788,''),
('MENÜ','Ingame-Pause',None,'Menüpunkt','Lebensarchiv',788,'freigeschaltet'),
('MENÜ','Ingame-Pause',None,'Menüpunkt','Hauptmenü',788,''),
('MENÜ','Hauptmenü',None,'Dialog','Neue Geschichte beginnen',786,'nur wenn Spielstand überschrieben würde'),
]
# Zeilennummern für Menüs prüfen
for i,l in enumerate(D,1):
    if l.startswith('**Ingame-Pause:**'): ip=i
    if l.startswith('**Neues Leben:**'): nl=i
rows=[];cnt={}
for sc,sh,t0,typ,txt,ln,h in T:
    if ln==788: ln=ip
    if ln==786: ln=nl
    cnt[sc]=cnt.get(sc,0)+1
    sid=f'TXT_{sc if sc!="MENÜ" else "MENU"}_{cnt[sc]:03d}'
    if t0 is None: s,st='','interaktiv – kein Filmzeitcode'
    else:
        dur=max(1.5,len(txt)/15+0.5); s=(tc(t0+1),tc(t0+1+dur)); st='vorläufig/geschätzt'
    rows.append([sid,sc,sh,typ,txt,s[0] if s else '',s[1] if s else '',st,'de-DE',h,ln])
with open(OUT+'genesis_bildschirmtexte.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['SubtitleID','Szene','Shot/Ort','Typ','Text','Start-Zeitcode','End-Zeitcode','Zeitcode-Status','Sprache','Hinweis','Quelle (Zeile im Drehbuch)']);w.writerows(rows)
print('texte',len(rows))
# Sprachliste gegen Untertitelregeln prüfen
S=list(csv.reader(open(OUT+'genesis_sprachzeilen_C00-C21.csv',encoding='utf-8'),delimiter=';'))
H=S[0];ix={h:i for i,h in enumerate(H)}
long=[r[0] for r in S[1:] if len(r[ix['Text']])>84]
def s2(x):h,m,se,f=map(int,x.split(':'));return h*3600+m*60+se+f/24
fast=[r[0] for r in S[1:] if r[ix['Start-Zeitcode']] and len(r[ix['Text']])/max(0.1,s2(r[ix['End-Zeitcode']])-s2(r[ix['Start-Zeitcode']]))>17]
print('long',len(long),long);print('fast',len(fast),fast)
# --- 3) Geräusche/UI
X=[]
V25=glob.glob(a.v62+'/x/*/04_PRODUKTIONSREGISTER/196_TESTSLICE_ASSETS.csv')[0]
for r in csv.DictReader(open(V25,encoding='utf-8-sig')):
    if r['Type']=='Sound':
        n=r['SourceName']
        if n.startswith('Amb_'): L,lu,bus='Loop 60–120 s, nahtlos','-30 LUFS (Loop, kurzfristig gemessen), ≤ -1 dBTP','AMBIENCE'
        else: L,lu,bus='One-Shots 0,2–0,6 s, mind. 8 Varianten je Untergrund','-24 LUFS (Referenz-Satz), ≤ -1 dBTP','FOLEY'
        X.append([r['AssetID'],'Testausschnitt VS01 (V25)',n,L,lu,bus,'NOT_CREATED','',''])
V33=glob.glob(a.v62+'/inner/*/01_REGISTER/15_V33_AUDIO_CUES_24.csv')[0]
for r in csv.DictReader(open(V33,encoding='utf-8-sig')):
    b=r['MixBus']
    if b.startswith('UI'): L,lu='0,1–0,8 s','-26 LUFS (One-Shot), ≤ -3 dBTP'
    elif b=='CANON_ORIGINAL': L,lu='aus Drehbuch-Cue (M08/M09)','folgt Musikplan, ≤ -1 dBTP'
    elif b=='BLEND': L,lu='Übergang 2–6 s (Annahme)','kein eigener Pegel – Überblendung, ≤ -1 dBTP'
    else: L,lu='Loop/Schicht 30–90 s (Annahme)','-28 LUFS, ≤ -1 dBTP'
    X.append([r['CueID'],'V33 Gameplay-Cue ('+r['State']+')',r['DesignIntent']+' | Übergang: '+r['TransitionRule']+' | Verbot: '+r['Prohibition'],L,lu,b,r['Status'],'',''])
V61=glob.glob(a.v62+'/x/*/04_PRODUKTIONSREGISTER/226_VOLLSPIEL_ANFORDERUNGEN.csv')[0]
for r in csv.DictReader(open(V61,encoding='utf-8-sig')):
    if r['Discipline'] in('Audio','UI'):
        a=r['Discipline']=='Audio'
        X.append([r['RequirementID'],'V61 '+r['Discipline']+'-Anforderung ('+r['StageID']+')',r['ConcreteRequiredDeliverable']+' [Anker: '+r['SourceAnchor']+']',
          'je nach Szene (offen)' if a else 'UI-Klänge 0,1–0,8 s, falls nötig',
          'Szenenmix -24 LUFS integriert, ≤ -1 dBTP' if a else '-26 LUFS (One-Shot), ≤ -3 dBTP',
          'SCENE_MIX (offen)' if a else 'UI',r['State'],'',''])
SA=('KI-generiert (geplant): Stable Audio, Stability AI','geplant: Stable Audio Commercial & Usage Licensing, https://kb.stability.ai/knowledge-base/stable-audio-commerical-and-usage-licensing (geprüft 23.10.2026)')
EL=('KI-generiert (geplant): ElevenLabs (Text-to-Speech, Voice Design)','geplant: ElevenLabs Terms of Service EEA, bezahlter Tarif, https://elevenlabs.io/terms-of-use-eu (geprüft 23.10.2026)')
for r in X:
    voice=bool(re.search(r'Stimm|Ensemble|Sprach|Dialog|Voice',r[2])); q,l=EL if voice else SA
    r[7]=q;r[8]=l;r[6]='SOURCE_MISSING (keine Datei; Paketstatus: '+r[6]+')';r+=['AUD-R09' if voice else 'AUD-R17','NONE']
with open(OUT+'genesis_geraeusche_ui_klaenge.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['ID','Herkunft','Beschreibung','Länge (Annahme)','Lautheitsziel (Annahme)','Mix-Bus','Status','Quelle','Lizenz','Rechte-ID','Authorization']);w.writerows(X)
from collections import Counter
print('sfx',len(X),Counter(x[1].split(' (')[0] for x in X))
