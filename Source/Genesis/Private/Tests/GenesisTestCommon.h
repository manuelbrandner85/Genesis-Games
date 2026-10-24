#pragma once
#include "Misc/AutomationTest.h"

/** Flags shared by all Genesis automation tests (one definition: unity builds merge the test files). */
inline constexpr EAutomationTestFlags GenesisTestFlags = EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::ProductFilter;
