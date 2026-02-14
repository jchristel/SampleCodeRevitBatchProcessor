using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.UI.CustomControls.CustomDataGrid;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace duHastNet.Utils.WPF.ViewModels
{
    /// <summary>
    /// Selection functionality for BaseDynamicGridViewModel.
    /// Provides single and multi-selection support with commands.
    /// </summary>
    public abstract partial class BaseDynamicGridViewModel<TData>
        where TData : DynamicRowData, new()
    {
        #region Selection Properties

        /// <summary>
        /// The currently selected item (for single selection mode).
        /// Generated property with automatic change notification.
        /// </summary>
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(HasSelection))]
        [NotifyCanExecuteChangedFor(nameof(DeleteSelectedCommand))]
        [NotifyCanExecuteChangedFor(nameof(ProcessSelectedCommand))]
        [NotifyCanExecuteChangedFor(nameof(ClearSelectionCommand))]
        private TData _selectedItem;

        private ObservableCollection<TData> _selectedItems;

        /// <summary>
        /// Collection of selected items (for extended/multiple selection mode)
        /// </summary>
        public ObservableCollection<TData> SelectedItems
        {
            get => _selectedItems ?? (_selectedItems = new ObservableCollection<TData>());
            set
            {
                if (_selectedItems != null)
                {
                    _selectedItems.CollectionChanged -= OnSelectedItemsCollectionChanged;
                }

                _selectedItems = value;

                if (_selectedItems != null)
                {
                    _selectedItems.CollectionChanged += OnSelectedItemsCollectionChanged;
                }

                OnPropertyChanged();
                OnPropertyChanged(nameof(HasSelection));
                OnPropertyChanged(nameof(SelectionCount));
                OnSelectionChanged();
            }
        }

        /// <summary>
        /// Whether any items are currently selected
        /// </summary>
        public bool HasSelection => SelectedItem != null || (SelectedItems?.Count > 0);

        /// <summary>
        /// Number of selected items
        /// </summary>
        public int SelectionCount => SelectedItems?.Count ?? (SelectedItem != null ? 1 : 0);

        /// <summary>
        /// Partial method called when SelectedItem changes.
        /// Used to trigger selection-related side effects.
        /// </summary>
        partial void OnSelectedItemChanged(TData value)
        {
            OnSelectionChanged();
        }

        #endregion

        #region Selection Commands

        /// <summary>
        /// Command to delete all selected rows.
        /// Generated command name: DeleteSelectedCommand
        /// Can only execute when HasSelection is true.
        /// </summary>
        [RelayCommand(CanExecute = nameof(HasSelection))]
        private void DeleteSelected()
        {
            var selectedRows = GetSelectedRows().ToList(); // Create a copy to avoid collection modification issues

            foreach (var row in selectedRows)
            {
                Data.Remove(row);
            }

            ClearSelection();
        }

        /// <summary>
        /// Command to process selected rows.
        /// Generated command name: ProcessSelectedCommand
        /// Can only execute when HasSelection is true.
        /// Override ProcessSelectedRows() in derived classes for custom logic.
        /// </summary>
        [RelayCommand(CanExecute = nameof(HasSelection))]
        private void ProcessSelected()
        {
            ProcessSelectedRows();
        }

        /// <summary>
        /// Command to select all rows.
        /// Generated command name: SelectAllCommand
        /// </summary>
        [RelayCommand]
        private void SelectAll()
        {
            SelectAllRows();
        }

        /// <summary>
        /// Command to clear the current selection.
        /// Generated command name: ClearSelectionCommand
        /// Can only execute when HasSelection is true.
        /// </summary>
        [RelayCommand(CanExecute = nameof(HasSelection))]
        private void ClearSelectionCommand()
        {
            ClearSelection();
        }

        #endregion

        #region Selection Event Handlers

        private void OnSelectedItemsCollectionChanged(object sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
        {
            OnPropertyChanged(nameof(HasSelection));
            OnPropertyChanged(nameof(SelectionCount));

            // Notify commands that their CanExecute state may have changed
            DeleteSelectedCommand.NotifyCanExecuteChanged();
            ProcessSelectedCommand.NotifyCanExecuteChanged();
            ClearSelectionCommand.NotifyCanExecuteChanged();

            OnSelectionChanged();
        }

        /// <summary>
        /// Called whenever the selection changes. Override in derived classes for custom handling.
        /// </summary>
        protected virtual void OnSelectionChanged()
        {
            // Base implementation - derived classes can override for custom behavior
            System.Diagnostics.Debug.WriteLine($"Selection changed: {SelectionCount} items selected");
        }

        #endregion

        #region Selection Methods

        /// <summary>
        /// Gets all currently selected rows
        /// </summary>
        public IEnumerable<TData> GetSelectedRows()
        {
            if (SelectedItems?.Count > 0)
            {
                return SelectedItems;
            }
            else if (SelectedItem != null)
            {
                return new[] { SelectedItem };
            }

            return Enumerable.Empty<TData>();
        }

        /// <summary>
        /// Gets values from a specific property of all selected rows
        /// </summary>
        public IEnumerable<object> GetSelectedPropertyValues(string propertyName)
        {
            return GetSelectedRows()
                .Where(row => row.Values.ContainsKey(propertyName))
                .Select(row => row.Values[propertyName]);
        }

        /// <summary>
        /// Sets the selection to specific items
        /// </summary>
        public void SetSelection(IEnumerable<TData> items)
        {
            SelectedItems.Clear();

            if (items != null)
            {
                foreach (var item in items)
                {
                    SelectedItems.Add(item);
                }
            }
        }

        /// <summary>
        /// Selects items by a property value
        /// </summary>
        public void SelectByPropertyValue(string propertyName, object value)
        {
            var matchingItems = Data
                .Where(row => row.Values.ContainsKey(propertyName) &&
                             Equals(row.Values[propertyName], value))
                .ToList();

            SetSelection(matchingItems);
        }

        /// <summary>
        /// Selects all rows
        /// </summary>
        public void SelectAllRows()
        {
            SetSelection(Data);
        }

        /// <summary>
        /// Clears the current selection
        /// </summary>
        public void ClearSelection()
        {
            SelectedItems.Clear();
            SelectedItem = null;
        }

        #endregion

        #region Selection Command Implementations

        /// <summary>
        /// Process selected rows. Override in derived classes for application-specific logic.
        /// Called by ProcessSelectedCommand.
        /// </summary>
        protected virtual void ProcessSelectedRows()
        {
            var selectedRows = GetSelectedRows().ToList();

            // Base implementation - just log the selection
            System.Diagnostics.Debug.WriteLine($"Processing {selectedRows.Count} selected rows");

            // Override this method in derived classes to add specific processing logic
        }

        #endregion

        #region Helper Methods for Selection

        /// <summary>
        /// Checks if a specific row is selected
        /// </summary>
        public bool IsRowSelected(TData row)
        {
            return SelectedItems.Contains(row) || Equals(SelectedItem, row);
        }

        /// <summary>
        /// Toggles selection of a specific row
        /// </summary>
        public void ToggleRowSelection(TData row)
        {
            if (IsRowSelected(row))
            {
                SelectedItems.Remove(row);
                if (Equals(SelectedItem, row))
                {
                    SelectedItem = null;
                }
            }
            else
            {
                SelectedItems.Add(row);
            }
        }

        /// <summary>
        /// Gets the first selected row, or null if none selected
        /// </summary>
        public TData GetFirstSelectedRow()
        {
            return SelectedItem ?? SelectedItems?.FirstOrDefault();
        }

        /// <summary>
        /// Gets selected rows that have a specific property value
        /// </summary>
        public IEnumerable<TData> GetSelectedRowsWithPropertyValue(string propertyName, object value)
        {
            return GetSelectedRows()
                .Where(row => row.Values.ContainsKey(propertyName) &&
                             Equals(row.Values[propertyName], value));
        }

        #endregion
    }
}