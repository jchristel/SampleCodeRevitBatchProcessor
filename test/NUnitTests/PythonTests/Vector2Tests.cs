using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using IronPython.Runtime;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class Vector2Tests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to point2 class
            var pythonFilePath = Path.Combine(repoPath, @"duHast\Geometry\vector_2.py");

            //run the file
            engine.ExecuteFile(pythonFilePath, _scope);

            //store the engine instance
            _engine = engine;

        }

        [Test]
        public void Vector2_TestToJson()
        {
            // set up a point2 instance
            dynamic vector2Instance = _scope.GetVariable("Vector2")(0.0, 0.0);

            var result = vector2Instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0], \"x\": 0.0, \"y\": 0.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Vector2_TestToJsonUtf()
        {
            // set up a point2 instance
            dynamic vector2Instance = _scope.GetVariable("Vector2")(0.0, 0.0);

            var result = vector2Instance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0], \"x\": 0.0, \"y\": 0.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Vector2_Initialization_SetsComponents()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(3.0, 4.0);

            Assert.AreEqual(3.0, vector.x);
            Assert.AreEqual(4.0, vector.y);
        }

        [Test]
        public void Vector2_Constructor_InvalidType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() =>
                _scope.GetVariable("Vector2")("1.0", "2.0")
            );

            Assert.That(ex.Message, Does.Contain("All components must be of type float or int"));
        }

        [Test]
        public void Vector2_Addition_ReturnsNewVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector1 = Vector2(1.0, 2.0);
            var vector2 = Vector2(3.0, 4.0);

            var result = vector1 + vector2;

            Assert.AreEqual(4.0, result.x);
            Assert.AreEqual(6.0, result.y);
        }

        // Helper method to perform the addition
        private dynamic AddVector(dynamic vector, dynamic other)
        {
            return vector + other;
        }

        [Test]
        public void Vector2_Addition_WithNonVector_ThrowsTypeError()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(1.0, 2.0);
            var ex = Assert.Throws<TypeErrorException>(() => AddVector(vector, "not a vector"));

            Assert.IsTrue(ex.Message.Contains("Expected vector, got: str"));
        }

        [Test]
        public void Vector2_RightAddition_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = _scope.GetVariable("Vector2")(1.0, 2.0);

            // Create a Python-compatible list using PythonList since that is what __radd__ expects
            var pythonList = new PythonList { 4.0, 5.0};

            var result = vector.__radd__(pythonList);
            Assert.AreEqual(5.0, result.x);
            Assert.AreEqual(7.0, result.y);
        }

        [Test]
        public void Vector2_Subtraction_ReturnsNewVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector1 = Vector2(5.0, 3.0);
            var vector2 = Vector2(2.0, 1.0);

            var result = vector1 - vector2;

            Assert.AreEqual(3.0, result.x);
            Assert.AreEqual(2.0, result.y);
        }

        // Helper method to perform the addition
        private dynamic SubVector(dynamic vector, dynamic other)
        {
            return vector - other;
        }

        [Test]
        public void Vector2_Subtraction_WithNonVector_ThrowsNotImplemented()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(1.0, 2.0);

            var ex = Assert.Throws<Microsoft.CSharp.RuntimeBinder.RuntimeBinderException>(() => SubVector(vector, "not a vector"));
            Assert.IsTrue(ex.Message.Contains("Operator '-' cannot be applied"));
        }

        [Test]
        public void Vector2_RightSubtraction_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = _scope.GetVariable("Vector2")(1.0, 2.0);
            var pythonList = new PythonList { 4.0, 5.0};
            var result = vector.__rsub__(pythonList);

            Assert.AreEqual(3.0, result.x);
            Assert.AreEqual(3.0, result.y);
        }

        [Test]
        public void Vector2_Multiplication_Scalar_ReturnsNewVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(2.0, 3.0);

            var result = vector * 2.0;

            Assert.AreEqual(4.0, result.x);
            Assert.AreEqual(6.0, result.y);
        }

        [Test]
        public void Vector2_Division_Scalar_ReturnsNewVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(6.0, 3.0);

            var result = vector / 3.0;

            Assert.AreEqual(2.0, result.x);
            Assert.AreEqual(1.0, result.y);
        }

        [Test]
        public void Vector2_StringRepresentation_ReturnsCorrectFormat()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(1.0, 2.0);

            // Call the __str__ method directly
            var str = vector.__str__();

            Assert.AreEqual("Vector2D(1.0, 2.0)", str);
        }

        [Test]
        public void Vector2_Magnitude_ReturnsCorrectValue()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(3.0, 4.0);

            var magnitude = vector.magnitude();

            Assert.AreEqual(5.0, magnitude, 1e-9); // Using a tolerance for floating point comparison
        }

        [Test]
        public void Vector2_ScalarMultiplication_ReturnsNewVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(2.0, 3.0);

            var result = vector * 2.0; // Testing __mul__

            Assert.AreEqual(4.0, result.x);
            Assert.AreEqual(6.0, result.y);
        }

        [Test]
        public void Vector2_ScalarMultiplication_Reversed_ReturnsNewVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(2.0, 3.0);

            var result = vector.__rmul__(2.0);//2.0 * vector; // Testing __rmul__

            Assert.AreEqual(4.0, result.x);
            Assert.AreEqual(6.0, result.y);
        }

        [Test]
        public void Vector2_Negation_ReturnsCorrectVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(2.0, 3.0);

            var result = -vector; // Testing __neg__

            Assert.AreEqual(-2.0, result.x);
            Assert.AreEqual(-3.0, result.y);
        }

        [Test]
        public void Vector2_Positive_ReturnsSameVector()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(2.0, 3.0);

            var result = +vector; // Testing __pos__

            Assert.AreEqual(2.0, result.x);
            Assert.AreEqual(3.0, result.y);
        }

        [Test]
        public void Vector2_Absolute_ReturnsMagnitude()
        {
            dynamic Vector2 = _scope.GetVariable("Vector2");
            var vector = Vector2(3.0, 4.0);

            var magnitude = vector.__abs__();// Math.Abs(vector); // Testing __abs__

            Assert.AreEqual(5.0, magnitude, 1e-9); // Using a tolerance for floating point comparison
        }
    }
}
