"""Use: blender -b file.blend --python tools/blender/asset_audit.py -- output.json"""
import bpy,sys,json,time,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:raise SystemExit('usage: -- OUTPUT_JSON')
out=Path(args[0]).resolve();out.parent.mkdir(parents=True,exist_ok=True)
rows=[]; errors=[]
for obj in bpy.data.objects:
 if obj.type!='MESH':continue
 mesh=obj.data
 info={'name':obj.name,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'uv_layers':len(mesh.uv_layers),'materials':len(mesh.materials),'dims_m':[round(float(x),5) for x in obj.dimensions],'scale':list(obj.scale)}
 if len(mesh.vertices)<4 or len(mesh.polygons)<2:errors.append(obj.name+': insufficient mesh geometry')
 if not mesh.uv_layers:errors.append(obj.name+': no UV layer')
 if not mesh.materials:errors.append(obj.name+': no material slot')
 if any(abs(float(s)-1.0)>0.001 for s in obj.scale):errors.append(obj.name+': unapplied scale')
 rows.append(info)
if not rows:errors.append('No mesh objects in .blend')
report={'type':'BLENDER_GEOMETRY_AUDIT','blender_version':bpy.app.version_string,'blend_file':bpy.data.filepath,'meshes':rows,'errors':errors,'passed_static_checks':not errors,'unreal_import_tested':False,'visual_review_tested':False}
out.write_text(json.dumps(report,indent=2,ensure_ascii=False),'utf-8')
print(json.dumps({'file':str(out),'passed_static_checks':not errors,'errors':errors},ensure_ascii=False))
if errors:raise SystemExit(3)
