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
using duHastNet.AtTheLibrary.RevitActions;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows.Input;


namespace duHastNet.AtTheLibrary.Commands
{
    public class OpenFamilyIntoUIAsyncCommand
    {
        private readonly AsyncRelayCommand _command;
        private readonly ViewModels.FamiliesSelectionViewModel _familiesSelectionViewModel;
        private readonly ViewModels.FamiliesDataGridViewModel _familiesDataGridViewModel;
        private readonly Models.RevitFamiliesDataModel _revitFamiliesDataModel;

        public OpenFamilyIntoUIAsyncCommand(
           ViewModels.FamiliesSelectionViewModel familiesSelectionViewModel,
           ViewModels.FamiliesDataGridViewModel familiesDataGridViewModel,
           Models.RevitFamiliesDataModel revitFamiliesDataModel
           )
        {
            _revitFamiliesDataModel = revitFamiliesDataModel;
            _familiesSelectionViewModel = familiesSelectionViewModel;
            _familiesDataGridViewModel = familiesDataGridViewModel;

            _command = new AsyncRelayCommand(
                execute: ExecuteAsync,
                canExecute: () => !_familiesSelectionViewModel.IsWaitingForRevitCommandToFinish
            );

            _familiesSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
            _familiesDataGridViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }

        private async Task ExecuteAsync()
        {
            //deactivate the ui
            _familiesSelectionViewModel.IsWaitingForRevitCommandToFinish = true;

            try
            {
                (string message, MessageTypes messageType) = await RevitTask.RunAsync(
                    app =>
                    {
                        //Run Revit API code here
                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            // Execute the action to open the family into the UI
                            OpenFamilyIntoUIAction action = new OpenFamilyIntoUIAction(
                                revitModel: _revitFamiliesDataModel,
                                familiesSelectionViewModel: _familiesDataGridViewModel,
                                uiApp: app);
                            (string messageAction, MessageTypes messageActionType) = action.Execute(doc);

                            //TODO write messages to log...
                            _revitFamiliesDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            // return the message to the caller
                            return (messageAction, messageActionType);
                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the external event handler open family into Revit event: {ex.Message}", MessageTypes.Error);
                        }
                    });

                //pop message to user
                _familiesSelectionViewModel.AddMessage(message, messageType);
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

        private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(ViewModels.FamiliesSelectionViewModel.IsWaitingForRevitCommandToFinish))
            {
                _command.NotifyCanExecuteChanged();
            }
        }

        // Public ICommand wrapper so ViewModels can expose this as ICommand
        public ICommand Command => _command;

        public void Execute(object? parameter = null) => _command.Execute(null);
        public bool CanExecute(object? parameter = null) => _command.CanExecute(null);

        /// <summary>
        /// Must be called when the owning ViewModel is closing to prevent memory leaks.
        /// Unsubscribes from both ViewModels that were subscribed in the constructor.
        /// </summary>
        public void Dispose()
        {
            _familiesSelectionViewModel.PropertyChanged -= OnViewModelPropertyChanged;
            _familiesDataGridViewModel.PropertyChanged -= OnViewModelPropertyChanged;
        }
    }
}