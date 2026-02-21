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
using Autodesk.Revit.UI;
using duHastNet.AtTheLibrary.Models;
using System;

namespace duHastNet.AtTheLibrary.RevitActions
{
    public class OpenFamilyIntoUIAction : RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {
        private readonly ViewModels.FamiliesDataGridViewModel _familiesDataGridViewModel;
        public ViewModels.FamiliesDataGridViewModel FamiliesDataGridViewModel
        {
            get { return _familiesDataGridViewModel; }
        }

        private readonly UIApplication _uiApplication;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {

            try
            {
                //family to load
                var fam = _familiesDataGridViewModel.SelectedFamily;

                // log the action
                AddMessage($"Opening family {fam.FamilyName} into Revit", Utils.WPF.Stores.MessageTypes.Information);

                try
                {
                    var familyOpener = new duHastNet.RevitUtils.Families.FamilyOpenInUI();
                    bool loadResult = familyOpener.OpenFamilyIntoUI(_uiApplication, fam.FamilyFilePath.Value);

                    if (familyOpener.GetErrorMessages().Count > 0)
                    {
                        //log the error
                        AddMessage($"Error opening family {fam.FamilyName.Value} into Revit: \n{string.Join("\n", familyOpener.GetErrorMessages())}", Utils.WPF.Stores.MessageTypes.Error);
                    }
                    else
                    {
                        //log the success
                        AddMessage($"Opened family {fam.FamilyName} into Revit", Utils.WPF.Stores.MessageTypes.Information);
                    }
                }
                catch (Exception ex)
                {
                    //log the exception
                    AddMessage($"Opening family into Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                }
            }
            catch (Exception ex)
            {
                //log the exception
                AddMessage($"Error opening family into Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue("Opened family into Revit");
        }

        public OpenFamilyIntoUIAction(
            RevitFamiliesDataModel revitModel,
            ViewModels.FamiliesDataGridViewModel familiesSelectionViewModel,
            UIApplication uiApp
            )
        {
            {
                RevitModel = revitModel;
                _familiesDataGridViewModel = familiesSelectionViewModel;
                _uiApplication = uiApp;
            }
        }
    }
}
