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
using System.Windows.Controls;

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
    }
}
