using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PushIt;
using Serilog;

namespace Tests
{
    public class LoggerTests
    {
        private string _logDirectory;

        [SetUp]
        public void Setup()
        {
            string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            _logDirectory = Path.Combine(localAppDataPath, "duHast");
        }

        [Test]
        public void SetupLogger_CreatesLogDirectoryAndFile()
        {
            // Arrange
            if (Directory.Exists(_logDirectory))
            {
                Directory.Delete(_logDirectory, true);
            }


            PushIt.Main _main = new PushIt.Main();
            _main.setupLogger();

            // Assert
            Assert.That(Directory.Exists(_logDirectory), Is.True, "Log directory was not created.");
            string[] logFiles = Directory.GetFiles(_logDirectory, "log-pushit*.txt");
            Assert.That(logFiles.Length > 0, Is.True, "Log file was not created.");
        }

        [TearDown]
        public void TearDown()
        {
            Log.CloseAndFlush();
            if (Directory.Exists(_logDirectory))
            {
                Directory.Delete(_logDirectory, true);
            }
        }

    }
}
