using CommunityToolkit.Mvvm.Input;
using duHastNet.Utils.WPF.ViewModels;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Windows.Input;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// Base class for dynamic grid ViewModels providing common grid functionality
    /// including column management, row operations, selection, and state persistence.
    /// </summary>
    /// <typeparam name="TData">The type of data rows in the grid, must derive from DynamicRowData</typeparam>
    public abstract partial class BaseDynamicGridViewModel<TData> : ViewModelBase, IGridStateSupport
        where TData : DynamicRowData, new()
    {
        #region Private Fields for State Management

        private StateStore _stateStore;
        private DynamicDataGrid _associatedDataGrid;
        private string _gridStateId;
        private bool _stateManagementEnabled = true;
        protected IGridState _pendingStateToApply;

        #endregion

        #region Constructor

        protected BaseDynamicGridViewModel(StateStore stateStore = null)
        {
            _stateStore = stateStore;

            // Initialize collections
            ColumnDefinitions = [];
            Data = [];

            // Initialize available columns (derived classes override this)
            InitializeAvailableColumns();

            // Initialize selected items collection
            SelectedItems = [];

            // Load saved state after everything is initialized
            LoadSavedStateIfExists();
        }

        #endregion

        #region Abstract Methods - Must be implemented by derived classes

        /// <summary>
        /// Define what columns are available for this specific application
        /// </summary>
        protected abstract void InitializeAvailableColumns();

        /// <summary>
        /// Create a new row with default data for this application
        /// </summary>
        protected abstract TData CreateNewRow();

        /// <summary>
        /// Get default value for a specific column in this application context
        /// </summary>
        protected abstract object GetDefaultValueForColumn(AvailableColumnDefinition columnDef);

        #endregion

        #region Virtual Methods - Can be overridden by derived classes

        /// <summary>
        /// Determine if a column should be read-only by default
        /// </summary>
        protected virtual bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            return false;
        }

        /// <summary>
        /// Get default width for a column based on its data type
        /// </summary>
        protected virtual double GetDefaultWidthForType(Type dataType)
        {
            if (dataType == typeof(bool)) return 80;
            if (dataType == typeof(int)) return 80;
            if (dataType == typeof(double)) return 100;
            if (dataType == typeof(DateTime)) return 120;
            return 150;
        }

        /// <summary>
        /// Get standard default value for data types
        /// </summary>
        protected virtual object GetDefaultValue(Type dataType)
        {
            if (dataType == typeof(string)) return string.Empty;
            if (dataType == typeof(int)) return 0;
            if (dataType == typeof(double)) return 0.0;
            if (dataType == typeof(bool)) return false;
            if (dataType == typeof(DateTime)) return DateTime.Now;
            return dataType.IsValueType ? Activator.CreateInstance(dataType) : null;
        }

        #endregion

        #region ICloseable Implementation

        /// <summary>
        /// Called when the ViewModel is being closed or navigated away from.
        /// Saves current state and performs cleanup.
        /// </summary>
        public override void OnClosing()
        {
            System.Diagnostics.Debug.WriteLine("GridViewModel.OnClosing() called");

            // Save current state before closing
            if (_stateStore != null && StateManagementEnabled)
            {
                try
                {
                    var currentState = CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        _stateStore.SaveState(this, currentState);
                        System.Diagnostics.Debug.WriteLine($"Saved state for {GetGridStateId()} on closing");
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error saving state on closing: {ex.Message}");
                }
            }
            else
            {
                System.Diagnostics.Debug.WriteLine($"No StateStore available for {GetGridStateId()} on closing");
            }

            // Call base to cleanup any registered child ViewModels
            base.OnClosing();
        }

        #endregion

        #region IDisposable Implementation

        private bool _disposed = false;

        /// <summary>
        /// Disposes of resources used by this ViewModel.
        /// Override this method in derived classes to dispose of specific resources.
        /// </summary>
        public override void Dispose()
        {
            if (_disposed)
                return;

            System.Diagnostics.Debug.WriteLine($"GridViewModel.Dispose() called for {GetGridStateId()}");

            // Dispose managed resources
            DisposeManaged();

            // Clear references
            _stateStore = null;
            _associatedDataGrid = null;

            _disposed = true;

            // Call base to dispose any child ViewModels that implement IDisposable
            base.Dispose();
        }

        /// <summary>
        /// Override this method in derived classes to dispose of specific managed resources
        /// (event subscriptions, timers, etc.)
        /// </summary>
        protected virtual void DisposeManaged()
        {
            // Base implementation has no resources to dispose
            // Derived classes can override to clean up their specific resources
        }

        #endregion
    }
}
