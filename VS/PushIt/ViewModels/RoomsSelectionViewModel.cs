using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.ViewModels
{
    public class RoomsSelectionViewModel : ViewModelBase
    {

        private readonly Stores.NavigationStore _navigationStore;
        private readonly Stores.MessageStore _messageStore;
        private readonly Models.RevitDataModel _revitDataModel;

        private readonly ObservableCollection<RoomViewModel> _rooms;

        //binding in xaml propertry
        public IEnumerable<RoomViewModel> Rooms => _rooms;

        public RoomsSelectionViewModel(Models.RevitDataModel revitDataModel, Stores.NavigationStore navigationStore, Stores.MessageStore messageStore)
        {
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;

            _rooms = new ObservableCollection<RoomViewModel>();
            UpdateRooms();
        }
        private void UpdateRooms()
        {
            _rooms.Clear();
            foreach (Models.RoomsDataModel room in _revitDataModel.GetAllRooms())
            {
                {
                    ViewModels.RoomViewModel roomViewModel = new RoomViewModel(room);
                    _rooms.Add(roomViewModel);
                }
            }

        }
    }
}
