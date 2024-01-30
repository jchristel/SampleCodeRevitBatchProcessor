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
                        scriptRunners[script.PythonVersion.Replace(".", "")].ExecuteScript(script.ScriptFilePath, null);
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
            }
            
            return returnValue;
        }
    }
}
