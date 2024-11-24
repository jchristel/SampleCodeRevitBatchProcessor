using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class LoggerObjectTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.LoggerObjectClass, Is.Not.Null, "LoggerObject should be loaded.");
        }

        [Test]
        public void Constructor_InitializesDefaultValues()
        {
            dynamic logger = PythonEngineManager.LoggerObjectClass();
            Assert.That(logger.get_logger_obj(), Is.Not.Null);
        }

        [Test]
        public void LogFile_IsCreated()
        {
            string logName = "testLog";
            string outputPath = Path.GetTempPath();
            dynamic logger = PythonEngineManager.LoggerObjectClass(logName, outputPath);

            string logFilePath = Path.Combine(outputPath, logName, logName + ".txt");
            Assert.That(File.Exists(logFilePath), Is.True);
        }

        [Test]
        public void UpdateLogLevel_ChangesLogLevel()
        {
            dynamic logger = PythonEngineManager.LoggerObjectClass();
            logger.update_log_level((20, 40)); // Set log levels to INFO and ERROR

            Assert.That(logger.file_handler.level, Is.EqualTo(20)); // INFO
            Assert.That(logger.console_handler.level, Is.EqualTo(40)); // ERROR
        }

        [Test]
        public void ClearHandlers_RemovesAllHandlers()
        {
            dynamic logger = PythonEngineManager.LoggerObjectClass();
            logger.clear_handlers();

            Assert.That(logger.get_logger_obj().handlers.Count, Is.EqualTo(0));
        }

        [Test]
        public void InitHandlers_AddsHandlers()
        {
            dynamic logger = PythonEngineManager.LoggerObjectClass();
            logger.clear_handlers();
            logger.init_handlers();

            Assert.That(logger.get_logger_obj().handlers.Count, Is.GreaterThan(0));
        }

        [Test]
        public void GetLoggerObj_ReturnsLoggerObject()
        {
            dynamic logger = PythonEngineManager.LoggerObjectClass();
            var loggerObj = logger.get_logger_obj();

            Assert.That(loggerObj, Is.Not.Null);
            Assert.That(loggerObj.GetType().Name, Is.EqualTo("Logger"));
        }
    }
}
