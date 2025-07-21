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


using duHastNet.AtTheLibrary.RevitActions;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.ComponentModel;


namespace duHastNet.AtTheLibrary.Commands
{
    public class LoadFamilyAsyncCommand : Utils.WPF.Commands.CommandBase
    {

        private readonly ViewModels.FamiliesSelectionViewModel _familiesSelectionViewModel;
        private readonly ViewModels.FamiliesDataGridViewModel _familiesDataGridViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;
        private readonly Models.RevitFamiliesDataModel _revitFamiliesDataModel;


        public override async void Execute(object parameter)
        {
            //deactivate the ui
            _familiesSelectionViewModel.IsWaitingForRevitCommandToFinish = true;

            try
            {
                (string message, Utils.WPF.Stores.MessageTypes messageType) = await RevitTask.RunAsync(
                    app =>
                    {
                        //Run Revit API code here

                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            // Execute the action to refresh the room data with the Revit data
                            LoadFamilyAction action = new LoadFamilyAction(_revitFamiliesDataModel, _familiesDataGridViewModel);
                            (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) = action.Execute(doc);

                            //TODO write messages to log...
                            _revitFamiliesDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            // return the message to the caller
                            return (messageAction, messageActionType);
                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the external event handler refresh UI from rooms in model event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                        }
                    });

                //pop message to user
                _familiesSelectionViewModel.AddMessage(message, messageType);

                //update the view model
                if (messageType == MessageTypes.Information)
                {
                    // raise event to notify the view model that the model has been updated
                    _revitFamiliesDataModel.RaisePropertyChanged(Utilities.PropertyChangedEventNames.DATA_MODEL_FAMILIES_UPDATED);
                }
            }
            catch (Exception ex)
            {
                _familiesSelectionViewModel.AddMessage(ex.Message, MessageTypes.Error);
            }
            finally
            {
                //activate the ui
                _familiesSelectionViewModel.IsWaitingForRevitCommandToFinish = false;
            }
        }

        /// <summary>
        /// this command is always available
        /// </summary>
        /// <param name="parameter"></param>
        /// <returns></returns>
        public override bool CanExecute(object parameter)
        {
            // check if IsWaitingForRevitCommandToFinish is true
            if (_familiesSelectionViewModel.IsWaitingForRevitCommandToFinish)
            {
                return false;
            }
            return true;
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.FamiliesSelectionViewModel.IsWaitingForRevitCommandToFinish))
            {
                OnCanExecutedChanged();
            }
        }

        public LoadFamilyAsyncCommand(
           ViewModels.FamiliesSelectionViewModel familiesSelectionViewModel,
           ViewModels.FamiliesDataGridViewModel familiesDataGridViewModel,
           Models.RevitFamiliesDataModel revitFamiliesDataModel
           )
        {
            _revitFamiliesDataModel = revitFamiliesDataModel;
            _familiesSelectionViewModel = familiesSelectionViewModel;
            _familiesSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
            _familiesDataGridViewModel = familiesDataGridViewModel;
            _familiesDataGridViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
