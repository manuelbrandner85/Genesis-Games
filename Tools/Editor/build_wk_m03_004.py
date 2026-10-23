# -*- coding: utf-8 -*-
# WK-M03-004: L08 "Die Nacht der Naturgewalt" im Flussdorf (Graybox).
# Baut: Graybox-Materialien, Smart-Object-Definitionen der Flussdorf-Rollen, den Tagesablauf-StateTree (neu, alle
# Aktivitaeten aus den Projekteinstellungen), Quest L08 + Dialoge als Daten und das Level L_Flussdorf_Graybox.
# Struktur aus V21 L08 / V24 Kette B+C / V24-Weltbibel; Dialog-Wortlaut ist ARBEITSTEXT (Quellen enthalten keine Zeilen).
# Masse in cm, reale Groessen (Gelaender 110 cm, Tuer 120 x 220 cm, Raumhoehe 300 cm). Layout ist eine Graybox-Annahme.
# Run: UnrealEditor-Cmd.exe Genesis.uproject -run=pythonscript -script="<this file>"
import math

import unreal

EAL = unreal.EditorAssetLibrary
ELL = unreal.EditorLevelLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary

MAP_PATH = "/Game/Maps/L_Flussdorf_Graybox"
AI_DIR = "/Game/Genesis/AI"
QUEST_DIR = "/Game/Genesis/Quests"
L08_DIR = QUEST_DIR + "/L08"
MAT_DIR = "/Game/Genesis/Graybox"
CUBE = "/Engine/BasicShapes/Cube.Cube"
CYL = "/Engine/BasicShapes/Cylinder.Cylinder"
SPHERE = "/Engine/BasicShapes/Sphere.Sphere"
PLANE = "/Engine/BasicShapes/Plane.Plane"

SOURCE_NOTE = ("Struktur: V21 L08, V24 Missionsbibel Kette B+C (S24-04/05/06/07/08), V24 Weltbibel R01-R08, "
               "V24/V48 N01/N04/N05. Wortlaut: Arbeitstext, nicht Kanon.")
INT_MAX = 2147483647


def log(msg):
    unreal.log("GENESIS_BUILD " + msg)


# ---------------------------------------------------------------- Materialien (Graybox, physikalisch plausible Albedo)

def material(name, rgb, roughness, metallic=0.0):
    path = MAT_DIR + "/" + name
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    mat = TOOLS.create_asset(name, MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    color = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    color.set_editor_property("constant", unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    MEL.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", roughness)
    MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    metal = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 300)
    metal.set_editor_property("r", metallic)
    MEL.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat)
    return mat


def build_materials():
    return {
        # Albedo-Werte innerhalb realer Bereiche (Wasser dunkel und glatt, Gras ~0.1, Beton ~0.35).
        "water": material("M_GB_Wasser", (0.02, 0.035, 0.035), 0.04),
        "ground": material("M_GB_Wiese", (0.07, 0.11, 0.04), 0.9),
        "bed": material("M_GB_Flussbett", (0.08, 0.07, 0.05), 0.95),
        "concrete": material("M_GB_Beton", (0.35, 0.34, 0.32), 0.8),
        "wood": material("M_GB_Holz", (0.18, 0.11, 0.06), 0.75),
        "plaster": material("M_GB_Putz", (0.55, 0.52, 0.47), 0.85),
        "roof": material("M_GB_Dach", (0.12, 0.06, 0.05), 0.7),
        "steel": material("M_GB_Stahl", (0.56, 0.57, 0.58), 0.45, 1.0),
        "barrier": material("M_GB_Absperrung", (0.55, 0.04, 0.03), 0.5),
        "crack": material("M_GB_Riss", (0.015, 0.015, 0.015), 0.95),
        "debris": material("M_GB_Treibholz", (0.13, 0.10, 0.07), 0.9),
        "paper": material("M_GB_Aushang", (0.75, 0.73, 0.68), 0.9),
        "foliage": material("M_GB_Laub", (0.04, 0.08, 0.025), 0.85),
    }


# ---------------------------------------------------------------- Dialoge und Quest (Daten)

def make_asset(name, cls, folder):
    path = folder + "/" + name
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", cls)
    return TOOLS.create_asset(name, folder, cls, factory)


def cond(key, lo=1, hi=INT_MAX):
    c = unreal.GenesisStateCondition()
    c.set_editor_property("key", key)
    c.set_editor_property("min", lo)
    c.set_editor_property("max", hi)
    return c


