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

using System.Collections.Generic;
using System.Linq;
using Autodesk.Revit.DB;
using duHastNet.AtTheLibrary.Models;

namespace duHastNet.AtTheLibrary.RevitActions
{
    public class RefreshFamiliesDataWithRevitData: RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {

        private ViewModels.FamiliesSelectionViewModel _roomsSelectionViewModel;
        public ViewModels.FamiliesSelectionViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;


        /// <summary>
        /// Execute the refresh data from revit model action.
        /// This actions adds matching family types from the revit model to the data model.
        /// It will not add any types with no match in the data model!!
        /// </summary>
        /// <param name="doc"></param>
        /// <returns></returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try { 
                // refresh the rooms data model with the rooms from the revit model
                List<Models.FamilyDataModel> updatedFamilies = RefreshFamiliesData(
                    doc, 
                    RevitModel.GetAllFamilies(),
                    RevitModel.Settings.SupportedTypeParameterNames
                 );

                // clear all rooms in the data model
                // this will also clear all rooms if shared parameter setup in project file is wrong.
                RevitModel.ClearFamilies();

                // add updated rooms to the data model if there are any
                if (updatedFamilies != null)
                {
                    // add updated rooms
                    foreach (var updatedFamily in updatedFamilies)
                    {
                        RevitModel.AddFamily(updatedFamily);
                    }
                }
            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error refreshing family data from Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // get the ovearll error count
            int erroCount = GetErrorMessages().Count;

            // check if any error messages were added
            if (erroCount > 0)
            {
                if (erroCount > 3)
                {
                    //return abridged message
                    return ($"{erroCount} Errors occured. Refer to log file for details.", Utils.WPF.Stores.MessageTypes.Error);
                }
                else
                {
                    // return the message
                    return (string.Join("\n", GetErrorMessages()), Utils.WPF.Stores.MessageTypes.Error);
                }
            }
            else
            {
                // return the message
                return ("Refreshed families from Revit", Utils.WPF.Stores.MessageTypes.Information);
            }
        }

        /// <summary>
        /// Refresh the rooms data model with the rooms from the revit model
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="familiesDataModel"></param>
        /// <param name="supportedParameterName"></param>
        /// <returns></returns>
        public List<Models.FamilyDataModel> RefreshFamiliesData(Document doc, List<Models.FamilyDataModel> familiesDataModel, List<string> supportedParameterName)
        {
            // get all families from the Revit model
            List<Models.FamilyRevit> familiesInRevitModel = GetFamiliesFromModel(doc);

            //update the families data model with the families from the revit model
            familiesDataModel = UpdateFamiliesDataModel(familiesDataModel, familiesInRevitModel);

            //update the parameter visibility for the families in the data model based on the supported parameter names
            familiesDataModel = UpdateUIVisbility(familiesDataModel, supportedParameterName);

            // return the updated families data model
            return familiesDataModel;
        }

        /// <summary>
        /// Get all families from the revit model
        /// </summary>
        /// <param name="doc"></param>
        /// <returns></returns>
        public List<Models.FamilyRevit> GetFamiliesFromModel(Document doc)
        {
            List<Models.FamilyRevit> families = new List<Models.FamilyRevit>();
            // get all families from the revit model
            var familiesInModel = RevitUtils.Families.FamilyUtils.GetAllFamilies(doc);

            // convert the families to revit families
            families = Utilities.Revit.RevitFamilyObjectsConverter.ConvertFamiliesToRevitFamilies(
                families: familiesInModel.ToList(), 
                AddMessage: AddMessage
            );

            // add them to the list
            return families;
        }

        /// <summary>
        /// Update the families data model with the families from the revit model
        /// </summary>
        /// <param name="familiesDataModel"></param>
        /// <param name="familiesInRevitModel"></param>
        /// <returns></returns>
        public List<Models.FamilyDataModel> UpdateFamiliesDataModel(List<Models.FamilyDataModel> familiesDataModel, List<Models.FamilyRevit> familiesInRevitModel)
        {
            // loop over families and update the data model
            foreach(FamilyDataModel familyDataModel in familiesDataModel)
            {
                // get the family revit object
                FamilyRevit familyRevit = familiesInRevitModel.FirstOrDefault(f => f.Id.Value == familyDataModel.Id.Value);
                // if the family revit object is not null
                if (familyRevit != null)
                {
                    // update the family data model with the family revit object
                    familyDataModel.AddMatchingFamily(familyRevit);
                }
            }
            // update the families data model with the families from the revit model
            return familiesDataModel;
        }

        /// <summary>
        /// Update the parameter visibility for the families in the data model based on the supported parameter names
        /// </summary>
        /// <param name="familiesDataModel"></param>
        /// <param name="supportedParameterName"></param>
        /// <returns></returns>
        public List<FamilyDataModel> UpdateUIVisbility(List<FamilyDataModel> familiesDataModel, List<string> supportedParameterName)
        {
            //update the parameter visibility for the families in the data model based on the supported parameter names
            return familiesDataModel;
        }

        public RefreshFamiliesDataWithRevitData(RevitFamiliesDataModel revitModel, ViewModels.FamiliesSelectionViewModel roomsSelectionViewModel)
        {
            RevitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
        }
    }
}
