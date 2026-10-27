"""CR-001 Phase 3 (background Blender): look-check renders of the C02 micro assets.

    blender -b ArtSource/Blender/C02/C02_Mikrowelt.blend -P tools/v4_2/c02_render_checks.py -- <shot> [<shot> ...]

Shots: oozyte_nackt (egg + zona + polar body, brightfield focal plane), oozyte_spieler (the player's view into
the cumulus, darkfield fluid), eileiter (fold relief), zygote, zweizell. Renders go to ArtSource/Blender/C02/_renders.
Kept out of the interactive session: long Cycles renders blocked/crashed the MCP server there.
"""
import os
import runpy
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ld = runpy.run_path(str(ROOT / "tools/v4_2/c02_lookdev.py"), run_name="ld")
OUT = ROOT / "ArtSource/Blender/C02/_renders"
sc = bpy.context.scene


def only(names):
    for o in sc.objects:
        o.hide_render = not any(o.name.startswith(n) for n in names) and o.type in ("MESH", "CURVE")


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render(name, samples):
    if os.environ.get("C02_FAST"):                 # quick preview: 30 % size, few samples
        sc.render.resolution_percentage = 30
        samples = 16
        name += "_vorschau"
    sc.cycles.samples = samples
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name)


def shot_oozyte_nackt():
    only(["SM_C02_Oozyte", "SM_C02_Zona", "SM_C02_Polkoerper"])
    cam = ld["setup"](mode="bright")
    sc.render.resolution_x = sc.render.resolution_y = 1000
    ld["frame"](cam, [sc.objects["SM_C02_Zona"]])
    cam.data.ortho_scale = 200
    ld["focal_plane"](cam, 0.0, 0.08)
    render("oozyte_nackt_hell", 96)


def shot_oozyte_spieler():
    only(["SM_C02_Oozyte", "SM_C02_Zona", "SM_C02_Polkoerper", "C02_CUMULUS_Verteilung", "SM_C02_CumulusMatrix"])
    cam = ld["setup"](mode="dark")
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    cam.data.type = "PERSP"
    cam.data.lens = 24
    cam.data.dof.use_dof = False
    cam.data.clip_start, cam.data.clip_end = 0.5, 5000
    cam.location = (-380, -120, 60)
    look_at(cam, (0, 0, 0))
    lamp = sc.objects["L_C02_Schraeglicht"]
    lamp.location = (-300, -250, 250)
    look_at(lamp, (0, 0, 0))
    lamp.data.size = 200
    lamp.data.energy = 3500000.0                   # measured: cumulus ~400 um away, cells read at mid-grey
    render("oozyte_spielersicht_dunkel", 96)


def shot_cumulus_nah():
    """Close to the corona (as the cell approaching the oocyte sees it): single cells with their nuclei."""
    only(["SM_C02_Oozyte", "SM_C02_Zona", "C02_CUMULUS_Verteilung", "SM_C02_CumulusMatrix"])
    cam = ld["setup"](mode="dark")
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    cam.data.type = "PERSP"
    cam.data.lens = 35
    cam.data.dof.use_dof = False
    cam.data.clip_start, cam.data.clip_end = 0.2, 3000
    cam.location = (-150, -40, 30)
    look_at(cam, (0, 0, 0))
    lamp = sc.objects["L_C02_Schraeglicht"]
    lamp.location = (-130, -90, 90)
    look_at(lamp, (0, 0, 0))
    lamp.data.size = 60
    lamp.data.energy = 1.0e6                       # measured in the preview: 2.5e5 left the cloud dull grey
    render("cumulus_nah_dunkel", 128)


def shot_named(name, objects, mode, scale, z=0.0, fstop=0.08):
    only(objects)
    cam = ld["setup"](mode=mode)
    sc.render.resolution_x = sc.render.resolution_y = 1000
    ld["frame"](cam, [sc.objects[o] for o in objects if o in sc.objects][:1])
    cam.data.ortho_scale = scale
    ld["focal_plane"](cam, z, fstop)
    render(name, 96)


