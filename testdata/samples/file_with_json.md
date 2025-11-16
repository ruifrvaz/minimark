# Plugin Injection System

This document provides a comprehensive overview of Daisy-m4's plugin injection system, detailing how modules are dynamically loaded, registered, and managed at runtime.

---

## Overview

Daisy-m4 uses a sophisticated plugin injection system that combines:
- **Configuration-driven activation** via `appconfig.json`
- **Reflection-based discovery** using interfaces and attributes
- **Assembly loading strategies** with fallback mechanisms
- **Dependency injection** for service registration
- **Pool-based management** for module lifecycle
- **MSBuild integration** for automatic plugin deployment

---

## Architecture Components

### 1. Configuration System

#### ApplicationSettings (`appconfig.json`)
The central configuration file controls which plugins are loaded and how they behave:

```json
{
  "ApplicationSettings": {
    "Receivers": {
      "Daisy.Receivers.Console": { "RunOnCores": ["Daisy.Workflows.Starter"] },
      "Daisy.Receivers.WeatherEvent": { "RunOnCores": ["Daisy.Workflows.Weather"] }
    },
    "Transmitters": [
      "Daisy.Transmitters.Console",
      "Daisy.Transmitters.WorkflowTrigger"
    ],
    "Abilities": [
      "Daisy.Abilities.Operator",
      "Daisy.Abilities.Terminate",
      "Daisy.Abilities.OutputValidator",
      "Daisy.Abilities.Weather"
    ],
    "Workflows": [
      "Daisy.Workflows.Starter",
      "Daisy.Workflows.Weather"
    ],
    "PathTraverseOrder": {
      "ListWorkflowsPath": 1,
      "TerminatePath": 2,
      "WorkflowTriggerPath": 3,
      "GetWeatherByCityPath": 50,
      "OutputValidatorPath": 9999
    }
  }
}
```

**Key Configuration Sections:**
- `Receivers`: Maps receiver assemblies to their target workflow cores
- `Transmitters`: List of transmitter assemblies to load
- `Abilities`: List of ability assemblies containing processing paths
- `Workflows`: List of workflow/core assemblies to instantiate
- `PathTraverseOrder`: Execution priority for ability paths (lower = earlier)

### 2. Factory Pattern

The plugin system uses dedicated factory classes for each plugin type:

#### StartupFactory
- **Purpose**: Bootstrap services and coordinate factory initialization
- **Key Methods**:
  - `LoadServices()`: Creates and configures the service provider
  - `RegisterServicesFromLoadedAssemblies()`: Registers services via reflection

#### AbilityFactory
- **Purpose**: Load ability modules and their processing paths
- **Discovery**: Finds classes implementing `IPath` interface
- **Configuration**: Uses `PathTraverseOrder` for execution priority
- **Rules**: Loads traverse rules via `[TraverseRule]` attribute

#### ReceiverFactory
- **Purpose**: Load receiver modules (External, LoopBack, Event types)
- **Discovery**: Finds classes implementing receiver interfaces
- **Deployment**: Registers receivers to appropriate pools

#### TransmitterFactory
- **Purpose**: Load transmitter modules (External, LoopBack types)
- **Discovery**: Finds classes implementing transmitter interfaces
- **Registration**: Adds transmitters to their respective pools

#### WorkflowFactory (CoreFactory)
- **Purpose**: Load workflow cores that run the orchestration
- **Discovery**: Finds classes implementing `ICore` interface
- **Management**: Registers cores for parallel execution

---

## Assembly Loading Strategy

### Dual Loading Approach
Each factory uses a two-step assembly loading strategy:

```csharp
Assembly assembly;
try
{
    // Step 1: Try loading by assembly name (referenced assemblies)
    assembly = Assembly.Load(assemblyName);
}
catch (FileNotFoundException)
{
    // Step 2: Fallback to file path loading (plugin assemblies)
    var assemblyPath = Path.Combine(AppContext.BaseDirectory, $"{assemblyName}.dll");
    if (File.Exists(assemblyPath))
    {
        assembly = Assembly.LoadFrom(assemblyPath);
    }
    else
    {
        continue; // Skip if assembly cannot be found
    }
}
```

**Benefits:**
- **Primary**: `Assembly.Load()` works for referenced assemblies already in the AppDomain
- **Fallback**: `Assembly.LoadFrom()` handles external plugin DLLs in the application directory
- **Graceful degradation**: Missing assemblies are logged but don't stop the application

### Assembly Location
Plugins are expected in the application's base directory (`AppContext.BaseDirectory`):
- Main application: `src/Daisy/bin/Debug/net8.0/`
- Plugin assemblies: Same directory as main executable
- Configuration file: `appconfig.json` in the same directory

---

