using IronPython.Runtime;
using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class Vector2Tests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.Vector2Class, Is.Not.Null, "Vector2Class should be loaded.");
        }

        [Test]
        public void Vector2_TestToJson()
        {
            // set up a point2 instance
            dynamic vector2Instance = PythonEngineManager.Vector2Class(0.0, 0.0);

            var result = vector2Instance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0], \"x\": 0.0, \"y\": 0.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Vector2_TestToJsonUtf()
        {
            // set up a point2 instance
            dynamic vector2Instance = PythonEngineManager.Vector2Class(0.0, 0.0);

            var result = vector2Instance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"components\": [0.0, 0.0], \"x\": 0.0, \"y\": 0.0}";

            Assert.That(jsonString, Is.EqualTo(result));
        }

        [Test]
        public void Vector2_Initialization_SetsComponents()
        {
            dynamic vector = PythonEngineManager.Vector2Class(3.0, 4.0);
           
            Assert.That(3.0, Is.EqualTo(vector.x));
            Assert.That(4.0, Is.EqualTo(vector.y));
        }

        [Test]
        public void Vector2_Constructor_InvalidType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() =>
                PythonEngineManager.Vector2Class("1.0", "2.0")
            );

            Assert.That(ex.Message, Does.Contain("All components must be of type float or int"));
        }

        [Test]
        public void Vector2_Addition_ReturnsNewVector()
        {
            dynamic vector1 = PythonEngineManager.Vector2Class(1.0, 2.0);
            dynamic vector2 = PythonEngineManager.Vector2Class(3.0, 4.0);

            var result = vector1 + vector2;

            Assert.That(4.0, Is.EqualTo(result.x));
            Assert.That(6.0, Is.EqualTo(result.y));
        }

        // Helper method to perform the addition
        private dynamic AddVector(dynamic vector, dynamic other)
        {
            return vector + other;
        }

        [Test]
        public void Vector2_Addition_WithNonVector_ThrowsTypeError()
        {
            dynamic vector = PythonEngineManager.Vector2Class(1.0, 2.0);
            var ex = Assert.Throws<TypeErrorException>(() => AddVector(vector, "not a vector"));

            Assert.That(ex.Message, Does.Contain("Expected vector, got: str"));
        }

        [Test]
        public void Vector2_RightAddition_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(1.0, 2.0);

            // Create a Python-compatible list using PythonList since that is what __radd__ expects
            var pythonList = new PythonList { 4.0, 5.0};

            var result = vector.__radd__(pythonList);
            Assert.That(5.0, Is.EqualTo(result.x));
            Assert.That(7.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_Subtraction_ReturnsNewVector()
        {
            dynamic vector1 = PythonEngineManager.Vector2Class(5.0, 3.0);
            dynamic vector2 = PythonEngineManager.Vector2Class(2.0, 1.0);
            
            var result = vector1 - vector2;

            Assert.That(3.0, Is.EqualTo(result.x));
            Assert.That(2.0, Is.EqualTo(result.y));
        }

        // Helper method to perform the addition
        private dynamic SubVector(dynamic vector, dynamic other)
        {
            return vector - other;
        }

        [Test]
        public void Vector2_Subtraction_WithNonVector_ThrowsNotImplemented()
        {
            dynamic vector = PythonEngineManager.Vector2Class(1.0, 2.0);

            var ex = Assert.Throws<Microsoft.CSharp.RuntimeBinder.RuntimeBinderException>(() => SubVector(vector, "not a vector"));
            Assert.That(ex.Message, Does.Contain("Operator '-' cannot be applied"));
        }

        [Test]
        public void Vector2_RightSubtraction_WithTuple_ShouldReturnNewVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(1.0, 2.0);
            var pythonList = new PythonList { 4.0, 5.0};
            var result = vector.__rsub__(pythonList);

            Assert.That(3.0, Is.EqualTo(result.x));
            Assert.That(3.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_Multiplication_Scalar_ReturnsNewVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(2.0, 3.0);
            var result = vector * 2.0;

            Assert.That(4.0, Is.EqualTo(result.x));
            Assert.That(6.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_Division_Scalar_ReturnsNewVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(6.0, 3.0);
            var result = vector / 3.0;

            Assert.That(2.0, Is.EqualTo(result.x));
            Assert.That(1.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_StringRepresentation_ReturnsCorrectFormat()
        {
            dynamic vector = PythonEngineManager.Vector2Class(1.0, 2.0);
            // Call the __str__ method directly
            var str = vector.__str__();

            Assert.That("Vector2D(1.0, 2.0)", Is.EqualTo(str));
        }

        [Test]
        public void Vector2_Magnitude_ReturnsCorrectValue()
        {
            dynamic vector = PythonEngineManager.Vector2Class(3.0, 4.0);
            var magnitude = vector.magnitude();

            Assert.That(5.0,Is.EqualTo( magnitude), "1e-9"); // Using a tolerance for floating point comparison
        }

        [Test]
        public void Vector2_ScalarMultiplication_ReturnsNewVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(2.0, 3.0);
            var result = vector * 2.0; // Testing __mul__

            Assert.That(4.0, Is.EqualTo(result.x));
            Assert.That(6.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_ScalarMultiplication_Reversed_ReturnsNewVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(2.0, 3.0);
            var result = vector.__rmul__(2.0);//2.0 * vector; // Testing __rmul__

            Assert.That(4.0, Is.EqualTo(result.x));
            Assert.That(6.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_Negation_ReturnsCorrectVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(2.0, 3.0);
            var result = -vector; // Testing __neg__

            Assert.That(-2.0, Is.EqualTo(result.x));
            Assert.That(-3.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_Positive_ReturnsSameVector()
        {
            dynamic vector = PythonEngineManager.Vector2Class(2.0, 3.0);
            var result = +vector; // Testing __pos__

            Assert.That(2.0, Is.EqualTo(result.x));
            Assert.That(3.0, Is.EqualTo(result.y));
        }

        [Test]
        public void Vector2_Absolute_ReturnsMagnitude()
        {
            dynamic vector = PythonEngineManager.Vector2Class(3.0, 4.0);
            var magnitude = vector.__abs__();// Math.Abs(vector); // Testing __abs__

            Assert.That(5.0, Is.EqualTo(magnitude), "1e-9"); // Using a tolerance for floating point comparison
        }

        [Test]
        public void Vector2_Equality_SameComponents_ShouldBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.Vector2Class(1.0, 2.0);
            dynamic vector2 = PythonEngineManager.Vector2Class(1.0, 2.0);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.True, "Vector2 instances with the same components should be equal.");
        }

        [Test]
        public void Vector2_Equality_DifferentComponents_ShouldNotBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.Vector2Class(1.0, 2.0);
            dynamic vector2 = PythonEngineManager.Vector2Class(3.0, 4.0);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.False, "Vector2 instances with different components should not be equal.");
        }

        [Test]
        public void Vector2_Equality_WithVector3_ShouldNotBeEqual()
        {
            // Arrange
            dynamic vector2 = PythonEngineManager.Vector2Class(1.0, 2.0);
            dynamic vector3 = PythonEngineManager.Vector3Class(1.0, 2.0, 3.0);

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => { var result = vector2 == vector3; });
            Assert.That(ex.Message, Does.Contain("Expected vector2, got: Vector3"));
        }

        [Test]
        public void Vector2_Equality_WithCloseFloatingPoints_ShouldBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.Vector2Class(1.000000001, 2.000000002);
            dynamic vector2 = PythonEngineManager.Vector2Class(1.000000002, 2.000000001);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.True, "Vector2 instances with components close to each other should be considered equal.");
        }
    }
}
