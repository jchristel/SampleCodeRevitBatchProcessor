using IronPython.Runtime.Exceptions;
using PythonTests.Setup;
using Newtonsoft.Json;

namespace PythonTests.DataTests.PropertyTests.GeometryTests
{
    public class DataPolygon
    {

        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.DataGeometryPolygon2Class, Is.Not.Null, "DataPolygonClass should be loaded.");
            Assert.That(PythonEngineManager.Point2Class, Is.Not.Null, "Point2Class should be loaded.");
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
            Assert.That(3, Is.EqualTo(instance.outer_loop.Count));
            Assert.That(0.0, Is.EqualTo(instance.outer_loop[0].x));
            Assert.That(2.0, Is.EqualTo(instance.outer_loop[2].y));

            // Act & Assert for inner loops
            Assert.That(1, Is.EqualTo(instance.inner_loops.Count));
            Assert.That(3, Is.EqualTo(instance.inner_loops[0].Count));
            Assert.That(1.5, Is.EqualTo(instance.inner_loops[0][1].x));
            Assert.That(1.5, Is.EqualTo(instance.inner_loops[0][1].y));
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
            Assert.That(3, Is.EqualTo(instance.outer_loop.Count));
            Assert.That(3.0, Is.EqualTo(instance.outer_loop[2].x));
            Assert.That(3.0, Is.EqualTo(instance.outer_loop[2].y));

            // Act & Assert for inner loops
            Assert.That(0, Is.EqualTo(instance.inner_loops.Count)); // Should be empty as no inner loops were provided
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
            Assert.That(3, Is.EqualTo(instance.outer_loop.Count));
            Assert.That(4.0, Is.EqualTo(instance.outer_loop[2].x));
            Assert.That(4.0, Is.EqualTo(instance.outer_loop[2].y));

