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

using CommunityToolkit.Mvvm.Input;
using System;
using System.Windows.Input;

namespace duHastNet.AtTheLibrary.Commands
{
    public class OpenAvailableParametersCommand
    {
        private readonly RelayCommand _command;

        public OpenAvailableParametersCommand(
            duHastNet.Utils.WPF.Stores.NavigationStore navigationStore,
            duHastNet.Utils.WPF.Stores.StateStore stateStore,
            Func<Utils.WPF.ViewModels.ViewModelBase> createViewModel,
            ViewModels.FamiliesDataGridViewModel familiesDataGridViewModel,
            Models.RevitFamiliesDataModel revitFamiliesDataModel
        )
        {
            _command = new RelayCommand(() =>
            {
                //save the state
                try
                {
                    var currentState = familiesDataGridViewModel.CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        stateStore.SaveState(familiesDataGridViewModel, currentState);
                        System.Diagnostics.Debug.WriteLine($"Forced save of grid state for {familiesDataGridViewModel.GetGridStateId()} before closing");
                    }
                }
                catch (Exception stateEx)
                {
                    System.Diagnostics.Debug.WriteLine($"Error forcing state save: {stateEx.Message}");
                }

                // Get states from StateStore for settings persistence
                var statesForSettings = stateStore.GetStatesForSettings();
                revitFamiliesDataModel.Settings.NavigationStates = statesForSettings;

                // navigate to new view
                navigationStore.CurrentViewModel = createViewModel();
            });
        }

        // Public ICommand wrapper so ViewModels can expose this as ICommand
        public ICommand Command => _command;

        public void Execute(object? parameter = null) => _command.Execute(null);
        public bool CanExecute(object? parameter = null) => _command.CanExecute(null);
    }
}