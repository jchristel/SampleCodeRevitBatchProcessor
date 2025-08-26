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


using duHastNet.Utils.WPF.Stores;
using System;
using System.ComponentModel;

namespace duHastNet.UI.FamilyReloaderUI.Commands
{
    public class RefreshFamilyFileMatchDataCommand: duHastNet.Utils.WPF.Commands.CommandBase
    {

        private readonly ViewModels.FamiliesSelectionViewModel _familiesSelectionViewModel;
        //private readonly ViewModels.FamiliesDataGridViewModel _familiesDataGridViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;
        private readonly Models.FamiliesDataModel _revitFamiliesDataModel;

        public RefreshFamilyFileMatchDataCommand(
           ViewModels.FamiliesSelectionViewModel familiesSelectionViewModel,
           Models.FamiliesDataModel revitFamiliesDataModel)
        {
            _familiesSelectionViewModel = familiesSelectionViewModel;
            _revitFamiliesDataModel = revitFamiliesDataModel;

            _familiesSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }

        /// <summary>
        /// this command is available if there are no errors in the view model
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        public override bool CanExecute(object parameter)
        {
            // check if there are any errors ( there is only one which relateds to a valid library path )
            if (!_familiesSelectionViewModel.LibraryDirectoryPathValid)
            {
                return false;
            }
            return true;
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.FamiliesSelectionViewModel.LibraryDirectoryPathValid))
            {
                OnCanExecutedChanged();
            }
        }

        public override void Execute(object parameter)
        {
            
            try
            {
                // Execute the action to refresh the room data with the Revit data
                Actions.RefreshFamilyMatchStatusAction action = new Actions.RefreshFamilyMatchStatusAction(_revitFamiliesDataModel);
                (string messageAction, duHastNet.Utils.WPF.Stores.MessageTypes messageActionType) = action.Execute();

                //TODO write messages to log...
                _revitFamiliesDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                //pop message to user
                _familiesSelectionViewModel.AddMessage(messageAction, messageActionType);

                //update the view model
                if (messageActionType == MessageTypes.Information)
                {
                    // raise event to notify the view model that the model has been updated
                    _revitFamiliesDataModel.RaisePropertyChanged(Models.Constants.DATA_MODEL_FAMILIES_UPDATED);
                }
            }
            catch (Exception ex)
            {
                _familiesSelectionViewModel.AddMessage(ex.Message, MessageTypes.Error);
            }
            finally
            {
            }
        }
    }
}
