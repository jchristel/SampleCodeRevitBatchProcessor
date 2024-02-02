using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Serilog;

namespace RBP_Launcher
{
    public class Launcher
    {
        public static void LaunchIt(Utilities.Configs.LauncherHeadlessConfiguration launcherConfig, Utilities.Configs.ScriptConfiguration flowConfig)
        {
            try
            {
                // start excuting flow
                Console.WriteLine("Starting ...");
                Log.Information("Starting ...");
                // get python script runners
                Dictionary<string, IScriptRunner> pythonScriptRunners = Utilities.PythonScriptRunners.GetAvailablePythonScriptRunners();
                // run pre flow scripts
                Console.WriteLine("Starting pre flow groups scripts...");
                Log.Information("Starting pre flow groups scripts...");
                bool preScriptsExecutionStatus = Launcher_Headless.Utilities.ExcuteScripts.RunScripts(flowConfig.PreScript, pythonScriptRunners);
                // check if all scripts finished successfully
                if (preScriptsExecutionStatus)
                {
                    int counter = 0;
                    Log.Debug("All pre flow scripts executed successfully.");
                    Console.WriteLine("Batch processor flow session...");
                    Log.Information("Batch processor flow session...");
                    // start all scrit groups
                    foreach (RBP_Launcher.Utilities.Configs.ScriptConfiguration.Script rbpScriptGroup in flowConfig.BatchProcessorScripts)
                    {
                        counter++;

                        //log out put
                        Console.WriteLine($"Starting batch processor flow session {counter} of {flowConfig.BatchProcessorScripts.Count}");
                        Log.Information($"Starting batch processor flow session {counter} of {flowConfig.BatchProcessorScripts.Count}");

                        bool flowGroupExecutionStatus = Launcher_Headless.Utilities.ExcuteScripts.RunBatchProcessorScripts(
                            rbpScriptGroup,
                            launcherConfig,
                            pythonScriptRunners);

                        if (!flowGroupExecutionStatus)
                        {
                            throw new Exception($"Flow group {counter} failed to execute without an exception. Exiting.");
                        }
                    }

                    // run post flow scripts
                    Console.WriteLine("Starting post flow groups scripts...");
                    Log.Information("Starting post flow groups scripts...");
                    bool postScriptsExecutionStatus = Launcher_Headless.Utilities.ExcuteScripts.RunScripts(flowConfig.PostScript, pythonScriptRunners);
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
            catch (Exception)
            {
                //bubble up whatever went wrong
                throw;
            }
        }
    }
}
