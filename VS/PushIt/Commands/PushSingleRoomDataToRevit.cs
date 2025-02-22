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

using System;
using System.ComponentModel;

namespace PushIt.Commands
{
    public class PushSingleRoomDataToRevit: CommandBase
    {
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;

        private readonly Stores.MessageStore _messageStore;
        private readonly Action _action;


        public override bool CanExecute(object parameter)
        {
            // if safety off mode enabled this command is always available
            if (_roomsSelectionViewModel.SafetyOffMode) { return true; }

            // check if IsMatchingRevitRoomsEmpty is true and call the base CanExecute method
            return _roomsSelectionViewModel.IsMatchingRevitRoomsEmpty && base.CanExecute(parameter);
        }

        public override void Execute(object parameter)
        {
            try
            {
                _action?.Invoke();
                // get the selected room id

                var selectedRoomId = _roomsSelectionViewModel.SelectedRoom != null ? _roomsSelectionViewModel.SelectedRoom.Id.Value : "";
                _messageStore.SetCurrentMessage($"Pushed data for [{selectedRoomId}] into Revit room.", Stores.MessageTypes.Information);

            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage($"Failed to push data into Revit room: {ex.Message}", Stores.MessageTypes.Error);
            }
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.IsMatchingRevitRoomsEmpty))
            {
                OnCanExecutedChanged();
            }
        }

        public PushSingleRoomDataToRevit(
            ViewModels.RoomsSelectionViewModel roomsSelectionViewModel,
            Models.RevitDataModel revitDataModel,
            Stores.MessageStore messageStore,
            Action action
            )
        {
            _revitDataModel = revitDataModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _messageStore = messageStore;
            _action = action;
            _roomsSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
