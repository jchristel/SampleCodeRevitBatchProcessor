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
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows.Input;

namespace duHastNet.PushIt.Commands
{
    public class SaveRoomDataAsyncCommand
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
            //deactivate the ui
            _roomsMainViewModel.IsWaitingForRevitCommandToFinish = true;

            try
            {
                (string message, Utils.WPF.Stores.MessageTypes messageType) = await RevitTask.RunAsync(
                    app =>
                    {
                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {
                            //add new rooms to the data model first
                            UpdateRoomDataModelWithNewRooms actionUpdate = new(
                                _revitDataModel,
                                _roomsMainViewModel
                            );
                            (string messageActionUpdate, Utils.WPF.Stores.MessageTypes messageActionTypeUpdate) =
                                actionUpdate.Execute(doc);
                            _revitDataModel.LogMessages(actionUpdate.GetLogMessagesAndLogTypes());

                            // sync split rooms from Revit into _splitRooms
                            UpdateRoomDataModelWithSplitRooms actionSplit = new(
                                _revitDataModel,
                                _roomsMainViewModel
                            );
                            (string messageActionSplit, Utils.WPF.Stores.MessageTypes messageActionTypeSplit) =
                                actionSplit.Execute(doc);
                            _revitDataModel.LogMessages(actionSplit.GetLogMessagesAndLogTypes());

                            // Refresh room data with current Revit model state
                            RefreshRoomDataWithRevitData action = new(
                                revitModel: _revitDataModel,
                                roomsMainViewModel: _roomsMainViewModel,
                                revitMockRooms: actionUpdate.CurrentMockRoomsData
                            );
                            (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) =
                                action.Execute(doc);
                            _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            // Get column-header properties from the data model.
                            // RevitDataModel.LoadParameterData() already loaded these via
                            // IDataSource.GetHeaderProperties() so we read them from the
                            // model rather than calling ReadRoomsData directly. This means
                            // SaveRoomDataAsyncCommand works for any data source provider,
                            // not just CSV.
                            var properties = _revitDataModel.GetAllParameters();

                            if (properties == null || properties.Count == 0)
                            {
                                return ("Failed to read column properties from the data model. " +
                                        "Ensure data has been loaded before saving.",
                                        MessageTypes.Error);
                            }

                            //build data rows
                            List<List<string>> roomData = BuildDataRows(
                                rooms: _revitDataModel.GetAllRooms(),
                                properties: properties
                            );

                            //build header rows
                            List<List<string>> headerRows = BuildHeaderRows(properties);

                            var writer = new duHastNet.FileIOWrapper.WriteToColumnBasedTextFile();

                            // Write header rows first
                            writer.WriteToTextFile(
                                filePath: _roomsMainViewModel.SaveFilePath,
                                header: [],
                                data: headerRows
                            );

                            if (writer.GetErrorHistory().Count > 0)
                            {
                                List<(string, Utils.WPF.Stores.MessageTypes)> errorsToLog = [];
                                foreach (var error in writer.GetErrorHistory())
                                    errorsToLog.Add((error, Utils.WPF.Stores.MessageTypes.Error));
                                _revitDataModel.LogMessages(errorsToLog);
                                return ("Failed to write data header. Check log for details.", MessageTypes.Error);
                            }

                            // Append data rows
                            writer.WriteToTextFile(
                                filePath: _roomsMainViewModel.SaveFilePath,
                                header: [],
                                data: roomData,
                                writeType: "a"
                            );

                            if (writer.GetErrorHistory().Count > 0)
                            {
                                List<(string, Utils.WPF.Stores.MessageTypes)> errorsToLog = [];
                                foreach (var error in writer.GetErrorHistory())
                                    errorsToLog.Add((error, Utils.WPF.Stores.MessageTypes.Error));
                                _revitDataModel.LogMessages(errorsToLog);
                                return ("Failed to write data. Check log for details.", MessageTypes.Error);
                            }

                            (string messageActionSave, Utils.WPF.Stores.MessageTypes messageActionTypeSafe) =
                                ($"Saved {roomData.Count} rooms to file: {_roomsMainViewModel.SaveFilePath}",
                                 MessageTypes.Information);

                            return (
                                $"{messageActionUpdate}\n{messageAction}\n{messageActionSave}",
                                Utilities.MessageActionTypesUtils.CombineMessageActionType(
                                    [messageActionTypeUpdate, messageActionType, messageActionTypeSafe])
                            );
                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the save handler: {ex.Message}",
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
                //activate the ui
                _roomsMainViewModel.IsWaitingForRevitCommandToFinish = false;
            }
        }

        private List<List<string>> BuildHeaderRows(List<Models.RoomDataProperty> properties)
        {
            List<List<string>> headerRows = [];
            List<string> headerRow0 = [];
            List<string> headerRow1 = [];
            List<string> headerRow2 = [];
            List<string> headerRow3 = [];
            List<string> headerRow4 = [];

            foreach (var property in properties)
            {
                headerRow0.Add(property.Name);
                headerRow1.Add(property.ParameterGUID);
                headerRow2.Add(property.IsReadOnly.ToString());
                headerRow3.Add(property.ShowInUI.ToString());
                headerRow4.Add(property.RevitTakesPrecedenceAfterInitialPush.ToString());
            }

            // Append synthetic count column
            headerRow0.Add("Count");
            headerRow1.Add(string.Empty);
            headerRow2.Add(string.Empty);
            headerRow3.Add(string.Empty);
            headerRow4.Add(string.Empty);

            headerRows.Add(headerRow0);
            headerRows.Add(headerRow1);
            headerRows.Add(headerRow2);
            headerRows.Add(headerRow3);
            headerRows.Add(headerRow4);
            return headerRows;
        }

        /// <summary>
        /// Builds a single data row from a room's properties in the order defined
        /// by <paramref name="properties"/>.
        /// </summary>
        private List<string> BuildDataRowFromRoom(
            Models.RoomBase room,
            List<Models.RoomDataProperty> properties,
            int countPushed = 0)
        {
            List<string> dataRow = [];

            foreach (var property in properties)
            {
                string propertyValue = room.GetPropertyValueByGUID(property.ParameterGUID);
                dataRow.Add(propertyValue ?? string.Empty);
            }

            dataRow.Add(countPushed.ToString());

            return dataRow;
        }

        /// <summary>
        /// Builds all data rows for the provided room list.
        /// </summary>
        private List<List<string>> BuildDataRows(
            List<Models.RoomDataModel> rooms,
            List<Models.RoomDataProperty> properties)
        {
            List<List<string>> dataRows = [];

            foreach (Models.RoomDataModel room in rooms)
            {
                if (room.MatchingRevitRooms.Count == 0)
                {
                    dataRows.Add(BuildDataRowFromRoom(room, properties));
                }
                else
                {
                    foreach (var matched in room.MatchingRevitRooms)
                        dataRows.Add(BuildDataRowFromRoom(matched, properties, countPushed: 1));
                }
            }

            return dataRows;
        }

        private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(ViewModels.RoomsMainViewModel.IsWaitingForRevitCommandToFinish) ||
                e.PropertyName == nameof(ViewModels.RoomsMainViewModel.HasErrors))
            {
                _command.NotifyCanExecuteChanged();
            }
        }

        public SaveRoomDataAsyncCommand(
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
