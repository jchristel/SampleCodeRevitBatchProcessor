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
using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.Utilities;
using duHastNet.PushIt.ViewModels.DataSource;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.ComponentModel;
using System.Windows.Input;

namespace duHastNet.PushIt.Commands
{
    /// <summary>
    /// Clears the room data model and reloads it from the currently configured
    /// data source, then refreshes the Revit model to match.
    /// <para>
    /// Previously this command keyed its <c>CanExecute</c> on
    /// <c>RoomsMainViewModel.DataFilePathValid</c>. That property no longer
    /// exists; the guard is now
    /// <c>!DataSourceViewModel.HasValidationErrors</c>, which works for any
    /// data source provider — not just CSV files.
    /// </para>
    /// </summary>
    public class ReloadDataFromFileAsyncCommand
    {
        private readonly ViewModels.RoomsMainViewModel _roomsMainViewModel;
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly AsyncRelayCommand _command;

        public ICommand Command => _command;

        private bool CanExecute()
        {
            return !_roomsMainViewModel.IsWaitingForRevitCommandToFinish
                && !_roomsMainViewModel.DataSourceViewModel.HasValidationErrors;
        }

        private async System.Threading.Tasks.Task Execute()
        {
            // Flush any in-progress edits in the DataSourceViewModel back to the
            // settings model before loading, so the correct path / connection
            // details are in place when RevitDataModel.LoadRoomsData() is called.
            _roomsMainViewModel.DataSourceViewModel.SaveToSettings(
                _revitDataModel.Settings.DataSource);

            _roomsMainViewModel.IsWaitingForRevitCommandToFinish = true;

            try
            {
                (string message, Utils.WPF.Stores.MessageTypes messageType) = await RevitTask.RunAsync(
                    app =>
                    {
                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            _revitDataModel.ClearAllRooms();
                            _revitDataModel.LoadRoomsData();

                            _revitDataModel.ClearParameters();
                            _revitDataModel.LoadParameterData();

                            VerifyParametersInModel actionVerify = new(_revitDataModel);
                            (string messageActionVerify, Utils.WPF.Stores.MessageTypes messageActionTypeVerify) =
                                actionVerify.Execute(doc);
                            _revitDataModel.LogMessages(actionVerify.GetLogMessagesAndLogTypes());

                            if (messageActionTypeVerify == MessageTypes.Error)
                            {
                                return (messageActionVerify, messageActionTypeVerify);
                            }

                            UpdateRoomDataModelWithNewRooms actionUpdate = new(
                                _revitDataModel,
                                _roomsMainViewModel);
                            (string messageActionUpdate, Utils.WPF.Stores.MessageTypes messageActionTypeUpdate) =
                                actionUpdate.Execute(doc);
                            _revitDataModel.LogMessages(actionUpdate.GetLogMessagesAndLogTypes());

                            RefreshRoomDataWithRevitData action = new(
                                revitModel: _revitDataModel,
                                roomsMainViewModel: _roomsMainViewModel,
                                revitMockRooms: actionUpdate.CurrentMockRoomsData);
                            (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) =
                                action.Execute(doc);
                            _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            return (
                                $"{messageActionUpdate}\n{messageAction}",
                                Utilities.MessageActionTypesUtils.CombineMessageActionType(
                                    [messageActionTypeUpdate, messageActionType])
                            );
                        }
                        catch (Exception ex)
                        {
                            return (
                                $"An exception occurred within the reload handler: {ex.Message}",
                                Utils.WPF.Stores.MessageTypes.Error);
                        }
                    });

                if (messageType == MessageTypes.Information)
                {
                    _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
                }

                _roomsMainViewModel.AddMessage(message, messageType);
            }
            catch (Exception ex)
            {
                _roomsMainViewModel.AddMessage(ex.Message, MessageTypes.Error);
            }
            finally
            {
                _roomsMainViewModel.IsWaitingForRevitCommandToFinish = false;
            }
        }

        private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            // Re-evaluate CanExecute when the waiting flag or data source
            // validation state changes.
            if (e.PropertyName == nameof(ViewModels.RoomsMainViewModel.IsWaitingForRevitCommandToFinish) ||
                e.PropertyName == nameof(ViewModels.RoomsMainViewModel.HasErrors))
            {
                _command.NotifyCanExecuteChanged();
            }
        }

        public ReloadDataFromFileAsyncCommand(
            ViewModels.RoomsMainViewModel roomsMainViewModel,
            Models.RevitDataModel revitDataModel)
        {
            _revitDataModel = revitDataModel;
            _roomsMainViewModel = roomsMainViewModel;
            _command = new AsyncRelayCommand(Execute, CanExecute);
            _roomsMainViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
