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
using System.Collections.Generic;
using System.ComponentModel;

namespace duHastNet.PushIt.Models
{
    public class RevitDataModel : INotifyPropertyChanged
    {
        public Models.RoomsDataModelContainer _roomsContainer;
        public Models.CategoryDataModelContainer _categoriesContainer;
        public Models.ParameterDataModelContainer _parameterDataContainer;
        private readonly Models.AvailableParameterContainer _availableParameterContainer;
        private Models.Settings _settings;

        private Utils.Logging.SimpleLogger _logger;
        private string _revitDocumentTitle = string.Empty;

        // ── Startup messages ──────────────────────────────────────────────────

        /// <summary>
        /// Durable record of messages generated during the startup sequence
        /// (settings validation, parameter load, room load). Written by Revit
        /// actions and startup helpers; read by <c>Main.ExecuteInternal</c> to
        /// forward entries to the UI message store once the window is visible.
        /// <para>
        /// This list is never serialised. It is runtime-only and is cleared at
        /// the start of each startup or manual reload sequence via
        /// <see cref="ClearStartupMessages"/>.
        /// </para>
        /// </summary>
        private readonly List<(string Message, Utils.WPF.Stores.MessageTypes Type)> _startupMessages
            = new List<(string, Utils.WPF.Stores.MessageTypes)>();

        /// <summary>
        /// Appends a message to the startup message list.
        /// Called by Revit actions and startup helpers during the startup sequence.
        /// </summary>
        public void AddStartupMessage(string message, Utils.WPF.Stores.MessageTypes type)
        {
            _startupMessages.Add((message, type));
        }

        /// <summary>
        /// Clears all previously recorded startup messages.
        /// Call this at the beginning of any startup or reload sequence so that
        /// stale messages from a prior run are not re-surfaced.
        /// </summary>
        public void ClearStartupMessages()
        {
            _startupMessages.Clear();
        }

        /// <summary>
        /// Returns a read-only view of the startup messages accumulated so far.
        /// </summary>
        public IReadOnlyList<(string Message, Utils.WPF.Stores.MessageTypes Type)> GetStartupMessages()
        {
            return _startupMessages.AsReadOnly();
        }

        // ── Document title ────────────────────────────────────────────────────

        /// <summary>
        /// The title of the active Revit document, set during initialisation in
        /// <see cref="Main.ExecuteInternal"/> and surfaced in the UI via
        /// <see cref="ViewModels.RoomsMainViewModel.RevitDocumentTitle"/>.
        /// </summary>
        public string RevitDocumentTitle
        {
            get => _revitDocumentTitle;
            set
            {
                if (_revitDocumentTitle == value) return;
                _revitDocumentTitle = value;
                OnPropertyChanged(nameof(RevitDocumentTitle));
            }
        }

