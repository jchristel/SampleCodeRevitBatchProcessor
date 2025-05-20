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
    public class RefreshRoomDataWithRevitData : RevitActionBase, duHastNet.RevitUtils.RevitActions.IRevitAction
    {

        private ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        public ViewModels.RoomsSelectionViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;

        //current set or push it mock rooms
        private List<RoomRevit> _roomsData;

        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(Document doc)
        {
            try
            {
                // refresh the rooms data model rooms from the SoA with the rooms from the revit model
                List<Models.RoomDataModel> updatedSoARooms = RefreshRoomData(
                    doc,
                    RevitModel._roomsContainer.GetAllRooms(), // returns SoA rooms only
                    RevitModel.Settings.SupportedCategories
                 );

                // refresh the rooms data model with the new rooms from the revit model
                List<Models.RoomDataModel> updatedNewRooms = RefreshRoomData(
                    doc,
                    RevitModel._roomsContainer.GetAllNewRooms(), // returns new rooms only
                    RevitModel.Settings.SupportedCategories
                );

                // do not remove any new room with 0 placed revit rooms in case the new room is placed in a non primary design option...

                // clear all rooms in the data model (SoA and new rooms)
                // this will also clear all rooms if shared parameter setup in project file is wrong.
                RevitModel.ClearAllRooms();

                int countSoARooms = 0;
                // add updated SoA rooms to the data model if there are any
                if (updatedSoARooms != null)
                {
                    // add updated rooms
                    foreach (var rooms in updatedSoARooms)
                    {
                        RevitModel.AddRoom(rooms);
                    }
                    countSoARooms = updatedSoARooms.Count;
                }

                int countNewRooms = 0;
                if (updatedNewRooms != null && updatedNewRooms.Count > 0)
                {
                    // add updated rooms
                    foreach (var room in updatedNewRooms)
                    {
                        RevitModel.AddNewRoom(room);
                    }
                    countNewRooms = updatedNewRooms.Count;
                }

                return ($"{countSoARooms} SoA rooms and {countNewRooms} new rooms in data model updated with rooms from the Revit model.", Utils.WPF.Stores.MessageTypes.Information);


            }
            catch (System.Exception ex)
            {
                //log the exception
                AddMessage($"Error refreshing room data from Revit: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            }

            // build the return message depending on error count
            return GetReturnValue("Refreeshed pushed room count from Revit.");
        }

        /// <summary>
        /// Refresh the rooms data model with the rooms from the revit model
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="roomsDataModel"></param>
        /// <param name="supportedCategoryName"></param>
        /// <returns></returns>
        public List<Models.RoomDataModel> RefreshRoomData(
            Document doc,
            List<Models.RoomDataModel> roomsDataModel,
            List<string> supportedCategoryName)
        {

            // check if we already have the current set of revit rooms
            if (_roomsData == null)
            {
                _roomsData = Utilities.Revit.FamilyGet.GetAllSupportedFamilies(
                    doc: doc,
                    roomsDataModel: roomsDataModel,
                    supportedCategoryName: supportedCategoryName,
                    AddMessage: AddMessage);
            }


            //if the update failed return the rooms data model unchanged
            if (_roomsData == null || _roomsData.Count == 0)
            {
                return roomsDataModel;
            }

            // get the documents current design set and option
            (string designSetName, string designOptionName) = Utilities.Revit.DesignSetAndOptionUtils.GetActiveDesignSetAndOptionName(doc);

            // update the ui with the current design set and option
            _roomsSelectionViewModel.ActiveDesignOptionName = designOptionName;
            _roomsSelectionViewModel.ActiveDesignSetName = designSetName;

            // update rooms data model with revit rooms
            roomsDataModel = Utilities.UpdateRoomDataModelWithRoomsRevitModelUtils.UpdateRoomDataModelWithRoomsRevitModel(
                 roomsDataModel: roomsDataModel,
                 roomsRevit: _roomsData,
                 revitModelActiveDesignSetName: designSetName,
                 revitModelActiveDesignOptionName: designOptionName);

            return roomsDataModel;
        }


        public RefreshRoomDataWithRevitData(
            RevitDataModel revitModel,
            ViewModels.RoomsSelectionViewModel roomsSelectionViewModel,
            List<Models.RoomRevit> revitMockRooms = null)
        {
            RevitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _roomsData = revitMockRooms;
        }
    }
}
