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

namespace duHastNet.AtTheLibrary.Commands
{
    public class OpenAvailableParametersCommand : Utils.WPF.Commands.CommandBase
    {
        private readonly duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Func<Utils.WPF.ViewModels.ViewModelBase> _createViewModel;
        private readonly ViewModels.FamiliesDataGridViewModel _familyDataGridViewModel;
        private readonly duHastNet.Utils.WPF.Stores.StateStore _stateStore;
        private readonly Models.RevitFamiliesDataModel _revitFamiliesDataModel;


        public override void Execute(object parameter)
        {
            //save the state
            try
            {
                var currentState = _familyDataGridViewModel.CreateStateFromViewModel();
                if (currentState != null)
                {
                    _stateStore.SaveState(_familyDataGridViewModel, currentState);
                    System.Diagnostics.Debug.WriteLine($"Forced save of grid state for {_familyDataGridViewModel.GetGridStateId()} before closing");
                }
            }
            catch (Exception stateEx)
            {
                System.Diagnostics.Debug.WriteLine($"Error forcing state save: {stateEx.Message}");
                //_familyDataGridViewModel.AddMessage($"Warning: Could not save grid state: {stateEx.Message}", duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }

            // Get states from StateStore for settings persistence
            var statesForSettings = _stateStore.GetStatesForSettings();
            _revitFamiliesDataModel.Settings.NavigationStates = statesForSettings;

            // navigate to new view
            _navigationStore.CurrentViewModel = _createViewModel();
        }

        public OpenAvailableParametersCommand(
            duHastNet.Utils.WPF.Stores.NavigationStore navigationStore,
            duHastNet.Utils.WPF.Stores.StateStore stateStore,
            Func<Utils.WPF.ViewModels.ViewModelBase> createViewModel,
            ViewModels.FamiliesDataGridViewModel familiesDataGridViewModel,
            Models.RevitFamiliesDataModel revitFamiliesDataModel
        )
        {
            _navigationStore = navigationStore;
            _stateStore = stateStore;
            _createViewModel = createViewModel;
            _revitFamiliesDataModel = revitFamiliesDataModel;
            _familyDataGridViewModel = familiesDataGridViewModel;
        }
    }
}
