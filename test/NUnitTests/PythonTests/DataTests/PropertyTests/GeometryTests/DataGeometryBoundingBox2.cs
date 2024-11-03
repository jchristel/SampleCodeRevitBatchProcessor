using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests
{
    public class DataGeometryBoundingBox2
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.DataGeometryBoundingBox2Class, "DataGeometryBoundingBox2 should be loaded.");
            Assert.IsNotNull(PythonEngineManager.Point2Class, "Point2Class should be loaded.");
        }

        [Test]
        public void Constructor_WithValidJson_ShouldSetBoundingBox()
        {
            // Arrange
            string json = @"{""bounding_box"":{ ""min_x"": 1.1, ""min_y"": 2.2, ""max_x"": 3.3, ""max_y"": 4.4 }}";

            // Act
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class(json);

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
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class(invalidJson);

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
            var ex = Assert.Throws<AttributeErrorException>(() => PythonEngineManager.DataGeometryBoundingBox2Class(invalidJson));
            Assert.That(ex.Message, Does.Contain("Node bounding box 2 failed to initialise with: 'list' object has no attribute 'get'"));
        }

        [Test]
        public void SetBoundingBoxByPoints_WithValidPoints_ShouldUpdateBoundingBox()
        {
            // Arrange
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic minPoint = PythonEngineManager.Point2Class(5.5, 6.6);
            dynamic maxPoint = PythonEngineManager.Point2Class(7.7, 8.8);

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
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic maxPoint = PythonEngineManager.Point2Class(7.7, 8.8);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => instance.set_bounding_box_by_points("invalid", maxPoint));
            Assert.That(ex.Message, Does.Contain("Min needs to be a point2 instance"));
        }

        [Test]
        public void SetBoundingBoxByPoints_WithInvalidMax_ShouldThrowValueError()
        {
            // Arrange
            dynamic instance = PythonEngineManager.DataGeometryBoundingBox2Class();
            dynamic minPoint = PythonEngineManager.Point2Class(5.5, 6.6);

            // Act & Assert
            var ex = Assert.Throws<ValueErrorException>(() => instance.set_bounding_box_by_points(minPoint, "invalid"));
            Assert.That(ex.Message, Does.Contain("Max needs to be a point2 instance"));
        }
    }
}
