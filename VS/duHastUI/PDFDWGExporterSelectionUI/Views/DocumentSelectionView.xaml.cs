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


using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Media;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.Views
{
    /// <summary>
    /// Interaction logic for DocumentSelectionView.xaml
    /// </summary>
    public partial class DocumentSelectionView : UserControl
    {
        public DocumentSelectionView()
        {
            InitializeComponent();
        }

        private void Export_OnClick(object sender, EventArgs e)
        {
            var dialog = new System.Windows.Forms.FolderBrowserDialog();
            dialog.Description = "Browse to export folder";
            var dialogResult = dialog.ShowDialog();
            if (dialogResult == System.Windows.Forms.DialogResult.OK)
            {
                ExportFilePathTextBox.Text = dialog.SelectedPath;

                // Since setting the property explicitly bypasses the data binding, 
                // we must explicitly update it by calling BindingExpression.UpdateSource()
                this.ExportFilePathTextBox
                  .GetBindingExpression(TextBox.TextProperty)
                  .UpdateSource();
            }
        }

        /// <summary>
        /// keep track of columns re-ordered by user
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void RoomsDataGrid_ColumnReordered(object sender, EventArgs e)
        {
            // check the view model
            if (DataContext is ViewModels.DocumentSelectionViewModel vm)
            {

                var dataGrid = sender as DataGrid;
                if (dataGrid != null && dataGrid.ItemsSource is DataView dataView)
                {
                    var reorderedColumns = dataGrid.Columns
                                                   .OrderBy(c => c.DisplayIndex)
                                                   .Select(c => c.Header.ToString())
                                                   .ToList();

                    // Pass the new column order and the DataView to the ViewModel
                    vm.ColumnOrderChangedCommand.Execute(new Tuple<IEnumerable<string>, DataView>(reorderedColumns, dataView));
                }
            }
        }


        /// <summary>
        /// lock all columns but the check box column
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void DataGrid_AutoGeneratingColumn(object sender, DataGridAutoGeneratingColumnEventArgs e)
        {
            // List of columns that should be editable
            var editableColumns = new HashSet<string>
            {
                Models.Constants.ColumnHeaderExport // Example: Allow editing only the checkbox column
            };

            // Lock all columns except those in the editable list
            if (!editableColumns.Contains(e.Column.Header.ToString()))
            {
                e.Column.IsReadOnly = true; // Prevent editing
            }
            else
            {
                e.Column.IsReadOnly = false; // Allow editing for the specific column
            }
        }

        public void DataGrid_OnCellEditEnding(object sender, DataGridCellEditEndingEventArgs e)
        {
            //in wpf add:
            //CellEditEnding="DataGrid_OnCellEditEnding"
            if (e.Row.DataContext is DataRowView rowView)
            {
                rowView.EndEdit(); // Forces the update
            }
        }

        public void DataGrid_OnLostFocus(object sender, RoutedEventArgs e)
        {
            //in wpf add:
            //LostFocus = "DataGrid_OnLostFocus"
            var grid = sender as DataGrid;
            if (grid!=null)
            {
                grid.CommitEdit(DataGridEditingUnit.Cell, true);
                //grid.CommitEdit(DataGridEditingUnit.Row,true);
            }
        }

        public void DataGRid_PreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            //in wpf add
            //PreviewMouseLeftButtonDown="DataGRid_PreviewMouseLeftButtonDown"
            var originalElement = e.OriginalSource as DependencyObject;
            var cell = FindParent<DataGridCell>(originalElement);
            if (cell != null)
            {
                var dataGrid = sender as DataGrid;
                if (dataGrid != null)
                {
                    if (!cell.IsFocused) cell.Focus();
                    dataGrid.BeginEdit();
                }

                //need this for check boxes:
                var checkBox = FindParent<CheckBox>(originalElement);
                if (checkBox != null) 
                { 
                    DataGrid grid = sender as DataGrid;
                    grid.CommitEdit(DataGridEditingUnit.Cell, true);
                    grid.CommitEdit(DataGridEditingUnit.Row, true);
                    //Console.WriteLine(checkBox.IsChecked);

                    if(cell.DataContext is DataRowView drv && cell.Column is DataGridBoundColumn boundCol)
                    {
                        var bindingPath = (boundCol.Binding as Binding).Path.Path;
                        if(!string.IsNullOrEmpty(bindingPath))
                        {
                            var isChecked = checkBox.IsChecked ?? false;
                            // inverse the result since this is executed just before the check box is clicked on
                            drv[bindingPath] = !isChecked;
                            System.Diagnostics.Debug.WriteLine(isChecked);
                        }
                    }
                }
            }
        }

        private T FindParent<T>(DependencyObject child) where T : DependencyObject
        {
            while (child != null && !(child is T)) 
            {
                child = VisualTreeHelper.GetParent(child);
            }
            return child as T;
        }
    }
}
