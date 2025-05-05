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
using duHastNet.PushIt.Models;

namespace duHastNet.PushIt.RevitActions
{
    public class RefreshRoomDataWithRevitData: RevitActionBase, IRevitAction
    {
       
        private ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        public ViewModels.RoomsSelectionViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;

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

                //remove any new room with 0 placed revit rooms
                // this is needed to remove any new rooms that are not placed in the model
                List<Models.RoomDataModel> updatedNewRoomsFiltered = new List<Models.RoomDataModel>();
                if (updatedNewRooms != null)
                {
                    foreach (var room in updatedNewRooms)
                    {
                        if (room.MatchingRevitRooms.Count > 0)
                        {
                            updatedNewRoomsFiltered.Add(room);
                        }
                    }
                }

                // clear all rooms in the data model (SoA and new rooms)
                // this will also clear all rooms if shared parameter setup in project file is wrong.
                RevitModel.ClearRooms();

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
                if (updatedNewRoomsFiltered != null && updatedNewRoomsFiltered.Count>0)
                {
                    // add updated rooms
                    foreach (var room in updatedNewRoomsFiltered)
                    {
                        RevitModel.AddNewRoom(room);
                    }
                    countNewRooms = updatedNewRoomsFiltered.Count;
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
            string refreshMessage = "";
            // check if all shared parameters exist and are bound to the correct categories
            bool parameterCheck = Utilities.Revit.SharedParameters.SharedParametersCheck(
                doc, 
                roomsDataModel, 
                supportedCategoryName, 
                out refreshMessage);
            
            // if not get out
            if (!parameterCheck){
                AddMessage(refreshMessage, Utils.WPF.Stores.MessageTypes.Error);
                return null;
            }
            else
            {
                AddMessage("Successfully checked shared parameter mapping in file.", Utils.WPF.Stores.MessageTypes.Log);
            }

            // get supported categories
            List<Category> categories = duHastNet.RevitUtils.Categories.CategoryUtils.GetMainCategoriesByName(doc, supportedCategoryName);
            if (categories.Count == 0)
            {
                if (supportedCategoryName.Count > 0)
                {
                    // build a string of supported categories
                    string supportedCategories = string.Join(", ", supportedCategoryName);
                    AddMessage($"Supported categories are invalid: {supportedCategories}", Utils.WPF.Stores.MessageTypes.Error);
                }
                else
                {
                    AddMessage("No supported categories provided.", Utils.WPF.Stores.MessageTypes.Error);
                }
                return null;
            }

            // convert revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = duHastNet.RevitUtils.Categories.CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            // get the documents current design set and option
            (string designSetName, string designOptionName) = Utilities.Revit.DesignSetAndOptionUtils.GetActiveDesignSetAndOptionName(doc);

            // update the ui with the current design set and option
            _roomsSelectionViewModel.ActiveDesignOptionName = designOptionName;
            _roomsSelectionViewModel.ActiveDesignSetName = designSetName;


            //get families of supported built in categories
            List<FamilyInstance> familyInstances = duHastNet.RevitUtils.Families.FamilyUtils.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            //check if any families in the model
            if (familyInstances.Count == 0)
            {
                // if that is not the case return the rooms data model unchanged after popping a message to the user
                AddMessage("No rooms found in the model.", Utils.WPF.Stores.MessageTypes.Information);

                // need to remove any family instances from the rooms data model from previous runs
                foreach (var room in roomsDataModel)
                {
                    // remove all matching revit rooms from the room data model
                    // SoA and split rooms
                    room.ClearAllMatchingRevitRooms();
                }
                
                //return the updated model
                return roomsDataModel;
            }

            // convert family instances to revit rooms
            List <duHastNet.PushIt.Models.RoomsRevit> revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(
                familyInstances, 
                roomsDataModel[0],
                AddMessage
            );

            // update rooms data model with revit rooms
            roomsDataModel = Utilities.UpdateRoomDataModelWithRoomsRevitModelUtils.UpdateRoomDataModelWithRoomsRevitModel(
                 roomsDataModel: roomsDataModel,
                 roomsRevit: revitRooms,
                 revitModelActiveDesignSetName: designSetName,
                 revitModelActiveDesignOptionName: designOptionName);

            return roomsDataModel;
        }


        public RefreshRoomDataWithRevitData(RevitDataModel revitModel, ViewModels.RoomsSelectionViewModel roomsSelectionViewModel)
        {
            RevitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
        }
    }
}
