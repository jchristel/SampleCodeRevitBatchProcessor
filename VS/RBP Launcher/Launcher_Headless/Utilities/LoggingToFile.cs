using Serilog;
using System;
using System.IO;
using RBP_Launcher.Utilities;

namespace RBP_Launcher.Utilities
{
    public class LoggingToFile
    {
        public static void SetupFileLogger()
        {
            
                // Specify the log file directory
                string logDirectory = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    Constants.settingsFolderName, Constants.logFolderName);

                // Ensure the log directory exists; create it if it doesn't
                if (!Directory.Exists(logDirectory))
                {
                    Directory.CreateDirectory(logDirectory);
                }

                // Configure Serilog to write log events to a file in the specified directory
                Log.Logger = new LoggerConfiguration()
                    .WriteTo.File(Path.Combine(logDirectory, Constants.logFileName), rollingInterval: RollingInterval.Day)  // Output to a file
                    .CreateLogger();
            
        }
    }
}
