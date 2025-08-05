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

using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.Utils.WPF.ViewModels;
using duHastNet.Utils.WPF.Commands;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Input;

namespace duHastNet.UI.CustomControls.ViewModels
{
    public class CellEditorViewModel : BaseDynamicGridViewModel<CellEditorRowData>
    {
        #region Additional Commands
        public ICommand DuplicateRowCommand { get; }
        #endregion

        public CellEditorViewModel()
        {
            // Initialize the duplicate row command
            DuplicateRowCommand = new RelayCommand(param => DuplicateRowFromParameter(param));
        }

        private void DuplicateRowFromParameter(object parameter)
        {
            if (parameter is CellEditorRowData row)
            {
                DuplicateRow(row);
            }
        }
        public void LoadData(List<string> headers, List<List<object>> dataRows)
        {
            // Clear existing data
            ColumnDefinitions.Clear();
            Data.Clear();
            AvailableColumns.Clear();
            ClearStoredColumnData();

            // Create column definitions from headers
            for (int i = 0; i < headers.Count; i++)
            {
                var header = headers[i];
                var dataType = InferDataType(dataRows, i);

                var availableColumn = new AvailableColumnDefinition(
                    propertyName: $"Column_{i}",
                    displayName: header,
                    dataType: dataType,
                    category: "Data",
                    description: $"Column containing {header} data");

                AvailableColumns.Add(availableColumn);

                var columnDef = new DynamicColumnDefinition(
                    availableColumn.PropertyName,
                    availableColumn.DisplayName,
                    availableColumn.DataType)
                {
                    Width = GetDefaultWidthForType(availableColumn.DataType),
                    IsReadOnly = false
                };

                ColumnDefinitions.Add(columnDef);
            }

            // Create row data
            for (int rowIndex = 0; rowIndex < dataRows.Count; rowIndex++)
            {
                var row = new CellEditorRowData();
                var dataRow = dataRows[rowIndex];

                for (int colIndex = 0; colIndex < headers.Count && colIndex < dataRow.Count; colIndex++)
                {
                    var propertyName = $"Column_{colIndex}";
                    var value = dataRow[colIndex];

                    // Convert value to appropriate type if needed
                    var columnDef = ColumnDefinitions.FirstOrDefault(cd => cd.PropertyName == propertyName);
                    if (columnDef != null)
                    {
                        value = ConvertValueToType(value, columnDef.DataType);
                    }

                    row.Values[propertyName] = value;
                }

                Data.Add(row);
            }
        }

        public void DuplicateRow(CellEditorRowData sourceRow)
        {
            if (sourceRow == null) return;

            var newRow = new CellEditorRowData();

            // Copy all values from source row
            foreach (var kvp in sourceRow.Values)
            {
                newRow.Values[kvp.Key] = kvp.Value;
            }

            // Find the index of the source row and insert the new row after it
            var sourceIndex = Data.IndexOf(sourceRow);
            if (sourceIndex >= 0 && sourceIndex < Data.Count - 1)
            {
                Data.Insert(sourceIndex + 1, newRow);
            }
            else
            {
                Data.Add(newRow);
            }
        }

        public void RemoveRow(CellEditorRowData row)
        {
            if (row != null && Data.Contains(row))
            {
                Data.Remove(row);
            }
        }

        private Type InferDataType(List<List<object>> dataRows, int columnIndex)
        {
            if (dataRows == null || dataRows.Count == 0)
                return typeof(string);

            // Look at the first few non-null values to infer type
            for (int i = 0; i < Math.Min(5, dataRows.Count); i++)
            {
                if (columnIndex < dataRows[i].Count && dataRows[i][columnIndex] != null)
                {
                    var value = dataRows[i][columnIndex];
                    var valueType = value.GetType();

                    // Return specific types we handle
                    if (valueType == typeof(bool))
                        return typeof(bool);
                    if (valueType == typeof(int))
                        return typeof(int);
                    if (valueType == typeof(double) || valueType == typeof(float))
                        return typeof(double);
                    if (valueType == typeof(DateTime))
                        return typeof(DateTime);

                    // Try to parse common types from strings
                    if (valueType == typeof(string))
                    {
                        var stringValue = value.ToString();

                        if (bool.TryParse(stringValue, out _))
                            return typeof(bool);
                        if (int.TryParse(stringValue, out _))
                            return typeof(int);
                        if (double.TryParse(stringValue, out _))
                            return typeof(double);
                        if (DateTime.TryParse(stringValue, out _))
                            return typeof(DateTime);
                    }
                }
            }

            return typeof(string); // Default to string
        }

        private object ConvertValueToType(object value, Type targetType)
        {
            if (value == null)
                return GetDefaultValue(targetType);

            if (targetType.IsAssignableFrom(value.GetType()))
                return value;

            try
            {
                if (targetType == typeof(bool))
                    return Convert.ToBoolean(value);
                if (targetType == typeof(int))
                    return Convert.ToInt32(value);
                if (targetType == typeof(double))
                    return Convert.ToDouble(value);
                if (targetType == typeof(DateTime))
                    return Convert.ToDateTime(value);
                if (targetType == typeof(string))
                    return value.ToString();
            }
            catch
            {
                return GetDefaultValue(targetType);
            }

            return value;
        }

        #region BaseDynamicGridViewModel Implementation

        protected override void InitializeAvailableColumns()
        {
            // This will be populated dynamically when LoadData is called
            AvailableColumns = new System.Collections.ObjectModel.ObservableCollection<AvailableColumnDefinition>();
        }

        protected override CellEditorRowData CreateNewRow()
        {
            var newRow = new CellEditorRowData();

            // Initialize with default values for all current columns
            foreach (var columnDef in ColumnDefinitions)
            {
                newRow.Values[columnDef.PropertyName] = GetDefaultValue(columnDef.DataType);
            }

            return newRow;
        }

        protected override object GetDefaultValueForColumn(AvailableColumnDefinition columnDef)
        {
            return GetDefaultValue(columnDef.DataType);
        }

        protected override bool GetDefaultReadOnlyForColumn(string propertyName)
        {
            // By default, no columns are read-only in the cell editor
            // This can be controlled via the ReadOnlyColumns property on the control
            return false;
        }

        #endregion
    }
}