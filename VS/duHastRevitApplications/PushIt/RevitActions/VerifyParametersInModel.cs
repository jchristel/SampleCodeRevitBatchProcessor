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

using Autodesk.Revit.DB;
using duHastNet.PushIt.Models;
using System.Collections.Generic;


namespace duHastNet.PushIt.RevitActions
{
    public class VerifyParametersInModel: RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {
        private readonly ViewModels.RoomsMainViewModel _roomsSelectionViewModel;
        public ViewModels.RoomsMainViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Autodesk.Revit.DB.Document doc)
        {
            try
            {
                //check if any parameters...
                if (RevitModel.GetAllParameters().Count == 0) {
                    AddMessage("Revit data model contains no parameter data!",
                         Utils.WPF.Stores.MessageTypes.Error);
                    return GetReturnValue("Past parameter check");
                }


                //check parameters from data model against revit model
                foreach(var parameter in RevitModel.GetAllParameters())
                {   
                    //check if the parameter has a GUID, if so check bindings
                    if (string.IsNullOrEmpty(parameter.ParameterGUID))
                    {
                        continue;
                    }

                    // get all bindings for this parameter
                    List<string> bindingsId = duHastNet.RevitUtils.Parameters.SharedParaUtils.ParameterBindingsByGUID(doc,parameter.ParameterGUID);
                    
                    //check if any bindings found
                    if (bindingsId == null)
                    {
                        AddMessage($"parameter {parameter.ParameterName} {parameter.Name}: does not exist in the Revit model", Utils.WPF.Stores.MessageTypes.Error);
                    }

                    // check if parameter is bound to enabled categories
                    foreach (var supportedCategory in RevitModel.GetAllEnabledCategories())
                    {
                        if (!bindingsId.Contains(supportedCategory.Name) )
                        {
                            AddMessage(
                                $"Parameter {parameter.ParameterName} {parameter.Name} is not bound to category: {supportedCategory.Name}",
                                Utils.WPF.Stores.MessageTypes.Error);
                        }
                    }
                }
            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error refreshing parameter data from Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue("All required parameters are bound to all enabled categories in Revit.");
        }

        public VerifyParametersInModel(
            RevitDataModel revitModel
            )
        {
            RevitModel = revitModel;
        }
    }
}
