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
    /// Pure state store - manages state persistence without navigation concerns
    /// Works with any IGridState implementation
    /// </summary>
    public class StateStore
    {
        #region Private Fields

        private readonly StateManager _stateManager;
        private readonly object _stateLock = new object();

        #endregion

        #region Events

        /// <summary>
        /// Fired when state operations occur (optional for debugging/logging)
        /// </summary>
        public event EventHandler<GridStateEventArgs> StateOperationCompleted;

        #endregion

        #region Constructor

        /// <summary>
        /// Initializes a new instance of StateStore
        /// </summary>
        /// <param name="stateManager">Optional state manager. If null, a default one will be created.</param>
        public StateStore(StateManager stateManager = null)
        {
            _stateManager = stateManager ?? new StateManager();
        }

        #endregion

        #region Core State Management Methods

        /// <summary>
        /// Saves state for a specific key
        /// </summary>
        /// <param name="stateKey">Unique key for the state</param>
        /// <param name="state">The state to save</param>
        public void SaveState(string stateKey, IGridState state)
        {
            if (string.IsNullOrEmpty(stateKey) || state == null)
                return;

            try
            {
                // Ensure state has proper metadata
                state.GridId = stateKey;
                state.StateName = "Default";
                state.LastModified = DateTime.Now;

                // Save to state manager
                _stateManager.SaveState(stateKey, state);

                System.Diagnostics.Debug.WriteLine($"Saved state for key: {stateKey}");

                // Raise success event
                OnStateOperationCompleted(new GridStateEventArgs(state.GridId, state.StateName, state));
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving state for {stateKey}: {ex.Message}");

                // Raise error event
                OnStateOperationCompleted(new GridStateEventArgs(stateKey, "Default", ex));
            }
        }

        /// <summary>
        /// Saves state for a ViewModel that supports state management
        /// </summary>
        /// <param name="viewModel">The ViewModel requesting the save</param>
        /// <param name="state">The state to save</param>
        public void SaveState(IGridStateSupport viewModel, IGridState state)
        {
            if (viewModel == null || state == null)
                return;

            var stateKey = viewModel.GetGridStateId();
            SaveState(stateKey, state);
        }

        /// <summary>
        /// Loads state by state key
        /// </summary>
        /// <param name="stateKey">The state key to load</param>
        /// <returns>The saved state, or null if not found</returns>
        public IGridState LoadState(string stateKey)
        {
            if (string.IsNullOrEmpty(stateKey))
                return null;

            try
            {
                var state = _stateManager.LoadState(stateKey);

                if (state != null)
                {
                    System.Diagnostics.Debug.WriteLine($"Loaded state for key: {stateKey}");
                }
                else
                {
                    System.Diagnostics.Debug.WriteLine($"No saved state found for key: {stateKey}");
                }

                return state;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading state for key {stateKey}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Loads state for a ViewModel that supports state management
        /// </summary>
        /// <param name="viewModel">The ViewModel requesting the load</param>
        /// <returns>The saved state, or null if not found</returns>
        public IGridState LoadState(IGridStateSupport viewModel)
        {
            if (viewModel == null)
                return null;

            var stateKey = viewModel.GetGridStateId();
            return LoadState(stateKey);
        }

        /// <summary>
        /// Checks if a state exists for the specified state key
        /// </summary>
        /// <param name="stateKey">The state key to check</param>
        /// <returns>True if a state exists</returns>
        public bool HasState(string stateKey)
        {
            if (string.IsNullOrEmpty(stateKey))
                return false;

            return _stateManager.StateExists(stateKey);
        }

        /// <summary>
        /// Checks if a state exists for the specified ViewModel
        /// </summary>
        /// <param name="viewModel">The ViewModel to check</param>
        /// <returns>True if a state exists</returns>
        public bool HasState(IGridStateSupport viewModel)
        {
            if (viewModel == null)
                return false;

            var stateKey = viewModel.GetGridStateId();
            return HasState(stateKey);
        }

        /// <summary>
        /// Clears state for a specific state key
        /// </summary>
        /// <param name="stateKey">The state key to clear</param>
        public void ClearState(string stateKey)
        {
            if (string.IsNullOrEmpty(stateKey))
                return;

            _stateManager.ClearState(stateKey);
            System.Diagnostics.Debug.WriteLine($"Cleared state for key: {stateKey}");
        }

        /// <summary>
        /// Clears state for a ViewModel
        /// </summary>
        /// <param name="viewModel">The ViewModel whose state should be cleared</param>
        public void ClearState(IGridStateSupport viewModel)
        {
            if (viewModel == null)
                return;

            var stateKey = viewModel.GetGridStateId();
            ClearState(stateKey);
        }

        /// <summary>
        /// Clears all saved states
        /// </summary>
        public void ClearAllStates()
        {
            _stateManager.ClearAllStates();
            System.Diagnostics.Debug.WriteLine("Cleared all saved states");
        }

        #endregion

        #region Settings Integration

        /// <summary>
        /// Loads states from application settings
        /// Called during application startup
        /// </summary>
        /// <param name="statesFromSettings">Serialized states from settings</param>
        /// <param name="stateFactory">Factory function to create the appropriate state type</param>
        public void LoadStatesFromSettings(Dictionary<string, string> statesFromSettings, Func<IGridState> stateFactory)
        {
            if (statesFromSettings == null || stateFactory == null)
                return;

            var statesToLoad = new Dictionary<string, IGridState>();

            foreach (var kvp in statesFromSettings)
            {
                try
                {
                    if (!string.IsNullOrEmpty(kvp.Value))
                    {
                        var state = stateFactory();
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
                System.Diagnostics.Debug.WriteLine($"Loaded {statesToLoad.Count} states from settings");
            }
        }

        /// <summary>
        /// Gets states formatted for saving to application settings
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

            System.Diagnostics.Debug.WriteLine($"Prepared {settingsData.Count} states for settings");
            return settingsData;
        }

        #endregion

        #region Utility and Debug Methods

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

        /// <summary>
        /// Gets all saved states (for debugging/inspection)
        /// </summary>
        /// <returns>Dictionary of all saved states</returns>
        public Dictionary<string, IGridState> GetAllStates()
        {
            return _stateManager.GetAllStates();
        }

        /// <summary>
        /// Gets debug information about stored states
        /// </summary>
        /// <returns>Debug information string</returns>
        public string GetDebugInfo()
        {
            var info = new System.Text.StringBuilder();
            info.AppendLine("=== STATE STORE DEBUG ===");
            info.AppendLine($"Stored States: {StoredStateCount}");

            var allStates = _stateManager.GetAllStates();
            foreach (var kvp in allStates)
            {
                info.AppendLine($"  - {kvp.Key}: {kvp.Value?.GetSummary() ?? "null"}");
            }

            return info.ToString();
        }

        #endregion

        #region Event Helpers

        /// <summary>
        /// Raises the StateOperationCompleted event
        /// </summary>
        /// <param name="args">Event arguments</param>
        protected virtual void OnStateOperationCompleted(GridStateEventArgs args)
        {
            StateOperationCompleted?.Invoke(this, args);
        }

        #endregion
    }
}