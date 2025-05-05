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

using duHastNet.PushIt.ViewModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;
using duHastNet.PushIt.Models;

namespace duHastNet.PushIt.RevitActions
{
    public class UpdateRoomDataModelWithNewRooms : RevitActionBase, IRevitAction
    {

        private ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        public ViewModels.RoomsSelectionViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try
            {
                // get all new rooms from the model
                var roomsInModel = Utilities.Revit.FamilyGet.GetAllSupportedFamilies(
                    doc: doc,
                    roomsDataModel: RevitModel.GetAllRooms(),
                    supportedCategoryName: RevitModel.Settings.SupportedCategories,
                    AddMessage: RoomsSelectionViewModel.AddMessage);

                //check if any rooms where found in the model, if not get out
                if (roomsInModel == null || roomsInModel.Count == 0)
                {
                    return GetReturnValue("No new rooms found in the model.");
                }

                //check which rooms are marked as new and add them to the data model

                return ($"{countSoARooms} SoA rooms and {countNewRooms} new rooms in data model updated with rooms from the Revit model.", Utils.WPF.Stores.MessageTypes.Information);
            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error adding new rooms from Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue("Created new rooms from Revit.");
        }

    }   public UpdateRoomDataModelWithNewRooms(RevitDataModel revitModel, ViewModels.RoomsSelectionViewModel roomsSelectionViewModel)
        {
            RevitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
        }
    } }

