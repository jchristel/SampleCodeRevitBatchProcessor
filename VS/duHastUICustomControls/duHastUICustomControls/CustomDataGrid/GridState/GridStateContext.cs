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

using System.ComponentModel;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Internal context class to track state management information for each DataGrid instance.
    /// This class stores all the configuration and state needed to manage grid state for a specific DataGrid.
    /// </summary>
    internal class GridStateContext
    {
        /// <summary>
        /// Unique identifier for the grid. This is used to distinguish between different grids
        /// and organize their saved states.
        /// </summary>
        public string GridId { get; set; }

        /// <summary>
        /// State manager instance responsible for handling save/load operations for this grid.
        /// Each grid can have its own state manager with different storage locations or configurations.
        /// </summary>
        public GridStateManager StateManager { get; set; }

        /// <summary>
        /// State management options that control what gets saved/loaded and how.
        /// These options determine which aspects of the grid state are preserved (columns, filters, sorting, etc.).
        /// </summary>
        public GridStateOptions Options { get; set; }

        /// <summary>
        /// Name of the state to automatically save to when changes are detected (if auto-save is enabled).
        /// If this is set and auto-save is enabled in the options, the grid will automatically
        /// save its current state to this named state when changes occur.
        /// </summary>
        public string AutoSaveStateName { get; set; }

        /// <summary>
        /// Name of the state to automatically load when the grid is first loaded (if auto-load is enabled).
        /// If this is set, the grid will attempt to load this named state when it's first initialized.
        /// </summary>
        public string AutoLoadStateName { get; set; }

        /// <summary>
        /// Event handler for ViewModel property changes. This is stored to allow proper cleanup
        /// when the grid is disposed or state management is disabled. The handler monitors
        /// ViewModel property changes that might affect the grid state (like filter changes).
        /// </summary>
        public PropertyChangedEventHandler ViewModelPropertyChangedHandler { get; set; }

        /// <summary>
        /// Initializes a new instance of GridStateContext with default values.
        /// </summary>
        public GridStateContext()
        {
            // Set sensible defaults
            Options = new GridStateOptions();
        }

        /// <summary>
        /// Initializes a new instance of GridStateContext with the specified grid ID.
        /// </summary>
        /// <param name="gridId">The unique identifier for the grid.</param>
        public GridStateContext(string gridId) : this()
        {
            GridId = gridId;
        }

        /// <summary>
        /// Initializes a new instance of GridStateContext with full configuration.
        /// </summary>
        /// <param name="gridId">The unique identifier for the grid.</param>
        /// <param name="stateManager">The state manager to use for this grid.</param>
        /// <param name="options">The state management options.</param>
        public GridStateContext(string gridId, GridStateManager stateManager, GridStateOptions options) : this(gridId)
        {
            StateManager = stateManager;
            Options = options ?? new GridStateOptions();
        }

        /// <summary>
        /// Gets whether auto-save is enabled for this context.
        /// Auto-save is enabled if there's an auto-save state name and the options allow auto-save.
        /// </summary>
        public bool IsAutoSaveEnabled =>
            !string.IsNullOrEmpty(AutoSaveStateName) &&
            Options?.AutoSave == true;

        /// <summary>
        /// Gets whether auto-load is enabled for this context.
        /// Auto-load is enabled if there's an auto-load state name configured.
        /// </summary>
        public bool IsAutoLoadEnabled =>
            !string.IsNullOrEmpty(AutoLoadStateName);

        /// <summary>
        /// Gets whether state management is fully configured and ready to use.
        /// This checks that all required components are in place.
        /// </summary>
        public bool IsFullyConfigured =>
            !string.IsNullOrEmpty(GridId) &&
            StateManager != null &&
            Options != null;

        /// <summary>
        /// Creates a copy of this context with the same configuration.
        /// This is useful for creating backup contexts or transferring configuration.
        /// </summary>
        /// <returns>A new GridStateContext with the same configuration as this one.</returns>
        public GridStateContext Clone()
        {
            return new GridStateContext
            {
                GridId = GridId,
                StateManager = StateManager, // Note: This shares the same instance
                Options = Options, // Note: This shares the same instance
                AutoSaveStateName = AutoSaveStateName,
                AutoLoadStateName = AutoLoadStateName,
                // Note: ViewModelPropertyChangedHandler is not cloned as it's specific to the original grid
            };
        }

        /// <summary>
        /// Returns a string representation of this context for debugging purposes.
        /// </summary>
        /// <returns>A string containing the key configuration details.</returns>
        public override string ToString()
        {
            return $"GridStateContext: GridId='{GridId}', " +
                   $"AutoSave={(IsAutoSaveEnabled ? AutoSaveStateName : "Disabled")}, " +
                   $"AutoLoad={(IsAutoLoadEnabled ? AutoLoadStateName : "Disabled")}, " +
                   $"StateManager={(StateManager != null ? "Configured" : "None")}, " +
                   $"FullyConfigured={IsFullyConfigured}";
        }

        /// <summary>
        /// Validates the context configuration and returns any issues found.
        /// </summary>
        /// <returns>A list of validation error messages, or empty list if valid.</returns>
        public System.Collections.Generic.List<string> Validate()
        {
            var issues = new System.Collections.Generic.List<string>();

            if (string.IsNullOrWhiteSpace(GridId))
                issues.Add("GridId is required");

            if (StateManager == null)
                issues.Add("StateManager is required");

            if (Options == null)
                issues.Add("Options cannot be null");

            if (IsAutoSaveEnabled && StateManager == null)
                issues.Add("Cannot enable auto-save without a StateManager");

            if (IsAutoLoadEnabled && StateManager == null)
                issues.Add("Cannot enable auto-load without a StateManager");

            return issues;
        }

        /// <summary>
        /// Disposes of resources and cleans up event handlers.
        /// This should be called when the grid is being disposed or state management is being disabled.
        /// </summary>
        public void Dispose()
        {
            // Clear the event handler reference
            ViewModelPropertyChangedHandler = null;

            // Note: We don't dispose StateManager here because it might be shared between multiple grids
            // The StateManager should be disposed by whoever created it
        }
    }
}