def unset(key):
    return cond(key, 0, 0)


def cons(event_type="", flag="", value=1, target_speaker=True, extra=()):
    c = unreal.GenesisConsequence()
    c.set_editor_property("event_type", event_type)
    c.set_editor_property("flag_name", flag)
    c.set_editor_property("flag_value", value)
    c.set_editor_property("target_speaker", target_speaker)
    c.set_editor_property("extra_targets", list(extra))
    return c


def choice(choice_id, text, next_node="", consequences=(), trigger="", conditions=()):
    c = unreal.GenesisDialogChoice()
    c.set_editor_property("choice_id", choice_id)
    c.set_editor_property("text", text)
    c.set_editor_property("next_node_id", next_node)
    c.set_editor_property("consequences", list(consequences))
    c.set_editor_property("quest_trigger", trigger)
    c.set_editor_property("conditions", list(conditions))
    return c


def node(node_id, text, choices):
    n = unreal.GenesisDialogNode()
    n.set_editor_property("node_id", node_id)
    n.set_editor_property("text", text)
    n.set_editor_property("choices", choices)
    return n


def dialog(name, nodes):
    d = make_asset(name, unreal.GenesisDialogDefinition, L08_DIR)
    d.set_editor_property("dialog_id", name)
    d.set_editor_property("start_node_id", nodes[0].get_editor_property("node_id"))
    d.set_editor_property("nodes", nodes)
    d.set_editor_property("placeholder_content", False)
    d.set_editor_property("source_note", SOURCE_NOTE)
    EAL.save_loaded_asset(d)
    return d


def contact(target, dlg):
    c = unreal.GenesisStepContact()
    c.set_editor_property("target_id", target)
    c.set_editor_property("dialog", dlg)
    return c


def edge(trigger, next_step="", outcome=""):
    e = unreal.GenesisQuestEdge()
    e.set_editor_property("trigger", trigger)
    e.set_editor_property("next_step_id", next_step)
    e.set_editor_property("outcome_id", outcome)
    return e


def step(step_id, objective, contacts, edges):
    s = unreal.GenesisQuestStep()
    s.set_editor_property("step_id", step_id)
    s.set_editor_property("objective", objective)
    s.set_editor_property("contacts", contacts)
    s.set_editor_property("edges", edges)
    return s


