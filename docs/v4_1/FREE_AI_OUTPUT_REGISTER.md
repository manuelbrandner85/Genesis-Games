# FREE AI OUTPUT REGISTER

Jedes Asset hat **stabile AssetID** mit Herkunft und Versionsführung. Pflichtfelder: `asset_id`, `kind`, `created_utc`, `tool_id`, `tool_version`, `model_id`, `model_revision`, `model_license_evidence`, `source_canon_ids`, `input_hashes`, `generation_settings`, `prompt_hash`, `file_sha256`, `output_path`, `commercial_usage_status`, `privacy_permission`, `qa_evidence`, `reviewer`, `status`.

**Statusverlauf:** `REQUESTED → APPROVED_TASK → GENERATED_PREVIEW → BLENDER_VALIDATED → UNREAL_VALIDATED → QA_REVIEWED → DIRECTOR_ACCEPTED`. Nie direkt von `GENERATED_PREVIEW` zu `DIRECTOR_ACCEPTED`. Assets ohne Lizenz- oder Produktionsnachweis bleiben `BLOCKED`.

Das CLI `tools/v4_1/asset_register.py` erfasst überprüfbare Hashes in einem lokalen JSONL-Register. Es darf nur ein tatsächlich existierendes Artefakt erfassen; ein registrierter Hash beweist weder grafische Qualität noch Rechte oder Importfähigkeit. Keine Personenfotos/Voice-Klone ohne Nutzungsrecht. Für freigegebene Testreferenzen werden die Originaldateien in einem separaten Assets-Ordner belassen.
