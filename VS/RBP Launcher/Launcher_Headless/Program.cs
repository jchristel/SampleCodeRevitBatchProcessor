// See https://aka.ms/new-console-template for more information
using RBP_Launcher.Utilities;
using Serilog;
using Microsoft.Extensions.Configuration;

// setup logger
LoggingToFile.SetupFileLogger();

// setup console output
// Create an instance of the observer
var consoleObserver = new RBP_Launcher.Utilities.ConsoleOutputObserver();
// Set the observer instance to the service locator
RBP_Launcher.Utilities.Output.ServiceLocator.OutputObserver = consoleObserver;

try
{
    // get seetings file path from args past in
    string filePathFlow = GetFlowSettingsFromArgs(args);
    // read app settings
    var appSettings = RBP_Launcher.Utilities.Configs.AppSettings.GetAppSettings();
    if (appSettings != null)
    {
        // get flow settings
        Console.WriteLine($"Reading flow settings from {filePathFlow}");
        var scriptConfig = RBP_Launcher.Utilities.Configs.FlowSettings.GetFlowSettings(filePathFlow);
        if (scriptConfig != null)
        {
            //start launcher ...
            RBP_Launcher.Launcher.LaunchIt(appSettings, scriptConfig);
        }
        else
        {
            throw new Exception($"Failed to read flow settings from {filePathFlow}. Exiting");
        }
    }
    else
    {
        throw new Exception($"Failed to read settings from {RBP_Launcher.Utilities.Constants.settigsFilePath}. Exiting");
    }
}
catch(Exception ex)
{
    Console.WriteLine($"Exception {ex}");
    Log.Error(ex, "An error occurred in Main");
}


// Close and flush the log when the application exits
Log.CloseAndFlush();

/// <summary>
/// Retrieves --settings value from arguments
/// if not arguments are supplied an exception is thrown
/// </summary>
static string GetFlowSettingsFromArgs(string[] args)
{
    var configBuilder = new ConfigurationBuilder()
        .AddCommandLine(args); // This line adds command line arguments to configuration

    var configuration = configBuilder.Build();

    // YAccess configuration value for settings
    string? filePathFlow = configuration["settings"];
    if (filePathFlow == null)
    {
        PrintHelpText();
        throw new Exception("No --settings argument provided. Exiting");
    }
    Log.Information($"Value of --settings: {filePathFlow}");
    return filePathFlow;
}

/// <summary>
/// Prints out a help text on how to supply arguments 
/// </summary>
static void PrintHelpText()
{
    Console.WriteLine("Usage: Launcher_Headless.exe --settings <file path>");
    Console.WriteLine("Description: ");
    Console.WriteLine(" --settings \t\trequires the fully qualified file path to the flow settings .json file");
    Console.WriteLine("\t\t\tsample: Launcher_Headless.exe --settings \"C/my/file/samle.json\"");
}
