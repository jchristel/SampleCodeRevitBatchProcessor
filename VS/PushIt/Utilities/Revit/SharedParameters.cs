//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace duHast.PushIt.Utilities.Revit
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

        public static bool sharedParametersCheck(Document doc, List<Models.RoomDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            // check if rooms data model is empty
            if (roomsDataModel.Count == 0){ return false; }
           
            //get the first room data model to check if all shared parameters exist
            Models.RoomDataModel firstRoomDataModel = roomsDataModel[0];

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
