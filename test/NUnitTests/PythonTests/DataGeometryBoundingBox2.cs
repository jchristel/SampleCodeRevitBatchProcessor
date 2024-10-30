using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class DataGeometryBoundingBox2
    {
        dynamic dataBoundingBox2Class;
        dynamic point2Class;

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

            // set path to data geometry base
            var pythonFilePath_dataGeometryBoundingBox2 = Path.Combine(repoPath, @"duHast\Data\Objects\Properties\Geometry\geometry_bounding_box_2.py");

            // set path to point2 class
            var pythonFilePath_point2 = Path.Combine(repoPath, @"duHast\Geometry\point_2.py");

            //run the file
            engine.ExecuteFile(pythonFilePath_point2, _scope);            //run the file
            engine.ExecuteFile(pythonFilePath_dataGeometryBoundingBox2, _scope);

            dataBoundingBox2Class = _scope.GetVariable("DataBoundingBox2");
            point2Class = _scope.GetVariable("Point2");
            
            //store the engine instance
            _engine = engine;
        }

        [Test]
        public void Constructor_WithValidJson_ShouldSetBoundingBox()
        {
            // Arrange
            string json = @"
            {
                ""bounding_box"": {
                    ""point1"": { ""x"": 1.1, ""y"": 2.2 },
                    ""point2"": { ""x"": 3.3, ""y"": 4.4 }
                }
            }";

            // Act
            dynamic instance = dataBoundingBox2Class(json);

            // Assert
            Assert.AreEqual(1.1, instance.bounding_box.min_x);
            Assert.AreEqual(2.2, instance.bounding_box.min_y);
            Assert.AreEqual(3.3, instance.bounding_box.max_x);
            Assert.AreEqual(4.4, instance.bounding_box.max_y);
        }

        [Test]
        public void Constructor_WithInvalidJson_ShouldUseDefaultBoundingBox()
        {
            // Arrange
            string invalidJson = @"{ ""invalid_key"": {} }";

            // Act
            dynamic instance = dataBoundingBox2Class(invalidJson);

            // Assert - Default bounding box points should be 0.0, 0.0
            Assert.AreEqual(0.0, instance.bounding_box.min_x);
            Assert.AreEqual(0.0, instance.bounding_box.min_y);
            Assert.AreEqual(0.0, instance.bounding_box.max_x);
            Assert.AreEqual(0.0, instance.bounding_box.max_y);
        }

        [Test]
        public void Constructor_WithNonDictionaryJson_ShouldThrowTypeError()
        {
            // Arrange
            string invalidJson = "[1, 2, 3]";

            // Act & Assert
            var ex = Assert.Throws<AttributeErrorException>(() => dataBoundingBox2Class(invalidJson));
            Assert.That(ex.Message, Does.Contain("Node bounding box 2 failed to initialise with: 'list' object has no attribute 'get'"));
        }

        [Test]
        public void SetBoundingBoxByPoints_WithValidPoints_ShouldUpdateBoundingBox()
        {
            // Arrange
            dynamic instance = dataBoundingBox2Class();
            dynamic minPoint = point2Class(5.5, 6.6);
            dynamic maxPoint = point2Class(7.7, 8.8);

            // Act
            instance.set_bounding_box_by_points(minPoint, maxPoint);

            // Assert
            Assert.AreEqual(5.5, instance.bounding_box.min_x);
            Assert.AreEqual(6.6, instance.bounding_box.min_y);
            Assert.AreEqual(7.7, instance.bounding_box.max_x);
            Assert.AreEqual(8.8, instance.bounding_box.max_y);
        }

        [Test]
        public void SetBoundingBoxByPoints_WithInvalidMin_ShouldThrowValueError()
        {
            // Arrange
            dynamic instance = dataBoundingBox2Class();
            dynamic maxPoint = point2Class(7.7, 8.8);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => instance.set_bounding_box_by_points("invalid", maxPoint));
            Assert.That(ex.Message, Does.Contain("Min needs to be a point2 instance"));
        }

        [Test]
        public void SetBoundingBoxByPoints_WithInvalidMax_ShouldThrowValueError()
        {
            // Arrange
            dynamic instance = dataBoundingBox2Class();
            dynamic minPoint = point2Class(5.5, 6.6);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => instance.set_bounding_box_by_points(minPoint, "invalid"));
            Assert.That(ex.Message, Does.Contain("Max needs to be a point2 instance"));
        }
    }
}
