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

using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.Utilities;
using duHastNet.Utils.WPF.Stores;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.ComponentModel;

namespace duHastNet.PushIt.Commands
{
    public class SaveRoomDataAsyncCommand : Utils.WPF.Commands.CommandBase
    {
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;
        private readonly Models.RevitDataModel _revitDataModel;

        public override bool CanExecute(object parameter)
        {
            // check if IsWaitingForRevitCommandToFinish is true
            if (_roomsSelectionViewModel.IsWaitingForRevitCommandToFinish)
            {
                return false;
            }
            return _roomsSelectionViewModel.DataFilePathValid && base.CanExecute(parameter);
        }

        public override async void Execute(object parameter)
        {
            //deactivate the ui
            _roomsSelectionViewModel.IsWaitingForRevitCommandToFinish = true;

            try
            {
                (string message, Utils.WPF.Stores.MessageTypes messageType) = await RevitTask.RunAsync(
                    app =>
                    {
                        //Run Revit API code here

                        Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;
                        try
                        {

                            //add new rooms to the data model first
                            UpdateRoomDataModelWithNewRooms actionUpdate = new PushIt.RevitActions.UpdateRoomDataModelWithNewRooms(_revitDataModel, _roomsSelectionViewModel);
                            (string messageActionUpdate, Utils.WPF.Stores.MessageTypes messageActionTypeUpdate) = actionUpdate.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(actionUpdate.GetLogMessagesAndLogTypes());

                            // Execute the action to refresh the room data with the Revit data
                            RefreshRoomDataWithRevitData action = new RefreshRoomDataWithRevitData(
                                revitModel: _revitDataModel,
                                roomsSelectionViewModel: _roomsSelectionViewModel,
                                revitMockRooms: actionUpdate.CurrentMockRoomsData //re-use mock room data to speed things up
                            );

                            (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) = action.Execute(doc);

                            //write messages to log...
                            _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                            //get data properties from the current soa file
                            var properties = duHastNet.PushIt.Utilities.ReadRoomsData.GetRoomsDataHeaderRows(_revitDataModel.Settings.DataPath);

                            // check if the properties are null
                            if (properties == null)
                            {
                                return ("Failed to read properties from data file.", MessageTypes.Error);
                            }

                            //build data rows
                            List<List<string>> roomData = BuildDataRows(
                                rooms: _revitDataModel.GetAllRooms(),
                                properties: properties
                            );

                            //build header rows
                            List<List<string>> headerRows = BuildHeaderRows(properties);

                            var writer = new duHastNet.FileIOWrapper.WriteToColumnBasedTextFile();

                            //write the data to the file, start with the header rows
                            writer.WriteToTextFile(
                                filePath: _roomsSelectionViewModel.SaveFilePath,
                                header: new List<string>(), //write empty header since this supports single line headers only
                                data: headerRows
                            );

                            //check if any probs
                            if (writer.GetErrorHistory().Count > 0)
                            {
                                List<(string, Utils.WPF.Stores.MessageTypes)> errorsToLog = new List<(string, Utils.WPF.Stores.MessageTypes)>();
                                foreach (var error in writer.GetErrorHistory())
                                {
                                    errorsToLog.Add((error, Utils.WPF.Stores.MessageTypes.Error));
                                }
                                //log error messages
                                _revitDataModel.LogMessages(errorsToLog);
                                //pop message to user
                                return ("Failed to write data header. Check log for details.", MessageTypes.Error);
                            }

                            //write the data to the file
                            writer.WriteToTextFile(
                                filePath: _roomsSelectionViewModel.SaveFilePath,
                                header: new List<string>(), //write empty header since this supports single line headers only
                                data: roomData,
                                writeType: "a"
                            );

                            //check if any probs
                            if (writer.GetErrorHistory().Count > 0)
                            {
                                List<(string, Utils.WPF.Stores.MessageTypes)> errorsToLog = new List<(string, Utils.WPF.Stores.MessageTypes)>();
                                foreach (var error in writer.GetErrorHistory())
                                {
                                    errorsToLog.Add((error, Utils.WPF.Stores.MessageTypes.Error));
                                }
                                //log error messages
                                _revitDataModel.LogMessages(errorsToLog);
                                //pop message to user
                                return ("Failed to write data. Check log for details.", MessageTypes.Error);
                            }

                            //set a succesfull file saved message
                            (string messageActionSave, Utils.WPF.Stores.MessageTypes messageActionTypeSafe) =
                                ($"Saved {roomData.Count} rooms to file: {_roomsSelectionViewModel.SaveFilePath}", MessageTypes.Information);

                            // return the messages to the caller
                            return (
                                $"{messageActionUpdate}\n{messageAction}\n{messageActionSave}",
                                Utilities.MessageActionTypesUtils.CombineMessageActionType(new List<MessageTypes> { messageActionTypeUpdate, messageActionType, messageActionTypeSafe })
                            );
                        }
                        catch (Exception ex)
                        {
                            return ($"An exception occurred within the external event handler update after reload data event: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
                        }
                    });

                if (messageType == MessageTypes.Information)
                {
                    // raise event to notify the view model that the model has been updated
                    _revitDataModel.RaisePropertyChanged(PropertyChangedEventNames.DATA_MODEL_ROOMS_UPDATED);
                }

                //pop message to user
                _roomsSelectionViewModel.AddMessage(message, messageType);
            }
            catch (Exception ex)
            {
                _roomsSelectionViewModel.AddMessage(ex.Message, MessageTypes.Error);
            }
            finally
            {
                //activate the ui
                _roomsSelectionViewModel.IsWaitingForRevitCommandToFinish = false;
            }
        }



        private List<List<string>> BuildHeaderRows(List<Models.RoomDataProperty> properties)
        {
            //build header rows
            List<List<string>> headerRows = new List<List<string>>();
            List<string> headerRow0 = new List<string>();
            List<string> headerRow1 = new List<string>();
            List<string> headerRow2 = new List<string>();
            List<string> headerRow3 = new List<string>();

            foreach (var property in properties)
            {
                headerRow0.Add(property.Name);
                headerRow1.Add(property.ParameterGUID);
                headerRow2.Add(property.IsReadOnly.ToString());
                headerRow3.Add(property.ShowInUI.ToString());
            }
            //add the count values
            headerRow0.Add("Count");
            headerRow1.Add(string.Empty);
            headerRow2.Add(string.Empty);
            headerRow3.Add(string.Empty);

            headerRow0.Add("Split Count");
            headerRow1.Add(string.Empty);
            headerRow2.Add(string.Empty);
            headerRow3.Add(string.Empty);


            headerRows.Add(headerRow0);
            headerRows.Add(headerRow1);
            headerRows.Add(headerRow2);
            headerRows.Add(headerRow3);
            return headerRows;
        }


        /// <summary>
        /// builds a list of property values from a Room data model room.
        /// order of properties is defined by properties list past in.
        /// </summary>
        /// <param name="room"></param>
        /// <param name="properties"></param>
        /// <returns></returns>
        private List<string> BuildDataRowFromRoom(
            Models.RoomBase room,
            List<Models.RoomDataProperty> properties,
            int countPushed = 0,
            int countSplit = 0)
        {
            // get the property values for the room
            List<string> dataRow = new List<string>();

            // get the properties from the data model
            foreach (var property in properties)
            {
                string propertyValue = room.GetPropertyValueByGUID(property.ParameterGUID);
                if (propertyValue == null)
                {
                    dataRow.Add(string.Empty);
                }
                else
                {
                    dataRow.Add(propertyValue);
                }
            }

            // add count and split count
            dataRow.Add(countPushed.ToString());
            dataRow.Add(countSplit.ToString());

            return dataRow;
        }


        /// <summary>
        /// Build the data rows for the rooms
        /// </summary>
        /// <param name="rooms"></param>
        /// <param name="properties"></param>
        /// <returns></returns>
        private List<List<string>> BuildDataRows(List<Models.RoomDataModel> rooms,
            List<Models.RoomDataProperty> properties
        )
        {
            //build data rows
            List<List<string>> dataRows = new List<List<string>>();

            //loop over each room and get its report data
            foreach (Models.RoomDataModel room in rooms)
            {

                //build data for non pushed room (no matching room or split room in revit )
                if (room.MatchingRevitRooms.Count == 0 &&
                    room.MatchingSplitRevitRooms.Count == 0)
                {
                    // get the property values for the room
                    List<string> dataRow = BuildDataRowFromRoom(
                        room,
                        properties);

                    //add to overall data
                    dataRows.Add(dataRow);
                }
                else
                {
                    // need to check how many matching rooms there are and add 1 entry for each of them
                    for (int i = 0; i < room.MatchingRevitRooms.Count; i++)
                    {
                        // get the property values for the room
                        List<string> dataRow = BuildDataRowFromRoom(
                            room: room.MatchingRevitRooms[i],
                            properties: properties,
                            countPushed: 1,
                            countSplit: 0
                        );

                        //add to overall data
                        dataRows.Add(dataRow);
                    }

                    //loop over any split rooms:
                    for (int i = 0; i < room.MatchingSplitRevitRooms.Count; i++)
                    {
                        // get the property values for the room
                        List<string> dataRow = BuildDataRowFromRoom(
                            room: room.MatchingSplitRevitRooms[i],
                            properties: properties,
                            countPushed: 0,
                            countSplit: 1
                        );

                        //add to overall data
                        dataRows.Add(dataRow);
                    }
                }
            }
            return dataRows;
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.DataFilePath) ||
                e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.IsWaitingForRevitCommandToFinish))
            {
                OnCanExecutedChanged();
            }
        }


        public SaveRoomDataAsyncCommand(
            ViewModels.RoomsSelectionViewModel roomsSelectionViewModel,
            Models.RevitDataModel revitDataModel
            )
        {
            _revitDataModel = revitDataModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _roomsSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
