using duHastNet.Utils.WPF.Commands;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace duHastNet.Utils.WPF.ViewModels
{
    public abstract partial class BaseDynamicGridViewModel<TData> : INotifyPropertyChanged, ICloseable, IGridStateSupport
    where TData : DynamicRowData, new()
    {
        #region Private Fields for State Management

        private NavigationStore _navigationStore;
        private DynamicDataGrid _associatedDataGrid;
        private string _gridStateId;
        private bool _stateManagementEnabled = true;
        protected IGridState _pendingStateToApply;

        #endregion

        protected BaseDynamicGridViewModel(NavigationStore navigationStore = null)
        {
            _navigationStore = navigationStore;

            // Initialize collections
            ColumnDefinitions = [];
            Data = [];

            // Initialize commands
            AddRowCommand = new RelayCommand(_ => AddRow());
            RemoveRowCommand = new RelayCommand(param => RemoveRow(param));
            AddSelectedColumnCommand = new RelayCommand(param => AddSelectedColumn(param?.ToString()));
            RemoveColumnCommand = new RelayCommand(param => RemoveColumn(param?.ToString()));
            ToggleColumnLockCommand = new RelayCommand(param => ToggleColumnLock(param?.ToString()));
            ClearDataCommand = new RelayCommand(_ => ClearData());

            // Initialize available columns (derived classes override this)
            InitializeAvailableColumns();

            // Initialize selection commands
            DeleteSelectedCommand = new RelayCommand(_ => DeleteSelectedRows(), _ => HasSelection);
            ProcessSelectedCommand = new RelayCommand(_ => ProcessSelectedRows(), _ => HasSelection);
            SelectAllCommand = new RelayCommand(_ => SelectAllRows());
            ClearSelectionCommand = new RelayCommand(_ => ClearSelection(), _ => HasSelection);

            // Initialize selected items collection
            SelectedItems = [];

            // Load saved state after everything is initialized
            LoadSavedStateIfExists();
        }

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

        #region INotifyPropertyChanged

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        #endregion

        #region ICloseable

        public virtual void OnClosing()
        {
            // In DocumentSelectionViewModel.OnClosing()
            System.Diagnostics.Debug.WriteLine("GridViewModel.OnClosing() called");

            // Save current state before closing
            if (_navigationStore != null && StateManagementEnabled)
            {
                try
                {
                    var currentState = CreateStateFromViewModel();
                    if (currentState != null)
                    {
                        _navigationStore.SaveViewModelState(this, currentState);
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
                System.Diagnostics.Debug.WriteLine($"No NavigationStore available for {GetGridStateId()} on closing");
            }
        }

        #endregion
    }
}