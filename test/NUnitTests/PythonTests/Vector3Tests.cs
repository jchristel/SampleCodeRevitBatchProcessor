using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using IronPython.Runtime;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class Vector3Tests
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
            var pythonFilePath = Path.Combine(repoPath, @"duHast\Geometry\vector_3.py");

            //run the file
            engine.ExecuteFile(pythonFilePath, _scope);

            //store the engine instance
            _engine = engine;

        }

        [Test]
        public void Vector3_TestToJson()
        {
            // set up a point2 instance
            dynamic vector3Instance = _scope.GetVariable("Vector3")(0.0, 0.0, 0.0);

            var result = vector3Instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0, 0.0], \"x\": 0.0, \"y\": 0.0, \"z\": 0.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Vector3_TestToJsonUtf()
        {
            // set up a vector3 instance
            dynamic vector3Instance = _scope.GetVariable("Vector3")(0.0, 0.0, 0.0);

            var result = vector3Instance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0, 0.0], \"x\": 0.0, \"y\": 0.0, \"z\": 0.0}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Vector3_Initialization_SetsComponents()
        {
            dynamic Vector2 = _scope.GetVariable("Vector3");
            var vector = Vector2(3.0, 4.0, 5.0);

            Assert.AreEqual(3.0, vector.x);
            Assert.AreEqual(4.0, vector.y);
            Assert.AreEqual(5.0, vector.z);
        }

        [Test]
        public void Vector3_Constructor_InvalidType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() =>
                _scope.GetVariable("Vector3")("1.0", "2.0", "3.0")
            );

            Assert.That(ex.Message, Does.Contain("All components must be of type float or int"));
        }

        [Test]
        public void Vector3_Addition_TwoVectors_ShouldReturnNewVector()
        {
            dynamic vectorA = _scope.GetVariable("Vector3")(1.0, 2.0, 3.0);
            dynamic vectorB = _scope.GetVariable("Vector3")(4.0, 5.0, 6.0);
            dynamic result = vectorA + vectorB;

            Assert.AreEqual(5.0, result.x);
            Assert.AreEqual(7.0, result.y);
            Assert.AreEqual(9.0, result.z);
        }


        private dynamic addVectors(dynamic vector, dynamic other)
        {
            return vector + other;
        }
        [Test]
        public void Vector3_Addition_InvalidType_ShouldThrowTypeError()
        {
            dynamic vector = _scope.GetVariable("Vector3")(1.0, 2.0, 3.0);
            var ex = Assert.Throws<TypeErrorException>(() => addVectors(
                vector, "not a vector")
            );

            Assert.That(ex.Message, Does.Contain("Expected vector"));
        }

        [Test]
        public void Vector3_RightAddition_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = _scope.GetVariable("Vector3")(1.0, 2.0, 3.0);

            // Create a Python-compatible list using PythonList since that is what __radd__ expects
            var pythonList = new PythonList { 4.0, 5.0, 6.0 };

            // var result = new double[] { 4.0, 5.0, 6.0 } + vector;
            var result = vector.__radd__(pythonList);
            Assert.AreEqual(5.0, result.x);
            Assert.AreEqual(7.0, result.y);
            Assert.AreEqual(9.0, result.z);
        }

        [Test]
        public void Vector3_Subtraction_TwoVectors_ShouldReturnNewVector()
        {
            dynamic vectorA = _scope.GetVariable("Vector3")(4.0, 5.0, 6.0);
            dynamic vectorB = _scope.GetVariable("Vector3")(1.0, 2.0, 3.0);
            dynamic result = vectorA - vectorB;

            Assert.AreEqual(3.0, result.x);
            Assert.AreEqual(3.0, result.y);
            Assert.AreEqual(3.0, result.z);
        }

        [Test]
        public void Vector3_RightSubtraction_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = _scope.GetVariable("Vector3")(1.0, 2.0, 3.0);
            var pythonList = new PythonList { 4.0, 5.0, 6.0 };
            var result = vector.__rsub__(pythonList);

            Assert.AreEqual(3.0, result.x);
            Assert.AreEqual(3.0, result.y);
            Assert.AreEqual(3.0, result.z);
        }

        [Test]
        public void Vector3_ScalarMultiplication_ShouldReturnScaledVector()
        {
            dynamic vector = _scope.GetVariable("Vector3")(1.0, 2.0, 3.0);
            dynamic result = vector * 2.0;

            Assert.AreEqual(2.0, result.x);
            Assert.AreEqual(4.0, result.y);
            Assert.AreEqual(6.0, result.z);
        }

        [Test]
        public void Vector3_ScalarDivision_ShouldReturnScaledVector()
        {
            dynamic vector = _scope.GetVariable("Vector3")(2.0, 4.0, 6.0);
            dynamic result = vector / 2.0;

            Assert.AreEqual(1.0, result.x);
            Assert.AreEqual(2.0, result.y);
            Assert.AreEqual(3.0, result.z);
        }

        [Test]
        public void Vector3_ToString_ShouldReturnFormattedString()
        {
            dynamic vector = _scope.GetVariable("Vector3")(1.0, 2.0, 3.0);
            string result = vector.__str__();
            Assert.That(result, Is.EqualTo("Vector3D(1.0, 2.0, 3.0)"));
        }

    }

}