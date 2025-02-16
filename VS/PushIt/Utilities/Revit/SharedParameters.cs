using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace PushIt.Utilities.Revit
{
    public static class SharedParameters
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
            // check if rooms data model is empty
            if (roomsDataModel.Count == 0){ return false; }
           
            //get the first room data model to check if all shared parameters exist
            Models.RoomsDataModel firstRoomDataModel = roomsDataModel[0];

            // get all shared parameters in the model
            var test = RevitUtils.SharedParaUtils.GetSharedParameters(doc);

            // get shared parameters of interest bindings to categories
            List<string> bindingsId = RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, firstRoomDataModel.Id.ParameterGUID);
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
            
        }
    }
}
