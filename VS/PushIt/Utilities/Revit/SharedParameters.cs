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

        public static bool SharedParametersCheck(Document doc, List<Models.RoomDataModel> roomsDataModel, List<string> supportedCategoryName, Action<string, duHast.Utils.WPF.Stores.MessageTypes> printMessage)
        {
            // check if rooms data model is empty
            if (roomsDataModel.Count == 0){ return false; }
           
            //get the first room data model to check if all shared parameters exist
            Models.RoomDataModel firstRoomDataModel = roomsDataModel[0];

            // get all shared parameters in the model
            var test = RevitUtils.SharedParaUtils.GetSharedParameters(doc);

            // get shared parameters of interest bindings to categories
            List<string> bindingsId = RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, firstRoomDataModel.Id.ParameterGUID);

            List<Dictionary<(string Name, string GUID), List<string>>> otherPropertiesBindings = new List<Dictionary<(string Name, string GUID), List<string>>>();
            foreach (var property in firstRoomDataModel.Properties)
            {
                // skip if parameterGUID is empty
                if (property.ParameterGUID == "") { continue; }
                otherPropertiesBindings.Add(new Dictionary<(string Name,string GUID), List<string>> { { (property.Name, property.ParameterGUID), RevitUtils.SharedParaUtils.ParameterBindingsByGUID(doc, property.ParameterGUID) } });
            }

            // check if all shared parameters exist
            List<string> parameterMessages = new List<string>();

            if (bindingsId== null)
            {
                parameterMessages.Add($"Room Id [{firstRoomDataModel.Id.ParameterGUID}] shared parameters is  missing from file");
            }

            // check if all shared parameters are bound to the correct categories
            foreach (var var in otherPropertiesBindings)
            {
                if (var.Values == null)
                {
                    parameterMessages.Add($"{var.Keys} shared parameters is  missing from file");
                }
            }


            bool parameterBindingCheck = true;

            //check parameter bindings and give some user feedback if something is wrong
            // check id parameter
            if (bindingsId ==null || !CheckBindingsList(bindingsId, supportedCategoryName))
            {
                parameterMessages.Add($"The shared parameter 'Room Id' [{firstRoomDataModel.Id.ParameterGUID}]is not bound to the correct categories.");
                parameterBindingCheck = false;
            }

            //check other parameters
            foreach (Dictionary<(string Name, string GUID), List<string>> var in otherPropertiesBindings)
            {
                foreach (var kvp in var)
                {
                    if (kvp.Value == null || !CheckBindingsList(kvp.Value, supportedCategoryName))
                    {
                        parameterMessages.Add($"The shared parameter '{kvp.Key.Name}' [{kvp.Key.GUID}]is not bound to the correct categories.");
                        parameterBindingCheck = false;
                    }
                }
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
