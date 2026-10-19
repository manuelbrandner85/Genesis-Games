# WK-M03-003: builds the placeholder test quest TEST_Q01 ("Die Waage") and its dialogs as data assets.
# Content is PLACEHOLDER (not from the GENESIS story bible) and marked as such in the assets.
# Run: UnrealEditor-Cmd.exe Genesis.uproject -run=pythonscript -script="<this file>"
import unreal

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
DIR = "/Game/Genesis/Quests"


def log(msg):
    unreal.log("GENESIS_BUILD " + msg)


def make_asset(name, cls):
    path = DIR + "/" + name
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", cls)
    return TOOLS.create_asset(name, DIR, cls, factory)


def consequence(event_type="", flag="", flag_value=1, target_speaker=True):
    c = unreal.GenesisConsequence()
    c.set_editor_property("event_type", event_type)
    c.set_editor_property("flag_name", flag)
    c.set_editor_property("flag_value", flag_value)
    c.set_editor_property("target_speaker", target_speaker)
    return c


def choice(choice_id, text, trigger="", consequences=(), next_node="", required_trust=-2.0):
    c = unreal.GenesisDialogChoice()
    c.set_editor_property("choice_id", choice_id)
    c.set_editor_property("text", text)
    c.set_editor_property("quest_trigger", trigger)
    c.set_editor_property("consequences", list(consequences))
    c.set_editor_property("next_node_id", next_node)
    c.set_editor_property("required_trust", required_trust)
    return c


def node(node_id, text, choices):
    n = unreal.GenesisDialogNode()
    n.set_editor_property("node_id", node_id)
    n.set_editor_property("text", text)
    n.set_editor_property("choices", choices)
    return n


def dialog(name, dialog_id, nodes):
    d = make_asset(name, unreal.GenesisDialogDefinition)
    d.set_editor_property("dialog_id", dialog_id)
    d.set_editor_property("start_node_id", nodes[0].get_editor_property("node_id"))
    d.set_editor_property("nodes", nodes)
    d.set_editor_property("placeholder_content", True)
    EAL.save_loaded_asset(d)
    return d


def edge(trigger, next_step="", outcome=""):
    e = unreal.GenesisQuestEdge()
    e.set_editor_property("trigger", trigger)
    e.set_editor_property("next_step_id", next_step)
    e.set_editor_property("outcome_id", outcome)
    return e


def step(step_id, objective, npc, dlg, edges):
    s = unreal.GenesisQuestStep()
    s.set_editor_property("step_id", step_id)
    s.set_editor_property("objective", objective)
    s.set_editor_property("talk_to_npc_id", npc)
    s.set_editor_property("dialog", dlg)
    s.set_editor_property("edges", edges)
    return s


def main():
    market = dialog("D_TEST_Q01_Market", "D_TEST_Q01_MARKET", [
        node("N1", "[Platzhalter] Meine Waage zeigt falsch an. In der Werkstatt koennte man sie richten.", [
            choice("C_ACCEPT", "Ich frage in der Werkstatt nach.", trigger="T_ACCEPT"),
            choice("C_LATER", "Vielleicht spaeter."),
            choice("C_DECLINE", "Dafuer habe ich keine Zeit.", trigger="T_DECLINE",
                   consequences=[consequence("IGNORED_REQUEST")]),
        ]),
    ])
    workshop = dialog("D_TEST_Q01_Workshop", "D_TEST_Q01_WORKSHOP", [
        node("N1", "[Platzhalter] Eine Waage? Die bekomme ich hin.", [
            choice("C_THANKS", "Danke, ich bringe sie zum Markt.", trigger="T_REPAIRED",
                   consequences=[consequence(flag="Q01_SCALE_REPAIRED")]),
            choice("C_PAY_LATER", "Ich bezahle spaeter, versprochen.", trigger="T_REPAIRED", required_trust=0.1,
                   consequences=[consequence(flag="Q01_SCALE_REPAIRED"), consequence(flag="Q01_OWES_WORKSHOP")]),
            choice("C_LATER", "Ich komme spaeter wieder."),
        ]),
    ])
    handover = dialog("D_TEST_Q01_Return", "D_TEST_Q01_RETURN", [
        node("N1", "[Platzhalter] Und? Hast du sie?", [
            choice("C_GIVE", "Hier ist deine Waage.", trigger="T_GIVE", consequences=[consequence("HELPED")]),
            choice("C_KEEP", "Ich behalte sie.", trigger="T_KEEP", consequences=[consequence("PROMISE_BROKEN")]),
            choice("C_LATER", "Gleich."),
        ]),
    ])

    quest = make_asset("Q_TEST_Q01", unreal.GenesisQuestDefinition)
    quest.set_editor_property("quest_id", "TEST_Q01")
    quest.set_editor_property("title", "[Platzhalter] Die Waage")
    quest.set_editor_property("start_step_id", "S1")
    quest.set_editor_property("placeholder_content", True)
    quest.set_editor_property("steps", [
        step("S1", "Sprich mit der Haendlerin am Marktstand.", "NPC_TEST_02", market,
             [edge("T_ACCEPT", next_step="S2"), edge("T_DECLINE", outcome="DECLINED")]),
        step("S2", "Lass die Waage in der Werkstatt richten.", "NPC_TEST_01", workshop,
             [edge("T_REPAIRED", next_step="S3")]),
        step("S3", "Bring die Waage zum Marktstand.", "NPC_TEST_02", handover,
             [edge("T_GIVE", outcome="HELPED_MARKET"), edge("T_KEEP", outcome="KEPT_SCALE")]),
    ])
    EAL.save_loaded_asset(quest)

    errors = unreal.GenesisStoryLibrary.validate_quest(quest)
    log("quest %s steps=%d validation_errors=%d" % (quest.get_path_name(), len(quest.get_editor_property("steps")), len(errors)))
    for e in errors:
        log("  " + e)
    log("done")


main()
