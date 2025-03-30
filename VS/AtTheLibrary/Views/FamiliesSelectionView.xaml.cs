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

namespace duHast.AtTheLibrary.Views
{
    /// <summary>
    /// Interaction logic for FamiliesSelectionView.xaml
    /// </summary>
    public partial class FamiliesSelectionView : UserControl
    {
        public FamiliesSelectionView()
        {
            InitializeComponent();
        }

        private void PickFile_OnClick(object sender, EventArgs e)
        {
            var dialog = new System.Windows.Forms.OpenFileDialog();
            dialog.Filter = "csv Files (*.csv)|*.csv|All Files (*.*)|*.*";
            var dialogResult = dialog.ShowDialog();
            if (dialogResult == System.Windows.Forms.DialogResult.OK)
            {
                FilePathTextBox.Text = dialog.FileName;

                // Since setting the property explicitly bypasses the data binding, 
                // we must explicitly update it by calling BindingExpression.UpdateSource()
                this.FilePathTextBox
                  .GetBindingExpression(TextBox.TextProperty)
                  .UpdateSource();
            }
        }

        private void RoomsDataGrid_ColumnReordered(object sender, EventArgs e)
        {
            // check the view model
            if (DataContext is ViewModels.FamiliesSelectionViewModel vm)
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

    }
}