def build_story():
    # Weltobjekte: Gespraech beim Ansehen, unabhaengig von der Quest (Projekteinstellungen > Genesis World).
    station = dialog("D_OBJ_STATION", [
        node("START", "Messwerte: Luftdruck {Pressure} hPa ({Tendency} hPa in 3 h), Wind {Wind} m/s, Regen {Rain} mm/h, "
                      "Flusspegel {River} m über normal. {StationStatus}", [
            choice("C_NOTE_ALERT", "Alarm und Messwerte notieren.",
                   consequences=[cons("READINGS_OBSERVED", "Know.AlertSeen"), cons("", "Know.WarningBasis")],
                   trigger="SIGNS_RECOGNIZED", conditions=[cond("R06_STATION.Alert"), unset("Know.AlertSeen")]),
            choice("C_LEAVE", "Weitergehen."),
        ]),
    ])
    notice = dialog("D_OBJ_NOTICE", [
        node("START", "{NoticeText}", [
            choice("C_READ_WARNING", "Die Warnung genau lesen.",
                   consequences=[cons("", "Know.WarningBasis"), cons("", "Know.WarningRead")],
                   trigger="SIGNS_RECOGNIZED", conditions=[cond("R01_NOTICE.Warning"), unset("Know.WarningRead")]),
            choice("C_LEAVE", "Weitergehen."),
        ]),
    ])
    bridge = dialog("D_OBJ_BRIDGE", [
        node("START", "{BridgeStatus}", [
            choice("C_INSPECT", "Das Geländer genauer ansehen.", next_node="CRACK", conditions=[unset("Know.CrackSeen")]),
            choice("C_LEAVE", "Weitergehen."),
        ]),
        node("CRACK", "Über dem Pfeiler zieht sich ein Riss durch die Verankerung des Geländers. "
                      "Ob das trägt, kann nur eine Fachperson beurteilen.", [
            choice("C_REMEMBER", "Das merke ich mir.", consequences=[cons("BRIDGE_DAMAGE_OBSERVED", "Know.CrackSeen")]),
        ]),
    ])

    n05 = dialog("D_L08_N05_ENTSCHEIDEN", [
        node("START", "Gemeindekoordination. Was gibt es?", [
            choice("C_REPORT_ALERT", "Die Wetterstation zeigt Alarm: Der Luftdruck fällt stark.", next_node="ALERT",
                   consequences=[cons("ALERT_REPORTED", "Know.AlertReported")],
                   conditions=[cond("Know.AlertSeen"), unset("Know.AlertReported")]),
            choice("C_REPORT_CRACK", "Am Brückengeländer über dem Pfeiler ist ein Riss.", next_node="CRACK",
                   consequences=[cons("BRIDGE_DAMAGE_REPORTED", "Know.CrackReported", extra=["VS01_BRIDGE_01"])],
                   conditions=[cond("Know.CrackSeen"), unset("Know.CrackReported")]),
            choice("C_HELP", "Kann ich irgendwie helfen?", next_node="HELP",
                   consequences=[cons("HELP_OFFERED", "Know.HelpOffered")], conditions=[unset("Know.HelpOffered")]),
            choice("C_BYE", "Nichts weiter."),
        ]),
        node("ALERT", "Danke. Ich sehe mir die Werte an und entscheide über eine Warnung.", [choice("C_BACK", "Noch etwas.", next_node="START"), choice("C_END", "Gut.")]),
        node("CRACK", "Ich nehme die Meldung auf. Ohne Befund einer Fachperson gebe ich da nichts frei.", [choice("C_BACK", "Noch etwas.", next_node="START"), choice("C_END", "Gut.")]),
        node("HELP", "Sag den Leuten Bescheid, die den Aushang nicht sehen. Aber bring dich nicht selbst in Gefahr.", [choice("C_END", "Mach ich.")]),
    ])
    n01 = dialog("D_L08_N01_ENTSCHEIDEN", [
        node("START", "Werkstatt. Was brauchst du?", [
            choice("C_WARN", "Ein Unwetter zieht auf, die Station hat Alarm.", next_node="WARNED",
                   consequences=[cons("WARNING_RECEIVED", "Know.WarnedN01")],
                   conditions=[cond("Know.WarningBasis"), unset("Know.WarnedN01")]),
            choice("C_HELP_SECURE", "Ich helfe dir beim Sichern.", next_node="THANKS",
                   consequences=[cons("HELPED", "R03_WORKSHOP.Helped")],
                   conditions=[cond("Know.WarnedN01"), unset("R03_WORKSHOP.Helped"), unset("R03_WORKSHOP.Secured")]),
            choice("C_RUMOR", "Da zieht etwas auf, glaube ich.", next_node="RUMOR", conditions=[unset("Know.WarningBasis")]),
            choice("C_BYE", "Nichts, danke."),
        ]),
        node("WARNED", "Dann sichere ich das Lager, bevor es losgeht.", [
            choice("C_HELP_SECURE", "Ich helfe dir beim Sichern.", next_node="THANKS",
                   consequences=[cons("HELPED", "R03_WORKSHOP.Helped")], conditions=[unset("R03_WORKSHOP.Helped")]),
            choice("C_END", "Pass auf dich auf."),
        ]),
        node("THANKS", "Gut. Pack mit an, dann geht es schneller.", [choice("C_END", "Los.")]),
        node("RUMOR", "Ohne Messwerte mache ich hier nicht dicht. Frag an der Wetterstation nach.", [choice("C_END", "Gut.")]),
    ])
    n04 = dialog("D_L08_N04_ENTSCHEIDEN", [
        node("START", "Lieferungen. Für heute bin ich fast durch, morgen ab zehn geht es weiter.", [
            choice("C_WARN", "Ein Unwetter zieht auf, die Station hat Alarm.", next_node="WARNED",
                   consequences=[cons("WARNING_RECEIVED", "Know.WarnedN04")],
                   conditions=[cond("Know.WarningBasis"), unset("Know.WarnedN04")]),
            choice("C_CRACK", "Am Brückengeländer ist ein Riss.", next_node="CRACK",
                   consequences=[cons("BRIDGE_RISK_TOLD", "Know.CrackToldN04")],
                   conditions=[cond("Know.CrackSeen"), unset("Know.CrackToldN04")]),
            choice("C_BYE", "Gute Fahrt."),
        ]),
        node("WARNED", "Danke. Bei Sturm bleibt der Wagen stehen.", [choice("C_BACK", "Noch etwas.", next_node="START"), choice("C_END", "Gut.")]),
        node("CRACK", "Dann fahre ich da nicht drüber, bis jemand das geprüft hat.", [choice("C_BACK", "Noch etwas.", next_node="START"), choice("C_END", "Gut.")]),
    ])
    n05_after = dialog("D_L08_N05_DANACH", [
        node("START", "Die Nacht ist vorbei. {BridgeStatus} {TrailStatus}", [
            choice("C_THANKS", "Danke für die Auskunft.", trigger="AFTERMATH_TALKED"),
        ]),
    ])
    n01_after = dialog("D_L08_N01_DANACH", [node("START", "{WorkshopStatus}", [choice("C_END", "Verstehe.")])])
    n04_after = dialog("D_L08_N04_DANACH", [node("START", "{DeliveryStatus}", [choice("C_END", "Verstehe.")])])

    quest = make_asset("Q_L08", unreal.GenesisQuestDefinition, QUEST_DIR)
    quest.set_editor_property("quest_id", "L08")
    quest.set_editor_property("title", "Die Nacht der Naturgewalt")
    quest.set_editor_property("start_step_id", "ANZEICHEN")
    quest.set_editor_property("start_trigger", "WX_PRECURSOR")
    quest.set_editor_property("placeholder_content", False)
    quest.set_editor_property("source_note", SOURCE_NOTE)
    quest.set_editor_property("steps", [
        step("ANZEICHEN", "Das Wetter schlägt um: Der Luftdruck fällt, der Wind frischt auf. "
                          "Messwerte an der Wetterstation oder den Aushang am Dorfplatz prüfen.",
             [], [edge("SIGNS_RECOGNIZED", "ENTSCHEIDEN"), edge("WX_STORM", "UNWETTER")]),
        step("ENTSCHEIDEN", "Gefahr einschätzen: warnen, melden, im Rahmen der eigenen Fähigkeiten helfen "
                            "– oder sich selbst in Sicherheit bringen.",
             [contact("N05", n05), contact("N01", n01), contact("N04", n04)], [edge("WX_STORM", "UNWETTER")]),
        step("UNWETTER", "Unwetter. In Sicherheit bleiben.", [], [edge("WX_RECEDED", "MORGEN")]),
        step("MORGEN", "Nach dem Unwetter: Folgen ansehen – Brücke, Werkstatt, Wege.",
             [contact("N05", n05_after), contact("N01", n01_after), contact("N04", n04_after)],
             [edge("AFTERMATH_TALKED", outcome="FOLGEN_GESEHEN"), edge("WX_SETTLED", outcome="WEITERGEZOGEN")]),
    ])
    EAL.save_loaded_asset(quest)
    errors = unreal.GenesisStoryLibrary.validate_quest(quest)
    for e in errors:
        unreal.log_error("GENESIS_BUILD quest error: " + e)
    log("quest %s steps=%d errors=%d" % (quest.get_path_name(), len(quest.get_editor_property("steps")), len(errors)))


