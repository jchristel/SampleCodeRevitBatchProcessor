using PushIt.Utilities;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace PushIt.ViewModels
{
    public class RoomsSelectionViewModel : ViewModelBase
    {

        private readonly Stores.NavigationStore _navigationStore;
        private readonly Stores.MessageStore _messageStore;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly RevitExternalEventHandlerManager _eventManager;

        private readonly ObservableCollection<RoomViewModel> _rooms;


        private readonly Commands.RaiseRevitEventCommand _raiseRefreshGUICommand;

        //binding in xaml propertry
        public IEnumerable<RoomViewModel> Rooms => _rooms;

        public RoomsSelectionViewModel(
            Models.RevitDataModel revitDataModel, 
            Stores.NavigationStore navigationStore, 
            Stores.MessageStore messageStore,
            RevitExternalEventHandlerManager eventManager)
        {
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;
            _eventManager = eventManager;

            _rooms = new ObservableCollection<RoomViewModel>();
            UpdateRooms();

            // set up commands
            // refresh gui with data from model
            _raiseRefreshGUICommand = new Commands.RaiseRevitEventCommand(this, _revitDataModel, _messageStore, () => { _eventManager.RaiseRefreshUIDataEvent(); });   
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

        public ICommand RefreshGUICommand { get { return _raiseRefreshGUICommand; } }



        public override void OnClosing()
        {
            // Custom closing logic for RoomsSelectionViewModel
            _eventManager.DisposeEvents();
            base.OnClosing();
        }

    }
}
