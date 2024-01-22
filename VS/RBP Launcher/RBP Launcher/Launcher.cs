using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;

namespace RBP_Launcher
{
    public class Launcher
    {

        private readonly string _rbpFilePath;
        private readonly int _startInterval;
        private readonly List<string> _settingFiles;

        public Launcher(string rbpFilePath, int startInterval, List<string> settingFiles)
        {
            _rbpFilePath = rbpFilePath;
            _startInterval = startInterval;
            _settingFiles = settingFiles;
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
                                Console.ForegroundColor = ConsoleColor.Green; // Set color for process output
                                Console.WriteLine($"Process {i + 1} Output: {e.Data}");
                                Console.ResetColor(); // Reset color to default
                            }
                        };

                        process.ErrorDataReceived += (sender, e) =>
                        {
                            if (!string.IsNullOrEmpty(e.Data))
                            {
                                Console.ForegroundColor = ConsoleColor.Red; // Set color for process error
                                Console.WriteLine($"Process {i + 1} Error: {e.Data}");
                                Console.ResetColor(); // Reset color to default
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
                        Console.WriteLine($"Process {i + 1} exited with code {exitCode}");
                    }

                    // Wait for intervall before starting the next process
                    if (i < _settingFiles.Count-1)
                    {
                        Console.WriteLine($"Waiting for {_startInterval} second(s) before starting the next process...");
                        Thread.Sleep(_startInterval * 1000); // seconds in milliseconds
                    }
                }

            Console.WriteLine("All processes have finished. Proceeding with the program.");
        }
    }
}