        public Settings Settings
        {
            get => _settings;
            set
            {
                _settings = value;

                // Load category data from the new settings
                LoadCategoryDataFromSettings();

                // Read column-header metadata from the data source
                LoadParameterData();
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        public void RaisePropertyChanged(string name)
        {
            OnPropertyChanged(name);
        }

        #region rooms

        public void AddRoom(Models.RoomDataModel room)
        {
            _roomsContainer.AddRoom(room);
        }

        public void AddNewRoom(Models.RoomDataModel room)
        {
            _roomsContainer.AddNewRoom(room);
        }

        public List<Models.RoomDataModel> GetAllRooms()
        {
            // Returns SoA rooms combined with any new rooms added through the UI
            return _roomsContainer.GetAllRoomsCombined();
        }

        public void ClearAllRooms()
        {
            _roomsContainer.ClearAllRooms();
        }

        public void ClearNewRooms()
        {
            _roomsContainer.ClearNewRooms();
        }

        public void ClearRooms()
        {
            _roomsContainer.ClearRooms();
        }

        public void RemovePlacedRevitRoom(long revitElementId)
        {
            _roomsContainer.RemovePlacedRevitRoom(revitElementId);
        }

        public void RemovePlacedNewRevitRoom(string roomId, long revitElementId)
        {
            _roomsContainer.RemoveNewPlacedRevitRoom(
               roomId: roomId,
               revitElementId: revitElementId
            );
        }

        public void AddPlacedRevitRoom(string roomId, Models.RoomRevit revitRoom)
        {
            _roomsContainer.AddPlacedRevitRoom(roomId, revitRoom);
        }

        public void AddPlacedNewRevitRoom(string roomId, Models.RoomRevit revitRoom)
        {
            _roomsContainer.AddPlacedNewRevitRoom(roomId, revitRoom);
        }

        public void AddPlacedSplitRevitRoom(string splitRoomId, Models.RoomRevit revitRoom)
        {
            _roomsContainer.AddPlacedSplitRevitRoom(splitRoomId, revitRoom);
        }

        public void RemovePlacedSplitRevitRoom(string splitRoomId, long revitElementId)
        {
            _roomsContainer.RemovePlacedSplitRevitRoom(splitRoomId, revitElementId);
        }

        public void AddSplitRoom(Models.RoomDataModel room)
        {
            _roomsContainer.AddSplitRoom(room);
        }

        public List<Models.RoomDataModel> GetAllSplitRooms()
        {
            return _roomsContainer.GetAllSplitRooms();
        }

        public void ClearSplitRooms()
        {
            _roomsContainer.ClearSplitRooms();
        }

        public int GetNextSplitCounter(string parentRoomId)
        {
            return _roomsContainer.GetNextSplitCounter(parentRoomId);
        }

        /// <summary>
        /// Loads room records from the active data source into the model.
        /// The provider is resolved via <see cref="Utilities.DataSourceFactory"/>
        /// based on <see cref="Settings.DataSource"/>.<see cref="DataSourceSettings.SourceType"/>.
        /// No caller needs to change when a new provider is added.
        /// </summary>
        /// <exception cref="InvalidOperationException">
        /// Re-thrown from the data source provider (e.g. missing drofus credentials,
        /// HTTP error) with a user-readable message. The caller —
        /// <see cref="Commands.ReloadDataFromFileAsyncCommand"/> — catches this and
        /// surfaces it in the UI message banner.
        /// </exception>
        public void LoadRoomsData()
        {
            if (_settings?.DataSource == null ||
                _settings.DataSource.SourceType == DataSourceType.None)
            {
                // No data source configured yet — nothing to load
                return;
            }

            var dataSource = Utilities.DataSourceFactory.Create(_settings.DataSource.SourceType);

            List<Models.RoomDataModel>? rooms;
            try
            {
                rooms = dataSource.GetRoomsData(_settings.DataSource);
            }
            catch (Exception ex)
            {
                // Wrap and re-throw so the message reaches the UI banner via
                // ReloadDataFromFileAsyncCommand's catch block, without crashing Revit.
                throw new InvalidOperationException(
                    $"Failed to load room data: {ex.Message}", ex);
            }

            if (rooms == null) return;

            foreach (Models.RoomDataModel room in rooms)
            {
                AddRoom(room);
            }
        }

        #endregion

        #region categories

        /// <summary>
        /// Adds Revit categories to the container, skipping any that are already present.
        /// Used to register all categories supported by the current Revit model.
        /// </summary>
        public void LoadSupportedCategoryData(List<Models.CategoryDataModel> revitCategories)
        {
            foreach (Models.CategoryDataModel category in revitCategories)
            {
                if (!_categoriesContainer.CategoryExists(category))
                {
                    AddCategory(category);
                }
            }
        }

        public void LoadCategoryDataFromSettings()
        {
            if (Settings == null) return;
            if (Settings.EnabledCategoryNames == null) return;

            ClearCategories();

            foreach (var cat in Settings.EnabledCategoryNames)
            {
                // All categories stored in settings are treated as enabled
                AddCategory(new Models.CategoryDataModel(cat, true));
            }
        }

        public void AddCategory(Models.CategoryDataModel category)
        {
            _categoriesContainer.AddCategory(category);
        }

        public List<Models.CategoryDataModel> GetAllCategories()
        {
            return _categoriesContainer.GetAllCategories();
        }

        public List<Models.CategoryDataModel> GetAllEnabledCategories()
        {
            return _categoriesContainer.GetAllEnabledCategories();
        }

        public void ClearCategories()
        {
            _categoriesContainer.ClearCategories();
        }

        public List<string> GetEnabledCategoryNames()
        {
            return _categoriesContainer.GetEnabledCategoryNames();
        }

        #endregion

        #region parameters

        /// <summary>
        /// Loads column-header metadata (parameter definitions) from the active
        /// data source without reading all room records.
        /// Used to populate the parameter list shown in the UI.
        /// The provider is resolved via <see cref="Utilities.DataSourceFactory"/>.
        /// </summary>
        /// <exception cref="InvalidOperationException">
        /// Re-thrown from the data source provider with a user-readable message.
        /// Surfaced in the UI banner by the calling command.
        /// </exception>
        public void LoadParameterData()
        {
            if (_settings?.DataSource == null ||
                _settings.DataSource.SourceType == DataSourceType.None)
            {
                return;
            }

            var dataSource = Utilities.DataSourceFactory.Create(_settings.DataSource.SourceType);

            List<Models.RoomDataProperty>? parameters;
            try
            {
                parameters = dataSource.GetHeaderProperties(_settings.DataSource);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException(
                    $"Failed to load parameter data: {ex.Message}", ex);
            }

            if (parameters == null) return;

            ClearParameters();

            foreach (var parameter in parameters)
            {
                AddParameter(parameter);
            }
        }

        public void AddParameter(Models.RoomDataProperty parameter)
        {
            _parameterDataContainer.AddParameter(parameter);
        }

        public List<Models.RoomDataProperty> GetAllParameters()
        {
            return _parameterDataContainer.GetAllParameters();
        }

        public void ClearParameters()
        {
            _parameterDataContainer.ClearParameters();
        }

        #endregion

        #region available parameters

        /// <summary>
        /// Adds a shared parameter to the available-parameters list.
        /// <para>
        /// Call this from <c>Main.LoadSharedParametersFromDocument</c> for every
        /// shared parameter that is bound in the active Revit document. Duplicate
        /// GUIDs are silently ignored by the container.
        /// </para>
        /// </summary>
        /// <param name="parameter">The parameter to register. Must not be <c>null</c>.</param>
        public void AddAvailableParameter(Models.AvailableParameter parameter)
        {
            _availableParameterContainer.AddParameter(parameter);
        }

        /// <summary>
        /// Returns a read-only snapshot of all shared parameters currently
        /// registered as available in the active Revit document.
        /// </summary>
        public IReadOnlyList<Models.AvailableParameter> GetAllAvailableParameters()
        {
            return _availableParameterContainer.GetAll();
        }

        /// <summary>
        /// Removes all entries from the available-parameters list.
        /// Call this before re-reading parameters from the document to avoid
        /// accumulating stale entries across reloads.
        /// </summary>
        public void ClearAvailableParameters()
        {
            _availableParameterContainer.Clear();
        }

        /// <summary>
        /// Returns <c>true</c> when a parameter with the supplied GUID exists in
        /// the available-parameters list (case-insensitive).
        /// </summary>
        /// <param name="guid">The GUID string to look up.</param>
        public bool AvailableParameterExistsByGuid(string guid)
        {
            return _availableParameterContainer.ContainsGuid(guid);
        }

        /// <summary>
        /// Returns <c>true</c> when a parameter with the supplied display name
        /// exists in the available-parameters list (case-insensitive).
        /// </summary>
        /// <param name="name">The display name to look up.</param>
        public bool AvailableParameterExistsByName(string name)
        {
            return _availableParameterContainer.ContainsName(name);
        }

        #endregion

        public void InitialiseLogger(string filePath)
        {
            _logger = new Utils.Logging.SimpleLogger(filePath);
        }

        public void LogMessages(List<(string, Utils.WPF.Stores.MessageTypes)> messages)
        {
            if (_logger == null) return;

            _logger.LogMessagesFireAndForget(messages);
        }

        public RevitDataModel()
        {
            _roomsContainer = new Models.RoomsDataModelContainer();
            _categoriesContainer = new Models.CategoryDataModelContainer();
            _parameterDataContainer = new ParameterDataModelContainer();
            _availableParameterContainer = new Models.AvailableParameterContainer();
        }
    }
}