            // Act & Assert for inner loops
            Assert.That(2, Is.EqualTo(instance.inner_loops.Count));
            Assert.That(3, Is.EqualTo(instance.inner_loops[0].Count));
            Assert.That(3.0, Is.EqualTo(instance.inner_loops[0][2].x));
            Assert.That(7.0, Is.EqualTo(instance.inner_loops[1][2].y));
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
            Assert.That(1, Is.EqualTo(polygon.outer_loop.Count));
            Assert.That(1.0, Is.EqualTo(polygon.outer_loop[0].x));
            Assert.That(1.0, Is.EqualTo(polygon.outer_loop[0].y));
        }

        [Test]
        public void AddPointToOuterLoop_ShouldThrowTypeError_WhenNotPoint2()
        {
            // Arrange
            dynamic polygon = PythonEngineManager.DataGeometryPolygon2Class();

            // Act & Assert
            var ex = Assert.Throws<TypeErrorException>(() => polygon.add_point_to_outer_loop("NotAPoint"));
            Assert.That(ex.Message, Does.Contain("Point must be an instance of Point2"));
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

            Console.WriteLine(polygon.to_json());
            // Assert
            Assert.That(1, Is.EqualTo(polygon.inner_loops.Count));
            Assert.That(3, Is.EqualTo(polygon.inner_loops[0].Count));
            Assert.That(0.0, Is.EqualTo(polygon.inner_loops[0][0].x));
            Assert.That(1.0, Is.EqualTo(polygon.inner_loops[0][1].x));
            Assert.That(2.0, Is.EqualTo(polygon.inner_loops[0][2].x));
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
            Assert.That(ex.Message, Does.Contain("An inner loop must contain at least 3 points"));
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
            Assert.That(ex.Message, Does.Contain("All points in the loop must be instances of Point2"));
        }

        [Test]
        public void EqualInstances_ShouldReturnTrue()
        {
            var jsonString = JsonConvert.SerializeObject(new
            {
                outer_loop = new[]
                {
                new { x = 0.0, y = 0.0 },
                new { x = 1.0, y = 0.0 },
                new { x = 1.0, y = 1.0 }
            },
                inner_loops = new[]
                {
                new[]
                {
                    new { x = 0.5, y = 0.5 },
                    new { x = 0.6, y = 0.5 },
                    new { x = 0.5, y = 0.6 }
                }
            }
            });

            

            var polygonA = PythonEngineManager.DataGeometryPolygon2Class(jsonString);
            var polygonB = PythonEngineManager.DataGeometryPolygon2Class(jsonString);

            Console.WriteLine(polygonA.to_json());

            Assert.That(polygonA == polygonB, Is.True, "Expected equal instances to return true.");
        }

        [Test]
        public void NotEqualInstances_ShouldReturnTrue()
        {
            var jsonStringA = JsonConvert.SerializeObject(new
            {
                outer_loop = new[]
                {
                new { x = 0.0, y = 0.0 },
                new { x = 1.0, y = 0.0 },
                new { x = 1.0, y = 1.0 }
            },
                inner_loops = new[]
                {
                new[]
                {
                    new { x = 0.5, y = 0.5 },
                    new { x = 0.6, y = 0.5 },
                    new { x = 0.5, y = 0.6 }
                }
            }
            });

            var jsonStringB = JsonConvert.SerializeObject(new
            {
                outer_loop = new[]
                {
                new { x = 0.0, y = 0.0 },
                new { x = 1.0, y = 0.0 },
                new { x = 2.0, y = 2.0 } // Different point for inequality
            },
                inner_loops = new[]
                {
                new[]
                {
                    new { x = 0.5, y = 0.5 },
                    new { x = 0.6, y = 0.5 },
                    new { x = 0.5, y = 0.6 }
                }
            }
            });

            Console.WriteLine($"jsonStringA: {jsonStringA}");
            Console.WriteLine($"jsonStringB: {jsonStringB}");

            var polygonA = PythonEngineManager.DataGeometryPolygon2Class(jsonStringA);
            var polygonB = PythonEngineManager.DataGeometryPolygon2Class(jsonStringB);

            Assert.That(polygonA != polygonB, Is.True, "Expected unequal instances to return true.");
        }

        [Test]
        public void EqualOperator_WithIdenticalPolygonData_ShouldReturnTrue()
        {
            var jsonString = JsonConvert.SerializeObject(new
            {
                outer_loop = new[]
                {
                new { x = 1.0, y = 1.0 },
                new { x = 2.0, y = 2.0 },
                new { x = 3.0, y = 3.0 }
            },
                inner_loops = new[]
                {
                new[]
                {
                    new { x = 1.5, y = 1.5 },
                    new { x = 1.6, y = 1.5 },
                    new { x = 1.5, y = 1.6 }
                }
            }
            });

            var polygonA = PythonEngineManager.DataGeometryPolygon2Class(jsonString);
            var polygonB = PythonEngineManager.DataGeometryPolygon2Class(jsonString);

            Assert.That(polygonA == polygonB, Is.True, "Expected '==' to return true for identical polygon data.");
        }

        [Test]
        public void NotEqualOperator_WithDifferentPolygonData_ShouldReturnTrue()
        {
            var jsonStringA = JsonConvert.SerializeObject(new
            {
                outer_loop = new[]
                {
                new { x = 1.0, y = 1.0 },
                new { x = 2.0, y = 2.0 },
                new { x = 3.0, y = 3.0 }
            },
                inner_loops = new[]
                {
                new[]
                {
                    new { x = 1.5, y = 1.5 },
                    new { x = 1.6, y = 1.5 },
                    new { x = 1.5, y = 1.6 }
                }
            }
            });

            var jsonStringB = JsonConvert.SerializeObject(new
            {
                outer_loop = new[]
                {
                new { x = 1.0, y = 1.0 },
                new { x = 2.0, y = 2.0 },
                new { x = 4.0, y = 4.0 } // Different point
            },
                inner_loops = new[]
                {
                new[]
                {
                    new { x = 1.5, y = 1.5 },
                    new { x = 1.6, y = 1.5 },
                    new { x = 1.5, y = 1.6 }
                }
            }
            });

            var polygonA = PythonEngineManager.DataGeometryPolygon2Class(jsonStringA);
            var polygonB = PythonEngineManager.DataGeometryPolygon2Class(jsonStringB);

            Assert.That(polygonA != polygonB, Is.True, "Expected '!=' to return true for different polygon data.");
        }
    }
}
