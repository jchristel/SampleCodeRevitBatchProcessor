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
using Autodesk.Revit.DB;
using duHastNet.AtTheLibrary.Models;


namespace duHastNet.AtTheLibrary.RevitActions
{
    public class LoadFamilyAction: RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {

        private ViewModels.FamiliesSelectionViewModel _familiesSelectionViewModel;
        public ViewModels.FamiliesSelectionViewModel FamiliesSelectionViewModel => _familiesSelectionViewModel;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            
            try
            {
                //family to load
                var fam = _familiesSelectionViewModel.SelectedFamily;
                
                // log the action
                AddMessage($"Loading family {fam.FamilyName} and type {fam.FamilyTypeName} into Revit", Utils.WPF.Stores.MessageTypes.Log);

                // attempt to highlight and zoom to selected elements
                try
                {
                    var familyLoader = new duHastNet.RevitUtils.Families.FamilyLoad();
                    bool loadResult = familyLoader.LoadFamilyType(doc, fam.FamilyName.Value,fam.FamilyTypeName.Value, true);

                    if (familyLoader.GetErrorMessages().Count > 0)
                    {
                        //log the error
                        AddMessage($"Error loading family {fam.FamilyName} and type {fam.FamilyTypeName} into Revit: {string.Join("\n", familyLoader.GetErrorMessages())}", Utils.WPF.Stores.MessageTypes.Error);
                    }
                    else
                    {
                        //log the success
                        AddMessage($"Loaded family {fam.FamilyName} and type {fam.FamilyTypeName} into Revit", Utils.WPF.Stores.MessageTypes.Information);
                    }
                }
                catch (Exception ex)
                {
                    //log the exception
                    AddMessage($"Error highlighting rooms in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                }
            }
            catch (Exception ex)
            {
                //log the exception
                AddMessage($"Error highlighting rooms in Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue("Highlighted rooms in Revit");
        }

        public LoadFamilyAction(
            RevitFamiliesDataModel revitModel,
            ViewModels.FamiliesSelectionViewModel familiesSelectionViewModel
           )
        {
            RevitModel = revitModel;
            _familiesSelectionViewModel = familiesSelectionViewModel;
        }
    }
}
