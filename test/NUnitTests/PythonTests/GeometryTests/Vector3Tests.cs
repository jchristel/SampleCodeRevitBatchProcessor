using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using IronPython.Runtime;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class Vector3Tests
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.Vector3Class, Is.Not.Null, "Vector3Class should be loaded.");
        }

        [Test]
        public void Vector3_TestToJson()
        {
            // set up a point2 instance
            dynamic vector3Instance = PythonEngineManager.Vector3Class(0.0, 0.0, 0.0);

            var result = vector3Instance.to_json_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0, 0.0], \"x\": 0.0, \"y\": 0.0, \"z\": 0.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Vector3_TestToJsonUtf()
        {
            // set up a vector3 instance
            dynamic vector3Instance = PythonEngineManager.Vector3Class(0.0, 0.0, 0.0);

            var result = vector3Instance.to_json_utf_ordered();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0, 0.0], \"x\": 0.0, \"y\": 0.0, \"z\": 0.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Vector3_Initialization_SetsComponents()
        {
            dynamic vector = PythonEngineManager.Vector3Class(3.0, 4.0, 5.0);
           
            Assert.That(3.0, Is.EqualTo(vector.x));
            Assert.That(4.0, Is.EqualTo(vector.y));
            Assert.That(5.0, Is.EqualTo(vector.z));
        }

        [Test]
        public void Vector3_Constructor_InvalidType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() =>
                PythonEngineManager.Vector3Class("1.0", "2.0", "3.0")
            );

            Assert.That(ex.Message, Does.Contain("All components must be of type float or int"));
        }

        [Test]
        public void Vector3_Addition_TwoVectors_ShouldReturnNewVector()
        {
            dynamic vectorA = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            dynamic vectorB = PythonEngineManager.Vector3Class(4.0, 5.0, 6.0);
            dynamic result = vectorA + vectorB;

            Assert.That(5.0, Is.EqualTo(result.x));
            Assert.That(7.0, Is.EqualTo(result.y));
            Assert.That(9.0, Is.EqualTo(result.z));
        }


        private dynamic addVectors(dynamic vector, dynamic other)
        {
            return vector + other;
        }
        [Test]
        public void Vector3_Addition_InvalidType_ShouldThrowTypeError()
        {
            dynamic vector = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            var ex = Assert.Throws<TypeErrorException>(() => addVectors(
                vector, "not a vector")
            );

            Assert.That(ex.Message, Does.Contain("Expected vector"));
        }

        [Test]
        public void Vector3_RightAddition_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);

            // Create a Python-compatible list using PythonList since that is what __radd__ expects
            var pythonList = new PythonList { 4.0, 5.0, 6.0 };

            // var result = new double[] { 4.0, 5.0, 6.0 } + vector;
            var result = vector.__radd__(pythonList);
            Assert.That(5.0, Is.EqualTo(result.x));
            Assert.That(7.0, Is.EqualTo(result.y));
            Assert.That(9.0, Is.EqualTo(result.z));
        }

        [Test]
        public void Vector3_Subtraction_TwoVectors_ShouldReturnNewVector()
        {
            dynamic vectorA = PythonEngineManager.Vector3Class(4.0, 5.0, 6.0);
            dynamic vectorB = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            dynamic result = vectorA - vectorB;

            Assert.That(3.0, Is.EqualTo(result.x));
            Assert.That(3.0, Is.EqualTo(result.y));
            Assert.That(3.0, Is.EqualTo(result.z));
        }

        [Test]
        public void Vector3_RightSubtraction_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            var pythonList = new PythonList { 4.0, 5.0, 6.0 };
            var result = vector.__rsub__(pythonList);

            Assert.That(3.0, Is.EqualTo(result.x));
            Assert.That(3.0, Is.EqualTo(result.y));
            Assert.That(3.0, Is.EqualTo(result.z));
        }

        [Test]
        public void Negation_ShouldNegateComponents_Vector3()
        {
            // Arrange
            dynamic vector = PythonEngineManager.Vector3Class(1.0, -2.0, 3.0);

            // Act
            dynamic negatedVector = -vector;

            // Assert
            Assert.That(-1.0, Is.EqualTo(negatedVector.x));
            Assert.That(2.0, Is.EqualTo(negatedVector.y));
            Assert.That(-3.0, Is.EqualTo(negatedVector.z));
        }

        [Test]
        public void Vector3_ScalarMultiplication_ShouldReturnScaledVector()
        {
            dynamic vector = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            dynamic result = vector * 2.0;

            Assert.That(2.0, Is.EqualTo(result.x));
            Assert.That(4.0, Is.EqualTo(result.y));
            Assert.That(6.0, Is.EqualTo(result.z));
        }

        [Test]
        public void Vector3_ScalarDivision_ShouldReturnScaledVector()
        {
            dynamic vector = PythonEngineManager.Vector3Class(2.0, 4.0, 6.0);
            dynamic result = vector / 2.0;

            Assert.That(1.0, Is.EqualTo(result.x));
            Assert.That(2.0, Is.EqualTo(result.y));
            Assert.That(3.0, Is.EqualTo(result.z));
        }

        [Test]
        public void Vector3_ToString_ShouldReturnFormattedString()
        {
            dynamic vector = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            string result = vector.__str__();
            Assert.That(result, Is.EqualTo("Vector3D(1.0, 2.0, 3.0)"));
        }

        [Test]
        public void Vector3_Equality_SameComponents_ShouldBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            dynamic vector2 = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.True, "Vector3 instances with the same components should be equal.");
        }

        [Test]
        public void Vector3_Equality_DifferentComponents_ShouldNotBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);
            dynamic vector2 = PythonEngineManager.Vector3Class(4.0, 5.0, 6.0);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.False, "Vector3 instances with different components should not be equal.");
        }

        [Test]
        public void Vector3_Equality_WithVector2_ShouldNotBeEqual()
        {
            // Arrange
            dynamic vector2 = PythonEngineManager.Vector2Class(1.0, 2.0);
            dynamic vector3 = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);

            // Act & Assert
            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => { var result = vector3 == vector2; });
            Assert.That(ex.Message, Does.Contain("Expected vector3, got: Vector2"));
        }

        public void Vector3_Equality_WithCloseFloatingPoints_ShouldBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.Vector3Class(1.000000001, 2.000000002, 3.000000003);
            dynamic vector2 = PythonEngineManager.Vector3Class(1.000000002, 2.000000001, 3.000000002);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.True, "Vector3 instances with components close to each other should be considered equal.");
        }

    }

}