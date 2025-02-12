using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;
using RevitUtils;

namespace PushIt.RevitActions
{
    public static class RefreshRoomDataWithRevitData
    {

        public static bool CheckBindingsList(List<string> bindings, List<string> supportedCategoryNames)
        {
            // check if all shared parameters exist and are bound to the correct categories
            foreach (string supportedCategoryName in supportedCategoryNames)
            {
                if (!bindings.Contains(supportedCategoryName))
                {
                    return false;
                }
            }
            return true;
        }

        public static bool sharedParametersCheck(Document doc, List<Models.RoomsDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            
            //get the first room data modelto check if all shared parameters exist
            Models.RoomsDataModel firstRoomDataModel = roomsDataModel[0];
            var test = RevitUtils.SharedParaUtils.GetSharedParameters(doc);
            List<string> bindingsId = RevitUtils.SharedParaUtils.ParameterBindingsByGUID  (doc, firstRoomDataModel.Id.ParameterGUID);
            List<string> bindingsAreaBriefed = RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, firstRoomDataModel.AreaBriefed.ParameterGUID);
            List<string> bindingsAreaDesigned = RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, firstRoomDataModel.AreaDesigned.ParameterGUID);
            List<string> bindingsNameShort = RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, firstRoomDataModel.NameShort.ParameterGUID);
            List<string> bindingsDepartment = RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, firstRoomDataModel.Department.ParameterGUID);
            List<string> bindingsSubDepartment = RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, firstRoomDataModel.SubDepartment.ParameterGUID);

            // check if all shared parameters exist and are bound to the correct categories
            bool parameterCheck = CheckBindingsList(bindingsId, supportedCategoryName) &&
                CheckBindingsList(bindingsAreaBriefed, supportedCategoryName) &&
                CheckBindingsList(bindingsAreaDesigned, supportedCategoryName) &&
                CheckBindingsList(bindingsNameShort, supportedCategoryName) &&
                CheckBindingsList(bindingsDepartment, supportedCategoryName) &&
                CheckBindingsList(bindingsSubDepartment, supportedCategoryName);

            return parameterCheck;
            //return false;
        }

        public static List<PushIt.Models.RoomsRevit> ConvertFamiliesToRevitRooms(List<FamilyInstance> familyInstances, Models.RoomsDataModel sampleModelRoom)
        {
            List<Models.RoomsRevit> revitRooms = new List<PushIt.Models.RoomsRevit>();
            Dictionary<string, ElementId> sharedParameterIdsByGUIDs = RevitUtils.SharedParaUtils.GetSharedParameterIdsByGUID(familyInstances[0].Document);

            foreach (FamilyInstance familyInstance in familyInstances)
            { 
                IList<Parameter> parameters = familyInstance.GetOrderedParameters();
                string id_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.Id.ParameterGUID]);

                // ignore fam instance if id is null or empt
                if (id_value == null || id_value=="")
                {
                    continue;
                }

                // convert area values from square feet to square meters
                string areaBriefed_value_string = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.AreaBriefed.ParameterGUID]);
                double areaBriefed_value = 0;
                if (double.TryParse(areaBriefed_value_string, out double areaBriefed ))
                {
                    areaBriefed_value = areaBriefed * 0.092903; // Convert square feet to square meters
                }
                areaBriefed_value_string = areaBriefed_value.ToString();

                // convert area values from square feet to square meters
                string areaDesigned_value_string = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.AreaDesigned.ParameterGUID]);
               
                double areaDesigned_value = 0;
                if (double.TryParse(areaDesigned_value_string, out double areaDesigned))
                {
                    areaDesigned_value = areaDesigned * 0.092903; // Convert square feet to square meters
                }
                areaDesigned_value_string = areaDesigned_value.ToString();

                string nameShort_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.NameShort.ParameterGUID]);
                string department_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.Department.ParameterGUID]);
                string subDepartment_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.SubDepartment.ParameterGUID]);

                // create a new revit room
                Models.RoomsRevit revitRoom = new Models.RoomsRevit(id_value, areaBriefed_value_string, areaDesigned_value_string, nameShort_value, department_value, subDepartment_value);
                  
                revitRooms.Add(revitRoom);
            }
            return revitRooms;
        }

        public static List<Models.RoomsDataModel> RefreshRoomData(Document doc, List<Models.RoomsDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            // check if all shared parameters exist and are bound to the correct categories
            bool parameterCheck = sharedParametersCheck(doc, roomsDataModel, supportedCategoryName);
            
            // if not get out
            if (!parameterCheck){
                return null;
            }

            // get supported categories
            List<Category> categories = RevitUtils.CategoryUtils.GetMainCategoriesByName(doc, supportedCategoryName);
            if (categories.Count == 0)
            {
                return null;
            }

            // conver revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            //get families of supported built in categories
            List<FamilyInstance> familyInstances = RevitUtils.Families.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            // convert family instances to revit rooms
            List < PushIt.Models.RoomsRevit > revitRooms = ConvertFamiliesToRevitRooms(familyInstances, roomsDataModel[0]);



            return roomsDataModel;
        }
    }
}
