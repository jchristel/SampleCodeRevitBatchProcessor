using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using RBP_Launcher.Utilities.Output;

namespace RBP_Launcher
{
    public class RBPSubProcessLauncher
    {

        private readonly string _rbpFilePath;
        private readonly int _startInterval;
        private readonly List<string> _settingFiles;

        public RBPSubProcessLauncher(string? rbpFilePath, int? startInterval, List<string>? settingFiles)
        {
            //check if any past in value is null, if so throw an exception, otherwise assign to class variable
            _rbpFilePath = rbpFilePath ?? throw new ArgumentNullException(nameof(rbpFilePath));
            _startInterval = startInterval ?? throw new ArgumentNullException(nameof(startInterval));
            _settingFiles = settingFiles ?? throw new ArgumentNullException(nameof(settingFiles));
        }

        public string RBPFilePath => _rbpFilePath;

        public int StartInterval => _startInterval;

        public List<string> SettingFiles => _settingFiles;


        public void LaunchApplicationsAndWait()
        {
            
            // Loop to start the process three times with a 2-minute wait in between
            for (int i = 0; i < _settingFiles.Count; i++)
            {
                // add settings file argument to path before passing to rbp
                string arg = "--settings_file \"" + _settingFiles[i] + "\"";
                // Create a new process start info
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = _rbpFilePath,
                    Arguments = arg,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                // Create a new process
                using (Process process = new Process { StartInfo = startInfo })
                {
                    // Attach event handlers to capture the output
                    process.OutputDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            ServiceLocator.OutputObserver?.Update($"Process {i + 1} Output: {e.Data}");
                        }
                    };

                    process.ErrorDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            ServiceLocator.OutputObserver?.Update($"Process {i + 1} [{KeyWords.Error}]: {e.Data}");
                        }
                    };

                    // Start the process
                    process.Start();

                    // Begin asynchronous reading of the output streams
                    process.BeginOutputReadLine();
                    process.BeginErrorReadLine();

                    // Wait for the process to finish
                    process.WaitForExit();

                    // Check the exit code
                    int exitCode = process.ExitCode;
                    ServiceLocator.OutputObserver?.Update($"Process {i + 1} exited with code {exitCode}");
                }

                // Wait for intervall before starting the next process
                if (i < _settingFiles.Count-1)
                {
                    ServiceLocator.OutputObserver?.Update($"Waiting for {_startInterval} second(s) before starting the next process...");
                    Thread.Sleep(_startInterval * 1000); // seconds in milliseconds
                }
            }

            ServiceLocator.OutputObserver?.Update("All processes have finished. Proceeding with the program.");
        }
    }
}