## Reflection-Based Discovery

### Interface-Based Discovery
Each plugin type implements specific interfaces that factories scan for:

```csharp
// Example from AbilityFactory
var abilityInterface = typeof(IPath);
var abilityPaths = types
    .Where(t => t is { IsClass: true, IsAbstract: false }
                && abilityInterface.IsAssignableFrom(t)
                && settings.PathTraverseOrder.ContainsKey(t.Name));
```

**Plugin Interfaces:**
- **Receivers**: `IExternalReceiver`, `ILoopBackReceiver`, `IEventReceiver`
- **Abilities**: `IPath` (with traversal rules)
- **Transmitters**: `IExternalTransmitter`, `ILoopBackTransmitter`
- **Workflows**: `ICore`
- **Services**: `IDaisyService`

### Attribute-Based Configuration
Abilities use attributes for advanced configuration:

```csharp
[TraverseRule(PathType = typeof(SomeSpecificPath))]
public class CustomTraverseRule : ITraverseRule
{
    // Rule implementation
}
```

**Key Attributes:**
- `[TraverseRule]`: Links traverse rules to specific path types
- Used for both `CanTraverse` and `Traversed` rule discovery

---

## Dependency Injection Integration

### Service Registration
The `StartupFactory.RegisterServicesFromLoadedAssemblies()` method:

1. **Collects** all plugin assembly names from configuration
2. **Loads** each assembly using the dual loading strategy
3. **Scans** for classes implementing `IDaisyService`
4. **Instantiates** services with settings parameter
5. **Registers** services in the `ServiceContainer`

```csharp
var serviceTypes = assembly.GetTypes()
    .Where(type => serviceInterface.IsAssignableFrom(type) && type.IsClass && !type.IsAbstract);

foreach (var serviceType in serviceTypes)
{
    var service = (IDaisyService)Activator.CreateInstance(serviceType, settings);
    ServiceContainer.Instance.Services.Add(service);
}
```

### Service Container
- **Singleton**: `ServiceContainer.Instance` provides global access
- **Lifecycle**: Services are cleaned up via `CleanupServiceProvider()`
- **Configuration**: All services receive `ApplicationSettings` during construction

---

## Pool-Based Module Management

### Pool Architecture
Each plugin type is managed by dedicated pool singletons:

```csharp
// Examples from Resources.Pools namespace
ExternalReceivers.Instance.Pool.Add(receiver);
ExternalTransmitters.Instance.Pool.Add(transmitter);
Cores.Instance.Pool.Add(core);
```

**Available Pools:**
- `Cores`: Workflow execution containers
- `ExternalReceivers` / `LoopBackReceivers` / `EventReceivers`: Input handlers
- `ExternalTransmitters` / `LoopBackTransmitters`: Output handlers
- `Paths`: Processing abilities (with traversal rules)

### Pool Benefits
- **Isolation**: Each plugin type has its own management space
- **Reusability**: Modules can be shared across workflow cores
- **Communication**: Pools enable inter-core communication
- **Lifecycle**: Centralized management of plugin instances

---

## MSBuild Integration

### Project Structure
Plugin projects use wildcard references for automatic inclusion:

```xml
<!-- Main application (Daisy.csproj) -->
<ItemGroup>
  <!-- Abilities -->
  <ProjectReference Include="..\Daisy.Abilities\*\*.csproj" />
  
  <!-- Receivers -->
  <ProjectReference Include="..\Daisy.Receivers\*\*.csproj" />
  
  <!-- Transmitters -->
  <ProjectReference Include="..\Daisy.Transmitters\*\*.csproj" />
  
  <!-- Workflows -->
  <ProjectReference Include="..\Daisy.Workflows\*\*.csproj" />
</ItemGroup>
```

### Plugin Deployment
- **Build-time**: Plugin assemblies are copied to the main application's output directory
- **Runtime**: Factories discover and load plugins from the application directory
- **Configuration**: Plugin assembly loading is handled automatically by the factories
- **References**: Wildcard patterns automatically include new plugin projects

---

## Initialization Sequence

The plugin system initializes in a specific order during application startup:

```csharp
// From Program.Main()
var settings = StartupFactory.AppSettingsConfiguration.LoadApplicationSettings();
var serviceProvider = StartupFactory.LoadServices(settings);

AbilityFactory.LoadAbilities(settings, serviceProvider);
TransmitterFactory.LoadExternalTransmitters(settings, serviceProvider);
TransmitterFactory.LoadLoopBackTransmitters(settings, serviceProvider);
ReceiverFactory.LoadExternalReceivers(settings, serviceProvider);
ReceiverFactory.LoadLoopBackReceivers(settings, serviceProvider);
ReceiverFactory.LoadEventReceivers(settings, serviceProvider);
WorkflowFactory.LoadCores(settings, serviceProvider);
```

