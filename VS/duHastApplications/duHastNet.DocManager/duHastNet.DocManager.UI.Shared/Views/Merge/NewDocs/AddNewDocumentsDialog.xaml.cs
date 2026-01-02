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

using duHastNet.DocManager.UI.Shared.ViewModels;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;

namespace duHastNet.DocManager.UI.Shared.Views.Merge.NewDocs
{
    /// <summary>
    /// Interaction logic for AddNewDocumentsDialog.xaml
    /// </summary>
    public partial class AddNewDocumentsDialog : Window
    {
        public AddNewDocumentsDialog()
        {
            InitializeComponent();
        }

        /// <summary>
        /// Constructor with ViewModel
        /// </summary>
        public AddNewDocumentsDialog(ViewModels.Merge.NewDocs.AddNewDocumentsDialogViewModel viewModel) : this()
        {
            DataContext = viewModel;

            // Generate dynamic columns for custom fields
            GenerateCustomFieldColumns(viewModel);

            // Subscribe to RequestClose event
            viewModel.RequestClose += (sender, e) =>
            {
                DialogResult = viewModel.DialogConfirmed;
                Close();
            };
        }

        /// <summary>
        /// Generates DataGrid columns for each custom field definition
        /// </summary>
        private void GenerateCustomFieldColumns(ViewModels.Merge.NewDocs.AddNewDocumentsDialogViewModel viewModel)
        {
            if (viewModel.CustomFieldDefinitions == null || viewModel.CustomFieldDefinitions.Count == 0)
                return;

            // Find the index to insert custom field columns (before the Status column)
            // Status is the last column, so insert before it
            int insertIndex = DocumentsDataGrid.Columns.Count - 1;

            for (int i = 0; i < viewModel.CustomFieldDefinitions.Count; i++)
            {
                var fieldDefinition = viewModel.CustomFieldDefinitions[i];

                // Create a template column for the custom field
                var column = new DataGridTemplateColumn
                {
                    Header = fieldDefinition.PropertyName,
                    Width = new DataGridLength(120),
                    IsReadOnly = false
                };

                // Create the cell template with a TextBox for editing
                var cellTemplate = new DataTemplate();
                var textBoxFactory = new FrameworkElementFactory(typeof(System.Windows.Controls.TextBox));
                
                // Bind to CustomFieldValues[index].Value
                var binding = new System.Windows.Data.Binding($"CustomFieldValues[{i}].Value")
                {
                    Mode = BindingMode.TwoWay,
                    UpdateSourceTrigger = UpdateSourceTrigger.PropertyChanged
                };
                textBoxFactory.SetBinding(System.Windows.Controls.TextBox.TextProperty, binding);
                textBoxFactory.SetValue(System.Windows.Controls.TextBox.BorderThicknessProperty, new Thickness(0));
                textBoxFactory.SetValue(System.Windows.Controls.TextBox.BackgroundProperty, System.Windows.Media.Brushes.Transparent);
                textBoxFactory.SetValue(System.Windows.Controls.TextBox.VerticalAlignmentProperty, VerticalAlignment.Center);

                cellTemplate.VisualTree = textBoxFactory;
                column.CellTemplate = cellTemplate;

                // Insert the column before the Status column
                DocumentsDataGrid.Columns.Insert(insertIndex, column);
                insertIndex++;
            }
        }
    }
}
