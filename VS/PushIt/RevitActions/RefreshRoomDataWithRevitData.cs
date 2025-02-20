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
using PushIt.Models;
using PushIt.ViewModels;
using RevitUtils;

namespace PushIt.RevitActions
{
    public class RefreshRoomDataWithRevitData:IRevitAction
    {
        private readonly RevitDataModel _revitModel;
        private ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        public Models.RevitDataModel RevitModel => _revitModel;
        public ViewModels.RoomsSelectionViewModel RoomsSelectionViewModel => _roomsSelectionViewModel;


        public void Execute(Document doc)
        {
            List<Models.RoomDataModel> updatedRooms = RefreshRoomData(
                doc, 
                _revitModel._roomsContainer.GetAllRooms(),
                _revitModel.Settings.SupportedCategories
             );
            
            if (updatedRooms != null)
            {
                //clear all rooms
                _revitModel.ClearRooms();
                // add updated rooms
                foreach (var rooms in updatedRooms)
                {
                    _revitModel.AddRoom(rooms);
                }
            }
        }

        /// <summary>
        /// Refresh the rooms data model with the rooms from the revit model
        /// </summary>
        /// <param name="doc"></param>
        /// <param name="roomsDataModel"></param>
        /// <param name="supportedCategoryName"></param>
        /// <returns></returns>
        public List<Models.RoomDataModel> RefreshRoomData(Document doc, List<Models.RoomDataModel> roomsDataModel, List<string> supportedCategoryName)
        {
            // check if all shared parameters exist and are bound to the correct categories
            bool parameterCheck = Utilities.Revit.SharedParameters.sharedParametersCheck(doc, roomsDataModel, supportedCategoryName);
            
            // if not get out
            if (!parameterCheck){
                return null;
            }

            // get supported categories
            List<Category> categories = RevitUtils.CategoryUtils.GetMainCategoriesByName(doc, supportedCategoryName);
            if (categories.Count == 0)
            {
                return null;
            }

            // convert revit categories into revit builtIncategories for filtering
            List<BuiltInCategory> familyInstanceFilterCategories = CategoryUtils.GetBuiltInCategoriesFromCategories(categories);

            //get families of supported built in categories
            List<FamilyInstance> familyInstances = RevitUtils.Families.GetFamilyInstancesByBuiltInCategories(doc, familyInstanceFilterCategories);

            // convert family instances to revit rooms
            List <PushIt.Models.RoomsRevit> revitRooms = Utilities.Revit.RevitRoomObjectsConverter.ConvertFamiliesToRevitRooms(familyInstances, roomsDataModel[0]);


            // get the documents current design set and option
            (string designSetName, string designOptionName) = Utilities.Revit.DesignSetAndOptionUtils.GetActiveDesignSetAndOptionName(doc);

            // update the ui with the current design set and option
            _roomsSelectionViewModel.ActiveDesignOptionName = designOptionName;
            _roomsSelectionViewModel.ActiveDesignSetName = designSetName;

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
            _revitModel = revitModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
        }
    }
}
