using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Serilog;
using RBP_Launcher.Utilities.Output;

namespace RBP_Launcher
{
    public class Launcher
    {
        public static void LaunchIt(Utilities.Configs.LauncherHeadlessConfiguration launcherConfig, Utilities.Configs.ScriptConfiguration flowConfig)
        {
            try
            {
                // start excuting flow
                ServiceLocator.OutputObserver?.Update("Starting ...");
                Log.Information("Starting ...");
                // get python script runners
                Dictionary<string, Interfaces.IScriptRunner> pythonScriptRunners = Utilities.PythonScriptRunners.GetAvailablePythonScriptRunners();
                // run pre flow scripts
                ServiceLocator.OutputObserver?.Update("Starting pre flow groups scripts...");
                Log.Information("Starting pre flow groups scripts...");
                bool preScriptsExecutionStatus = Utilities.ExcuteScripts.RunScripts(flowConfig.PreScript, pythonScriptRunners);
                // check if all scripts finished successfully
                if (preScriptsExecutionStatus)
                {
                    int counter = 0;
                    Log.Debug("All pre flow scripts executed successfully.");
                    ServiceLocator.OutputObserver?.Update("Batch processor flow session...");
                    Log.Information("Batch processor flow session...");
                    // start all scrit groups
                    if(flowConfig.BatchProcessorScripts != null)
                    {
                        foreach (Utilities.Configs.ScriptConfiguration.Script rbpScriptGroup in flowConfig.BatchProcessorScripts)
                        {
                            counter++;

                            //log out put
                            ServiceLocator.OutputObserver?.Update($"Starting batch processor flow session {counter} of {flowConfig.BatchProcessorScripts.Count}");
                            Log.Information($"Starting batch processor flow session {counter} of {flowConfig.BatchProcessorScripts.Count}");

                            bool flowGroupExecutionStatus = Utilities.ExcuteScripts.RunBatchProcessorScripts(
                                rbpScriptGroup: rbpScriptGroup,
                                appSettings: launcherConfig,
                                scriptRunners: pythonScriptRunners);

                            if (!flowGroupExecutionStatus)
                            {
                                throw new Exception($"Flow group {counter} failed to execute without an exception. Exiting.");
                            }
                        }
                    }
                    else
                    {
                        string message = "No Batch processor scripts provided...";
                        ServiceLocator.OutputObserver?.Update(message);
                        Log.Information(message);
                    }

                    // run post flow scripts
                    ServiceLocator.OutputObserver?.Update("Starting post flow groups scripts...");
                    Log.Information("Starting post flow groups scripts...");
                    bool postScriptsExecutionStatus = Utilities.ExcuteScripts.RunScripts(flowConfig.PostScript, pythonScriptRunners);
                    // check if all scripts finished successfully
                    if (postScriptsExecutionStatus)
                    {
                        Log.Debug("All post flow group scripts executed successfully.");
                        ServiceLocator.OutputObserver?.Update("Finished!");
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
