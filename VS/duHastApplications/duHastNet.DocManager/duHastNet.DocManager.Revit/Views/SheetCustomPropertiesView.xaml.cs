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
    /// Code-behind for <see cref="SheetCustomPropertiesView"/>.
    /// <para>
    /// Generates one editable <see cref="DataGridTextColumn"/> per active custom field
    /// definition when the DataContext is set. This is necessary because WPF DataGrid
    /// does not support dynamic column count binding from XAML alone.
    /// </para>
    /// </summary>
    public partial class SheetCustomPropertiesView : UserControl
    {
        public SheetCustomPropertiesView()
        {
            InitializeComponent();
            DataContextChanged += OnDataContextChanged;
        }

        /// <summary>
        /// Rebuilds the dynamic custom-field columns whenever the DataContext changes
        /// to a <see cref="SheetCustomPropertiesViewModel"/>.
        /// </summary>
        private void OnDataContextChanged(object sender, DependencyPropertyChangedEventArgs e)
        {
            if (e.NewValue is not SheetCustomPropertiesViewModel vm) return;

            BuildCustomFieldColumns(vm);
        }

        /// <summary>
        /// Adds one editable text column per custom field definition.
        /// Existing dynamic columns (beyond the three fixed ones) are removed first.
        /// <para>
        /// Each column binds to <c>CustomFieldValues[index].Value</c> via an
        /// <see cref="IndexedCustomFieldValueConverter"/> to avoid hard-coding property
        /// paths, since the number of custom fields is unknown at design time.
        /// </para>
        /// </summary>
        private void BuildCustomFieldColumns(SheetCustomPropertiesViewModel vm)
        {
            // Remove any previously generated dynamic columns (beyond the 3 fixed ones).
            const int fixedColumnCount = 3;
            while (CustomPropertiesGrid.Columns.Count > fixedColumnCount)
            {
                CustomPropertiesGrid.Columns.RemoveAt(CustomPropertiesGrid.Columns.Count - 1);
            }

            int fieldIndex = 0;
            foreach (var definition in vm.CustomFieldDefinitions)
            {
                int capturedIndex = fieldIndex;

                var column = new DataGridTextColumn
                {
                    Header = definition.PropertyName,
                    Width = new DataGridLength(140),
                    IsReadOnly = false,
                    Binding = new Binding($"CustomFieldValues[{capturedIndex}].Value")
                    {
                        Mode = BindingMode.TwoWay,
                        UpdateSourceTrigger = UpdateSourceTrigger.LostFocus
                    }
                };

                var editingStyle = new Style(typeof(TextBox));
                editingStyle.Setters.Add(new Setter(TextBox.PaddingProperty, new Thickness(4, 0, 4, 0)));
                editingStyle.Setters.Add(new Setter(TextBox.VerticalAlignmentProperty, VerticalAlignment.Center));
                column.EditingElementStyle = editingStyle;

                var elementStyle = new Style(typeof(TextBlock));
                elementStyle.Setters.Add(new Setter(TextBlock.PaddingProperty, new Thickness(4, 0, 4, 0)));
                elementStyle.Setters.Add(new Setter(TextBlock.VerticalAlignmentProperty, VerticalAlignment.Center));
                column.ElementStyle = elementStyle;

                CustomPropertiesGrid.Columns.Add(column);
                fieldIndex++;
            }
        }
    }
}
