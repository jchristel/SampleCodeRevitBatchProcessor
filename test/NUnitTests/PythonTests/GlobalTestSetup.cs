using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PythonTests.Setup;

namespace PythonTests
{
    [SetUpFixture]
    public class GlobalTestSetup
    {
        [OneTimeSetUp]
        public void GlobalSetup()
        {

            // Ensure the Python engine and scope are initialized
            var engine = PythonEngineManager.PythonEngine;
            var scope = PythonEngineManager.Scope;

            try
            {
                // geometry classes
                PythonEngineManager.BoundingBoxBaseClass = scope.GetVariable("BoundingBoxBase");
                PythonEngineManager.BoundingBox2Class = scope.GetVariable("BoundingBox2");
                PythonEngineManager.BoundingBox3Class = scope.GetVariable("BoundingBox3");
                PythonEngineManager.MatrixClass = scope.GetVariable("Matrix");
                PythonEngineManager.Point2Class = scope.GetVariable("Point2");
                PythonEngineManager.Point3Class = scope.GetVariable("Point3");
                PythonEngineManager.VectorBaseClass = scope.GetVariable("VectorBase");
                PythonEngineManager.Vector2Class = scope.GetVariable("Vector2");
                PythonEngineManager.Vector3Class = scope.GetVariable("Vector3");

                // data classes
                PythonEngineManager.DataBaseClass = scope.GetVariable("DataBase");
                PythonEngineManager.DataDesingSetOptionClass = scope.GetVariable("DataDesignSetOption");
                PythonEngineManager.DataElementGeometryBaseClass = scope.GetVariable("DataElementGeometryBase");
                PythonEngineManager.DataGeometryBaseClass = scope.GetVariable("DataGeometryBase");
                PythonEngineManager.DataGeometryBoundingBox2Class = scope.GetVariable("DataGeometryBoundingBox2");
                PythonEngineManager.DataInstancePropertiesClass = scope.GetVariable("DataInstanceProperties");
                PythonEngineManager.DataGeometryPolygon2Class = scope.GetVariable("DataGeometryPolygon2");
                PythonEngineManager.DataPropertyClass = scope.GetVariable("DataProperty");

            }
            catch (MissingMemberException ex)
            {
                Console.WriteLine("Error: Python class not found in scope - " + ex.Message);
                throw;
            }
        
    }

        [OneTimeTearDown]
        public void GlobalTeardown()
        {
            PythonEngineManager.Shutdown();
        }
    }
}
