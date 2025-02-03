using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class ResultTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.ResultClass, Is.Not.Null, "Result should be loaded.");
        }

        [Test]
        public void Constructor_InitializesDefaultValues()
        {
            dynamic result = PythonEngineManager.ResultClass();
            Assert.That("-", Is.EqualTo(result.message));
            Assert.That(result.status, Is.True);
            Assert.That(result.result, Is.Empty);
        }

        [Test]
        public void AppendMessage_AppendsMessageCorrectly()
        {
            dynamic result = PythonEngineManager.ResultClass();
            result.append_message("First message");
            Assert.That("First message", Is.EqualTo(result.message));

            result.append_message("Second message");
            Assert.That("First message\nSecond message", Is.EqualTo(result.message));
        }

        [Test]
        public void Update_CombinesResultsCorrectly()
        {
            dynamic result1 = PythonEngineManager.ResultClass();
            dynamic result2 = PythonEngineManager.ResultClass();

            result1.append_message("Message 1");
            result2.append_message("Message 2");
            result2.status = false;
            result2.result.append("Result 1");

            result1.update(result2);

            Assert.That("Message 1\nMessage 2", Is.EqualTo(result1.message));
            Assert.That(1, Is.EqualTo(result1.result.Count));
            Assert.That("Result 1", Is.EqualTo(result1.result[0]));
            Assert.That(result1.status, Is.False);
        }

        [Test]
        public void Update_ThrowsTypeErrorIfNotResultInstance()
        {
            dynamic result = PythonEngineManager.ResultClass();

            var ex = Assert.Throws<TypeErrorException>(() =>
            {
                result.update("Not a Result");
            });
            Assert.That(ex.Message, Does.Contain("otherResult must be an instance of Result"));
        }

        [Test]
        public void UpdateSep_AppendsMessageAndUpdatesStatus()
        {
            dynamic result = PythonEngineManager.ResultClass();

            result.update_sep(false, "Update message");
            Console.WriteLine(result.message);
            Assert.That("Update message", Is.EqualTo(result.message), "message");
            Assert.That(result.status, Is.False);

            result.update_sep(true, "Another update");
            Assert.That("Update message\nAnother update", Is.EqualTo(result.message));
        }

        [Test]
        public void UpdateStatus_CombinesWithLogicalAnd()
        {
            dynamic result = PythonEngineManager.ResultClass();

            result.update_status(false);
            Assert.That(result.status, Is.False);

            result.update_status(true);
            Assert.That(result.status, Is.False);
        }
    }
}
