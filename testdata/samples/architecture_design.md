# Engine Design Overview

This document outlines the design of the Daisy orchestration engine.  
It describes how the central `Impulse` object flows across modular plugins and provides technical guidance for extending or debugging the engine.

---

## Main Concepts

### 1. **Impulse**
The `Impulse` is the central data object that carries state across the workflow.  
It contains `.Input`, `.Output`, and `.Error` and evolves as it passes through modules:

- Created by a **Receiver**
- Enriched or transformed by one or more **Abilities** (via `Paths`)
- Consumed by **Transmitters**

### 2. **Cores**
A **Core** is the container where workflows execute.  
- Each core can run in parallel with others.  
- Cores communicate through **Pools**.  

### 3. **Pools**
Pools (`Daisy.Resources.Pools`) hold collections of module instances that are currently running.  
They are singletons that:  
- Enable module reuse across cores.  
- Support inter-core communication.  

### 4. **Paths and PathFinder Service**
Abilities are traversed using `Paths`.  
The **PathFinder Service** (`IPathFinder`) manages traversal:  
- Matches candidate paths via `TraverseRules`  
- Filters out paths that were already traversed (`TraversedRules`)  
- Executes qualified paths in priority (`TraverseOrder`)  

The PathFinder is implemented as a IDaisyService service and loaded into the application's custom ServiceCollection, making it testable, maintainable, and properly integrated into the solution architecture.  

---

## Workflow Modules

### 1. **Receivers**
Receivers ingest external input and initialize an `Impulse`.  
Examples:  
- `OcrReceiver`: Populates `Impulse.Input` from an image file path (`FilePath:*`).  
- `AzureDevOpsPipelineRunnerReceiver`: Polls Azure DevOps for pipeline run completion.  

### 2. **Abilities**
Abilities contain one or more `Paths`. Each path includes:  
- `TraverseRules`: Conditions for execution.  
- `TraversedRules`: Prevents re-processing.  
- `TraverseOrder`: Optional execution priority.  
- Processing logic to mutate or enrich the `Impulse`.  

**Assistants** are specialized Abilities that integrate with external AI services.  

### 3. **Transmitters**
Once traversal completes (no more paths qualify), Transmitters consume `Impulse.Output` and perform external actions.  
Examples:  
- `AzureDevOpsTransmitter`: Creates DevOps work items.  
- `GitTransmitter`: Commits and opens pull requests.  
- `AzureDevOpsPipelineRunnerTransmitter`: Runs build and deployment pipelines.  

---

## Startup Initialization

### Factories
Startup uses factories to load and register all modules:

```csharp
var settings = StartupFactory.AppSettingsConfiguration.LoadApplicationSettings();
var serviceProvider = StartupFactory.LoadServices(settings);

AbilityFactory.LoadAbilities(settings, serviceProvider);
TransmitterFactory.LoadTransmitters(settings, serviceProvider);
ReceiverFactory.LoadReceivers(settings, serviceProvider);
```

### Application Settings (`appconfig.json`)
`AppSettingsConfiguration` loads `ApplicationSettings` from `appconfig.json` and secrets.  
This configuration controls:  
- Which Receivers, Abilities, Transmitters, and Workflows are active.  
- Which APIs and credentials are available.  
- Path traverse order for workflow execution.  

Updating `appconfig.json` changes which modules are available at runtime.

### Dependency Injection & Reflection
- All modules are registered via DI.  
- Attributes (e.g., `[TraverseRule]`) enable reflection-based discovery and traversal.

> **Note**: For comprehensive details on the plugin injection system, including assembly loading strategies, reflection-based discovery, pool management, and factory patterns, see [`plugin_injection.md`](plugin_injection.md).  

---

## Extension and Debugging
For deeper technical reference, review the abstract classes and interfaces under `Daisy.Resources`.  
These define the contracts for Receivers, Abilities, Transmitters, and traversal rules.  