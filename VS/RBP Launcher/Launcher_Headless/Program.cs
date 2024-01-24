// See https://aka.ms/new-console-template for more information
using Launcher_Headless.Utilities;
using Serilog;

// setup logger
LoggingToFile.SetupFileLogger();

Console.WriteLine($"Reading settings from {Constants.settigsFilePath}");
string jsonApplicationSettings = File.ReadAllText(Constants.settigsFilePath);
LauncherHeadlessConfiguration configApplication = LauncherHeadlessConfiguration.FromJson(jsonApplicationSettings);
Console.WriteLine($"...RBP path:{configApplication.RbpFilePath}");


// Replace "path/to/your/file.json" with the actual path to your JSON file
string filePathFlow = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\RBP Launcher\Launcher_Headless\flowSampleSettings.json";
Console.WriteLine($"Reading flow settings from {filePathFlow}");

// Read the JSON string from the file
string jsonString = File.ReadAllText(filePathFlow);

ScriptConfiguration config = ScriptConfiguration.FromJson(jsonString);

// Access the properties of the deserialized object as needed
Console.WriteLine($"...Pre Script Python Version: {config.PreScript.PythonVersion}");
Console.WriteLine($"...Number of Batch Processor Scripts: {config.BatchProcessorScripts.Count}");
Console.WriteLine($"...First Batch Processor Start Interval: {config.BatchProcessorScripts[0].StartInterval}");


Console.WriteLine($"Starting ...");

Dictionary<string, RBP_Launcher.IScriptRunner> pythonScriptRunners = RBP_Launcher.Utilities.PythonScriptRunners.GetAvailablePythonScriptRunners();


//launch flow pre process
if (pythonScriptRunners.ContainsKey(config.PreScript.PythonVersion.Replace(".","")))
{
    Console.WriteLine($"Starting python {config.PreScript.PythonVersion} script at {config.PreScript.ScriptFilePath}");
    pythonScriptRunners[config.PreScript.PythonVersion.Replace(".","")].ExecuteScript(config.PreScript.ScriptFilePath, null);
}
else
{
    Console.WriteLine($"Python {config.PreScript.PythonVersion} not installed...");
}


int counter = 0;
// start all scrit groups
foreach (ScriptConfiguration.Script rbpScriptGroup in config.BatchProcessorScripts)
{
    counter = counter + 1;
    //launch pre process
    //TODO

    //log out put
    Log.Information($"Starting batch processor flow session {counter} of {config.BatchProcessorScripts.Count}");

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
if (pythonScriptRunners.ContainsKey(config.PostScript.PythonVersion.Replace(".", "")))
{
    Console.WriteLine($"Starting python {config.PostScript.PythonVersion} script at {config.PostScript.ScriptFilePath}");
    pythonScriptRunners[config.PostScript.PythonVersion.Replace(".", "")].ExecuteScript(config.PostScript.ScriptFilePath, null);
}
else
{
    Console.WriteLine($"Python {config.PostScript.PythonVersion} not installed...");
}

// Close and flush the log when the application exits
Log.CloseAndFlush();