# ---------------------------------------------------------------- KI-Assets

# Aktivitaet -> (Slot-Versaetze relativ zum Platz, Blickrichtung). Ein Mensch tritt von vorn an den Platz.
SOD = {
    "Home": ([(0, 0, 0)], 0.0),
    "Office": ([(0, 0, 0)], 0.0),
    "Secure": ([(0, 0, 0)], 0.0),
    "Deliver": ([(0, -60, 0), (0, 60, 0)], 0.0),
}


def build_ai():
    tree = unreal.GenesisNpcAssetBuilder.build_daily_life_state_tree(AI_DIR + "/ST_GenesisDailyLife")
    if not tree:
        raise RuntimeError("StateTree build failed")
    defs = {"Work": unreal.load_asset(AI_DIR + "/SOD_Work")}
    for activity, (slots, yaw) in SOD.items():
        d = unreal.GenesisNpcAssetBuilder.build_activity_definition(
            AI_DIR + "/SOD_" + activity, activity, [unreal.Vector(*s) for s in slots], [yaw] * len(slots))
        if not d:
            raise RuntimeError("definition failed: " + activity)
        defs[activity] = d
    log("statetree + %d smart object definitions" % len(defs))
    return defs


# ---------------------------------------------------------------- Level

class Builder:
    def __init__(self, mats):
        self.mats = mats
        self.meshes = {k: unreal.load_asset(v) for k, v in (("cube", CUBE), ("cyl", CYL), ("sphere", SPHERE), ("plane", PLANE))}
        self.count = 0

    def box(self, label, center, size, mat, mesh="cube", yaw=0.0, pitch=0.0, roll=0.0, collision=True):
        """Quader mit Mittelpunkt und Kantenlaengen in cm (Basis-Wuerfel = 100 cm, Pivot in der Mitte)."""
        actor = ELL.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*center), unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw))
        comp = actor.static_mesh_component
        comp.set_static_mesh(self.meshes[mesh])
        comp.set_material(0, self.mats[mat])
        actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
        if not collision:
            comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            comp.set_editor_property("can_ever_affect_navigation", False)
        actor.set_actor_label(label)
        actor.set_folder_path("Graybox")
        self.count += 1
        return actor

    def world_object(self, label, object_id, center, size, mat, interactable=False, show_key="", show_value=1,
                     at_least=False, blocking=False, height_key="", mesh="cube", yaw=0.0):
        actor = ELL.spawn_actor_from_class(unreal.GenesisWorldObject, unreal.Vector(*center), unreal.Rotator(yaw=yaw))
        comp = actor.get_component_by_class(unreal.StaticMeshComponent)
        comp.set_static_mesh(self.meshes[mesh])
        comp.set_material(0, self.mats[mat])
        actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
        actor.set_editor_property("object_id", object_id)
        actor.set_editor_property("interactable", interactable)
        actor.set_editor_property("show_when_key", show_key)
        actor.set_editor_property("show_when_value", show_value)
        actor.set_editor_property("show_when_at_least", at_least)
        actor.set_editor_property("blocking_when_shown", blocking)
        actor.set_editor_property("height_follows_key", height_key)
        if show_key:
            # Startzustand "nicht da": die Laufzeit schaltet nach dem Spielstand ein (Navmesh baut dynamisch neu).
            comp.set_visibility(False)
            comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            comp.set_editor_property("can_ever_affect_navigation", False)
        if height_key:
            comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            comp.set_editor_property("can_ever_affect_navigation", False)
        actor.set_actor_label(label)
        actor.set_folder_path("Weltobjekte")
        self.count += 1
        return actor

    def shell(self, label, center, size, door_side, height=300.0, wall=20.0, roof=True):
        """Hohles Gebaeude mit Tueroeffnung 120 x 220 cm in der Mitte der Tuerseite (N = +y, S = -y, E = +x, W = -x)."""
        cx, cy = center
        sx, sy = size
        z = height / 2.0
        for side in ("N", "S", "E", "W"):
            along_x = side in ("N", "S")
            length = sx if along_x else sy
            off = (sy / 2.0 - wall / 2.0) if along_x else (sx / 2.0 - wall / 2.0)
            sign = 1.0 if side in ("N", "E") else -1.0
            pos = (cx, cy + sign * off) if along_x else (cx + sign * off, cy)
            if side != door_side:
                self.box("%s_Wand_%s" % (label, side), (pos[0], pos[1], z), (length, wall, height) if along_x else (wall, length, height), "plaster")
                continue
            seg = (length - 120.0) / 2.0
            for k in (-1, 1):
                d = k * (60.0 + seg / 2.0)
                p = (pos[0] + d, pos[1]) if along_x else (pos[0], pos[1] + d)
                self.box("%s_Wand_%s_%d" % (label, side, k), (p[0], p[1], z), (seg, wall, height) if along_x else (wall, seg, height), "plaster")
            self.box("%s_Sturz" % label, (pos[0], pos[1], 220.0 + (height - 220.0) / 2.0),
                     (120.0, wall, height - 220.0) if along_x else (wall, 120.0, height - 220.0), "plaster")
        if roof:
            self.box("%s_Dach" % label, (cx, cy, height + 10.0), (sx + 40.0, sy + 40.0, 20.0), "roof")

    def spot(self, label, activity, center, visual_size, visual_mat, owners, definition, yaw=0.0, tags=()):
        spot = ELL.spawn_actor_from_class(unreal.GenesisActivitySpot, unreal.Vector(*center), unreal.Rotator(yaw=yaw))
        spot.set_actor_label(label)
        spot.set_folder_path("Aktivitaeten")
        visual = spot.get_component_by_class(unreal.StaticMeshComponent)
        visual.set_static_mesh(self.meshes["cube"])
        visual.set_material(0, self.mats[visual_mat])
        visual.set_relative_location(unreal.Vector(0, 0, visual_size[2] / 2.0), False, False)
        visual.set_relative_scale3d(unreal.Vector(visual_size[0] / 100.0, visual_size[1] / 100.0, visual_size[2] / 100.0))
        visual.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        visual.set_editor_property("can_ever_affect_navigation", False)
        spot.set_editor_property("definition", definition)
        spot.set_editor_property("owner_npc_ids", list(owners))
        spot.set_editor_property("tags", list(tags))
        spot.apply_definition()
        self.count += 1
        return spot


