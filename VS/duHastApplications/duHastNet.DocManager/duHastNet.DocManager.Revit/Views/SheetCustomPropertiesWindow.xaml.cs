//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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

using duHastNet.DocManager.Revit.ViewModels;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;

namespace duHastNet.DocManager.Revit.Views
{
    /// <summary>
    /// Window that collects custom property values for sheets being imported into the database.
    /// <para>
    /// Follows the same pattern as <c>AddNewDocumentsDialog</c>: the ViewModel is passed
    /// into the constructor, dynamic columns are generated in code-behind, and
    /// <see cref="SheetCustomPropertiesViewModel.RequestClose"/> closes the window and sets
    /// <see cref="Window.DialogResult"/>.
    /// </para>
    /// </summary>
    public partial class SheetCustomPropertiesWindow : Window
    {
        public SheetCustomPropertiesWindow()
        {
            InitializeComponent();
        }

        /// <summary>
        /// Constructs the window with the given ViewModel, generates dynamic custom field
        /// columns, and wires the close event.
        /// </summary>
        /// <param name="viewModel">The ViewModel to bind. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="viewModel"/> is null.
        /// </exception>
        public SheetCustomPropertiesWindow(SheetCustomPropertiesViewModel viewModel) : this()
        {
            _ = viewModel ?? throw new ArgumentNullException(nameof(viewModel));

            DataContext = viewModel;

            GenerateCustomFieldColumns(viewModel);

            viewModel.RequestClose += (sender, e) =>
            {
                DialogResult = viewModel.DialogConfirmed;
                Close();
            };
        }

        /// <summary>
        /// Inserts one editable column per active custom field definition into
        /// <see cref="SheetsDataGrid"/>, before the last (Status) column.
        /// Binds each column to <c>CustomFieldValues[index].Value</c>.
        /// </summary>
        private void GenerateCustomFieldColumns(SheetCustomPropertiesViewModel viewModel)
        {
            if (viewModel.CustomFieldDefinitions == null || viewModel.CustomFieldDefinitions.Count == 0)
                return;

            // Insert custom field columns after the three fixed columns.
            int insertIndex = SheetsDataGrid.Columns.Count;

            for (int i = 0; i < viewModel.CustomFieldDefinitions.Count; i++)
            {
                var fieldDefinition = viewModel.CustomFieldDefinitions[i];

                var column = new DataGridTemplateColumn
                {
                    Header = fieldDefinition.PropertyName,
                    Width = new DataGridLength(140),
                    IsReadOnly = false
                };

                var cellTemplate = new DataTemplate();
                var textBoxFactory = new FrameworkElementFactory(typeof(TextBox));

                var binding = new Binding($"CustomFieldValues[{i}].Value")
                {
                    Mode = BindingMode.TwoWay,
                    UpdateSourceTrigger = UpdateSourceTrigger.PropertyChanged
                };

                textBoxFactory.SetBinding(TextBox.TextProperty, binding);
                textBoxFactory.SetValue(TextBox.BorderThicknessProperty, new Thickness(0));
                textBoxFactory.SetValue(TextBox.BackgroundProperty, System.Windows.Media.Brushes.Transparent);
                textBoxFactory.SetValue(TextBox.VerticalAlignmentProperty, VerticalAlignment.Center);
                textBoxFactory.SetValue(TextBox.PaddingProperty, new Thickness(4, 0, 4, 0));

                cellTemplate.VisualTree = textBoxFactory;
                column.CellTemplate = cellTemplate;

                SheetsDataGrid.Columns.Insert(insertIndex, column);
                insertIndex++;
            }
        }
    }
}
