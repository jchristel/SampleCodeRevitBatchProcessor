
using duHastNet.Utils.WPF.Commands;
using duHastNet.Utils.WPF.Interfaces;
using global::duHastNet.UI.CustomControls.CustomDataGrid;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace duHastNet.Utils.WPF.ViewModels
{
    public abstract partial class BaseDynamicGridViewModel<TData> : INotifyPropertyChanged, duHastNet.Utils.WPF.Interfaces.ICloseable, IGridStateSupport
    where TData : DynamicRowData, new()
    {
        
        protected BaseDynamicGridViewModel()
        {
            // Initialize collections
            ColumnDefinitions = new ObservableCollection<DynamicColumnDefinition>();
            Data = new ObservableCollection<TData>();

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
            SelectedItems = new ObservableCollection<TData>();
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
        /// Determine if a column should be read-only by default. Needs to be overriden in application view model if colum,n locking is required!
        /// </summary>
        protected virtual bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            // Base implementation - no columns locked by default
            // Each application can override to define its own locking rules
            return false;
        }

        /// <summary>
        /// Get default width for a column based on its data type
        /// </summary>
        protected virtual double GetDefaultWidthForType(Type dataType)
        {
            if (dataType == typeof(bool))
                return 80;
            if (dataType == typeof(int))
                return 80;
            if (dataType == typeof(double))
                return 100;
            if (dataType == typeof(DateTime))
                return 120;

            // string and others
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
            // Perform state management cleanup
            PerformStateManagementCleanup();

            // Override this method in derived classes to perform clean-up operations
        }

        #endregion

    }
}

