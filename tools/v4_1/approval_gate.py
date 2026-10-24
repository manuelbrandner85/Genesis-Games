"""Approval-plan SHA validation. Cannot authenticate an actual human: governance check, never a sandbox."""
import argparse,hashlib,json,sys
from pathlib import Path
REQUIRED=['plan_id','tool_id','source_url','source_revision','license_evidence','download_size_gb','install_directory','commands','rollback']

def canonical(o):return json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
def digest(plan):return hashlib.sha256(canonical(plan)).hexdigest()
def check_plan(plan):
    missing=[x for x in REQUIRED if x not in plan or plan[x] in (None,'',[])]
    if missing:raise ValueError('MISSING_FIELDS: '+', '.join(missing))
    if not isinstance(plan['commands'],list):raise ValueError('COMMANDS_NOT_LIST')
    if plan.get('paid_api') is True or plan.get('cloud_service') is True:raise ValueError('PAID_OR_CLOUD_BLOCKED')
    return True

def valid_receipt(plan,receipt):
    check_plan(plan)
    return receipt.get('plan_sha256')==digest(plan) and receipt.get('approved') is True and receipt.get('scope')=='ONE_TOOL_REVISION' and receipt.get('confirmation')==f"FREIGABE {plan['plan_id']}"

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--receipt',type=Path);ap.add_argument('--verify',action='store_true');ap.add_argument('--interactive-receipt',action='store_true');args=ap.parse_args()
    p=json.loads(args.plan.read_text(encoding='utf8'));check_plan(p)
    if args.interactive_receipt:
        if not sys.stdin.isatty():raise SystemExit('BLOCKED: human interactive console required')
        print('Nur ein organisatorischer Freigabebeleg. Prüfe vorher Tool-Quelle, Lizenz, exakte Befehle, Downloadgröße, Risiken und Rollback.\n',json.dumps(p,indent=2,ensure_ascii=False))
        confirm=input('Bitte bei wirklich manueller Zustimmung exakt eingeben: FREIGABE '+p['plan_id']+'\n> ')
        if confirm!=f"FREIGABE {p['plan_id']}":raise SystemExit('NOT_APPROVED')
        receipt={'plan_sha256':digest(p),'approved':True,'scope':'ONE_TOOL_REVISION','confirmation':confirm,'created_by':'interactive_console'}
        out=args.receipt or args.plan.with_suffix('.approval.json')
        out.parent.mkdir(parents=True,exist_ok=True)
        if out.exists():raise SystemExit('BLOCKED: receipt exists, refusing overwrite')
        out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('RECEIPT_WRITTEN_NOT_INSTALLED:',out)
    elif args.verify:
        if not args.receipt:raise SystemExit('--receipt required')
        receipt=json.loads(args.receipt.read_text(encoding='utf8'))
        if not valid_receipt(p,receipt):raise SystemExit('NOT_APPROVED_OR_CHANGED_PLAN')
        print('PLAN_APPROVED_RECEIPT_MATCHES; NO INSTALLATION EXECUTED')
    else:print(json.dumps({'plan_hash_sha256':digest(p),'status':'REVIEW_REQUIRED','install_executed':False},indent=2))
if __name__=='__main__':main()
