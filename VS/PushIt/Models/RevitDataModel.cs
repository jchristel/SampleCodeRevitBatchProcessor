using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel;
using NUnit.Framework.Internal;

namespace PushIt.Models
{
    public class RevitDataModel:INotifyPropertyChanged
    {
        public Models.RoomsDataModelContainer _roomsContainer;
        private Models.Settings _settings;

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

        public void AddRoom(Models.RoomsDataModel room)
        {
            _roomsContainer.AddRoom(room);
        }

        public List<Models.RoomsDataModel> GetAllRooms()
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

        public void AddPlacedRevitRoom(string roomId, Models.RoomsRevit revitRoom)
        {
            _roomsContainer.AddPlacedRevitRoom(roomId, revitRoom);
        }

        public void LoadRoomsData()
        {
            // add rooms to RevitDataModel
            List<Models.RoomsDataModel> rooms = Utilities.ReadRoomsData.GetRoomsData(_settings.DataPath);

            // TODO: if no rooms return (need to pop message to user...)
            if (rooms == null) return;
            
            foreach (Models.RoomsDataModel room in rooms)
            {
                AddRoom(room);
            }
        }

        public RevitDataModel()
        {
            _roomsContainer = new Models.RoomsDataModelContainer();
        }
    }
}
