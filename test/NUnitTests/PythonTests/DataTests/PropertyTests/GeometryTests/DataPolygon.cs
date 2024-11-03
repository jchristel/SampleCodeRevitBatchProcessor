using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.DataTests.PropertyTests.GeometryTests
{
    public class DataPolygon
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataGeometryPolygon2Class, "DataPolygonClass should be loaded.");
            Assert.IsNotNull(PythonEngineManager.Point2Class, "Point2Class should be loaded.");
        }

        [Test]
        public void Constructor_WithValidJson_ShouldSetOuterAndInnerLoops()
        {
            // Arrange
            string json = @"{
            ""outer_loop"": [{""x"": 0.0, ""y"": 0.0}, {""x"": 1.0, ""y"": 1.0}, {""x"": 2.0, ""y"": 2.0}],
            ""inner_loops"": [
                [{""x"": 0.5, ""y"": 0.5}, {""x"": 1.5, ""y"": 1.5}, {""x"": 2.5, ""y"": 2.5}]
            ]
        }";
            dynamic instance = PythonEngineManager.DataGeometryPolygon2Class(json);

            // Act & Assert for outer loop
            Assert.AreEqual(3, instance.outer_loop.Count);
            Assert.AreEqual(0.0, instance.outer_loop[0].x);
            Assert.AreEqual(2.0, instance.outer_loop[2].y);

            // Act & Assert for inner loops
            Assert.AreEqual(1, instance.inner_loops.Count);
            Assert.AreEqual(3, instance.inner_loops[0].Count);
            Assert.AreEqual(1.5, instance.inner_loops[0][1].x);
            Assert.AreEqual(1.5, instance.inner_loops[0][1].y);
        }

        [Test]
        public void Constructor_WithInvalidOuterLoop_ShouldThrowValueError()
        {
            // Arrange - not enough points for a valid polygon
            string json = @"{
            ""outer_loop"": [{""x"": 0.0, ""y"": 0.0}, {""x"": 1.0, ""y"": 1.0}]
        }";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataGeometryPolygon2Class(json));
            Assert.That(ex.Message, Does.Contain("outer loop data needs to contain at least 3 points"));
        }

        [Test]
        public void Constructor_WithoutOuterLoop_ShouldThrowValueError()
        {
            // Arrange - missing the outer loop data entirely
            string json = @"{ ""inner_loops"": [] }";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataGeometryPolygon2Class(json));
            Assert.That(ex.Message, Does.Contain("Json did not contain any outer loop data"));
        }

        [Test]
        public void Constructor_WithEmptyJson_ShouldThrowValueError()
        {
            // Arrange - empty JSON object
            string json = @"{}";

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.DataGeometryPolygon2Class(json));
            Assert.That(ex.Message, Does.Contain("Json did not contain any outer loop data"));
        }

        [Test]
        public void Constructor_WithValidOuterLoopAndNoInnerLoop_ShouldInitializeCorrectly()
        {
            // Arrange - valid outer loop with no inner loops
            string json = @"{
            ""outer_loop"": [{""x"": 1.0, ""y"": 1.0}, {""x"": 2.0, ""y"": 2.0}, {""x"": 3.0, ""y"": 3.0}]
        }";
            dynamic instance = PythonEngineManager.DataGeometryPolygon2Class(json);

            // Act & Assert for outer loop
            Assert.AreEqual(3, instance.outer_loop.Count);
            Assert.AreEqual(3.0, instance.outer_loop[2].x);
            Assert.AreEqual(3.0, instance.outer_loop[2].y);

            // Act & Assert for inner loops
            Assert.AreEqual(0, instance.inner_loops.Count); // Should be empty as no inner loops were provided
        }

        [Test]
        public void Constructor_WithValidNestedInnerLoops_ShouldInitializeCorrectly()
        {
            // Arrange - outer loop and two sets of inner loops
            string json = @"{
            ""outer_loop"": [{""x"": 0.0, ""y"": 0.0}, {""x"": 2.0, ""y"": 2.0}, {""x"": 4.0, ""y"": 4.0}],
            ""inner_loops"": [
                [{""x"": 1.0, ""y"": 1.0}, {""x"": 2.0, ""y"": 2.0}, {""x"": 3.0, ""y"": 3.0}],
                [{""x"": 5.0, ""y"": 5.0}, {""x"": 6.0, ""y"": 6.0}, {""x"": 7.0, ""y"": 7.0}]
            ]
        }";
            dynamic instance = PythonEngineManager.DataGeometryPolygon2Class(json);

            // Act & Assert for outer loop
            Assert.AreEqual(3, instance.outer_loop.Count);
            Assert.AreEqual(4.0, instance.outer_loop[2].x);
            Assert.AreEqual(4.0, instance.outer_loop[2].y);

            // Act & Assert for inner loops
            Assert.AreEqual(2, instance.inner_loops.Count);
            Assert.AreEqual(3, instance.inner_loops[0].Count);
            Assert.AreEqual(3.0, instance.inner_loops[0][2].x);
            Assert.AreEqual(7.0, instance.inner_loops[1][2].y);
        }


        [Test]
        public void AddPointToOuterLoop_ShouldAddPointToOuterLoop()
        {
            // Arrange
            dynamic polygon = PythonEngineManager.DataGeometryPolygon2Class();
            dynamic point = PythonEngineManager.Point2Class(1.0, 1.0);

            // Act
            polygon.add_point_to_outer_loop(point);

            // Assert
            Assert.AreEqual(1, polygon.outer_loop.Count);
            Assert.AreEqual(1.0, polygon.outer_loop[0].x);
            Assert.AreEqual(1.0, polygon.outer_loop[0].y);
        }

        [Test]
        public void AddPointToOuterLoop_ShouldThrowTypeError_WhenNotPoint2()
        {
            // Arrange
            dynamic polygon = PythonEngineManager.DataGeometryPolygon2Class();

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => polygon.add_point_to_outer_loop("NotAPoint"));
            StringAssert.Contains("Point must be an instance of Point2", ex.Message);
        }

        [Test]
        public void AddInnerLoop_ShouldAddLoopToInnerLoops()
        {
            // Arrange
            dynamic polygon = PythonEngineManager.DataGeometryPolygon2Class();
            dynamic point1 = PythonEngineManager.Point2Class(0.0, 0.0);
            dynamic point2 = PythonEngineManager.Point2Class(1.0, 1.0);
            dynamic point3 = PythonEngineManager.Point2Class(2.0, 2.0);
            
            // Create a Python list for the inner loop
            var innerLoop = new IronPython.Runtime.PythonList { point1, point2, point3 };

            // Act
            polygon.add_inner_loop(innerLoop);

            // Assert
            Assert.AreEqual(1, polygon.inner_loops.Count);
            Assert.AreEqual(3, polygon.inner_loops[0].Count);
            Assert.AreEqual(0.0, polygon.inner_loops[0][0].x);
            Assert.AreEqual(1.0, polygon.inner_loops[0][1].x);
            Assert.AreEqual(2.0, polygon.inner_loops[0][2].x);
        }

        [Test]
        public void AddInnerLoop_ShouldThrowValueError_WhenLoopHasLessThanThreePoints()
        {
            // Arrange
            dynamic polygon = PythonEngineManager.DataGeometryPolygon2Class();
            dynamic point1 = PythonEngineManager.Point2Class(0.0, 0.0);
            dynamic point2 = PythonEngineManager.Point2Class(1.0, 1.0);
            var innerLoop = new IronPython.Runtime.PythonList { point1, point2 };

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => polygon.add_inner_loop(innerLoop));
            StringAssert.Contains("An inner loop must contain at least 3 points", ex.Message);
        }

        [Test]
        public void AddInnerLoop_ShouldThrowTypeError_WhenNonPointInLoop()
        {
            // Arrange
            dynamic polygon = PythonEngineManager.DataGeometryPolygon2Class();
            dynamic point1 = PythonEngineManager.Point2Class(0.0, 0.0);
            var innerLoop = new IronPython.Runtime.PythonList { point1, "NotAPoint", point1 };

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => polygon.add_inner_loop(innerLoop));
            StringAssert.Contains("All points in the loop must be instances of Point2", ex.Message);
        }
    }
}
