using Serilog;
using System.Diagnostics;
using RBP_Launcher.Utilities.Output;
namespace RBP_Launcher
{
    public class RunnerCPython : Interfaces.IScriptRunner
    {
        private readonly string _versionNumber;
        private readonly string _versionNotProvided = "NA";

        public RunnerCPython()
        {
            _versionNumber = _versionNotProvided;
        }

        public RunnerCPython(string versionNumber)
        {
            // remove any separating . in version number
            _versionNumber = versionNumber.Replace(".", ""); 

        }

        public string VersionNumber => _versionNumber;



        private string? GetPythonPath() 
        {
            if (_versionNumber == _versionNotProvided)
            {
                KeyValuePair<string, string> pythonVersion = Utilities.CPythonInstall.GetLatestPythonVersion();
                return pythonVersion.Value;
            }
            else
            {
                Dictionary<string, string> pythonInstalled = Utilities.CPythonInstall.GetAllStandardPythonInstalls();
                if (pythonInstalled.ContainsKey(_versionNumber))
                {
                    return pythonInstalled[_versionNumber];
                }
                else
                {
                    return null;
                }
            }
        }

        public bool ExecuteScript(string scriptFilePath, List<string>? scriptArguments = null)
        {
            bool executedWithoutExceptions = true;
            try
            {
                //get standard python versions available
                string? pythonDirectoryPath = GetPythonPath();
                // check if we have python installed as required
                if(pythonDirectoryPath == null)
                {
                    if(_versionNumber == _versionNotProvided)
                    {
                        throw new Exception("No standard Python version is installed.");
                    }
                    else
                    {
                        throw new Exception($"Python version {_versionNumber} is not installed.");
                    }
                }

                // Replace "path/to/your/python.exe" with the actual path to your Python executable
                string pythonExecutablePath = Path.Combine(pythonDirectoryPath,"Python.exe");

                // Create a new process start info
                var startInfo = new ProcessStartInfo
                {
                    FileName = pythonExecutablePath,
                    Arguments = $"\"{scriptFilePath}\" {scriptArguments}",
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                // Create and start the process
                using (var process = new Process { StartInfo = startInfo })
                {
                    // Attach event handlers to capture the output
                    process.OutputDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            ServiceLocator.OutputObserver?.Update($"CPython Process Output: {e.Data}");
                        }
                    };

                    process.ErrorDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            ServiceLocator.OutputObserver?.Update($"CPython Process [{KeyWords.Error}]: {e.Data}");
                        }
                    };
                    process.Start();

                    // Begin asynchronous reading of the output streams
                    process.BeginOutputReadLine();
                    process.BeginErrorReadLine();

                    process.WaitForExit();
                }
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(RunnerIronPython), nameof(ExecuteScript));
                executedWithoutExceptions = false;
            }
            return executedWithoutExceptions;
        }
    }
}
