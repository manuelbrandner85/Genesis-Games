using UnrealBuildTool;
public class Genesis : ModuleRules
{
    public Genesis(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new [] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput" });
        PrivateDependencyModuleNames.AddRange(new [] { "UMG", "AIModule", "NavigationSystem", "GameplayTasks", "Json", "JsonUtilities" });
        if (Target.bBuildEditor)
        {
            PrivateDependencyModuleNames.Add("UnrealEd");   // Play-in-Editor automation tests only
        }
    }
}
