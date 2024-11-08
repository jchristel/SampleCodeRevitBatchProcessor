using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests.Setup
{
    public static class PythonEngineManager
    {
        private static ScriptEngine _pythonEngine;
        private static ScriptScope _scope;

        public static dynamic BoundingBox2Class { get; set; }
        public static dynamic BoundingBox3Class { get; set; }
        public static dynamic BoundingBoxBaseClass{ get; set; }
        public static dynamic MatrixClass { get; set; }
        public static dynamic Point2Class { get; set; }
        public static dynamic Point3Class { get; set; }
        public static dynamic VectorBaseClass { get; set; }
        public static dynamic Vector2Class { get; set; }
        public static dynamic Vector3Class { get; set; }



        public static dynamic DataBaseClass { get; set; }
        public static dynamic DataCeilingClass { get; set; }
        public static dynamic DataDoorClass { get; set; }
        public static dynamic DataFamilyBaseClass { get; set; }
        public static dynamic DataLevelBuildingClass { get; set; }
        public static dynamic DataRoomClass { get; set; }
        public static dynamic DataSheetViewPortClass { get; set; }
        public static dynamic DataSheetClass { get; set; }
        public static dynamic DataTagClass { get; set; }
        public static dynamic DataView3DClass { get; set; }
        public static dynamic DataViewBaseClass { get; set; }
        public static dynamic DataViewElevationClass { get; set; }
        public static dynamic DataViewPlanClass { get; set; }
        public static dynamic DataViewScheduleClass { get; set; }


        public static dynamic DataDesingSetOptionClass { get; set; }
        public static dynamic DataElementGeometryBaseClass { get; set; }
        public static dynamic DataGeometryBaseClass { get; set; }
        public static dynamic DataGeometryBoundingBox2Class { get; set; }
        public static dynamic DataInstancePropertiesClass { get; set; }
        public static dynamic DataGeometryPolygon2Class { get; set; }
        public static dynamic DataPropertyClass { get; set; }
        public static dynamic DataLevelBaseClass { get; set; }
        public static dynamic DataLevelClass { get; set; }
        public static dynamic DataPhasingClass { get; set; }
        public static dynamic DataRevitModelClass { get; set; }
        public static dynamic DataScheduleSegmentClass { get; set; }
        public static dynamic DataTypePropertiesClass { get; set; }
        public static ScriptEngine PythonEngine => _pythonEngine ??= InitializePythonEngine();
        public static ScriptScope Scope => _scope ??= PythonEngine.CreateScope();


        private static ScriptEngine InitializePythonEngine()
        {
            // get a python engine
            ScriptEngine _pythonEngine = PythonRunner.SetupEngine();
            _scope = _pythonEngine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            var pythonFilePaths = new[]
            {
                Path.Combine(repoPath, @"duHast\Geometry\bounding_box_2.py"),
                Path.Combine(repoPath, @"duHast\Geometry\bounding_box_3.py"),
                Path.Combine(repoPath, @"duHast\Geometry\point_2.py"),
                Path.Combine(repoPath, @"duHast\Geometry\point_3.py"),
                Path.Combine(repoPath, @"duHast\Geometry\matrix.py"),
                Path.Combine(repoPath, @"duHast\Geometry\vector_base.py"),
                Path.Combine(repoPath, @"duHast\Geometry\vector_2.py"),
                Path.Combine(repoPath, @"duHast\Geometry\vector_3.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_base.py"),

                Path.Combine(repoPath, @"duHast\Data\Objects\data_base.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_ceiling.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_door.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_family_base.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_level_building.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_room.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_sheet_view_port.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_sheet.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_tag.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_view_3d.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_view_base.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_view_plan.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_view_elevation.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\data_view_schedule.py"),
                
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_design_set_option.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_element_geometry_base.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_instance_properties.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_property.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_level_base.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_level.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_phasing.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_revit_model.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_schedule_segement.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\data_type_properties.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\Geometry\geometry_base.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\Geometry\geometry_bounding_box_2.py"),
                Path.Combine(repoPath, @"duHast\Data\Objects\Properties\Geometry\geometry_polygon_2.py")
            };

            foreach (var filePath in pythonFilePaths)
            {
                _pythonEngine.ExecuteFile(filePath, _scope);
            }

            return _pythonEngine;
        }

        public static void Shutdown()
        {
            _pythonEngine?.Runtime.Shutdown();
            _pythonEngine = null;
            _scope = null;
            DataGeometryPolygon2Class = null;
            Point2Class = null;
        }
    }

}
