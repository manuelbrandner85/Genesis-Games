"""G7: final-quality Cycles renders of the furnished R03 workshop (headless).

    blender -b ArtSource/Blender/G7/R03_Werkstatt_G7.blend -P tools/v4/g7/render_room.py -- OUTDIR [SAMPLES] [EXPOSURE] [SHOT,SHOT]

Light is physical and matches the Unreal level: sun from the level's DirectionalLight (pitch -38,
yaw 215 -> comes from the north-east, ~100 klx), Poly Haven sky HDRI hausdorf_meadow (CC0) around the
building, LED bar 4000 lm / 4000 K as an area light. 1 W = 683 lm (Blender has no photometric units;
the same factor is used for every light, so the ratios are real). Camera: 35 mm full frame sensor,
exposure fixed for an interior (EV ~6) instead of per shot. AgX, OptiX, OIDN with albedo/normal.
"""
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
samples = int(argv[1]) if len(argv) > 1 else 1024
exposure = float(argv[2]) if len(argv) > 2 else 2.0
only = set(argv[3].split(",")) if len(argv) > 3 else None   # optional subset of shot names
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
ROOT = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", ".."))
LM_PER_W = 683.0

for n in ("LD_Key", "LD_Fill", "LD_Rim", "LD_Floor"):
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = True
for o in sc.objects:
    if o.name.startswith("UCX_"):
        o.hide_render = True

# sky: HDRI, scaled so the open sky gives ~15 klx on the ground (overcast part of a clear morning)
w = sc.world
w.use_nodes = True
nt = w.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(os.path.join(ROOT, "ArtSource", "External", "PolyHaven", "hausdorf_meadow", "hausdorf_meadow_2k.exr"), check_existing=True)
bg = nt.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = 15000.0 / LM_PER_W / 1.0
outn = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs["Background"], outn.inputs["Surface"])


def light(name, kind, loc, rot, energy, **kw):
    o = bpy.data.objects.get(name)
    if o is None:
        L = bpy.data.lights.new(name, kind)
        o = bpy.data.objects.new(name, L)
        sc.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    o.data.energy = energy
    for k, v in kw.items():
        setattr(o.data, k, v)
    o.hide_render = False
    return o


# sun: UE rotator (pitch -38, yaw 215) travels towards (-0.645, -0.452, -0.616) in UE = (-0.645, +0.452, -0.616) in Blender
d = Vector((-0.645, 0.452, -0.616)).normalized()
sun = light("RM_Sun", "SUN", (0, 0, 10), d.to_track_quat("-Z", "Y").to_euler(), 100000.0 / LM_PER_W, angle=math.radians(0.53))
sun.data.color = (1.0, 0.96, 0.90)
# LED bar under the diffuser (bar origin Blender (0.65, -2.18, 3.46), diffuser 0.62 m lower)
led = light("RM_LED", "AREA", (0.65, -2.18, 3.46 - 0.645), (0, 0, 0), 4000.0 / LM_PER_W, shape="RECTANGLE", size=1.48, size_y=0.05)
led.data.color = (1.0, 0.89, 0.78)          # ~4000 K
led.visible_camera = False                   # the diffuser mesh is what the camera sees

prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "OPTIX"
prefs.get_devices()
for dv in prefs.devices:
    dv.use = dv.type == "OPTIX"
sc.render.engine = "CYCLES"
sc.cycles.device = "GPU"
sc.cycles.samples = samples
sc.cycles.adaptive_threshold = 0.01
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
sc.cycles.max_bounces, sc.cycles.diffuse_bounces, sc.cycles.glossy_bounces, sc.cycles.transmission_bounces = 16, 8, 6, 16
sc.cycles.sample_clamp_indirect = 10.0
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = exposure
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_depth = "16"

cam = sc.camera
cam.data.sensor_width = 36.0
cam.data.dof.use_dof = True
# cameras as in the Unreal review (UE local -> Blender: y flipped), eye height 1.65 m
SHOTS = {
    "room_overview": ((-2.9, 2.3, 1.70), (2.0, -1.2, 0.8), 18, 4.0),
    "room_generator": ((-1.15, 1.50, 1.05), (0.5, 2.0, 0.28), 35, 4.0),
    "room_bench": ((-0.60, -0.20, 1.65), (0.5, -2.38, 0.92), 24, 4.0),
    "room_window": ((-1.8, 1.0, 1.60), (3.3, -1.4, 1.5), 24, 5.6),
}
for name, (loc, tgt, focal, fstop) in SHOTS.items():
    if only and name not in only:
        continue
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = focal
    cam.data.dof.focus_distance = (Vector(tgt) - Vector(loc)).length
    cam.data.dof.aperture_fstop = fstop
    sc.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("SHOT", name)
print("ROOM_RENDER_DONE", out)