# Geografie (Graybox-Annahme, Weltbibel-Topologie ist kein geografischer Plan):
# Fluss laeuft Nord-Sued (y) zwischen x = 4500 und 6000 cm. Westufer: Dorf (R01, R02, R03, R07, R08).
# Ostufer: Waldweg/Wetterstation R06 und der Abholpunkt der Lieferperson. Bruecke R04 bei y = 0,
# Umweg R05 am Ufer entlang nach Sueden zum Steg bei y = -8000.
RIVER_W, RIVER_E = 4500.0, 6000.0
BED_Z, WATER_Z = -400.0, -300.0


def build_level(defs, mats):
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if EAL.does_asset_exist(MAP_PATH):
        les.load_level(MAP_PATH)
        for a in ELL.get_all_level_actors():
            ELL.destroy_actor(a)
    else:
        les.new_level(MAP_PATH)
    b = Builder(mats)

    # Gelaende: Ufer 4,5 m dick bis unter das Flussbett, damit die Uferkante senkrecht ist (kein Weg durchs Wasser).
    b.box("Ufer_West", ((-6000 + RIVER_W) / 2.0, -2000, -225), (RIVER_W + 6000, 18000, 450), "ground")
    b.box("Ufer_Ost", ((RIVER_E + 11000) / 2.0, -2000, -225), (11000 - RIVER_E, 18000, 450), "ground")
    b.box("Flussbett", ((RIVER_W + RIVER_E) / 2.0, -2000, BED_Z - 25), (RIVER_E - RIVER_W, 18000, 50), "bed")
    b.world_object("Wasserspiegel", "WEATHER", ((RIVER_W + RIVER_E) / 2.0, -2000, WATER_Z), (RIVER_E - RIVER_W, 18000, 2),
                   "water", height_key="WX.RiverCm")

    # Ufergelaender (110 cm) ausser an Bruecke und Steg.
    for x in (RIVER_W - 10, RIVER_E + 10):
        for y0, y1 in ((-11000, -8200), (-7800, -250), (250, 7000)):
            b.box("Ufergelaender", (x, (y0 + y1) / 2.0, 55), (8, y1 - y0, 110), "steel")

    # R04 Bruecke VS01_BRIDGE_01: 4 m breit, Belag 40 cm, Pfeiler in der Mitte, Gelaender 110 cm.
    deck_x0, deck_x1 = RIVER_W - 300, RIVER_E + 300
    mid = (deck_x0 + deck_x1) / 2.0
    b.world_object("R04_Bruecke", "VS01_BRIDGE_01", (mid, 0, -20), (deck_x1 - deck_x0, 400, 40), "concrete", interactable=True)
    b.box("R04_Pfeiler", (mid, 0, (BED_Z - 40) / 2.0), (120, 320, -BED_Z - 40), "concrete")
    for y in (-195, 195):
        b.box("R04_Gelaender", (mid, y, 55), (deck_x1 - deck_x0, 6, 110), "steel")
    # Sichtbarer Riss an der Gelaenderverankerung ueber dem Pfeiler (S24-04: "Ein Riss am Gelaender").
    b.world_object("R04_Riss", "VS01_BRIDGE_01", (mid, -199, 30), (90, 2, 60), "crack", show_key="Damage", show_value=1, at_least=True, yaw=0.0)
    for x in (deck_x0 + 40, deck_x1 - 40):
        b.world_object("R04_Sperre", "VS01_BRIDGE_01", (x, 0, 60), (30, 400, 120), "barrier", show_key="Blocked", blocking=True)
    b.world_object("R04_Truemmer", "VS01_BRIDGE_01", (mid, 60, 40), (260, 160, 80), "debris", show_key="Damage", show_value=2,
                   at_least=True, blocking=True, yaw=25.0)

    # R05 Uferweg und Steg (Umweg).
    steg_y = -8000
    b.box("R05_Steg", ((RIVER_W + RIVER_E) / 2.0, steg_y, -15), (RIVER_E - RIVER_W + 400, 200, 30), "wood")
    for y in (steg_y - 95, steg_y + 95):
        b.box("R05_Steg_Gelaender", ((RIVER_W + RIVER_E) / 2.0, y, 55), (RIVER_E - RIVER_W + 400, 5, 110), "wood")
    for x in (RIVER_W - 150, RIVER_E + 150):
        b.world_object("R05_Sperre", "R05_TRAIL", (x, steg_y, 60), (30, 200, 120), "barrier", show_key="Blocked", blocking=True)
    b.world_object("R05_Treibholz", "R05_TRAIL", ((RIVER_W + RIVER_E) / 2.0, steg_y, 30), (400, 180, 50), "debris", show_key="Open", show_value=0)
    for i, y in enumerate(range(-7500, -500, 1000)):
        b.box("R05_Weg_%02d" % i, (RIVER_W - 400, y, 1), (220, 1000, 2), "bed", collision=False)

    # R01 Dorfplatz: Steintreppe, Dorfbaum, Aushangtafel (Weltbibel-Landmarken).
    sq = (1000.0, 0.0)
    for i in range(3):
        b.box("R01_Treppe_%d" % i, (sq[0] - 900 + i * 35, sq[1] - 400, 8.5 + i * 17), (35 * (3 - i) + 35, 400, 17 * (i + 1)), "concrete")
    b.box("R01_Baum_Stamm", (sq[0] - 300, sq[1] + 300, 250), (50, 50, 500), "wood", mesh="cyl")
    b.box("R01_Baum_Krone", (sq[0] - 300, sq[1] + 300, 650), (550, 550, 450), "foliage", mesh="sphere", collision=False)
    b.world_object("R01_Aushangtafel", "R01_NOTICE", (sq[0], sq[1] + 700, 140), (200, 12, 120), "paper", interactable=True)
    for x in (-95, 95):
        b.box("R01_Aushang_Pfosten", (sq[0] + x, sq[1] + 700, 100), (10, 10, 200), "wood")
    b.world_object("R01_Aushang_Warnung", "R01_NOTICE", (sq[0], sq[1] + 692, 150), (60, 2, 40), "barrier", show_key="Warning")
    b.spot("R01_Sprechstunde", "Office", (sq[0] + 500, sq[1] + 400, 0), (120, 60, 75), "wood", ["N05"], defs["Office"], yaw=-90.0)

    # R02 Markt (Verkaufsdach, Kisten) - in diesem Paket ohne Figur.
    b.box("R02_Stand", (2800, 2600, 50), (300, 120, 100), "wood")
    b.box("R02_Dach", (2800, 2600, 260), (400, 250, 10), "roof", collision=False)
    for x, y in ((2600, 2400), (3000, 2400)):
        b.box("R02_Kiste", (x, y, 25), (60, 40, 50), "wood")

    # R03 Werkstatt: 8 x 6 m, Tuer nach Norden; Werkbank an der Suedwand, Teilelager an der Ostwand.
    ws = (1500.0, -3000.0)
    b.shell("R03_Werkstatt", ws, (800, 600), "N", height=350.0)
    b.spot("R03_Werkbank", "Work", (ws[0], ws[1] - 230, 0), (200, 80, 90), "wood", ["N01"], defs["Work"])
    b.spot("R03_Teilelager", "Secure", (ws[0] + 300, ws[1], 0), (60, 300, 200), "steel", ["N01"], defs["Secure"])

    # R07 Wohnhaeuser (Privatorte N01, N05) und das Haus der Lieferperson an R08.
    homes = (("R07_Haus_N01", (-200.0, 3800.0), "S", "N01"), ("R07_Haus_N05", (-2600.0, 2200.0), "E", "N05"),
             ("R08_Haus_N04", (-3600.0, 5400.0), "S", "N04"))
    for label, c, door, owner in homes:
        b.shell(label, c, (700, 600), door, height=300.0)
        b.spot(label + "_Wohnen", "Home", (c[0], c[1], 0), (120, 80, 45), "wood", [owner], defs["Home"])

    # R08 Bushaltestelle und Zufahrt.
    b.box("R08_Unterstand", (-2000, 4700, 250), (300, 150, 10), "roof", collision=False)
    b.box("R08_Fahrplan", (-1800, 4600, 120), (8, 8, 240), "steel")

    # R06 Waldweg und Wetterstation (Ostufer): Messmast 10 m, Technikhaus, Messkasten.
    st = (7800.0, 1800.0)
    b.box("R06_Messmast", (st[0], st[1], 500), (20, 20, 1000), "steel", mesh="cyl")
    b.shell("R06_Technik", (st[0] + 400, st[1] + 300), (300, 250), "W", height=260.0)
    b.world_object("R06_Messkasten", "R06_STATION", (st[0] - 150, st[1], 75), (60, 40, 150), "plaster", interactable=True)
    for i in range(12):
        x = 8800 + (i % 4) * 500 + (i * 37 % 120)
        y = -1000 + (i // 4) * 900 + (i * 53 % 200)
        b.box("R06_Waldrand_Stamm", (x, y, 400), (40, 40, 800), "wood", mesh="cyl")
        b.box("R06_Waldrand_Krone", (x, y, 900), (400, 400, 500), "foliage", mesh="sphere", collision=False)

    # Abholpunkt der Lieferperson am Ostufer (Graybox-Annahme: Route fuehrt ueber die Bruecke).
    b.spot("Ost_Abholpunkt", "Deliver", (7400.0, -1500.0, 0), (120, 100, 40), "wood", ["N04"], defs["Deliver"], yaw=180.0, tags=["Deliver"])

    # Figuren an ihren Orten zur Startzeit (10:00).
    for npc_id, loc in (("N01", (ws[0], ws[1] + 100, 95)), ("N04", (-3600, 5000, 95)), ("N05", (sq[0] + 300, sq[1] + 200, 95))):
        npc = ELL.spawn_actor_from_class(unreal.GenesisNpcCharacter, unreal.Vector(*loc), unreal.Rotator(0, 0, 0))
        npc.set_actor_label(npc_id)
        npc.set_folder_path("Figuren")
        npc.set_editor_property("character_asset_id", npc_id)
        npc.apply_appearance(npc_id)

    start = ELL.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(sq[0] - 200, sq[1] - 800, 100), unreal.Rotator(yaw=60.0))
    start.set_actor_label("PlayerStart")

    nav = ELL.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(2500, -2000, 0), unreal.Rotator(0, 0, 0))
    nav.set_actor_label("Navigation")
    nav.set_actor_scale3d(unreal.Vector(85.0, 90.0, 8.0))  # Brush 200 cm -> 170 x 180 x 16 m

    # Licht und Himmel wie im Testlevel (Sonne + Himmel, manuelle Belichtung; Himmels-Controller kommt vom GameMode).
    sun = ELL.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0.0, -42.0, 35.0))
    sun.set_actor_label("Sonne")
    sc = sun.light_component
    sc.set_editor_property("intensity", 90000.0)
    sc.set_editor_property("atmosphere_sun_light", True)
    sc.set_editor_property("light_source_angle", 0.5357)
    sc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    ELL.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)).set_actor_label("Atmosphaere")
    sky = ELL.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    sky.set_actor_label("Himmelslicht")
    sky.light_component.set_editor_property("real_time_capture", True)
    sky.light_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    ELL.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0)).set_actor_label("Wolken")
    fog = ELL.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
    fog.set_actor_label("Hoehennebel")
    fog.component.set_editor_property("fog_density", 0.004)
    fog.component.set_editor_property("enable_volumetric_fog", True)
    ppv = ELL.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
    ppv.set_actor_label("Belichtung")
    ppv.set_editor_property("unbound", True)
    s = ppv.get_editor_property("settings")
    for prop, value in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_bias", 0.0),
                        ("auto_exposure_apply_physical_camera_exposure", True), ("camera_iso", 100.0),
                        ("camera_shutter_speed", 100.0), ("depth_of_field_fstop", 16.0)):
        s.set_editor_property("override_" + prop, True)
        s.set_editor_property(prop, value)
    ppv.set_editor_property("settings", s)

    les.save_current_level()
    log("level saved %s actors=%d built=%d" % (MAP_PATH, len(ELL.get_all_level_actors()), b.count))


def main():
    mats = build_materials()
    build_story()
    defs = build_ai()
    build_level(defs, mats)
    log("done")


main()
