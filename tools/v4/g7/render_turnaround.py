"""G7: Cycles turnaround of a look-dev .blend (headless: blender -b file.blend -P this.py -- OUTDIR [SAMPLES] [OBJECT]).
Uses the LD_Cam camera, orbits it around the object centre in four views plus one close-up per socket."""
import bpy, math, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
samples = int(argv[1]) if len(argv) > 1 else 256
obj_name = argv[2] if len(argv) > 2 else None
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "OPTIX"
prefs.get_devices()
for d in prefs.devices:
    d.use = d.type == "OPTIX"
sc.cycles.device = "GPU"
sc.cycles.samples = samples
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
sc.render.image_settings.file_format = "PNG"
cam = sc.camera
gen = sc.objects[obj_name] if obj_name else next(o for o in sc.objects if o.name.startswith("SM_"))
for o in sc.objects:
    if o.name.startswith("SM_") and o is not gen:
        o.hide_render = True
bb = [gen.matrix_world @ Vector(c) for c in gen.bound_box]
size = max(max(v[i] for v in bb) - min(v[i] for v in bb) for i in range(3))
centre = Vector((sum(v.x for v in bb) / 8, sum(v.y for v in bb) / 8, max(v.z for v in bb) * 0.48))
radius, height = 2.55 * size, 1.05 * size


def shoot(name, loc, target, lens=50, fstop=8):
    cam.location = loc
    cam.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.data.dof.focus_distance = (target - Vector(loc)).length
    cam.data.dof.aperture_fstop = fstop
    sc.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)


for name, ang in (("view_front34", -125), ("view_back34", 55), ("view_left", 180), ("view_right", 0)):
    a = math.radians(ang)
    shoot(name, (centre.x + radius * math.cos(a), centre.y + radius * math.sin(a), height), centre)
for s in [o for o in gen.children if o.name.startswith("SOCKET_")]:
    p = s.matrix_world.translation
    d = Vector((-0.3, -1.0, 0.08)).normalized() if s.name != "SOCKET_TryStart" else Vector((-1.0, -0.55, 0.35)).normalized()
    shoot("close_" + s.name.replace("SOCKET_", ""), tuple(p + d * 0.42), p, lens=85, fstop=5.6)
print("TURNAROUND_DONE", out)
