using UnrealBuildTool;

public class Genesis : ModuleRules
{
	public Genesis(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"UMG",
			"Json",
			"JsonUtilities",
			"DeveloperSettings"
		});

		if (Target.bBuildEditor)
		{
			// Nur fuer Editor-Automationstests (Play-in-Editor).
			PrivateDependencyModuleNames.Add("UnrealEd");
		}
	}
}
