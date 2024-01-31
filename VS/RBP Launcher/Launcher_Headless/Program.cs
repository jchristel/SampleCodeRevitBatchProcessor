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
            Console.WriteLine("Starting ...");
            Log.Information("Starting ...");
            // get python script runners
            Dictionary<string, RBP_Launcher.IScriptRunner> pythonScriptRunners = RBP_Launcher.Utilities.PythonScriptRunners.GetAvailablePythonScriptRunners();
            // run pre flow scripts
            Console.WriteLine("Starting pre flow groups scripts...");
            Log.Information("Starting pre flow groups scripts...");
            bool preScriptsExecutionStatus = Launcher_Headless.Utilities.ExcuteScripts.RunScripts(scriptConfig.PreScript, pythonScriptRunners);
            // check if all scripts finished successfully
            if (preScriptsExecutionStatus)
            {
                int counter = 0;
                Log.Debug("All pre flow scripts executed successfully.");
                Console.WriteLine("Batch processor flow session...");
                Log.Information("Batch processor flow session...");
                // start all scrit groups
                foreach (RBP_Launcher.Utilities.Configs.ScriptConfiguration.Script rbpScriptGroup in scriptConfig.BatchProcessorScripts)
                {
                    counter++;
                    
                    //log out put
                    Console.WriteLine($"Starting batch processor flow session {counter} of {scriptConfig.BatchProcessorScripts.Count}");
                    Log.Information($"Starting batch processor flow session {counter} of {scriptConfig.BatchProcessorScripts.Count}");

                    bool flowGroupExecutionStatus = Launcher_Headless.Utilities.ExcuteScripts.RunBatchProcessorScripts(
                        rbpScriptGroup,
                        appSettings,
                        pythonScriptRunners);

                    if (!flowGroupExecutionStatus)
                    {
                        throw new Exception($"Flow group {counter} failed to execute without an exception. Exiting.");
                    }
                }

                // run post flow scripts
                Console.WriteLine("Starting post flow groups scripts...");
                Log.Information("Starting post flow groups scripts...");
                bool postScriptsExecutionStatus = Launcher_Headless.Utilities.ExcuteScripts.RunScripts(scriptConfig.PostScript, pythonScriptRunners);
                // check if all scripts finished successfully
                if (postScriptsExecutionStatus)
                {
                    Log.Debug("All post flow group scripts executed successfully.");
                    Console.WriteLine("Finished!");
                }
                else
                {
                    throw new Exception("One or multiple post flow scripts failed to execute. Exiting");
                }
            }
            else
            {
                throw new Exception("One or multiple pre flow scripts failed to execute. Exiting");
            }
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

