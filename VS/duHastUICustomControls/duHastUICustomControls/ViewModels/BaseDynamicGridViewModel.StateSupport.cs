using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using System;
using System.Collections.Generic;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// State support functionality for BaseDynamicGridViewModel.
    /// Implements IGridStateSupport for state management via StateStore.
    /// </summary>
    public abstract partial class BaseDynamicGridViewModel<TData>
        where TData : DynamicRowData, new()
    {
        

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
        /// Gets a unique identifier for this ViewModel's grid state.
        /// Override in derived classes to provide application-specific identifiers.
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
                AddViewModelMetadata(state);

                System.Diagnostics.Debug.WriteLine($"Successfully captured state for grid '{gridId}'");
                return state;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error capturing state: {ex.Message}");
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
            return ApplyState(state);
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
                ApplyPendingStateIfExists();
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

        #region State Management Implementation

        /// <summary>
        /// Load saved state when ViewModel is ready
        /// </summary>
        private void LoadSavedStateIfExists()
        {
            System.Diagnostics.Debug.WriteLine($"LoadSavedStateIfExists called for {GetGridStateId()}");

            if (_stateStore == null || !StateManagementEnabled)
            {
                System.Diagnostics.Debug.WriteLine("StateStore is null or state management disabled");
                return;
            }

            try
            {
                var savedState = _stateStore.LoadState(GetGridStateId());
                System.Diagnostics.Debug.WriteLine($"Loaded state: {(savedState == null ? "null" : "found")}");

                if (savedState != null)
                {
                    if (_associatedDataGrid != null)
                    {
                        System.Diagnostics.Debug.WriteLine("Grid already associated, applying state immediately");
                        ApplyState(savedState);
                    }
                    else
                    {
                        _pendingStateToApply = savedState;
                        System.Diagnostics.Debug.WriteLine($"Grid not ready, stored pending state for {GetGridStateId()}");
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
            System.Diagnostics.Debug.WriteLine($"ApplyPendingStateIfExists called. Pending state: {(_pendingStateToApply == null ? "null" : "exists")}");

            if (_pendingStateToApply != null)
            {
                try
                {
                    System.Diagnostics.Debug.WriteLine("Applying pending state...");
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
        /// Direct state application method
        /// </summary>
        private bool ApplyState(IGridState state)
        {
            System.Diagnostics.Debug.WriteLine($"ApplyState called for {GetGridStateId()}");

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
                System.Diagnostics.Debug.WriteLine($"ApplyState: Exception: {ex.Message}");
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
            }

            return newState;
        }

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

            state.Metadata["ViewModelType"] = GetType().FullName;
            state.Metadata["ViewModelAssembly"] = GetType().Assembly.GetName().Name;
            state.Metadata["StateCreatedBy"] = "BaseDynamicGridViewModel";
            state.Metadata["DataCount"] = Data?.Count ?? 0;
            state.Metadata["ColumnDefinitionsCount"] = ColumnDefinitions?.Count ?? 0;
            state.Metadata["AvailableColumnsCount"] = AvailableColumns?.Count ?? 0;
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
    }
}