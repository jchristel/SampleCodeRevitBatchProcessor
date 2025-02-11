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
            var test = RevitUtils.SharedParas.GetSharedParameters(doc);
            List<string> bindingsId = RevitUtils.SharedParas.ParameterBindingsByGUID  (doc, firstRoomDataModel.Id.ParameterGUID);
            List<string> bindingsAreaBriefed = RevitUtils.SharedParas.ParameterBindingsByGUID(doc, firstRoomDataModel.AreaBriefed.ParameterGUID);
            List<string> bindingsAreaDesigned = RevitUtils.SharedParas.ParameterBindingsByGUID(doc, firstRoomDataModel.AreaDesigned.ParameterGUID);
            List<string> bindingsNameShort = RevitUtils.SharedParas.ParameterBindingsByGUID(doc, firstRoomDataModel.NameShort.ParameterGUID);
            List<string> bindingsDepartment = RevitUtils.SharedParas.ParameterBindingsByGUID(doc, firstRoomDataModel.Department.ParameterGUID);
            List<string> bindingsSubDepartment = RevitUtils.SharedParas.ParameterBindingsByGUID(doc, firstRoomDataModel.SubDepartment.ParameterGUID);

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



        public static List<Models.RoomsDataModel> RefreshRoomData(Document doc, List<Models.RoomsDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            // check if all shared parameters exist and are bound to the correct categories
            bool parameterCheck = sharedParametersCheck(doc, roomsDataModel, supportedCategoryName);
            // if not get out
            if (!parameterCheck){
                return null;
            }
            

            return roomsDataModel;
        }
    }
}
