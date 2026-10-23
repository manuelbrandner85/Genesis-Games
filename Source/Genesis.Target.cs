using UnrealBuildTool;
using System.Collections.Generic;
public class GenesisTarget : TargetRules
{
    public GenesisTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("Genesis");
    }
}
