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
using System.ComponentModel;


namespace duHastNet.PushIt.Models
{
    public class RevitDataModel:INotifyPropertyChanged
    {
        public Models.RoomsDataModelContainer _roomsContainer;
        public Models.CategoryDataModelContainer _categoriesContainer;
        private Models.Settings _settings;

        private Utils.Logging.SimpleLogger _logger;

        public Settings Settings { get => _settings; set => _settings = value; }

        //event handlers for property changed
        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }


        public void RaisePropertyChanged(string name)
        {
            OnPropertyChanged(name);
        }

        public void AddRoom(Models.RoomDataModel room)
        {
            _roomsContainer.AddRoom(room);
        }

        public List<Models.RoomDataModel> GetAllRooms()
        {
            return _roomsContainer.GetAllRooms();
        }

        public void ClearRooms()
        {
            _roomsContainer.ClearRooms();
        }

        public void RemovePlacedRevitRoom(int revitElementId)
        {
            _roomsContainer.RemovePlacedRevitRoom(revitElementId);
        }


        public void RemovePlacedNewRevitRoom(string roomId, int revitElementId)
        {
             _roomsContainer.RemoveNewPlacedRevitRoom(
                roomId: roomId,
                revitElementId: revitElementId
             );
        }

        public void AddPlacedRevitRoom(string roomId, Models.RoomsRevit revitRoom)
        {
            _roomsContainer.AddPlacedRevitRoom(roomId, revitRoom);
        }

        public void AddPlacedNewRevitRoom(string roomId, Models.RoomsRevit revitRoom)
        {
            _roomsContainer.AddPlacedNewRevitRoom(roomId, revitRoom);
        }

        public void LoadRoomsData()
        {
            // add rooms to RevitDataModel
            List<Models.RoomDataModel> rooms = Utilities.ReadRoomsData.GetRoomsData(_settings.DataPath);

            // TODO: if no rooms return (need to pop message to user...)
            if (rooms == null) return;
            
            foreach (Models.RoomDataModel room in rooms)
            {
                AddRoom(room);
            }
        }


        public void AddCategory(Models.CategoryDataModel category)
        {
            _categoriesContainer.AddCategory(category);
        }

        public List<Models.CategoryDataModel> GetAllCategories()
        {
            return _categoriesContainer.GetAllCategories();
        }

        public void ClearCategories()
        {
            _categoriesContainer.ClearCategories();
        }

        public void LoadCategoryData(List<Models.CategoryDataModel> revitCategories)
        {
            foreach (Models.CategoryDataModel category in revitCategories)
            {
                AddCategory(category);
            }
        }

        public void InitialiseLogger(string filePath)
        {
            _logger = new Utils.Logging.SimpleLogger(filePath);
        }

        public void LogMessages(List<(string, Utils.WPF.Stores.MessageTypes)> messages)
        {
            if(_logger == null)
            {
                return;
            }

            _logger.LogMessagesFireAndForget(messages);
        }


        public RevitDataModel()
        {
            _roomsContainer = new Models.RoomsDataModelContainer();
            _categoriesContainer = new Models.CategoryDataModelContainer();
        }
    }
}
