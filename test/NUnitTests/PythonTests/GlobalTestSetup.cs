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
                PythonEngineManager.DataCeilingClass = scope.GetVariable("DataCeiling");
                PythonEngineManager.DataDoorClass = scope.GetVariable("DataDoor");
                PythonEngineManager.DataFamilyBaseClass = scope.GetVariable("DataFamilyBase");
                PythonEngineManager.DataLevelBuildingClass = scope.GetVariable("DataLevelBuilding");
                PythonEngineManager.DataRoomClass = scope.GetVariable("DataRoom");
                PythonEngineManager.DataSheetViewPortClass = scope.GetVariable("DataSheetViewPort");
                PythonEngineManager.DataSheetClass = scope.GetVariable("DataSheet");
                PythonEngineManager.DataTagClass = scope.GetVariable("DataTag");
                PythonEngineManager.DataViewThreeDClass = scope.GetVariable("DataViewThreeD");
                PythonEngineManager.DataViewBaseClass = scope.GetVariable("DataViewBase");
                PythonEngineManager.DataViewElevationClass = scope.GetVariable("DataViewElevation");
                PythonEngineManager.DataViewPlanClass = scope.GetVariable("DataViewPlan");
                PythonEngineManager.DataViewScheduleClass = scope.GetVariable("DataViewSchedule");

                //data properties
                PythonEngineManager.DataDesingSetOptionClass = scope.GetVariable("DataDesignSetOption");
                PythonEngineManager.DataElementGeometryBaseClass = scope.GetVariable("DataElementGeometryBase");
                PythonEngineManager.DataInstancePropertiesClass = scope.GetVariable("DataInstanceProperties");
                PythonEngineManager.DataLevelBaseClass = scope.GetVariable("DataLevelBase");
                PythonEngineManager.DataLevelClass = scope.GetVariable("DataLevel");
                PythonEngineManager.DataPhasingClass = scope.GetVariable("DataPhasing");
                PythonEngineManager.DataPropertyNamesClass = scope.GetVariable("DataPropertyNames");
                PythonEngineManager.DataRevitModelClass = scope.GetVariable("DataRevitModel");
                PythonEngineManager.DataScheduleSegmentClass = scope.GetVariable("DataScheduleSegment");
                PythonEngineManager.DataTypePropertiesClass = scope.GetVariable("DataTypeProperties");
                PythonEngineManager.DataPropertyClass = scope.GetVariable("DataProperty");
                PythonEngineManager.DataViewPortTypeNames = scope.GetVariable("DataViewPortTypeNames");

                //data properties -- geometry
                PythonEngineManager.DataGeometryBaseClass = scope.GetVariable("DataGeometryBase");
                PythonEngineManager.DataGeometryBoundingBox2Class = scope.GetVariable("DataGeometryBoundingBox2");
                PythonEngineManager.DataGeometryPolygon2Class = scope.GetVariable("DataGeometryPolygon2");

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
