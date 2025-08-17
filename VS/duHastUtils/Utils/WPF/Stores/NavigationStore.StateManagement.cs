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


using duHastNet.Utils.WPF.Interfaces;
using System;
using System.Collections.Generic;

namespace duHastNet.Utils.WPF.Stores
{
    /// <summary>
    /// Simple state management functionality for NavigationStore (one state per ViewModel)
    /// </summary>
    public partial class NavigationStore
    {
        #region INavigationStateSupport Implementation

        /// <summary>
        /// Gets the number of stored states
        /// </summary>
        public int StoredStateCount
        {
            get
            {
                lock (_stateLock)
                {
                    return _stateManager.GetAllStates().Count;
                }
            }
        }

        #endregion

        #region State Management Properties

        /// <summary>
        /// Loads state for the current ViewModel (if it supports state management)
        /// </summary>
        private void LoadCurrentViewModelState()
        {
            try
            {
                var key = GetCurrentViewModelKey();
                if (string.IsNullOrEmpty(key))
                    return;

                // Check if current ViewModel supports state management using the interface
                if (_currentViewModel is IGridStateSupport gridStateSupport &&
                    gridStateSupport.StateManagementEnabled)
                {
                    var state = _stateManager.LoadState(key).Result;
                    if (state != null)
                    {
                        // Delay loading slightly to allow ViewModel to initialize
                        System.Windows.Application.Current?.Dispatcher.BeginInvoke(
                            new Action(() => {
                                try
                                {
                                    var success = gridStateSupport.ApplyStateToViewModel(state);

                                    // Raise event
                                    if (success)
                                    {
                                        OnStateOperationCompleted(new GridStateEventArgs(state.GridId, state.StateName, state));
                                    }
                                    else
                                    {
                                        OnStateOperationCompleted(CreateErrorEventArgs(
                                            state.GridId,
                                            state.StateName,
                                            "Failed to apply state to ViewModel"));
                                    }
                                }
                                catch (Exception ex)
                                {
                                    System.Diagnostics.Debug.WriteLine($"Error applying state to ViewModel: {ex.Message}");
                                    OnStateOperationCompleted(CreateErrorEventArgs(
                                            state.GridId,
                                            state.StateName,
                                            "Failed to apply state to ViewModel"));
                                }
                            }),
                            System.Windows.Threading.DispatcherPriority.Background);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading ViewModel state: {ex.Message}");

                // Raise error event
                OnStateOperationCompleted(new GridStateEventArgs(
                    GetCurrentViewModelKey() ?? "Unknown",
                    "Default",
                    ex));
            }
        }

        #endregion

        #region Public State Management Methods

        /// <summary>
        /// Saves a ViewModel's grid state
        /// </summary>
        /// <param name="viewModelKey">Unique key for the ViewModel</param>
        /// <param name="state">The grid state to save</param>
        public void SaveViewModelState(string viewModelKey, IGridState state)
        {
            if (string.IsNullOrEmpty(viewModelKey) || state == null)
                return;

            // Fire and forget - don't wait for completion
            _ = _stateManager.SaveState(viewModelKey, state);
        }

        /// <summary>
        /// Loads a ViewModel's grid state
        /// </summary>
        /// <param name="viewModelKey">Unique key for the ViewModel</param>
        /// <returns>The saved grid state, or null if not found</returns>
        public IGridState LoadViewModelState(string viewModelKey)
        {
            if (string.IsNullOrEmpty(viewModelKey))
                return null;

            return _stateManager.LoadState(viewModelKey).Result;
        }

        /// <summary>
        /// Gets all saved ViewModel states
        /// </summary>
        /// <returns>Dictionary of all saved states</returns>
        public Dictionary<string, IGridState> GetAllViewModelStates()
        {
            var allStates = _stateManager.GetAllStates();
            var result = new Dictionary<string, IGridState>();

            foreach (var kvp in allStates)
            {
                result[kvp.Key] = kvp.Value;
            }

            return result;
        }

        /// <summary>
        /// Clears state for a specific ViewModel
        /// </summary>
        /// <param name="viewModelKey">Unique key for the ViewModel</param>
        public void ClearViewModelState(string viewModelKey)
        {
            if (string.IsNullOrEmpty(viewModelKey))
                return;

            _stateManager.ClearState(viewModelKey);
        }

        /// <summary>
        /// Clears all saved ViewModel states
        /// </summary>
        public void ClearAllViewModelStates()
        {
            _stateManager.ClearAllStates();
        }

        /// <summary>
        /// Checks if a state exists for the specified ViewModel
        /// </summary>
        /// <param name="viewModelKey">Unique key for the ViewModel</param>
        /// <returns>True if a state exists</returns>
        public bool HasViewModelState(string viewModelKey)
        {
            return _stateManager.StateExists(viewModelKey);
        }

        #endregion

        #region Settings Integration

        /// <summary>
        /// Loads ViewModel states from application settings
        /// Called during application startup
        /// </summary>
        /// <param name="gridStatesFromSettings">Serialized states from settings</param>
        public void LoadStatesFromSettings(Dictionary<string, string> gridStatesFromSettings)
        {
            if (gridStatesFromSettings == null)
                return;

            var statesToLoad = new Dictionary<string, IGridState>();

            foreach (var kvp in gridStatesFromSettings)
            {
                try
                {
                    if (!string.IsNullOrEmpty(kvp.Value))
                    {
                        var state = new States.GridState ();
                        if (state.Deserialize(kvp.Value))
                        {
                            statesToLoad[kvp.Key] = state;
                        }
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error loading state for {kvp.Key}: {ex.Message}");
                }
            }

            if (statesToLoad.Count > 0)
            {
                _stateManager.LoadStatesFromExternal(statesToLoad);
            }
        }

        /// <summary>
        /// Gets ViewModel states formatted for saving to application settings
        /// Called during application shutdown
        /// </summary>
        /// <returns>Dictionary of serialized states for settings</returns>
        public Dictionary<string, string> GetStatesForSettings()
        {
            var settingsData = new Dictionary<string, string>();
            var allStates = _stateManager.GetAllStates();

            foreach (var kvp in allStates)
            {
                try
                {
                    var serialized = kvp.Value?.Serialize();
                    if (!string.IsNullOrEmpty(serialized))
                    {
                        settingsData[kvp.Key] = serialized;
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error serializing state for {kvp.Key}: {ex.Message}");
                }
            }

            return settingsData;
        }

        #endregion

        #region State Debug Information

        /// <summary>
        /// Gets debug information about stored states
        /// </summary>
        /// <returns>Debug information string</returns>
        public string GetStateDebugInfo()
        {
            return _stateManager.GetDebugInfo();
        }

        /// <summary>
        /// Gets comprehensive debug information including both navigation and state
        /// </summary>
        /// <returns>Complete debug information string</returns>
        public string GetCompleteDebugInfo()
        {
            var info = new System.Text.StringBuilder();
            info.AppendLine(GetNavigationDebugInfo());
            info.AppendLine();
            info.AppendLine(GetStateDebugInfo());
            return info.ToString();
        }

        #endregion

        // Add this helper method to your NavigationStore class
        private GridStateEventArgs CreateErrorEventArgs(string gridId, string stateName, string errorMessage)
        {
            var args = new GridStateEventArgs(gridId, stateName)
            {
                Exception = new InvalidOperationException(errorMessage),
                Success = false
            };
            return args;
        }

    }
}

