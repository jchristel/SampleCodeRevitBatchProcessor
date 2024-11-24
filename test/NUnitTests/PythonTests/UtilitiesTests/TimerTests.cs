using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.UtilitiesTests
{
    public class TimerTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.TimerClass,Is.Not.Null, "Timer should be loaded.");
        }

        [Test]
        public void Constructor_InitializesDefaultValues()
        {
            dynamic timer = PythonEngineManager.TimerClass();
            Assert.That(timer.is_running(), Is.False);
        }

        [Test]
        public void Start_StartsTimer()
        {
            dynamic timer = PythonEngineManager.TimerClass();
            timer.start();
            Assert.That(timer.is_running(), Is.True);
        }

        [Test]
        public void Stop_StopsTimerAndReturnsElapsedTime()
        {
            dynamic timer = PythonEngineManager.TimerClass();
            timer.start();
            System.Threading.Thread.Sleep(1000); // Sleep for 1 second to simulate elapsed time
            string elapsedTime = timer.stop();
            Assert.That(timer.is_running(), Is.False);
            Assert.That(elapsedTime, Does.Contain("Elapsed time: "));
        }

        [Test]
        public void Start_ThrowsTimerErrorIfAlreadyRunning()
        {
            dynamic timer = PythonEngineManager.TimerClass();
            timer.start();

            var ex = Assert.Throws<System.Exception>(() =>
            {
                timer.start();
            });
            Assert.That(ex.Message, Does.Contain("Timer is running. Use .stop() to stop it"));
        }

        [Test]
        public void Stop_ThrowsTimerErrorIfNotRunning()
        {
            dynamic timer = PythonEngineManager.TimerClass();

            var ex = Assert.Throws<System.Exception>(() =>
            {
                timer.stop();
            });

            Assert.That(ex.Message, Does.Contain("Timer is not running. Use .start() to start it"));
        }

        [Test]
        public void IsRunning_ReturnsCorrectStatus()
        {
            dynamic timer = PythonEngineManager.TimerClass();
            Assert.That(timer.is_running(), Is.False);

            timer.start();
            Assert.That(timer.is_running(), Is.True);

            timer.stop();
            Assert.That(timer.is_running(), Is.False);
        }
    }
}
