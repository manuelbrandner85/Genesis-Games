"""Validate V4.2 scene registry and menu flow. No Unreal runtime claim."""
import argparse, hashlib, json, pathlib, sys

def audit(root:pathlib.Path):
    errors=[];warnings=[]
    try:
        scenes=json.loads((root/'docs/v4_2/SCENE_MATRIX_C00_C21.json').read_text(encoding='utf-8'))
        menu=json.loads((root/'docs/v4_2/MENU_FLOW.json').read_text(encoding='utf-8'))
    except Exception as e:return {'status':'INVALID','errors':[str(e)]}
    items=scenes['scenes']; ids=[s.get('scene_id') for s in items]
    expected=[f'C{i:02d}' for i in range(22)]
    if ids!=expected:errors.append('scene ID/order mismatch (must be C00..C21 exactly)')
    if len(set(ids))!=22:errors.append('duplicate/missing scene ID')
    if scenes.get('replay_master_rule',{}).get('shared_master_asset_id')!='C00_ORIGINAL_MASTER':errors.append('C00/C20 master reference must be shared')
    if any(item.get('implementation_status') not in ['NOT_IMPLEMENTED','SPECIFIED','BUILT_UNTESTED','ENGINE_TESTED','ACCEPTED'] for item in items):errors.append('invalid scene implementation status')
    for item in items:
        if item.get('implementation_status') in ('ENGINE_TESTED','ACCEPTED') and not item.get('sequence_asset_path'):
            errors.append(item['scene_id']+': has engine claim without asset path')
        if item.get('approval_status')=='SOURCE_PENDING':warnings.append(item['scene_id']+': original source not verified')
    nodes=menu['nodes']; nodeids=[n['id'] for n in nodes];nodemap={n['id']:n for n in nodes}
    if len(set(nodeids))!=len(nodeids):errors.append('menu duplicate node ID')
    for node in nodes:
        for edge in node.get('edges',[]):
            if edge not in nodemap:errors.append('bad edge '+node['id']+'->'+edge)
    reachable=set();to_visit=[menu['initial']]
    while to_visit:
        nid=to_visit.pop()
        if nid not in nodemap or nid in reachable:continue
        reachable.add(nid);to_visit.extend(nodemap[nid]['edges'])
    for essential in ['MAIN_MENU','IN_GAME','SETTINGS','ACCESSIBILITY','CREDITS','QUIT','EXIT']:
        if essential not in reachable:errors.append('unreachable '+essential)
    if len(reachable)!=len(nodes):errors.append('unreachable menu nodes: '+str(sorted(set(nodeids)-reachable)))
    return {'status':'STATIC_PASS_ONLY_NOT_ENGINE_TESTED' if not errors else 'INVALID','errors':errors,'warnings':warnings,'scene_count':len(items),'menu_nodes':len(nodes)}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[2]);a=ap.parse_args();r=audit(a.root);print(json.dumps(r,ensure_ascii=False,indent=2));sys.exit(bool(r['errors']))
