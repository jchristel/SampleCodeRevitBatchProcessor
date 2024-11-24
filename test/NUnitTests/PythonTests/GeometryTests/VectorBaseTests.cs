using PythonTests.Setup;
using IronPython.Runtime.Exceptions;

namespace PythonTests.GeometryTests
{
    public class VectorBaseTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.VectorBaseClass, Is.Not.Null, "VectorBaseClass should be loaded.");
        }

        [Test]
        public void Constructor_ShouldInitializeWithValidComponents()
        {
            // Arrange
            var components = new object[] { 3.0, 4.0 };

            // Act
            dynamic vector = PythonEngineManager.VectorBaseClass(components);

            // Assert
            Assert.That(vector, Is.Not.Null);
            Assert.That(2, Is.EqualTo(vector.components.Count));
            Assert.That(3.0,Is.EqualTo( vector.components[0]));
            Assert.That(4.0, Is.EqualTo(vector.components[1]));
        }

        [Test]
        public void Constructor_ShouldThrowTypeErrorForInvalidComponent()
        {
            // Arrange
            var invalidComponent = new object[] { 3.0, "invalid" };

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.VectorBaseClass(invalidComponent));
            Assert.That(ex.Message, Does.Contain("All components must be of type float or int,"));
        }

        [Test]
        public void Magnitude_ShouldReturnCorrectValue()
        {
            // Arrange
            var components = new object[] { 3.0, 4.0 };
            dynamic vector = PythonEngineManager.VectorBaseClass(components);

            // Act
            double magnitude = vector.magnitude();

            // Assert
            Assert.That(magnitude, Is.EqualTo(5.0).Within(0.001));
        }

        [Test]
        public void CheckDimensionCompatibility_ShouldThrowIncompatibleVectorDimensionsException()
        {
            // Arrange
            var components1 = new object[] { 1.0, 2.0, 3.0 };
            var components2 = new object[] { 1.0, 2.0 };
            dynamic vector1 = PythonEngineManager.VectorBaseClass(components1);
            dynamic vector2 = PythonEngineManager.VectorBaseClass(components2);

            // Act & Assert
            var ex = Assert.Throws<Exception>(() => vector1._check_dimension_compatibility(vector2));
            Assert.That(ex.Message, Does.Contain("Dimension mismatch: 3 vs 2"));
        }

        [Test]
        public void Negation_ShouldReturnNegativeVector()
        {
            // Arrange
            var components = new object[] { 1.0, -2.0, 3.0 };
            dynamic vector = PythonEngineManager.VectorBaseClass(components);

            // Act
            // Act & Assert
            var ex = Assert.Throws<System.NotImplementedException>(() => { var negated = -vector; });
            Assert.That(ex.Message, Does.Contain("Negation is not implemented in VectorBase"));

        }

        [Test]
        public void MagnitudeOfZeroVector_ShouldReturnZero()
        {
            // Arrange
            var components = new object[] { 0.0, 0.0, 0.0 };
            dynamic vector = PythonEngineManager.VectorBaseClass(components);

            // Act
            double magnitude = vector.magnitude();

            // Assert
            Assert.That(magnitude, Is.EqualTo(0.0).Within(0.001));
        }

        [Test]
        public void StringRepresentation_ShouldReturnFormattedString()
        {
            // Arrange
            var components = new object[] { 1.0, 2.0, 3.0 };
            dynamic vector = PythonEngineManager.VectorBaseClass(components);

            // Act
            string vectorString = vector.__str__();

            // Assert
            Assert.That(vectorString, Is.EqualTo("Vector (1.0, 2.0, 3.0)"));
        }

        [Test]
        public void VectorBase_Equality_SameComponents_ShouldBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.VectorBaseClass(1.0, 2.0, 3.0);
            dynamic vector2 = PythonEngineManager.VectorBaseClass(1.0, 2.0, 3.0);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.True, "Vectors with the same components should be equal.");
        }

        [Test]
        public void VectorBase_Equality_DifferentComponents_ShouldNotBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.VectorBaseClass(1.0, 2.0, 3.0);
            dynamic vector2 = PythonEngineManager.VectorBaseClass(4.0, 5.0, 6.0);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.False, "Vectors with different components should not be equal.");
        }

        [Test]
        public void VectorBase_Equality_WithCloseFloatingPoints_ShouldBeEqual()
        {
            // Arrange
            dynamic vector1 = PythonEngineManager.VectorBaseClass(1.000000001, 2.000000002);
            dynamic vector2 = PythonEngineManager.VectorBaseClass(1.000000002, 2.000000001);

            // Act & Assert
            Assert.That(vector1 == vector2, Is.True, "VectorBase instances with components close to each other should be considered equal.");
        }

    }
}
