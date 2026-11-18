using IronPython.Runtime;
using PythonTests.Setup;
using System.Text.RegularExpressions;

namespace PythonTests.UtilitiesTests
{
    /// <summary>
    /// Tests for the logging code of duHast.Utilities: LoggerObject (levels), the add_logger decorator (log_decorator),
    /// the file / console filters (logger_filtering), the handlers (logging_handlers) and the formatters (logger_formatting).
    /// Each test uses its own LoggerObject writing to a temp directory; the console handler is a CustomStreamHandler collecting the console output.
    /// </summary>
    public class LoggingTests
    {
        private dynamic loggerObject;      // LoggerObject
        private dynamic consoleOutput;     // list of the messages the console handler let through
        private string logDirectory;

        [SetUp]
        public void SetUp()
        {
            PythonEngineManager.PythonEngine.Execute(@"
import tempfile, io, logging, functools, time
from duHast.Utilities.Objects.logger_object import LoggerObject
from duHast.Utilities.logging_handlers import CustomStreamHandler
from duHast.Utilities.log_decorator import get_add_logger_decorator

def _make_logger(name, levels):
    console = []
    directory = tempfile.mkdtemp()
    lo = LoggerObject(log_name=name, output_path=directory, log_level=levels,
                      cons_stream_hndlr=functools.partial(CustomStreamHandler, console.append))
    return lo, console, directory

def _file_text(lo):
    lo.file_handler.flush()
    with io.open(lo.log_file_path, encoding='utf-8') as f:
        return f.read()
", PythonEngineManager.Scope);
            StartLogger((10, 30));
        }

        [TearDown]
        public void TearDown()
        {
            try { loggerObject.clear_handlers(); } catch { }
            try { if (Directory.Exists(logDirectory)) Directory.Delete(logDirectory, true); } catch { }
        }

        private void StartLogger((int file, int console) levels)
        {
            try { loggerObject?.clear_handlers(); } catch { }
            dynamic make = PythonEngineManager.Scope.GetVariable("_make_logger");
            dynamic created = make("test_" + Guid.NewGuid().ToString("N"), new PythonTuple(new object[] { levels.file, levels.console }));
            loggerObject = created[0];
            consoleOutput = created[1];
            logDirectory = (string)created[2];
        }

        private string FileText() => (string)PythonEngineManager.Scope.GetVariable("_file_text")(loggerObject);

        private List<string> ConsoleLines() => ((IEnumerable<object>)consoleOutput).Select(o => (string)o).ToList();

        private dynamic NewDecorator(bool errorsInConsole = true, bool suppressExceptions = true, bool recordTime = false) =>
            PythonEngineManager.Scope.GetVariable("get_add_logger_decorator")(loggerObject, errorsInConsole, suppressExceptions, recordTime);

        /// <summary>Defines a decorated python function and returns it. 'body' is the python function body (indented 4 spaces).</summary>
        private dynamic Decorated(dynamic addLogger, string signature, string body, string decoratorArguments = "")
        {
            PythonEngineManager.Scope.SetVariable("_add_logger", addLogger);
            PythonEngineManager.Scope.SetVariable("_lo", loggerObject);
            PythonEngineManager.PythonEngine.Execute(
                $"@_add_logger({decoratorArguments})\ndef _decorated({signature}):\n{body}\n", PythonEngineManager.Scope);
            return PythonEngineManager.Scope.GetVariable("_decorated");
        }

        // ---------------------------------------- LoggerObject levels ----------------------------------------

        [TestCase(10, 30, 10)]
        [TestCase(30, 40, 30)]
        [TestCase(40, 20, 20)]
        public void LoggerLevel_IsTheMoreVerboseOfTheTwoHandlers(int file, int console, int expected)
        {
            StartLogger((file, console));
            Assert.That((int)loggerObject.new_logger.level, Is.EqualTo(expected));
            Assert.That((int)loggerObject.file_handler.level, Is.EqualTo(file));
            Assert.That((int)loggerObject.console_handler.level, Is.EqualTo(console));
        }

        [Test]
        public void UpdateLogLevel_AdjustsTheLoggerAndTheStoredLevels()
        {
            StartLogger((30, 30));
            loggerObject.update_log_level(new PythonTuple(new object[] { 10, 40 }));
            Assert.That((int)loggerObject.new_logger.level, Is.EqualTo(10));
            Assert.That((int)loggerObject.file_log_level, Is.EqualTo(10));
            Assert.That((int)loggerObject.console_log_level, Is.EqualTo(40));

            loggerObject.update_log_level(new PythonTuple(new object[] { 40, 50 }));
            Assert.That((int)loggerObject.new_logger.level, Is.EqualTo(40));
        }

        [Test]
        public void DebugMessage_ReachesTheFileOnly_WhenOnlyTheFileIsAtDebug()
        {
            loggerObject.new_logger.debug("a debug message");
            loggerObject.new_logger.warning("a warning");
            Assert.That(FileText(), Does.Contain("a debug message").And.Contain("a warning"));
            Assert.That(ConsoleLines(), Is.EqualTo(new[] { "a warning" }));
        }

        [Test]
        public void DebugMessage_IsDropped_WhenNeitherHandlerWantsIt()
        {
            StartLogger((20, 30));
            loggerObject.new_logger.debug("a debug message");
            Assert.That(FileText(), Does.Not.Contain("a debug message"));
        }

        [Test]
        public void Handlers_OneFileOneConsole_EvenAfterInitialisingAgain()
        {
            loggerObject.init_handlers();
            loggerObject.init_handlers();
            var names = ((IEnumerable<object>)loggerObject.new_logger.handlers).Select(h => (string)((dynamic)h).name).OrderBy(n => n).ToList();
            Assert.That(names, Is.EqualTo(new[] { "console", "file" }));
        }

        [Test]
        public void LogFile_LineFormat_LevelTimeMessage()
        {
            loggerObject.new_logger.info("hello file");
            Assert.That(FileText().Trim(), Does.Match(@"^INFO \| \d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3} \| hello file$"));
        }

        // ---------------------------------------- filters ----------------------------------------

        private bool Passes(string filter, string? block)
        {
            PythonEngineManager.Scope.SetVariable("_block", block);
            PythonEngineManager.PythonEngine.Execute($@"
from duHast.Utilities.logger_filtering import {filter}
_record = logging.LogRecord('n', 20, 'p', 1, 'm', None, None)
if _block is not None:
    _record.block = _block
_passes = {filter}().filter(_record)
", PythonEngineManager.Scope);
            return (bool)PythonEngineManager.Scope.GetVariable("_passes");
        }

        [TestCase(null, true)]
        [TestCase("file", false)]
        [TestCase("console", true)]
        [TestCase("something else", true)]
        public void FilterFile_StopsOnlyRecordsBlockedForTheFile(string? block, bool expected) =>
            Assert.That(Passes("FilterFile", block), Is.EqualTo(expected));

        [TestCase(null, true)]
        [TestCase("console", false)]
        [TestCase("file", true)]
        [TestCase("something else", true)]
        public void FilterConsole_StopsOnlyRecordsBlockedForTheConsole(string? block, bool expected) =>
            Assert.That(Passes("FilterConsole", block), Is.EqualTo(expected));

        [Test]
        public void BlockedRecords_ReachOnlyTheOtherHandler()
        {
            PythonEngineManager.Scope.SetVariable("_logger", loggerObject.new_logger);
            PythonEngineManager.PythonEngine.Execute(@"
_logger.warning('everywhere')
_logger.warning('only the console', extra={'block': 'file'})
_logger.warning('only the file', extra={'block': 'console'})
", PythonEngineManager.Scope);
            Assert.That(ConsoleLines(), Is.EqualTo(new[] { "everywhere", "only the console" }));
            string file = FileText();
            Assert.That(file, Does.Contain("everywhere").And.Contain("only the file").And.Not.Contain("only the console"));
        }

        // ---------------------------------------- handlers ----------------------------------------

        /// <summary>The python class names of the objects in a list.</summary>
        private static List<string> PythonTypeNames(dynamic objects)
        {
            PythonEngineManager.Scope.SetVariable("_objects", objects);
            PythonEngineManager.PythonEngine.Execute("_type_names = [type(o).__name__ for o in _objects]", PythonEngineManager.Scope);
            return ((IEnumerable<object>)PythonEngineManager.Scope.GetVariable("_type_names")).Select(o => (string)o).ToList();
        }

        [Test]
        public void StandardHandlers_AreNamedLeveledFilteredAndFormatted()
        {
            dynamic file = loggerObject.file_handler;
            dynamic console = loggerObject.console_handler;
            Assert.That((string)file.name, Is.EqualTo("file"));
            Assert.That((string)console.name, Is.EqualTo("console"));
            Assert.That(PythonTypeNames(file.filters), Is.EqualTo(new[] { "FilterFile" }));
            Assert.That(PythonTypeNames(console.filters), Is.EqualTo(new[] { "FilterConsole" }));
            Assert.That(PythonTypeNames(new PythonList { file }), Is.EqualTo(new[] { "RotatingFileHandler" }));
        }

        [Test]
        public void CustomStreamHandler_CallsTheFunctionWithEachFormattedMessage()
        {
            loggerObject.new_logger.warning("one");
            loggerObject.new_logger.error("two");
            Assert.That(ConsoleLines(), Is.EqualTo(new[] { "one", "two" }));
        }

        [Test]
        public void CustomStreamHandler_RespectsItsLevel()
        {
            loggerObject.new_logger.info("below the console level");
            Assert.That(ConsoleLines(), Is.Empty);
            loggerObject.update_log_level(new PythonTuple(new object[] { 10, 10 }));
            loggerObject.new_logger.info("now shown");
            Assert.That(ConsoleLines(), Is.EqualTo(new[] { "now shown" }));
        }

        [Test]
        public void CustomStreamHandler_FunctionThatFails_DoesNotBreakLogging()
        {
            PythonEngineManager.PythonEngine.Execute(@"
import logging
from duHast.Utilities.logging_handlers import CustomStreamHandler
def _failing(message):
    raise ValueError('boom')
_handler = CustomStreamHandler(_failing)
_probe = logging.getLogger('failing_handler_probe')
_probe.propagate = False
_probe.setLevel(10)
_probe.addHandler(_handler)
_raise_setting = logging.raiseExceptions
logging.raiseExceptions = False
try:
    _probe.info('does not raise')
    _survived = True
finally:
    logging.raiseExceptions = _raise_setting
    _probe.removeHandler(_handler)
", PythonEngineManager.Scope);
            Assert.That((bool)PythonEngineManager.Scope.GetVariable("_survived"), Is.True);
        }

        [Test]
        public void CustomStreamHandler_WriteHandsTheTextToTheFunction()
        {
            PythonEngineManager.PythonEngine.Execute(@"
from duHast.Utilities.logging_handlers import CustomStreamHandler
_written = []
CustomStreamHandler(_written.append).write('text')
", PythonEngineManager.Scope);
            Assert.That((string)PythonEngineManager.Scope.GetVariable("_written")[0], Is.EqualTo("text"));
        }

        // ---------------------------------------- formatters ----------------------------------------

        private string Format(string formatterFunction, double? created = null)
        {
            PythonEngineManager.Scope.SetVariable("_created", created);
            PythonEngineManager.PythonEngine.Execute($@"
from duHast.Utilities import logger_formatting
_record = logging.LogRecord('n', 20, 'p', 1, 'the message', None, None)
if _created is not None:
    _record.created = _created
    _record.msecs = (_created % 1) * 1000
_formatted = logger_formatting.{formatterFunction}().format(_record)
", PythonEngineManager.Scope);
            return (string)PythonEngineManager.Scope.GetVariable("_formatted");
        }

        [Test]
        public void MessageOnlyFormatter_ShowsTheMessage() => Assert.That(Format("msg_only"), Is.EqualTo("the message"));

        [Test]
        public void LocalFormatter_LevelLocalTimeMessage() =>
            Assert.That(Format("level_time_local_msg_formatter"), Does.Match(@"^INFO \| \d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3} \| the message$"));

        [Test]
        public void UtcFormatter_ShowsTheUtcTimeOfTheRecord()
        {
            Assert.That(Format("level_time_utc_msg_formatter", 0), Is.EqualTo("INFO | 1970-01-01 00:00:00.000 | the message"));
            Assert.That(Format("level_time_utc_msg_formatter", 86400.5), Is.EqualTo("INFO | 1970-01-02 00:00:00.500 | the message"));
        }

        [Test]
        public void UtcFormatter_TimeIsNotFrozenWhenTheFormatterIsCreated()
        {
            PythonEngineManager.PythonEngine.Execute(@"
from duHast.Utilities import logger_formatting
_formatter = logger_formatting.level_time_utc_msg_formatter()
_first = logging.LogRecord('n', 20, 'p', 1, 'first', None, None)
_first.created = 1000.0
_second = logging.LogRecord('n', 20, 'p', 1, 'second', None, None)
_second.created = 5000.0
_a = _formatter.format(_first)
_b = _formatter.format(_second)
", PythonEngineManager.Scope);
            string a = (string)PythonEngineManager.Scope.GetVariable("_a");
            string b = (string)PythonEngineManager.Scope.GetVariable("_b");
            Assert.That(Regex.Match(a, @"\d\d:\d\d:\d\d").Value, Is.Not.EqualTo(Regex.Match(b, @"\d\d:\d\d:\d\d").Value));
        }

        // ---------------------------------------- the decorator ----------------------------------------

        [Test]
        public void Decorator_LogsStartAndFinish_AndReturnsTheResult()
        {
            dynamic add = Decorated(NewDecorator(), "a, b", "    return a + b");
            Assert.That((int)add(1, 2), Is.EqualTo(3));
            string file = FileText();
            Assert.That(file, Does.Contain("Started function: _decorated").And.Contain("Finished function: _decorated. Return value is: 3"));
        }

        [Test]
        public void Decorator_KeepsTheNameAndDocString()
        {
            dynamic function = Decorated(NewDecorator(), "", "    'the doc'\n    return 1");
            Assert.That((string)function.__name__, Is.EqualTo("_decorated"));
            Assert.That((string)function.__doc__, Is.EqualTo("the doc"));
        }

        [Test]
        public void Decorator_ArgumentsAreLoggedAtDebug_FileOnlyByDefault()
        {
            dynamic add = Decorated(NewDecorator(), "a, b=0", "    return a + b");
            add(1, b: 3);
            Assert.That(FileText(), Does.Contain("function _decorated called with args: 1, b=3"));
            Assert.That(string.Join("\n", ConsoleLines()), Does.Not.Contain("called with args"));
        }

        [Test]
        public void Decorator_ArgumentsAreLoggedWhenTheLevelIsLowered()
        {
            StartLogger((30, 30));
            dynamic add = Decorated(NewDecorator(), "a", "    return a", "log_level=(10, 10)");
            add(7);
            Assert.That(FileText(), Does.Contain("called with args: 7"));
            Assert.That(string.Join("\n", ConsoleLines()), Does.Contain("called with args: 7"));
        }

        [Test]
        public void Decorator_NoArguments_LogsThatAtInfo()
        {
            dynamic function = Decorated(NewDecorator(), "", "    return 1");
            function();
            Assert.That(FileText(), Does.Contain("function _decorated called with no arguments"));
        }

        [Test]
        public void Decorator_FalsyResult_NoReturnValueInTheLog()
        {
            dynamic function = Decorated(NewDecorator(), "", "    return 0");
            Assert.That((int)function(), Is.EqualTo(0));
            string file = FileText();
            Assert.That(file, Does.Contain("Finished function: _decorated"));
            Assert.That(file, Does.Not.Contain("Return value is"));
        }

        [Test]
        public void Decorator_ExceptionSuppressed_ReturnsNone_LogsTheErrorWithTracebackAndFinishWithErrors()
        {
            dynamic function = Decorated(NewDecorator(), "", "    raise ValueError('bad value')");
            Assert.That(function(), Is.Null);
            string file = FileText();
            Assert.That(file, Does.Contain("Error raised in _decorated function. ValueError: bad value"));
            Assert.That(file, Does.Contain("Traceback (most recent call last)"));
            Assert.That(file, Does.Contain("Finished function _decorated with errors."));
            Assert.That(string.Join("\n", ConsoleLines()), Does.Contain("Error raised in _decorated function"), "errors go to the console by default");
        }

        [Test]
        public void Decorator_ExceptionNotSuppressed_IsRaisedAgain_AndTheFinishLineSaysWithErrors()
        {
            dynamic function = Decorated(NewDecorator(suppressExceptions: false), "", "    raise ValueError('bad value')");
            var raised = Assert.Throws<IronPython.Runtime.Exceptions.ValueErrorException>(() => function());
            Assert.That(raised!.Message, Is.EqualTo("bad value"));
            string file = FileText();
            Assert.That(file, Does.Contain("Error raised in _decorated function"));
            Assert.That(file, Does.Contain("Finished function _decorated with errors."));
        }

        [Test]
        public void Decorator_ErrorsNotInConsole_ErrorIsInTheFileOnly()
        {
            dynamic function = Decorated(NewDecorator(errorsInConsole: false), "", "    raise ValueError('quiet')");
            function();
            Assert.That(FileText(), Does.Contain("Error raised in _decorated function"));
            Assert.That(string.Join("\n", ConsoleLines()), Does.Not.Contain("Error raised"));
        }

        [Test]
        public void Decorator_RecordTime_LogsTheElapsedTime()
        {
            dynamic function = Decorated(NewDecorator(recordTime: true), "", "    return 'x'");
            Assert.That((string)function(), Is.EqualTo("x"));
            Assert.That(FileText(), Does.Match(@"Elapsed time for _decorated is : \d"));
        }

        [Test]
        public void Decorator_NoRecordTime_NoElapsedTime()
        {
            dynamic function = Decorated(NewDecorator(), "", "    return 'x'");
            function();
            Assert.That(FileText(), Does.Not.Contain("Elapsed time"));
        }

        [Test]
        public void Decorator_LogLevel_AppliesDuringTheCallAndIsRestoredAfterwards()
        {
            PythonEngineManager.Scope.SetVariable("_seen", new PythonList());
            dynamic function = Decorated(NewDecorator(), "", "    _seen.append((_lo.file_handler.level, _lo.console_handler.level, _lo.new_logger.level))\n    return 1", "log_level=(20, 40)");
            function();
            dynamic seen = PythonEngineManager.Scope.GetVariable("_seen");
            Assert.That(((IEnumerable<object>)seen[0]).Select(Convert.ToInt32), Is.EqualTo(new[] { 20, 40, 20 }), "file, console and logger level during the call");
            Assert.That((int)loggerObject.file_handler.level, Is.EqualTo(10));
            Assert.That((int)loggerObject.console_handler.level, Is.EqualTo(30));
            Assert.That((int)loggerObject.new_logger.level, Is.EqualTo(10));
            Assert.That(FileText(), Does.Contain("Updated log levels to (20, 40)"));
        }

        [Test]
        public void Decorator_LevelsRestoredAlsoWhenTheFunctionFails()
        {
            dynamic function = Decorated(NewDecorator(), "", "    raise ValueError('x')", "log_level=(20, 40)");
            function();
            Assert.That((int)loggerObject.file_handler.level, Is.EqualTo(10));
            Assert.That((int)loggerObject.console_handler.level, Is.EqualTo(30));
        }

        [Test]
        public void Decorator_SameLevelsAsTheLogger_NoLevelChangeLogged()
        {
            dynamic function = Decorated(NewDecorator(), "", "    return 1");
            function();
            Assert.That(FileText(), Does.Not.Contain("Updated log levels"));
        }

        [Test]
        public void Decorator_NestedCalls_EachRestoresTheLevelsOfItsCaller()
        {
            PythonEngineManager.Scope.SetVariable("_levels_seen", new PythonList());
            dynamic addLogger = NewDecorator();
            PythonEngineManager.Scope.SetVariable("_add_logger", addLogger);
            PythonEngineManager.Scope.SetVariable("_lo", loggerObject);
            PythonEngineManager.PythonEngine.Execute(@"
@_add_logger(log_level=(10, 10))
def _inner():
    _levels_seen.append(('inner', _lo.console_handler.level))

@_add_logger(log_level=(20, 40))
def _outer():
    _levels_seen.append(('outer before', _lo.console_handler.level))
    _inner()
    _levels_seen.append(('outer after', _lo.console_handler.level))

_outer()
", PythonEngineManager.Scope);
            dynamic seen = PythonEngineManager.Scope.GetVariable("_levels_seen");
            Assert.That(((IEnumerable<object>)seen).Select(t => $"{((dynamic)t)[0]}={((dynamic)t)[1]}"), Is.EqualTo(new[] { "outer before=40", "inner=10", "outer after=40" }));
            Assert.That((int)loggerObject.console_handler.level, Is.EqualTo(30));
        }
    }
}