def shot_eileiter():
    only(["SM_C02_Eileiter"])
    tube = sc.objects["SM_C02_Eileiter"]
    if "Kette" not in tube.modifiers:              # chain three segments, as in the game: no cut ends in view
        arr = tube.modifiers.new("Kette", "ARRAY")
        arr.count = 3
        arr.use_merge_vertices = True
        arr.merge_threshold = 0.5
    cam = ld["setup"](mode="dark")
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    cam.data.type = "PERSP"
    cam.data.lens = 18
    cam.data.dof.use_dof = False
    cam.data.clip_start, cam.data.clip_end = 0.5, 20000
    o = sc.objects["SM_C02_Eileiter"].location
    cam.location = o + Vector((1450, -60, 30))     # inside the middle segment, looking along the tube (+X)
    look_at(cam, o + Vector((2900, 30, -20)))
    lamp = sc.objects["L_C02_Schraeglicht"]
    lamp.location = o + Vector((1490, 80, 120))    # the light travelling with the viewer (as the pawn's lamp in game)
    look_at(lamp, o + Vector((2200, 0, 0)))
    lamp.data.size = 60
    lamp.data.energy = float(__import__("os").environ.get("C02_LAMP", "1500000"))   # walls ~500 um away: measured
    if __import__("os").environ.get("C02_PREVIEW"):
        sc.render.resolution_x, sc.render.resolution_y = 480, 270
        render("eileiter_vorschau_" + __import__("os").environ.get("C02_LAMP", "x"), 16)
        return
    render("eileiter_innen_dunkel", 128)


def shot_spermium():
    only(["SM_C02_Spermium_Pose"])
    cam = ld["setup"](mode="bright")
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    ld["frame"](cam, [sc.objects["SM_C02_Spermium_Pose"]])
    ld["focal_plane"](cam, 0.0, 0.5)
    render("spermium_hell", 96)
    cam.data.ortho_scale = 12.0
    cam.location = sc.objects["SM_C02_Spermium_Pose"].matrix_world @ Vector((-2.5, 0, 50))
    ld["focal_plane"](cam, cam.location.z - 50.0, 0.5)
    render("spermium_kopf_hell", 96)



def shot_spermium_dunkel():
    """Dark field, as the player sees the cells in the fluid: oblique lamp, black background."""
    only(["SM_C02_Spermium_Pose"])
    cam = ld["setup"](mode="dark")
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    pose = sc.objects["SM_C02_Spermium_Pose"]
    ld["frame"](cam, [pose])
    ld["focal_plane"](cam, 0.0, 0.5)
    lamp = sc.objects["L_C02_Schraeglicht"]
    lamp.location = pose.matrix_world @ Vector((-10, -30, 25))
    look_at(lamp, pose.matrix_world.translation)
    lamp.data.size = 15
    lamp.data.energy = float(os.environ.get("C02_SPERM_LAMP", "25000"))
    render("spermium_dunkel", 96)
    cam.data.ortho_scale = 12.0
    cam.location = pose.matrix_world @ Vector((-2.5, 0, 50))
    ld["focal_plane"](cam, cam.location.z - 50.0, 0.5)
    render("spermium_kopf_dunkel", 96)


def shot_oozyte_plasma():
    """Close-up of the ooplasm (40 um field) to judge the granulation."""
    only(["SM_C02_Oozyte", "SM_C02_Zona", "SM_C02_Polkoerper"])
    cam = ld["setup"](mode="bright")
    sc.render.resolution_x = sc.render.resolution_y = 1000
    ld["frame"](cam, [sc.objects["SM_C02_Zona"]])
    cam.data.ortho_scale = 40
    cam.location.x += 45.0                               # towards the rim: plasma, membrane, perivitelline space, zona
    ld["focal_plane"](cam, 0.0, 0.08)
    render("oozyte_plasma_hell", 96)


SHOTS = {
    "spermium_dunkel": shot_spermium_dunkel,
    "oozyte_plasma": shot_oozyte_plasma,
    "cumulus_nah": shot_cumulus_nah,
    "spermium": shot_spermium,
    "oozyte_nackt": shot_oozyte_nackt,
    "oozyte_spieler": shot_oozyte_spieler,
    "eileiter": shot_eileiter,
    "zygote": lambda: shot_named("zygote_hell", ["SM_C02_Zygote", "SM_C02_Zona_Z", "SM_C02_Vorkern", "SM_C02_Polkoerper_Z"], "bright", 200),
    "zweizell": lambda: shot_named("zweizell_hell", ["SM_C02_Blastomere", "SM_C02_Zona_2Z", "SM_C02_Kern_2Z", "SM_C02_Polkoerper_2Z"], "bright", 200),
}

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(SHOTS)
    for a in args:
        SHOTS[a]()
