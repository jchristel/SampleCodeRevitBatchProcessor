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
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {
        #region Text Filtering

        /// <summary>
        /// Displays a dialog for entering filter text and logic (AND/OR) for a specific column.
        /// </summary>
        private static void ShowFilterTextDialog(DataGrid dataGrid, string propertyName)
        {
            var currentFilter = GetCurrentFilterText(dataGrid, propertyName);

            var dialog = new FilterTextDialog(propertyName, currentFilter)
            {
                Owner = Window.GetWindow(dataGrid)
            };

            if (dialog.ShowDialog() == true)
            {
                ApplyTextFilter(dataGrid, propertyName, dialog.FilterText, dialog.UseAndLogic);
            }
        }

        /// <summary>
        /// Applies a text filter to a column and refreshes the DataGrid to show filtered results.
        /// </summary>
        private static void ApplyTextFilter(DataGrid dataGrid, string propertyName, string filterText, bool useAndLogic)
        {
            SetColumnTextFilter(dataGrid, propertyName, filterText, useAndLogic);
            ApplyAllColumnFilters(dataGrid);

            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Stores filter information for a column in the DataGrid's resource collection.
        /// </summary>
        private static void SetColumnTextFilter(DataGrid dataGrid, string propertyName, string filterText, bool useAndLogic)
        {
            var filterKey = $"TextFilter_{propertyName}";
            var logicKey = $"TextFilterLogic_{propertyName}";

            if (string.IsNullOrWhiteSpace(filterText))
            {
                dataGrid.Resources.Remove(filterKey);
                dataGrid.Resources.Remove(logicKey);
            }
            else
            {
                dataGrid.Resources[filterKey] = filterText;
                dataGrid.Resources[logicKey] = useAndLogic;
            }
        }

        /// <summary>
        /// Tests whether an item value passes a text filter using the specified logic (AND/OR).
        /// </summary>
        /// <param name="itemValue">The value from the item to test.</param>
        /// <param name="filterText">The filter text containing one or more search terms separated by spaces.</param>
        /// <param name="useAndLogic">True to require ALL terms to match (AND), false to require ANY term to match (OR).</param>
        /// <returns>True if the item passes the filter, false otherwise.</returns>
        private static bool PassesTextFilter(string itemValue, string filterText, bool useAndLogic)
        {
            if (string.IsNullOrWhiteSpace(filterText)) return true;

            var filterTerms = filterText.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);

            if (useAndLogic)
            {
                return filterTerms.All(term =>
                    itemValue.IndexOf(term, StringComparison.OrdinalIgnoreCase) >= 0);
            }
            else
            {
                return filterTerms.Any(term =>
                    itemValue.IndexOf(term, StringComparison.OrdinalIgnoreCase) >= 0);
            }
        }

        #endregion
    }
}