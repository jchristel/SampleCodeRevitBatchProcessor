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


using PushIt.Utilities;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Windows.Data;
using System.Windows.Input;

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

        //observable collection of supported categories in Revit to push data into
        private readonly ObservableCollection<RoomViewModel> _supportedCategories;
        //default view of the supported categories collection
        private ICollectionView _supportedCategoriesView;

        //command to raise an event to refresh the gui
        private readonly Commands.RaiseRevitEventCommand _raiseRefreshGUICommand;
        //command to push a single room to revit
        private readonly Commands.PushSingleRoomDataToRevit _raisePushSingleRoomCommand;
        //command to raise an event to reload data from file path
        private readonly Commands.ReloadDataCommand _raiseReloadDataCommand;
        //command to highlight a room in Revit
        private readonly Commands.RaiseRevitEventCommand _highLightRoomCommand;

        #region settings

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

        #endregion settings

        #region Column Filtering

        // Field to return a default list of column names
        private readonly List<string> _columnNameDefaultList = new List<string>
        {
            "Room Id",
            "Area Briefed",
            "Area Designed",
            "Room Name Short",
            "Department",
            "Sub Department",
            "Count"
        };

        // Property to expose the default list of column names
        public List<string> ColumnNameDefaultList => _columnNameDefaultList;

        // field to store the selected column filter item
        private string _selectedColumnFilterItem;
        public string SelectedColumnFilterItem
        {
            get => _selectedColumnFilterItem;
            set
            {
                _selectedColumnFilterItem = value;
                OnPropertyChanged(nameof(SelectedColumnFilterItem));
                
                //update is filter applied property
                OnPropertyChanged(nameof(IsFilterApplied));
            }
        }

        // field to store the filter value
        private string _filterValue;
        public string FilterValue
        {
            get => _filterValue;
            set
            {
                _filterValue = value;
                OnPropertyChanged(nameof(FilterValue));

                //update is filter applied property
                OnPropertyChanged(nameof(IsFilterApplied));

                // Refresh the view to apply the filter
                _roomsView.Refresh(); 
            }
        }

        // Property to indicate if a filter is applied
        public bool IsFilterApplied => !string.IsNullOrEmpty(SelectedColumnFilterItem) && !string.IsNullOrEmpty(FilterValue);

        #endregion Column Filtering

        #region user selection

        //binding in xaml property to the default view of the rooms collection
        public ICollectionView Rooms => _roomsView;

        //binding in xaml property to the default view of the supported categories collection
        public ICollectionView SupportedCategories => _supportedCategoriesView;

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

        #endregion user selection

        #region Commands

        //commands
        public ICommand RefreshGUICommand { get { return _raiseRefreshGUICommand; } }
        public ICommand PushSingleRoomCommand { get { return _raisePushSingleRoomCommand; } }
        public ICommand ReloadDataCommand { get { return _raiseReloadDataCommand; } }
        public ICommand HighLightRoomCommand { get { return _highLightRoomCommand; } }

        #endregion Commands

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

        public void UpdateCategories()
        {

        }

        private bool RoomFilter(object item)
        {
            if (item is RoomViewModel room)
            {
                if (string.IsNullOrEmpty(SelectedColumnFilterItem) || string.IsNullOrEmpty(FilterValue))
                {
                    return true; // No filter applied
                }

                switch (SelectedColumnFilterItem)
                {
                    case "Room Id":
                        return room.Id.IndexOf(FilterValue, StringComparison.OrdinalIgnoreCase) >= 0;
                    case "Area Briefed":
                        return room.AreaBriefed.IndexOf(FilterValue, StringComparison.OrdinalIgnoreCase) >= 0;
                    case "Area Designed":
                        return room.AreaDesigned.IndexOf(FilterValue, StringComparison.OrdinalIgnoreCase) >= 0;
                    case "Room Name Short":
                        return room.NameShort.IndexOf(FilterValue, StringComparison.OrdinalIgnoreCase) >= 0;
                    case "Department":
                        return room.Department.IndexOf(FilterValue, StringComparison.OrdinalIgnoreCase) >= 0;
                    case "Sub Department":
                        return room.SubDepartment.IndexOf(FilterValue, StringComparison.OrdinalIgnoreCase) >= 0;
                    case "Count":
                        return room.Count.IndexOf(FilterValue, StringComparison.OrdinalIgnoreCase) >= 0;
                    default:
                        return true; // No filter applied
                }
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
            // rooms collection
            _rooms = new ObservableCollection<RoomViewModel>();
            _roomsView = CollectionViewSource.GetDefaultView(_rooms);
            // supported categories collection
            _supportedCategories = new ObservableCollection<SupportedCategoriesViewModel>();
            _supportedCategoriesView = CollectionViewSource.GetDefaultView(_supportedCategories);

            //set the data file path
            _dataFilePath = _revitDataModel.Settings.DataPath;

            // filter may need to be set after populating the collection...
            _roomsView.Filter = RoomFilter;

            //update supported categories from settings
            UpdateCategories();
            
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
            //highlight room in Revit
            _highLightRoomCommand = new Commands.RaiseRevitEventCommand(this, _revitDataModel, _messageStore, () => { _eventManager.HighlightSelectedRoomEventRaise(); });
        }
    }
}
