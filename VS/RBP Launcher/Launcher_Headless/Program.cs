// See https://aka.ms/new-console-template for more information
using Launcher_Headless.Utilities;


Console.WriteLine($"Reading settings from {Constants.settigsFilePath}");
string jsonApplicationSettings = File.ReadAllText(Constants.settigsFilePath);
LauncherHeadlessConfiguration configApplication = LauncherHeadlessConfiguration.FromJson(jsonApplicationSettings);
Console.WriteLine($"...RBP path:{configApplication.RbpFilePath}");


// Replace "path/to/your/file.json" with the actual path to your JSON file
string filePathFlow = @"C:\Users\janchristel\Documents\GitHub\RBP Launcher\Launcher_Headless\flowSampleSettings.json";
Console.WriteLine($"Reading flow settings from {filePathFlow}");

// Read the JSON string from the file
string jsonString = File.ReadAllText(filePathFlow);

ScriptConfiguration config = ScriptConfiguration.FromJson(jsonString);

// Access the properties of the deserialized object as needed
Console.WriteLine($"...Pre Script Python Version: {config.PreScript.PythonVersion}");
Console.WriteLine($"...Number of Batch Processor Scripts: {config.BatchProcessorScripts.Count}");
Console.WriteLine($"...First Batch Processor Start Interval: {config.BatchProcessorScripts[0].StartInterval}");

Console.WriteLine($"Starting ...");

//launch flow pre process
// TODO

// start all scrit groups
foreach (ScriptConfiguration.Script rbpScriptGroup in config.BatchProcessorScripts)
{
    //launch pre process
    //TODO

    // launch rbp
    RBP_Launcher.Launcher rbpLauncher = new RBP_Launcher.Launcher(
    rbpFilePath: configApplication.RbpFilePath,
    startInterval: rbpScriptGroup.StartInterval,
    settingFiles: rbpScriptGroup.SettingFiles
    );

    rbpLauncher.LaunchApplicationsAndWait();

    //launch post process
    // TODO
}

// launch flow post process
// TODO
