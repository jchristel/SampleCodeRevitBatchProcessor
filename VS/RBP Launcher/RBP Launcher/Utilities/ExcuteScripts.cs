using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Serilog;

namespace Launcher_Headless.Utilities
{
    public class ExcuteScripts
    {
        public static bool RunScripts(List<RBP_Launcher.Utilities.Configs.ScriptConfiguration.ScriptDetails> scripts, Dictionary<string, RBP_Launcher.IScriptRunner> scriptRunners)
        {
            bool returnValue = true;
            try
            {
                foreach (RBP_Launcher.Utilities.Configs.ScriptConfiguration.ScriptDetails script in scripts)
                {
                    // launch flow pre process
                    if (scriptRunners.ContainsKey(script.PythonVersion.Replace(".", "")))
                    {
                        Console.WriteLine($"Starting python {script.PythonVersion} script at {script.ScriptFilePath}");
                        //pythonScriptRunners[config.PreScript.PythonVersion.Replace(".", "")].ExecuteScript(config.PreScript.ScriptFilePath, new List<string> { "arg1", "arg1 value", "arg2", "arg2 value" });
                        bool executeScriptStatus = scriptRunners[script.PythonVersion.Replace(".", "")].ExecuteScript(script.ScriptFilePath, null);
                        //check what came back
                        if (!executeScriptStatus)
                        {
                            throw new Exception("Stopped executing scripts in que since previous script failed to execute without an exception.");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"Python {script.PythonVersion} not installed...");
                        throw new Exception($"Exception Python {script.PythonVersion} not installed occured in script execution.");
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
            RBP_Launcher.Utilities.Configs.ScriptConfiguration.Script rbpScriptGroup, 
            RBP_Launcher.Utilities.Configs.LauncherHeadlessConfiguration appSettings, 
            Dictionary<string, RBP_Launcher.IScriptRunner> scriptRunners
            )
        {
            bool returnValue = true;
            try
            {
                //launch pre process
                bool preGroupProcessScriptExecutionStatus = RunScripts(
                    new List<RBP_Launcher.Utilities.Configs.ScriptConfiguration.ScriptDetails> { rbpScriptGroup.PreScript }, 
                    scriptRunners
                    );
                
                //debug logging
                Log.Debug($"Pre group flow scripts executed with status {preGroupProcessScriptExecutionStatus}.");
                
                // check what came back
                if (!preGroupProcessScriptExecutionStatus)
                {
                    throw new Exception($"Pre group script: {rbpScriptGroup.PreScript.ScriptFilePath} failed to execute.");
                }
                
                // setup launcher instance
                RBP_Launcher.RBPSubProcessLauncher rbpLauncher = new RBP_Launcher.RBPSubProcessLauncher(
                    rbpFilePath: appSettings.RbpFilePath,
                    startInterval: rbpScriptGroup.StartInterval,
                    settingFiles: rbpScriptGroup.SettingFiles
                );
                // launch rbp
                rbpLauncher.LaunchApplicationsAndWait();

                //launch post process
                bool postGroupProcessScriptExecutionStatus = RunScripts(
                    new List<RBP_Launcher.Utilities.Configs.ScriptConfiguration.ScriptDetails> { rbpScriptGroup.PostScript }, 
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
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(ExcuteScripts), nameof(RunBatchProcessorScripts));
                returnValue = false;
                
            }
            return returnValue;
        }
    }
}
