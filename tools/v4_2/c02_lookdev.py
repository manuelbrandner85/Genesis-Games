"""CR-001 Phase 3 (inside Blender 5.2): look-dev stage for the C02 micro assets (1 unit = 1 um).

Brightfield-like stage to compare with the approved microscope references: a large, evenly lit fluid
background (transmitted light through the sample) plus a weak oblique light, as in Hoffman/DIC
illumination. Cycles on the GPU (OptiX), AgX. render_check(path, target, size) frames an object and
renders a still.
"""
import bpy
from mathutils import Vector


def setup(exposure=0.0, gpu=False, mode="dark"):
    """gpu=False: look checks on the CPU while Unreal/ComfyUI hold the graphics memory; final renders
    run on the GPU in a background Blender inside the GAMEFORGE gpu_slot."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    if gpu:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == "OPTIX"
    sc.cycles.device = "GPU" if gpu else "CPU"
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.samples = 512
    sc.cycles.use_denoising = True
    sc.cycles.denoising_use_gpu = gpu
    sc.cycles.max_bounces = 24
    sc.cycles.transmission_bounces = 24
    sc.cycles.transparent_max_bounces = 32
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "None"):
        try:
            sc.view_settings.look = look
            break
        except TypeError:
            continue
    sc.view_settings.exposure = exposure
    w = bpy.data.worlds.get("W_C02_Durchlicht") or bpy.data.worlds.new("W_C02_Durchlicht")
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    # dark: darkfield (dark fluid, light only from the side) - close to the in-game situation;
    # bright: transmitted light like the brightfield/DIC references
    bg.inputs["Color"].default_value = (0.012, 0.013, 0.015, 1) if mode == "dark" else (0.40, 0.40, 0.38, 1)
    bg.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    sc.world = w
    # Oblique light (condenser offset): gives the relief of Hoffman/DIC images
    lamp = bpy.data.objects.get("L_C02_Schraeglicht")
    if not lamp:
        ld = bpy.data.lights.new("L_C02_Schraeglicht", "AREA")
        lamp = bpy.data.objects.new("L_C02_Schraeglicht", ld)
        sc.collection.objects.link(lamp)
    lamp.data.energy = 30000.0 if mode == "dark" else 6000.0   # W, 60 x 60 unit area light (units are um): measured
    lamp.data.size = 60
    lamp.visible_camera = False
    lamp.location = (-40, -60, 120)
    lamp.rotation_euler = (0.45, -0.3, 0)
    cam = bpy.data.objects.get("CAM_C02_Pruef")
    if not cam:
        cam = bpy.data.objects.new("CAM_C02_Pruef", bpy.data.cameras.new("CAM_C02_Pruef"))
        sc.collection.objects.link(cam)
    cam.data.lens = 100
    cam.data.sensor_width = 36
    cam.data.clip_start = 0.05
    cam.data.clip_end = 10000
    sc.camera = cam
    return cam


def frame(cam, target_objs, margin=1.12):
    """Top view, orthographic like a microscope objective; the whole object inside the frame."""
    bpy.context.view_layer.update()              # fresh objects: matrix_world is only valid after an update
    pts = [o.matrix_world @ Vector(c) for o in target_objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) / 2
    sc = bpy.context.scene
    aspect = sc.render.resolution_x / sc.render.resolution_y
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max((hi - lo).x, (hi - lo).y * aspect) * margin
    cam.location = center + Vector((0, 0, max(50.0, (hi - lo).z * 4)))
    cam.rotation_euler = (0, 0, 0)


def render_check(path, objs, width=1600, height=900, samples=512, gpu=False, mode="dark"):
    sc = bpy.context.scene
    cam = setup(gpu=gpu, mode=mode)
    sc.render.resolution_x, sc.render.resolution_y = width, height
    frame(cam, objs)
    sc.cycles.samples = samples
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    return path


def optical_section(cam, center_z=0.0, thickness=24.0):
    """Like a microscope focal plane: only a slab around center_z is visible (ortho camera from +Z)."""
    cam.data.clip_start = max(0.05, cam.location.z - center_z - thickness / 2)
    cam.data.clip_end = cam.location.z - center_z + thickness / 2


def focal_plane(cam, focus_z=0.0, fstop=0.02):
    """Microscope-like optical section: sharp focal plane at focus_z, everything above/below blurs.
    (Clipping the camera instead would cut the cell surfaces open and lose the volume inside.)"""
    cam.data.clip_start = 0.05
    cam.data.clip_end = 100000
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = cam.location.z - focus_z
    cam.data.dof.aperture_fstop = fstop
    cam.data.dof.aperture_blades = 0
