using UnrealBuildTool;
using System.Collections.Generic;
public class GenesisEditorTarget : TargetRules
{
    public GenesisEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("Genesis");
    }
}
