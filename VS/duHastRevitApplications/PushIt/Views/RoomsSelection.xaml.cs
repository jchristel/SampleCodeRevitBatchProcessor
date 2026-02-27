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
using System;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.PushIt.Views
{
    /// <summary>
    /// Interaction logic for RoomsSelection.xaml
    /// </summary>
    public partial class RoomsSelection : UserControl
    {
        public RoomsSelection()
        {
            InitializeComponent();
        }

        // PickFile_OnClick has been removed. The Browse button for the data
        // source file is now handled entirely by
        // CsvDataSourceControlViewModel.BrowseCommand — no code-behind needed.

        /// <summary>
        /// Opens a save-file dialog and feeds the chosen path back into the
        /// SaveFilePath binding on RoomsMainViewModel.
        /// The hidden SaveAsPathTextBox is used as the binding intermediary
        /// (setting Text + calling UpdateSource) because WPF file dialogs do
        /// not support direct ViewModel binding out of the box.
        /// </summary>
        private void SaveFile_OnClick(object sender, EventArgs e)
        {
            var dialog = new System.Windows.Forms.SaveFileDialog
            {
                Filter = "Text files (*.csv)|*.csv|All files (*.*)|*.*"
            };
            var dialogResult = dialog.ShowDialog();
            if (dialogResult == System.Windows.Forms.DialogResult.OK)
            {
                SaveAsPathTextBox.Text = dialog.FileName;

                this.SaveAsPathTextBox
                    .GetBindingExpression(TextBox.TextProperty)
                    .UpdateSource();
            }
        }

        /// <summary>
        /// Registers the rooms data grid with its ViewModel when the grid is
        /// loaded so column management and state persistence work correctly.
        /// </summary>
        private void RoomSelectionGrid_Loaded(object sender, RoutedEventArgs e)
        {
            if (sender is DynamicDataGrid grid &&
                DataContext is ViewModels.RoomsMainViewModel mainViewModel)
            {
                mainViewModel.RoomsDataGridViewModel.AssociateWithDataGrid(grid);
            }
        }
    }
}
