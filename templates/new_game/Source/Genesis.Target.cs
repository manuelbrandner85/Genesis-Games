using UnrealBuildTool;
using System.Collections.Generic;
public class GenesisTarget : TargetRules
{
    public GenesisTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("Genesis");
    }
}
