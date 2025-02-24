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
using Autodesk.Revit.DB;

namespace duHast.PushIt.Utilities.Revit
{
    public static class SharedParameters
    {
        public static bool CheckBindingsList(List<string> bindings, List<string> supportedCategoryNames)
        {
            // check if bindings is null
            if (bindings == null) { return false; }



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

        public static bool sharedParametersCheck(Document doc, List<Models.RoomDataModel> roomsDataModel, List<string> supportedCategoryName, Action<string, duHast.Utils.WPF.Stores.MessageTypes> printMessage)
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


            // check if all shared parameters exist
            List<string> parameterMessages = new List<string>();

            if (bindingsId== null)
            {
                parameterMessages.Add($"Room Id [{firstRoomDataModel.Id.ParameterGUID}] shared parameters is  missing from file");
            }

            if (bindingsAreaBriefed == null)
            {
                parameterMessages.Add($"Room Area Briefed [{firstRoomDataModel.AreaBriefed.ParameterGUID}] shared parameters is  missing from file");
            }

            if (bindingsAreaDesigned == null)
            {
                parameterMessages.Add($"Room Area Designed [{firstRoomDataModel.AreaDesigned.ParameterGUID}] shared parameters is  missing from file");
            }

            if (bindingsNameShort == null) {
                parameterMessages.Add($"Room Name Short [{firstRoomDataModel.NameShort.ParameterGUID}] shared parameters is  missing from file");
            }

            if (bindingsDepartment == null) {
                parameterMessages.Add($"Room Department [{firstRoomDataModel.Department.ParameterGUID}] shared parameters is  missing from file");
            }

            if (bindingsSubDepartment == null) {
                parameterMessages.Add($"Room Sub Department [{firstRoomDataModel.SubDepartment.ParameterGUID}] shared parameters is  missing from file");
            }


            bool parameterBindingCheck = true;
            //check parameter bindings and give some user feedback if something is wrong
            if (bindingsId ==null || !CheckBindingsList(bindingsId, supportedCategoryName))
            {
                parameterMessages.Add($"The shared parameter 'Room Id' [{firstRoomDataModel.Id.ParameterGUID}]is not bound to the correct categories.");
                parameterBindingCheck = false;
            }

            if (bindingsAreaBriefed==null || !CheckBindingsList(bindingsAreaBriefed, supportedCategoryName))
            {
                parameterMessages.Add($"The shared parameter 'Room Area Briefed' [{firstRoomDataModel.AreaBriefed.ParameterGUID}]is not bound to the correct categories.");
                parameterBindingCheck = false;
            }

            if (bindingsAreaDesigned == null || !CheckBindingsList(bindingsAreaDesigned, supportedCategoryName))
            {
                parameterMessages.Add($"The shared parameter 'Room Area Designed' [{firstRoomDataModel.AreaDesigned.ParameterGUID}]is not bound to the correct categories.");
                parameterBindingCheck = false;
            }

            if (bindingsNameShort == null || !CheckBindingsList(bindingsNameShort, supportedCategoryName))
            {
                parameterMessages.Add($"The shared parameter 'Room Name Short' [{firstRoomDataModel.NameShort.ParameterGUID}]is not bound to the correct categories.");
                parameterBindingCheck = false;
            }

            if (bindingsDepartment == null || !CheckBindingsList(bindingsDepartment, supportedCategoryName))
            {
                parameterMessages.Add($"The shared parameter 'Room Department' [{firstRoomDataModel.Department.ParameterGUID}]is not bound to the correct categories.");
                parameterBindingCheck = false;
            }

            if (bindingsSubDepartment == null || !CheckBindingsList(bindingsSubDepartment, supportedCategoryName))
            {
                parameterMessages.Add($"The shared parameter 'Room Sub Department' [{firstRoomDataModel.SubDepartment.ParameterGUID}]is not bound to the correct categories.");
                parameterBindingCheck = false;
            }

            // print messages
            if (parameterMessages.Count>0)
            {
                // one long message
                string message = string.Join("\n", parameterMessages);
                printMessage(message, duHast.Utils.WPF.Stores.MessageTypes.Error);
            }

            //return false if any parameter is missing or not bound to the correct categories
            return parameterBindingCheck;
            
        }
    }
}
