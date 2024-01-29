// See https://aka.ms/new-console-template for more information
using Launcher_Headless.Utilities;
using Serilog;

// setup logger
LoggingToFile.SetupFileLogger();

try
{
    // read app settings
    var appSettings = RBP_Launcher.Utilities.Configs.AppSettings.GetAppSettings();
    if (appSettings != null)
    {
        // get flow settings
        // TODO: get settings path from arguments past in

        // Replace "path/to/your/file.json" with the actual path to your JSON file
        string filePathFlow = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\RBP Launcher\Launcher_Headless\flowSampleSettings.json";
        Console.WriteLine($"Reading flow settings from {filePathFlow}");
        var scriptConfig = RBP_Launcher.Utilities.Configs.FlowSettings.GetFlowSettings(filePathFlow);
        if (scriptConfig != null)
        {
            // start excuting flow
            Console.WriteLine($"Starting ...");
            // get python script runners
            Dictionary<string, RBP_Launcher.IScriptRunner> pythonScriptRunners = RBP_Launcher.Utilities.PythonScriptRunners.GetAvailablePythonScriptRunners();
            
            // launch flow pre process
            if (pythonScriptRunners.ContainsKey(scriptConfig.PreScript.PythonVersion.Replace(".", "")))
            {
                Console.WriteLine($"Starting python {scriptConfig.PreScript.PythonVersion} script at {scriptConfig.PreScript.ScriptFilePath}");
                //pythonScriptRunners[config.PreScript.PythonVersion.Replace(".", "")].ExecuteScript(config.PreScript.ScriptFilePath, new List<string> { "arg1", "arg1 value", "arg2", "arg2 value" });
                pythonScriptRunners[scriptConfig.PreScript.PythonVersion.Replace(".", "")].ExecuteScript(scriptConfig.PreScript.ScriptFilePath, null);
            }
            else
            {
                Console.WriteLine($"Python {scriptConfig.PreScript.PythonVersion} not installed...");
                throw new Exception($"Exception Python {scriptConfig.PreScript.PythonVersion} not installed occured in pre flow script execution.");
            }


            int counter = 0;
            // start all scrit groups
            foreach (RBP_Launcher.Utilities.Configs.ScriptConfiguration.Script rbpScriptGroup in scriptConfig.BatchProcessorScripts)
            {
                counter = counter + 1;
                //launch pre process
                //TODO

                //log out put
                Log.Information($"Starting batch processor flow session {counter} of {scriptConfig.BatchProcessorScripts.Count}");

                // launch rbp
                RBP_Launcher.Launcher rbpLauncher = new RBP_Launcher.Launcher(
                rbpFilePath: appSettings.RbpFilePath,
                startInterval: rbpScriptGroup.StartInterval,
                settingFiles: rbpScriptGroup.SettingFiles
                );

                rbpLauncher.LaunchApplicationsAndWait();

                //launch post process
                // TODO
            }

            // launch flow post process
            if (pythonScriptRunners.ContainsKey(scriptConfig.PostScript.PythonVersion.Replace(".", "")))
            {
                Console.WriteLine($"Starting python {scriptConfig.PostScript.PythonVersion} script at {scriptConfig.PostScript.ScriptFilePath}");
                pythonScriptRunners[scriptConfig.PostScript.PythonVersion.Replace(".", "")].ExecuteScript(scriptConfig.PostScript.ScriptFilePath, null);
            }
            else
            {
                Console.WriteLine($"Python {scriptConfig.PostScript.PythonVersion} not installed...");
                throw new Exception($"Exception Python {scriptConfig.PreScript.PythonVersion} not installed occured in post flow script execution.");
            }
        }
        else
        {
            Console.WriteLine($"Failed to read flow settings from {filePathFlow}. Exiting");
            Log.Debug($"Failed to read flow settings from {filePathFlow}. Exiting");
        }
    }
    else
    {
        Console.WriteLine($"Failed to read settings from {RBP_Launcher.Utilities.Constants.settigsFilePath}. Exiting");
        Log.Debug($"Failed to read settings from {RBP_Launcher.Utilities.Constants.settigsFilePath}. Exiting");
    }
}
catch(Exception ex)
{
    Console.WriteLine($"exited with exception {ex}");
    Log.Error(ex, "An error occurred in Main");
}


// Close and flush the log when the application exits
Log.CloseAndFlush();