**Initialization Steps:**
1. **Load Configuration**: Parse `appconfig.json` into `ApplicationSettings`
2. **Setup Services**: Create service provider and register framework services
3. **Load Abilities**: Discover and configure processing paths with traverse rules
4. **Load Transmitters**: Register output handlers to their pools
5. **Load Receivers**: Register input handlers to their pools  
6. **Load Workflows**: Instantiate workflow cores for parallel execution
7. **Start Execution**: Launch all cores with cancellation token support

---

## Plugin Development Guide

### Creating New Plugins

#### 1. Create Plugin Project
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\Daisy.Resources\Daisy.Resources.csproj" />
  </ItemGroup>
</Project>
```

#### 2. Implement Required Interface
```csharp
// Example: Custom Ability
public class MyCustomPath : IPath
{
    public string TraverseOrder { get; set; } = "100";
    public List<ITraverseRule> CanTraverseRules { get; set; } = new();
    public List<ITraverseRule> TraversedRules { get; set; } = new();

    public bool CanTraverse(Impulse impulse) => /* logic */;
    public bool Traversed(Impulse impulse) => /* logic */;
    public Impulse Traverse(Impulse impulse) => /* processing logic */;
}
```

#### 3. Update Configuration
```json
{
  "ApplicationSettings": {
    "Abilities": [
      "MyCustomPlugin"
    ],
    "PathTraverseOrder": {
      "MyCustomPath": 100
    }
  }
}
```

#### 4. Build and Deploy
The wildcard project references automatically include the new plugin in builds.

### Traverse Rules
For abilities requiring custom traversal logic:

```csharp
[TraverseRule(PathType = typeof(MyCustomPath))]
public class MyCustomRule : ITraverseRule
{
    public bool CanTraverse(Impulse impulse) => /* rule logic */;
}
```

---

## Troubleshooting

### Common Issues

#### 1. Assembly Not Found
**Error**: `FileNotFoundException` for plugin assembly
**Causes**: 
- Missing plugin DLL in application directory
- Incorrect assembly name in configuration
- Build failed for plugin project

**Solution**:
- Verify plugin builds successfully: `dotnet build`
- Check output directory contains plugin DLL
- Confirm assembly name matches configuration

#### 2. Interface Not Implemented
**Error**: Plugin types not discovered during reflection scan
**Causes**:
- Plugin doesn't implement required interface
- Plugin class is abstract or not public

**Solution**:
- Verify plugin implements correct interface (IPath, IReceiver, etc.)
- Ensure class is public and concrete (not abstract)

#### 3. Configuration Mismatch
**Error**: Plugin loaded but not activated
**Causes**:
- Missing configuration entry
- Incorrect module name in settings
- Path not listed in `PathTraverseOrder`

**Solution**:
- Add plugin to appropriate configuration array
- Verify spelling matches assembly name exactly
- Add path classes to `PathTraverseOrder` for abilities

#### 4. Dependency Issues
**Error**: Plugin fails to instantiate
**Causes**:
- Missing constructor with ApplicationSettings parameter
- Required dependencies not available

**Solution**:
- Ensure plugins have proper constructor signature
- Verify all dependencies are referenced and available

### Debugging Tips

1. **Enable Verbose Logging**: Factory classes log warnings for failed assemblies
2. **Check Build Output**: Verify all plugins copied to main application directory
3. **Validate Configuration**: Ensure JSON syntax is correct and complete
4. **Test Incrementally**: Add plugins one at a time to isolate issues
5. **Verify Interfaces**: Double-check interface implementations match factory expectations

---

## Best Practices

### Plugin Design
- **Single Responsibility**: Each plugin should have one clear purpose
- **Interface Compliance**: Fully implement required interfaces
- **Error Handling**: Handle exceptions gracefully without crashing the system
- **Configuration**: Accept settings via constructor parameter
- **Thread Safety**: Consider concurrent access in pool-managed environments

### Configuration Management
- **Consistent Naming**: Use assembly name exactly as configured
- **Logical Ordering**: Set appropriate `TraverseOrder` values for abilities
- **Core Targeting**: Configure receivers for appropriate workflow cores
- **API Management**: Centralize external API configurations

### Development Workflow
- **Build Often**: Use `dotnet build` to verify plugin compilation
- **Test Integration**: Validate plugins work within the full system
- **Format Code**: Always run `dotnet format` before committing
- **Update Documentation**: Keep configuration and documentation in sync

---

This plugin injection system provides flexibility and modularity while maintaining strong typing and configuration-driven behavior. The combination of reflection-based discovery, pool management, and MSBuild integration enables a robust plugin architecture that scales with the application's needs.