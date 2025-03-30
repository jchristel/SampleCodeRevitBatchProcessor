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
using Autodesk.Revit.DB;
using duHast.AtTheLibrary.Models;

namespace duHast.AtTheLibrary.RevitActions
{
    public class RefreshFamiliesDataWithRevitData: RevitActionBase, IRevitAction
    {

        private ViewModels.FamiliesSelectionViewModel _roomsSelectionViewModel;
        public ViewModels.FamiliesSelectionViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;


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

            // check if any error messages were added
            if (GetErrorMessages().Count > 0)
            {
                // return the message
                return (string.Join("\n", GetErrorMessages()), Utils.WPF.Stores.MessageTypes.Error);
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
        /// <param name="roomsDataModel"></param>
        /// <param name="supportedCategoryName"></param>
        /// <returns></returns>
        public List<Models.FamilyDataModel> RefreshFamiliesData(Document doc, List<Models.FamilyDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            return roomsDataModel;
        }


        public RefreshFamiliesDataWithRevitData(RevitFamiliesDataModel revitModel, ViewModels.FamiliesSelectionViewModel roomsSelectionViewModel)
        {
            RevitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
        }
    }
}
