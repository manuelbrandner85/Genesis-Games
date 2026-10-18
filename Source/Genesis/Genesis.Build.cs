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
			"DeveloperSettings",
			"GameplayTags",
			"NavigationSystem",
			"SmartObjectsModule",
			"StateTreeModule",
			"GameplayStateTreeModule"
		});

		if (Target.bBuildEditor)
		{
			// Nur im Editor: Automationstests (Play-in-Editor) und Asset-Builder (StateTree, Smart Objects).
			PrivateDependencyModuleNames.AddRange(new string[] { "UnrealEd", "StateTreeEditorModule", "AssetTools", "PropertyBindingUtils" });
		}
	}
}
