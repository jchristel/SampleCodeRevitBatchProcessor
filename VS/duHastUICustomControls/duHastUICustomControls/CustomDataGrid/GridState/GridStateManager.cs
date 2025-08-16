//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// Written by Claude
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


using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Threading;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Manages saving, loading, and organizing DataGrid states
    /// </summary>
    public class GridStateManager
    {
        private readonly GridStateOptions _options;
        private readonly Dictionary<string, List<DataGridState>> _stateCache;
        private readonly DispatcherTimer _autoSaveTimer;
        private readonly object _lockObject = new object();

        #region Events

        /// <summary>
        /// Fired when a state is successfully saved
        /// </summary>
        public event EventHandler<GridStateEventArgs> StateSaved;

        /// <summary>
        /// Fired when a state is successfully loaded
        /// </summary>
        public event EventHandler<GridStateEventArgs> StateLoaded;

        /// <summary>
        /// Fired when a state is deleted
        /// </summary>
        public event EventHandler<GridStateEventArgs> StateDeleted;

        /// <summary>
        /// Fired when an error occurs during state operations
        /// </summary>
        public event EventHandler<GridStateEventArgs> StateError;

        #endregion

        #region Constructor

        public GridStateManager(GridStateOptions options = null)
        {
            _options = options ?? new GridStateOptions();
            _stateCache = new Dictionary<string, List<DataGridState>>();

            // Set up auto-save timer
            if (_options.AutoSave)
            {
                _autoSaveTimer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromMilliseconds(_options.AutoSaveDelay)
                };
                _autoSaveTimer.Tick += OnAutoSaveTick;
            }

            // Ensure save directory exists
            EnsureSaveDirectoryExists();
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Saves a grid state with the specified name
        /// </summary>
        public async Task<bool> SaveStateAsync(string gridId, string stateName, DataGridState state)
        {
            try
            {
                if (string.IsNullOrEmpty(gridId) || string.IsNullOrEmpty(stateName) || state == null)
                    throw new ArgumentException("GridId, StateName, and State cannot be null or empty");

                state.GridId = gridId;
                state.StateName = stateName;
                state.LastModified = DateTime.Now;

                List<DataGridState> statesToRemove = null;

                // Update cache and determine states to remove (do this in lock)
                lock (_lockObject)
                {
                    if (!_stateCache.ContainsKey(gridId))
                    {
                        _stateCache[gridId] = new List<DataGridState>();
                    }

                    // Remove existing state with same name
                    _stateCache[gridId].RemoveAll(s => s.StateName == stateName);

                    // Add new state
                    _stateCache[gridId].Add(state);

                    // Enforce max states limit
                    if (_stateCache[gridId].Count > _options.MaxStatesPerGrid)
                    {
                        statesToRemove = _stateCache[gridId]
                            .OrderBy(s => s.LastModified)
                            .Take(_stateCache[gridId].Count - _options.MaxStatesPerGrid)
                            .ToList();

                        // Remove from cache
                        foreach (var stateToRemove in statesToRemove)
                        {
                            _stateCache[gridId].Remove(stateToRemove);
                        }
                    }
                }

                // Delete files outside the lock (async operations)
                if (statesToRemove != null)
                {
                    foreach (var stateToRemove in statesToRemove)
                    {
                        await DeleteStateFileAsync(gridId, stateToRemove.StateName);
                    }
                }

                // Save to file
                await SaveStateToFileAsync(state);

                StateSaved?.Invoke(this, new GridStateEventArgs(gridId, stateName, state));
                return true;
            }
            catch (Exception ex)
            {
                StateError?.Invoke(this, new GridStateEventArgs(gridId, stateName, ex));
                return false;
            }
        }

        /// <summary>
        /// Loads a grid state by name
        /// </summary>
        public async Task<DataGridState> LoadStateAsync(string gridId, string stateName)
        {
            try
            {
                if (string.IsNullOrEmpty(gridId) || string.IsNullOrEmpty(stateName))
                    throw new ArgumentException("GridId and StateName cannot be null or empty");

                // Try cache first
                lock (_lockObject)
                {
                    if (_stateCache.ContainsKey(gridId))
                    {
                        var cachedState = _stateCache[gridId].FirstOrDefault(s => s.StateName == stateName);
                        if (cachedState != null)
                        {
                            StateLoaded?.Invoke(this, new GridStateEventArgs(gridId, stateName, cachedState));
                            return cachedState;
                        }
                    }
                }

                // Load from file
                var state = await LoadStateFromFileAsync(gridId, stateName);
                if (state != null)
                {
                    // Update cache
                    lock (_lockObject)
                    {
                        if (!_stateCache.ContainsKey(gridId))
                        {
                            _stateCache[gridId] = new List<DataGridState>();
                        }
                        _stateCache[gridId].Add(state);
                    }

                    StateLoaded?.Invoke(this, new GridStateEventArgs(gridId, stateName, state));
                }

                return state;
            }
            catch (Exception ex)
            {
                StateError?.Invoke(this, new GridStateEventArgs(gridId, stateName, ex));
                return null;
            }
        }

        /// <summary>
        /// Gets all available state names for a grid
        /// </summary>
        public async Task<List<string>> GetAvailableStatesAsync(string gridId)
        {
            try
            {
                var stateNames = new HashSet<string>();

                // Add from cache
                lock (_lockObject)
                {
                    if (_stateCache.ContainsKey(gridId))
                    {
                        foreach (var state in _stateCache[gridId])
                        {
                            stateNames.Add(state.StateName);
                        }
                    }
                }

                // Add from files
                var directory = GetGridDirectory(gridId);
                if (Directory.Exists(directory))
                {
                    var files = Directory.GetFiles(directory, $"*{_options.FileExtension}");
                    foreach (var file in files)
                    {
                        var fileName = Path.GetFileNameWithoutExtension(file);
                        stateNames.Add(fileName);
                    }
                }

                return stateNames.OrderBy(n => n).ToList();
            }
            catch (Exception ex)
            {
                StateError?.Invoke(this, new GridStateEventArgs(gridId, null, ex));
                return new List<string>();
            }
        }

        /// <summary>
        /// Deletes a saved state
        /// </summary>
        public async Task<bool> DeleteStateAsync(string gridId, string stateName)
        {
            try
            {
                if (string.IsNullOrEmpty(gridId) || string.IsNullOrEmpty(stateName))
                    throw new ArgumentException("GridId and StateName cannot be null or empty");

                // Remove from cache
                lock (_lockObject)
                {
                    if (_stateCache.ContainsKey(gridId))
                    {
                        _stateCache[gridId].RemoveAll(s => s.StateName == stateName);
                    }
                }

                // Delete file
                await DeleteStateFileAsync(gridId, stateName);

                StateDeleted?.Invoke(this, new GridStateEventArgs(gridId, stateName));
                return true;
            }
            catch (Exception ex)
            {
                StateError?.Invoke(this, new GridStateEventArgs(gridId, stateName, ex));
                return false;
            }
        }

        /// <summary>
        /// Gets detailed information about all states for a grid
        /// </summary>
        public async Task<List<DataGridState>> GetStateInfoAsync(string gridId)
        {
            try
            {
                var states = new List<DataGridState>();

                // Load all states for this grid
                var stateNames = await GetAvailableStatesAsync(gridId);
                foreach (var stateName in stateNames)
                {
                    var state = await LoadStateAsync(gridId, stateName);
                    if (state != null)
                    {
                        states.Add(state);
                    }
                }

                return states.OrderByDescending(s => s.LastModified).ToList();
            }
            catch (Exception ex)
            {
                StateError?.Invoke(this, new GridStateEventArgs(gridId, null, ex));
                return new List<DataGridState>();
            }
        }

        /// <summary>
        /// Schedules an auto-save operation (if auto-save is enabled)
        /// </summary>
        public void ScheduleAutoSave(string gridId, string stateName, DataGridState state)
        {
            if (!_options.AutoSave || _autoSaveTimer == null)
                return;

            _autoSaveTimer.Tag = new { GridId = gridId, StateName = stateName, State = state };
            _autoSaveTimer.Stop();
            _autoSaveTimer.Start();
        }

        /// <summary>
        /// Clears the state cache for a specific grid
        /// </summary>
        public void ClearCache(string gridId = null)
        {
            lock (_lockObject)
            {
                if (gridId == null)
                {
                    _stateCache.Clear();
                }
                else if (_stateCache.ContainsKey(gridId))
                {
                    _stateCache.Remove(gridId);
                }
            }
        }

        #endregion

        #region Private Methods

        private void EnsureSaveDirectoryExists()
        {
            if (string.IsNullOrEmpty(_options.DefaultSaveLocation))
            {
                var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
                _options.DefaultSaveLocation = Path.Combine(appDataPath, "DuHastNet", "GridStates");
            }

            if (!Directory.Exists(_options.DefaultSaveLocation))
            {
                Directory.CreateDirectory(_options.DefaultSaveLocation);
            }
        }

        private string GetGridDirectory(string gridId)
        {
            var sanitizedGridId = SanitizeFileName(gridId);
            return Path.Combine(_options.DefaultSaveLocation, sanitizedGridId);
        }

        private string GetStateFilePath(string gridId, string stateName)
        {
            var directory = GetGridDirectory(gridId);
            var sanitizedStateName = SanitizeFileName(stateName);
            return Path.Combine(directory, $"{sanitizedStateName}{_options.FileExtension}");
        }

        private static string SanitizeFileName(string fileName)
        {
            var invalidChars = Path.GetInvalidFileNameChars();
            return new string(fileName.Where(c => !invalidChars.Contains(c)).ToArray());
        }

        private async Task SaveStateToFileAsync(DataGridState state)
        {
            var directory = GetGridDirectory(state.GridId);
            if (!Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            var filePath = GetStateFilePath(state.GridId, state.StateName);

            var json = JsonConvert.SerializeObject(state, Formatting.Indented);

            // Use StreamWriter for compatibility with older .NET Framework versions
            using (var writer = new StreamWriter(filePath))
            {
                await writer.WriteAsync(json);
            }
        }

        private async Task<DataGridState> LoadStateFromFileAsync(string gridId, string stateName)
        {
            var filePath = GetStateFilePath(gridId, stateName);
            if (!File.Exists(filePath))
                return null;

            string json;
            // Use StreamReader for compatibility with older .NET Framework versions
            using (var reader = new StreamReader(filePath))
            {
                json = await reader.ReadToEndAsync();
            }

            return JsonConvert.DeserializeObject<DataGridState>(json);
        }

        private async Task DeleteStateFileAsync(string gridId, string stateName)
        {
            var filePath = GetStateFilePath(gridId, stateName);
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }

            // Clean up directory if empty
            var directory = GetGridDirectory(gridId);
            if (Directory.Exists(directory) && !Directory.EnumerateFileSystemEntries(directory).Any())
            {
                Directory.Delete(directory);
            }
        }

        private async void OnAutoSaveTick(object sender, EventArgs e)
        {
            _autoSaveTimer.Stop();

            var tagObj = _autoSaveTimer.Tag;
            if (tagObj != null)
            {
                var tag = (dynamic)tagObj;
                await SaveStateAsync(tag.GridId, tag.StateName, tag.State);
            }
        }

        #endregion

        #region IDisposable

        public void Dispose()
        {
            if (_autoSaveTimer != null)
            {
                _autoSaveTimer.Stop();
                _autoSaveTimer.Tick -= OnAutoSaveTick;
            }
        }

        #endregion
    }
}