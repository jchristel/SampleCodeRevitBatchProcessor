using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Serilog;
using RBP_Launcher.Utilities.Output;

namespace RBP_Launcher.Utilities
{
    public class ExcuteScripts
    {
        public static bool RunScripts(List<Configs.ScriptConfiguration.ScriptDetails>? scripts, Dictionary<string, Interfaces.IScriptRunner> scriptRunners)
        {
            bool returnValue = true;
            try
            {
                // check for null value
                if(scripts == null)
                {
                    throw new ArgumentNullException(nameof(scripts));
                }
                foreach (Configs.ScriptConfiguration.ScriptDetails script in scripts)
                {   
                    //all property values on script instance must be set!
                    if(script.PythonVersion != null && script.ScriptFilePath != null) { 
                        // launch flow pre process
                        if (scriptRunners.ContainsKey(script.PythonVersion.Replace(".", "")))
                        {
                            ServiceLocator.OutputObserver?.Update($"Starting python {script.PythonVersion} script at {script.ScriptFilePath}");
                            //pythonScriptRunners[config.PreScript.PythonVersion.Replace(".", "")].ExecuteScript(config.PreScript.ScriptFilePath, new List<string> { "arg1", "arg1 value", "arg2", "arg2 value" });
                            bool executeScriptStatus = scriptRunners[script.PythonVersion.Replace(".", "")].ExecuteScript(script.ScriptFilePath, script.ScriptArguments);
                            //check what came back
                            if (!executeScriptStatus)
                            {
                                throw new Exception("Stopped executing scripts in que since previous script failed to execute without an exception.");
                            }
                        }
                        else
                        {
                            ServiceLocator.OutputObserver?.Update($"{KeyWords.Error} Python {script.PythonVersion} not installed...");
                            throw new Exception($"Exception Python {script.PythonVersion} not installed occured in script execution.");
                        }
                    }
                    else
                    {
                        throw new Exception($"Not all required properties have a value set. Python version: [{script.PythonVersion}], script file path: [{script.ScriptFilePath}]");
                    }
                }
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(ExcuteScripts), nameof(RunScripts));
                returnValue = false;
            }
            
            return returnValue;
        }

        public static bool RunBatchProcessorScripts(
            Configs.ScriptConfiguration.Script rbpScriptGroup, 
            Configs.LauncherHeadlessConfiguration appSettings, 
            Dictionary<string, Interfaces.IScriptRunner> scriptRunners
            )
        {
            bool returnValue = true;
            try
            {
                if (rbpScriptGroup.PreScript != null)
                { 
                    //launch pre process
                    bool preGroupProcessScriptExecutionStatus = RunScripts(
                        new List<Configs.ScriptConfiguration.ScriptDetails> { rbpScriptGroup.PreScript },
                        scriptRunners
                        );

                    //debug logging
                    Log.Debug($"Pre group flow scripts executed with status {preGroupProcessScriptExecutionStatus}.");
                    // check what came back
                    if (!preGroupProcessScriptExecutionStatus)
                    {
                        throw new Exception($"Pre group script: {rbpScriptGroup.PreScript.ScriptFilePath} failed to execute.");
                    }
                }
                else
                {
                    ServiceLocator.OutputObserver?.Update("No pre group script specified.");
                    Log.Information("No pre group script specified.");
                }
               
                
                // setup launcher instance
                RBPSubProcessLauncher rbpLauncher = new RBPSubProcessLauncher(
                    rbpFilePath: appSettings.RbpFilePath,
                    startInterval: rbpScriptGroup.StartInterval,
                    settingFiles: rbpScriptGroup.SettingFiles
                );
                // launch rbp
                rbpLauncher.LaunchApplicationsAndWait();

                if (rbpScriptGroup.PostScript != null)
                {

                    //launch post process
                    bool postGroupProcessScriptExecutionStatus = RunScripts(
                        new List<Configs.ScriptConfiguration.ScriptDetails> { rbpScriptGroup.PostScript },
                        scriptRunners
                        );

                    //debug logging
                    Log.Debug($"Post group flow scripts executed with status {postGroupProcessScriptExecutionStatus}.");

                    // check what came back
                    if (!postGroupProcessScriptExecutionStatus)
                    {
                        throw new Exception($"Post group script: {rbpScriptGroup.PostScript.ScriptFilePath} failed to execute.");
                    }
                }
                else
                {
                    ServiceLocator.OutputObserver?.Update("No post group script specified.");
                    Log.Information("No pre group script specified.");
                }

            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(ExcuteScripts), nameof(RunBatchProcessorScripts));
                returnValue = false;
            }
            return returnValue;
        }
    }
}
