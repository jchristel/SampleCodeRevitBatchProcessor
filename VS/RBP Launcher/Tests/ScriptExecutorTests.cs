using NUnit.Framework;
using System.Collections.Generic;

namespace Tests
{
    [TestFixture]
    public class ScriptExecutorTests
    {
        [Test]
        public void ExecuteScript_WithValidFilePath_True()
        {
            // Get the directory where the test assembly is located
            var testDirectory = TestContext.CurrentContext.TestDirectory;

            // Construct the relative path to your Python script
            var scriptFilePath = Path.Combine(testDirectory, "PythonScripts", "empty.py");

            // Arrange
            var scriptExecutor = new RBP_Launcher.RunnerIronPython();
            //var scriptFilePath = "path/to/your/script.py"; // Replace with the actual path to your Python script

            // Act
            bool result = scriptExecutor.ExecuteScript(scriptFilePath);
            // Assertion to check is false
            Assert.That(result, Is.EqualTo(true), "Expected result was true");
        }

        [Test]
        public void ExecuteScript_WithInvalidFilePath_False()
        {
            // Get the directory where the test assembly is located
            var testDirectory = TestContext.CurrentContext.TestDirectory;
       
            // Construct the relative path to Python script
            var scriptFilePath = Path.Combine(testDirectory, "PythonScripts", "doesNotExist.py");

            // Arrange
            var scriptExecutor = new RBP_Launcher.RunnerIronPython();
           
            // Act
            bool result = scriptExecutor.ExecuteScript(scriptFilePath);
            // Assertion to check is false
            Assert.That(result, Is.EqualTo(false), "Expected result was false");
        }

        [Test]
        public void ExecuteScript_WithArguments_Success()
        {
            // Get the directory where the test assembly is located
            var testDirectory = TestContext.CurrentContext.TestDirectory;

            // Construct the relative path to Python script
            var scriptFilePath = Path.Combine(testDirectory, "PythonScripts", "no_args.py");

            // Arrange
            var scriptExecutor = new RBP_Launcher.RunnerIronPython();
            var scriptArguments = new List<string> { "arg1", "arg2" };

            // Act
            bool result = scriptExecutor.ExecuteScript(scriptFilePath, scriptArguments);
            // Assertion to check is true
            Assert.That(result, Is.EqualTo(true), "Expected result was true");
        }

        [Test]
        public void ExecuteScript_WithSingleArgument_Success()
        {
            // Get the directory where the test assembly is located
            var testDirectory = TestContext.CurrentContext.TestDirectory;

            // Construct the relative path to Python script
            var scriptFilePath = Path.Combine(testDirectory, "PythonScripts", "no_args.py");

            // Arrange
            var scriptExecutor = new RBP_Launcher.RunnerIronPython();
            var scriptArguments = new List<string> { "arg1"};

            // Act
            bool result = scriptExecutor.ExecuteScript(scriptFilePath, scriptArguments);
            // Assertion to check is true
            Assert.That(result, Is.EqualTo(true), "Expected result was true");
        }

        [Test]
        public void ExecuteScript_WithoutArguments_Success()
        {
            // Get the directory where the test assembly is located
            var testDirectory = TestContext.CurrentContext.TestDirectory;

            // Construct the relative path to Python script
            var scriptFilePath = Path.Combine(testDirectory, "PythonScripts", "no_args.py");

            // Arrange
            var scriptExecutor = new RBP_Launcher.RunnerIronPython();

            // Act
            bool result = scriptExecutor.ExecuteScript(scriptFilePath, null);
            // Assertion to check is false
            Assert.That(result, Is.EqualTo(false), "Expected result was false");
        }
    }
}
