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
using System.Collections.Generic;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// State support functionality for BaseDynamicGridViewModel.
    /// Implements IGridStateSupport for automatic state management via NavigationStore.
    /// </summary>
    public abstract partial class BaseDynamicGridViewModel<TData>
        where TData : DynamicRowData, new()
    {

        #region State Management (Simplified)

        /// <summary>
        /// Gets whether state management is enabled for this ViewModel
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
        /// Gets a unique identifier for this ViewModel's grid state
        /// </summary>
        public virtual string GetGridStateId()
        {
            if (!string.IsNullOrEmpty(_gridStateId))
                return _gridStateId;

            var viewModelType = GetType().Name;
            if (viewModelType.EndsWith("ViewModel"))
                viewModelType = viewModelType.Substring(0, viewModelType.Length - 9);
            if (viewModelType.EndsWith("VM"))
                viewModelType = viewModelType.Substring(0, viewModelType.Length - 2);

            _gridStateId = $"{viewModelType}_Grid";
            return _gridStateId;
        }

        /// <summary>
        /// Associates this ViewModel with a DynamicDataGrid - required for state management
        /// </summary>
        public virtual void AssociateWithDataGrid(DynamicDataGrid dataGrid)
        {

            if (_associatedDataGrid == dataGrid)
                return;

            _associatedDataGrid = dataGrid;

            if (_associatedDataGrid != null)
            {
                System.Diagnostics.Debug.WriteLine($"Associated ViewModel {GetType().Name} with DynamicDataGrid");
                ApplyPendingStateIfExists();
            }
        }

        /// <summary>
        /// Load saved state when ViewModel is ready
        /// </summary>
        private void LoadSavedStateIfExists()
        {
            if (_navigationStore == null || !StateManagementEnabled)
                return;

            try
            {
                var savedState = _navigationStore.LoadViewModelState(GetGridStateId());
                if (savedState != null)
                {
                    if (_associatedDataGrid != null)
                    {
                        ApplyState(savedState);
                    }
                    else
                    {
                        _pendingStateToApply = savedState;
                        System.Diagnostics.Debug.WriteLine($"Stored pending state for {GetGridStateId()}");
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading saved state: {ex.Message}");
            }
        }

        /// <summary>
        /// Apply pending state when grid becomes available
        /// </summary>
        private void ApplyPendingStateIfExists()
        {
            if (_pendingStateToApply != null)
            {
                try
                {
                    ApplyState(_pendingStateToApply);
                    _pendingStateToApply = null;
                    System.Diagnostics.Debug.WriteLine($"Applied pending state for {GetGridStateId()}");
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error applying pending state: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Creates current grid state
        /// </summary>
        public virtual IGridState CreateStateFromViewModel()
        {
            if (!StateManagementEnabled || _associatedDataGrid == null)
                return null;

            try
            {
                var gridId = GetGridStateId();
                var state = GridStateSerializer.CaptureState(_associatedDataGrid, gridId);
                AddViewModelMetadata(state);
                return state;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error creating state: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Applies state to the grid
        /// </summary>
        public virtual bool ApplyStateToViewModel(IGridState state)
        {
            return ApplyState(state);
        }

        /// <summary>
        /// Direct state application method
        /// </summary>
        private bool ApplyState(IGridState state)
        {
            if (!StateManagementEnabled || _associatedDataGrid == null || state == null)
            {
                System.Diagnostics.Debug.WriteLine("ApplyState: Preconditions failed");
                return false;
            }

            try
            {
                System.Diagnostics.Debug.WriteLine($"ApplyState: Converting state type {state.GetType().Name}");
                DataGridState gridState = ConvertToDataGridState(state);
                if (gridState == null)
                {
                    System.Diagnostics.Debug.WriteLine("ApplyState: Failed to convert to DataGridState");
                    return false;
                }

                System.Diagnostics.Debug.WriteLine($"ApplyState: About to apply state with {gridState.Columns?.Count ?? 0} columns and {gridState.Filters?.Count ?? 0} filters");

                var success = GridStateSerializer.ApplyState(_associatedDataGrid, gridState);

                System.Diagnostics.Debug.WriteLine($"ApplyState: GridStateSerializer.ApplyState returned {success}");

                if (success)
                {
                    OnStateApplied(gridState);
                    System.Diagnostics.Debug.WriteLine($"Successfully applied state for grid '{gridState.GridId}'");
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
        /// Converts IGridState to DataGridState
        /// </summary>
        private DataGridState ConvertToDataGridState(IGridState state)
        {
            System.Diagnostics.Debug.WriteLine($"ConvertToDataGridState: Input state type {state.GetType().Name}");

            if (state is DataGridState dataGridState)
            {
                System.Diagnostics.Debug.WriteLine("ConvertToDataGridState: Already DataGridState, returning directly");
                return dataGridState;
            }

            System.Diagnostics.Debug.WriteLine("ConvertToDataGridState: Converting from generic state");

            var newState = new DataGridState
            {
                GridId = state.GridId,
                StateName = state.StateName,
                CreatedDate = state.CreatedDate,
                LastModified = state.LastModified,
                Version = state.Version,
                Metadata = new Dictionary<string, object>(state.Metadata ?? new Dictionary<string, object>())
            };

            var serializedData = state.Serialize();
            System.Diagnostics.Debug.WriteLine($"ConvertToDataGridState: Serialized data length: {serializedData?.Length ?? 0}");

            if (!string.IsNullOrEmpty(serializedData))
            {
                var deserializeSuccess = newState.Deserialize(serializedData);
                System.Diagnostics.Debug.WriteLine($"ConvertToDataGridState: Deserialize success: {deserializeSuccess}");
                System.Diagnostics.Debug.WriteLine($"ConvertToDataGridState: After deserialize - Columns: {newState.Columns?.Count ?? 0}, Filters: {newState.Filters?.Count ?? 0}");
                // Deserialize the serialized data into the new state
            }

            return newState;
        }

        /// <summary>
        /// Adds ViewModel metadata to state
        /// </summary>
        protected virtual void AddViewModelMetadata(DataGridState state)
        {
            if (state?.Metadata == null)
                return;

            state.Metadata["ViewModelType"] = GetType().FullName;
            state.Metadata["ViewModelAssembly"] = GetType().Assembly.GetName().Name;
            state.Metadata["StateCreatedBy"] = "BaseDynamicGridViewModel";
            state.Metadata["DataCount"] = Data?.Count ?? 0;
            state.Metadata["ColumnDefinitionsCount"] = ColumnDefinitions?.Count ?? 0;
            state.Metadata["AvailableColumnsCount"] = AvailableColumns?.Count ?? 0;
        }

        /// <summary>
        /// Called after state is applied - override for custom behavior
        /// </summary>
        protected virtual void OnStateApplied(DataGridState appliedState)
        {
            // Override in derived classes for custom post-application logic
        }

        #endregion

    }
}