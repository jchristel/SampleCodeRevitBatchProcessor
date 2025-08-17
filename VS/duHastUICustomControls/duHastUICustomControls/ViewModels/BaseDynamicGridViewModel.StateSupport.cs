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

using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Interfaces;
using System;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// State support functionality for BaseDynamicGridViewModel.
    /// Implements IGridStateSupport for automatic state management via NavigationStore.
    /// </summary>
    public abstract partial class BaseDynamicGridViewModel<TData>
        where TData : DynamicRowData, new()
    {
        #region Private Fields

        private DynamicDataGrid _associatedDataGrid;
        private string _gridStateId;
        private bool _stateManagementEnabled = true;

        #endregion

        #region IGridStateSupport Implementation

        /// <summary>
        /// Gets whether state management is enabled for this ViewModel.
        /// Override in derived classes to disable state management for specific grids.
        /// </summary>
        public virtual bool StateManagementEnabled
        {
            get => _stateManagementEnabled;
            protected set
            {
                _stateManagementEnabled = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Creates a state object representing the current state of the ViewModel's grid.
        /// Uses GridStateSerializer to capture the complete DynamicDataGrid state.
        /// </summary>
        /// <returns>Current grid state, or null if state cannot be captured.</returns>
        public virtual IGridState CreateStateFromViewModel()
        {
            if (!StateManagementEnabled || _associatedDataGrid == null)
            {
                System.Diagnostics.Debug.WriteLine("State capture skipped: State management disabled or no associated grid");
                return null;
            }

            try
            {
                var gridId = GetGridStateId();
                if (string.IsNullOrEmpty(gridId))
                {
                    System.Diagnostics.Debug.WriteLine("State capture failed: No grid state ID available");
                    return null;
                }

                var state = GridStateSerializer.CaptureState(_associatedDataGrid, gridId);

                // Add ViewModel-specific metadata
                AddViewModelMetadata(state);

                System.Diagnostics.Debug.WriteLine($"Successfully captured state for grid '{gridId}'");
                return state;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error capturing state: {ex.Message}");
                // Return null on error - NavigationStore will handle this gracefully
                return null;
            }
        }

        /// <summary>
        /// Applies a saved state to the ViewModel's grid.
        /// Uses GridStateSerializer to restore the complete DynamicDataGrid state.
        /// </summary>
        /// <param name="state">The state to apply.</param>
        /// <returns>True if state was successfully applied.</returns>
        public virtual bool ApplyStateToViewModel(IGridState state)
        {
            if (!StateManagementEnabled || _associatedDataGrid == null)
            {
                System.Diagnostics.Debug.WriteLine("State application skipped: State management disabled or no associated grid");
                return false;
            }

            if (state == null)
            {
                System.Diagnostics.Debug.WriteLine("State application failed: State is null");
                return false;
            }

            if (!(state is DataGridState gridState))
            {
                System.Diagnostics.Debug.WriteLine($"State application failed: Expected DataGridState but got {state.GetType().Name}");
                return false;
            }

            try
            {
                // Validate state compatibility before applying
                var validation = GridStateSerializer.ValidateState(_associatedDataGrid, gridState);
                if (!validation.IsValid)
                {
                    System.Diagnostics.Debug.WriteLine($"State application failed: State is not compatible with current grid. Errors: {string.Join(", ", validation.Errors)}");
                    return false;
                }

                // Apply state with options
                var options = GetStateApplicationOptions();
                var success = GridStateSerializer.ApplyState(_associatedDataGrid, gridState, options);

                if (success)
                {
                    // Perform any post-application tasks
                    OnStateApplied(gridState);
                    System.Diagnostics.Debug.WriteLine($"Successfully applied state for grid '{gridState.GridId}'");
                }
                else
                {
                    System.Diagnostics.Debug.WriteLine($"Failed to apply state for grid '{gridState.GridId}'");
                }

                return success;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying state: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Gets a unique identifier for this ViewModel's grid state.
        /// Override in derived classes to provide application-specific identifiers.
        /// </summary>
        /// <returns>Unique state identifier.</returns>
        public virtual string GetGridStateId()
        {
            if (!string.IsNullOrEmpty(_gridStateId))
                return _gridStateId;

            // Generate default ID based on ViewModel type
            var viewModelType = GetType().Name;

            // Remove common suffixes to make IDs cleaner
            if (viewModelType.EndsWith("ViewModel"))
                viewModelType = viewModelType.Substring(0, viewModelType.Length - 9);
            if (viewModelType.EndsWith("VM"))
                viewModelType = viewModelType.Substring(0, viewModelType.Length - 2);

            _gridStateId = $"{viewModelType}_Grid";
            return _gridStateId;
        }

        #endregion

        #region Grid Association

        /// <summary>
        /// Associates this ViewModel with a specific DynamicDataGrid instance.
        /// This is required for state management to work properly.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to associate with this ViewModel.</param>
        public virtual void AssociateWithDataGrid(DynamicDataGrid dataGrid)
        {
            if (_associatedDataGrid == dataGrid)
                return;

            _associatedDataGrid = dataGrid;

            if (_associatedDataGrid != null)
            {
                System.Diagnostics.Debug.WriteLine($"Associated ViewModel {GetType().Name} with DynamicDataGrid");
                OnDataGridAssociated(_associatedDataGrid);
            }
            else
            {
                System.Diagnostics.Debug.WriteLine($"Disassociated ViewModel {GetType().Name} from DynamicDataGrid");
            }
        }

        /// <summary>
        /// Gets the currently associated DynamicDataGrid, if any.
        /// </summary>
        public DynamicDataGrid AssociatedDataGrid => _associatedDataGrid;

        /// <summary>
        /// Gets whether this ViewModel is currently associated with a DynamicDataGrid.
        /// </summary>
        public bool HasAssociatedDataGrid => _associatedDataGrid != null;

        #endregion

        #region Customization Points

        /// <summary>
        /// Sets a custom grid state identifier.
        /// Use this to override the default ID generation logic.
        /// </summary>
        /// <param name="gridStateId">Custom grid state identifier.</param>
        protected virtual void SetGridStateId(string gridStateId)
        {
            _gridStateId = gridStateId;
        }

        /// <summary>
        /// Gets the options to use when applying state to the grid.
        /// Override in derived classes to customize which aspects of state are restored.
        /// </summary>
        /// <returns>GridStateOptions specifying what to include in state restoration.</returns>
        protected virtual GridStateOptions GetStateApplicationOptions()
        {
            return new GridStateOptions
            {
                IncludeFilters = true,
                IncludeSorting = true,
                IncludeVisibility = true,
                IncludeColumnOrder = true,
                IncludeColumnWidths = true
            };
        }

        /// <summary>
        /// Adds ViewModel-specific metadata to the grid state before it's saved.
        /// Override in derived classes to include additional state information.
        /// </summary>
        /// <param name="state">The DataGridState to add metadata to.</param>
        protected virtual void AddViewModelMetadata(DataGridState state)
        {
            if (state?.Metadata == null)
                return;

            // Add ViewModel-specific metadata
            state.Metadata["ViewModelType"] = GetType().FullName;
            state.Metadata["ViewModelAssembly"] = GetType().Assembly.GetName().Name;
            state.Metadata["StateCreatedBy"] = "BaseDynamicGridViewModel";

            // Add data-specific metadata
            state.Metadata["DataCount"] = Data?.Count ?? 0;
            state.Metadata["ColumnDefinitionsCount"] = ColumnDefinitions?.Count ?? 0;
            state.Metadata["AvailableColumnsCount"] = AvailableColumns?.Count ?? 0;
        }

        /// <summary>
        /// Called when the ViewModel is associated with a DynamicDataGrid.
        /// Override in derived classes to perform additional setup.
        /// </summary>
        /// <param name="dataGrid">The newly associated DynamicDataGrid.</param>
        protected virtual void OnDataGridAssociated(DynamicDataGrid dataGrid)
        {
            // Base implementation does nothing
            // Override in derived classes for custom behavior
        }

        /// <summary>
        /// Called after state has been successfully applied to the grid.
        /// Override in derived classes to perform post-application tasks.
        /// </summary>
        /// <param name="appliedState">The state that was applied.</param>
        protected virtual void OnStateApplied(DataGridState appliedState)
        {
            // Base implementation does nothing
            // Override in derived classes for custom behavior

            // Example of what derived classes might do:
            // - Refresh calculated properties
            // - Update UI bindings
            // - Trigger data validation
            // - Log state application for auditing
        }

        #endregion

        #region State Management Utilities

        /// <summary>
        /// Manually triggers a save of the current grid state.
        /// Useful for forcing state save at specific moments.
        /// </summary>
        public virtual void SaveCurrentGridState()
        {
            if (!StateManagementEnabled)
            {
                System.Diagnostics.Debug.WriteLine("Manual state save skipped: State management disabled");
                return;
            }

            try
            {
                var state = CreateStateFromViewModel();
                if (state != null)
                {
                    // The NavigationStore will handle the actual saving
                    // This method is mainly for triggering the capture
                    System.Diagnostics.Debug.WriteLine("Manual grid state save completed");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Manual state save failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Gets validation information for the current grid state.
        /// Useful for debugging state compatibility issues.
        /// </summary>
        /// <returns>Validation result, or null if no grid is associated.</returns>
        public virtual GridStateValidationResult ValidateCurrentState()
        {
            if (_associatedDataGrid == null)
                return null;

            try
            {
                var currentState = CreateStateFromViewModel() as DataGridState;
                if (currentState == null)
                    return null;

                return GridStateSerializer.ValidateState(_associatedDataGrid, currentState);
            }
            catch (Exception ex)
            {
                var result = new GridStateValidationResult();
                result.AddError($"Validation failed: {ex.Message}");
                return result;
            }
        }

        /// <summary>
        /// Gets comprehensive diagnostic information about the grid and its state.
        /// Useful for troubleshooting state management issues.
        /// </summary>
        /// <returns>Diagnostic information string.</returns>
        public virtual string GetGridStateDiagnostics()
        {
            if (_associatedDataGrid == null)
                return "No DynamicDataGrid associated with this ViewModel";

            try
            {
                var currentState = CreateStateFromViewModel() as DataGridState;
                return GridStateSerializer.GetDiagnostics(_associatedDataGrid, currentState);
            }
            catch (Exception ex)
            {
                return $"Error getting diagnostics: {ex.Message}";
            }
        }

        #endregion

        #region State Management Cleanup Support

        /// <summary>
        /// Performs state management cleanup tasks.
        /// This method should be called from the main OnClosing() method.
        /// </summary>
        internal void PerformStateManagementCleanup()
        {
            try
            {
                // Perform final state save if enabled
                if (StateManagementEnabled && _associatedDataGrid != null)
                {
                    System.Diagnostics.Debug.WriteLine($"Performing final state save for {GetType().Name}");
                    SaveCurrentGridState();
                }

                // Clean up grid association
                if (_associatedDataGrid != null)
                {
                    System.Diagnostics.Debug.WriteLine($"Cleaning up grid association for {GetType().Name}");
                    _associatedDataGrid = null;
                }

                // Perform any additional state management cleanup
                OnStateManagementCleanup();

                System.Diagnostics.Debug.WriteLine($"State management cleanup completed for {GetType().Name}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error during state management cleanup for {GetType().Name}: {ex.Message}");
            }
        }

        /// <summary>
        /// Called during cleanup to perform additional state management cleanup tasks.
        /// Override in derived classes for custom cleanup logic.
        /// </summary>
        protected virtual void OnStateManagementCleanup()
        {
            // Base implementation does nothing
            // Override in derived classes for custom cleanup behavior

            // Examples of what derived classes might do:
            // - Clear temporary state files
            // - Unsubscribe from state change notifications
            // - Clean up validation resources
            // - Log final state information for auditing
        }

        #endregion
    }
}