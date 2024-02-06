using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities
{
    public class PythonScriptRunners
    {
        public const string ironPythonScriptRunnerName = "IronPython";
        public static Dictionary<string, Interfaces.IScriptRunner>GetAvailablePythonScriptRunners()
        {
            Dictionary<string, Interfaces.IScriptRunner>scriptRunners = new();
            
            //get all standard python installations
            //this can return an empty dictionary
            var standardPython = CPythonInstall.GetAllStandardPythonInstalls();

            //check if an ironpython installation exists
            string? latestInstallPath = IronPythonInstall.GetLatestVersionInstallPath();
            if (latestInstallPath != null)
            {
                // add iron python script runner
                scriptRunners.Add(ironPythonScriptRunnerName, new RunnerIronPython());
            }
            foreach (var python in standardPython)
            {
                scriptRunners.Add(python.Key, new RunnerCPython(python.Key));
            }

            return scriptRunners;
        }
    }
}
