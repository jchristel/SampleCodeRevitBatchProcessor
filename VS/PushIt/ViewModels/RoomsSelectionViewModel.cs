using Autodesk.Revit.DB.Architecture;
using PushIt.Utilities;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Data;
using System.Windows.Input;
using System.Xml.Linq;

namespace PushIt.ViewModels
{
    public class RoomsSelectionViewModel : ViewModelBase
    {
        private readonly Stores.NavigationStore _navigationStore;
        private readonly Stores.MessageStore _messageStore;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly RevitExternalEventHandlerManager _eventManager;

        //observable collection of rooms
        private readonly ObservableCollection<RoomViewModel> _rooms;
        //default view of the rooms collection
        private ICollectionView _roomsView;

        //command to raise an event to refresh the gui
        private readonly Commands.RaiseRevitEventCommand _raiseRefreshGUICommand;
        //command to push a single room to revit
        private readonly Commands.PushSingleRoomDataToRevit _raisePushSingleRoomCommand;
        //command to raise an event to reload data from file path
        private readonly Commands.ReloadDataCommand _raiseReloadDataCommand;

        private string _dataFilePath;
        public string DataFilePath
        {
            get => _dataFilePath;
            set
            {
                _dataFilePath = value;

                // update the data path in the settings
                _revitDataModel.Settings.DataPath = value;

                // call ui update
                OnPropertyChanged(nameof(DataFilePath));

            }
        }

        //binding in xaml propertry to the default view of the rooms collection
        public ICollectionView Rooms => _roomsView;

        //binding to show selected index
        private int _selectedIndex;
        public int SelectedIndex
        {
            get => _selectedIndex;
            set
            {
                if (_selectedIndex != value)
                {
                    _selectedIndex = value;
                    OnPropertyChanged(nameof(SelectedIndex));
                    OnPropertyChanged(nameof(SelectedRoom));
                    OnPropertyChanged(nameof(IsMatchingRevitRoomsEmpty));
                }
            }
        }

        //property to get the selected room from the revit data model
        public Models.RoomsDataModel SelectedRoom
        {
            get
            {
                // check if a default view exists
                if (_roomsView == null)
                {
                    return null;
                }
                // check if the selected index is within the bounds of the rooms collection
                if (_selectedIndex >= 0 && _selectedIndex < _roomsView.Cast<RoomViewModel>().Count())
                {
                    var selectedRoomViewModel = _roomsView.Cast<RoomViewModel>().ElementAt(_selectedIndex);
                    return _revitDataModel.GetAllRooms().FirstOrDefault(r => r.Id.Value == selectedRoomViewModel.Id);
                }
                // return null if the selected index is out of bounds
                return null;
            }
        }

        //property to check if the selected room has any matching Revit rooms
        //used to determine if the button to push the selected room to Revit should be enabled
        public bool IsMatchingRevitRoomsEmpty
        {
            get
            {
                var selectedRoom = SelectedRoom;
                if (selectedRoom != null && SelectedIndex >=0 )
                {
                    return selectedRoom.MatchingRevitRooms.Count == 0;
                }
                // if no room is selected, return false to avoid pushing null or stale data
                else if (SelectedIndex < 0)
                {
                    return false;
                }
                return true;
            }
        }

        //commands
        public ICommand RefreshGUICommand { get { return _raiseRefreshGUICommand; } }
        public ICommand PushSingleRoomCommand { get { return _raisePushSingleRoomCommand; } }
        public ICommand ReloadDataCommand { get { return _raiseReloadDataCommand; } }


        //updates the rooms in the observable collection with rooms from the data model
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

            //notify ui of changes
            _roomsView.Refresh();

            //notify ui of changes
            OnPropertyChanged(nameof(Rooms));
        }

        private bool RoomFilter(object item)
        {
            if (item is RoomViewModel room)
            {
                // Add your filtering logic here
                // For example, filter by a specific property of the room
                return true; // Return true to include the item, false to exclude it
            }
            return false;
        }


        /// <summary>
        /// used to catch events from the underlying model in order to update the ui
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Model_PropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check which property changed in the underlying model
            switch (e.PropertyName)
            {
                case PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED:
                    //update rooms in the view model
                    UpdateRooms();
                    break;

                // Add more cases for other properties as needed

                default:
                    // Handle changes for properties not explicitly handled
                    break;
            }
        }

        public void AddMessage(string message, Stores.MessageTypes messageType)
        {
            _messageStore.SetCurrentMessage(message, messageType);
        }


        /// <summary>
        /// Custom closing logic for RoomsSelectionViewModel
        /// Disposes all external events from the event manager
        /// </summary>
        public override void OnClosing()
        {
            // Custom closing logic for RoomsSelectionViewModel
            _eventManager.DisposeEvents();
            base.OnClosing();
        }

        public RoomsSelectionViewModel(
            Models.RevitDataModel revitDataModel,
            Stores.NavigationStore navigationStore,
            Stores.MessageStore messageStore,
            RevitExternalEventHandlerManager eventManager)
        {
            //store services
            _navigationStore = navigationStore;
            _messageStore = messageStore;
            _revitDataModel = revitDataModel;
            _eventManager = eventManager;

            //initialize properties
            _rooms = new ObservableCollection<RoomViewModel>();
            _roomsView = CollectionViewSource.GetDefaultView(_rooms);

            //set the data file path
            _dataFilePath = _revitDataModel.Settings.DataPath;

            // filter may need to be set after populating the collection...
            _roomsView.Filter = RoomFilter;

            //subscribe to underlying model changes
            _revitDataModel.PropertyChanged += Model_PropertyChanged;

            // add the view model to the event manager
            _eventManager.RoomsSelectionViewModel = this;
            //update rooms data with data from revit through an external event
            _eventManager.RefreshUIDataEventRaise();
           
            // set up commands
            // refresh gui with data from model
            _raiseRefreshGUICommand = new Commands.RaiseRevitEventCommand(this, _revitDataModel, _messageStore, () => { _eventManager.RefreshUIDataEventRaise(); });
            // push single room to revit
            _raisePushSingleRoomCommand = new Commands.PushSingleRoomDataToRevit(this, _revitDataModel, _messageStore, () => { _eventManager.PushItSingleEventRaise(); });
            //load data from file path
            _raiseReloadDataCommand = new Commands.ReloadDataCommand(this, _revitDataModel, _messageStore, () => { _eventManager.ReloadDataEventRaise(); });

        }
    }
}
