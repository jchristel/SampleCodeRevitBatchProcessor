using System;
using System.IO;
using Serilog;

namespace Utils
{
    public static class LoggerUtility

    {
        /// <summary>
        /// Sets up the logger using Serilog to log messages to a file.
        /// </summary>
        public static void setupLogger()
        {
            // Configure Serilog
            string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string logDirectory = Path.Combine(localAppDataPath, "duHast");
            Directory.CreateDirectory(logDirectory);
            Log.Logger = new LoggerConfiguration()
                .WriteTo.File(
                    path: Path.Combine(logDirectory, "log-pushit.txt"),
                    rollingInterval: RollingInterval.Day,
                    retainedFileCountLimit: 4) // Keep the last 4 weeks of logs
                .CreateLogger();

        }
    }
}
