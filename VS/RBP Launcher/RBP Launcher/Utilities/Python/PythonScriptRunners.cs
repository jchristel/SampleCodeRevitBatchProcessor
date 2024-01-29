using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities
{
    public class PythonScriptRunners
    {
        public static string ironPythonScriptRunnerName = "IronPython";
        public static Dictionary<string, IScriptRunner>GetAvailablePythonScriptRunners()
        {
            Dictionary<string, IScriptRunner>scriptRunners = new Dictionary<string, IScriptRunner>();
            
            
            //get all standard python installations
            var standardPython = CPythonInstall.GetAllStandardPythonInstalls();

            //TODO: some try catch here in case stuff is not installed at all!

            // add iron python script runner
            scriptRunners.Add(ironPythonScriptRunnerName, new RunnerIronPython());

            foreach (var python in standardPython)
            {
                scriptRunners.Add(python.Key, new RunnerCPython(python.Key));
            }

            return scriptRunners;
        }
    }
}
