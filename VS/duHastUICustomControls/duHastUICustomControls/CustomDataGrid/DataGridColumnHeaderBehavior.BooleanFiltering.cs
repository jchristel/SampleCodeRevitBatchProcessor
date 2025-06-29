using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid
{
    public static partial class DataGridColumnHeaderBehavior
    {
        #region Boolean Filtering

        /// <summary>
        /// Displays a dialog for filtering boolean columns with checkbox options.
        /// </summary>
        private static void ShowFilterBooleanDialog(DataGrid dataGrid, string propertyName)
        {
            var (showTrue, showFalse) = GetCurrentBooleanFilter(dataGrid, propertyName);

            var dialog = new FilterBooleanDialog(propertyName, showTrue, showFalse)
            {
                Owner = Window.GetWindow(dataGrid)
            };

            if (dialog.ShowDialog() == true)
            {
                if (dialog.FilterCleared)
                {
                    ClearColumnFilter(dataGrid, propertyName);
                }
                else
                {
                    ApplyBooleanFilter(dataGrid, propertyName, dialog.ShowTrue, dialog.ShowFalse);
                }
            }
        }

        /// <summary>
        /// Gets the current boolean filter state for a column.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to check.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <returns>A tuple indicating whether true and false values should be shown.</returns>
        private static (bool? showTrue, bool? showFalse) GetCurrentBooleanFilter(DataGrid dataGrid, string propertyName)
        {
            var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";

            bool? showTrue = dataGrid.Resources.Contains(showTrueKey) ? (bool?)dataGrid.Resources[showTrueKey] : null;
            bool? showFalse = dataGrid.Resources.Contains(showFalseKey) ? (bool?)dataGrid.Resources[showFalseKey] : null;

            return (showTrue, showFalse);
        }

        /// <summary>
        /// Applies a boolean filter to a column and refreshes the DataGrid.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to apply the filter to.</param>
        /// <param name="propertyName">The property name of the boolean column.</param>
        /// <param name="showTrue">Whether to show true values.</param>
        /// <param name="showFalse">Whether to show false values.</param>
        private static void ApplyBooleanFilter(DataGrid dataGrid, string propertyName, bool? showTrue, bool? showFalse)
        {
            SetColumnBooleanFilter(dataGrid, propertyName, showTrue, showFalse);
            ApplyAllColumnFilters(dataGrid);

            // Update filter icon for this column
            var column = dataGrid.Columns.FirstOrDefault(c => GetColumnPropertyName(c) == propertyName);
            if (column != null)
            {
                UpdateFilterIcon(dataGrid, column, propertyName);
            }
        }

        /// <summary>
        /// Stores boolean filter information for a column in the DataGrid's resource collection.
        /// </summary>
        /// <param name="dataGrid">The DataGrid to store the filter in.</param>
        /// <param name="propertyName">The property name of the column.</param>
        /// <param name="showTrue">Whether to show true values.</param>
        /// <param name="showFalse">Whether to show false values.</param>
        private static void SetColumnBooleanFilter(DataGrid dataGrid, string propertyName, bool? showTrue, bool? showFalse)
        {
            var showTrueKey = $"BooleanFilter_ShowTrue_{propertyName}";
            var showFalseKey = $"BooleanFilter_ShowFalse_{propertyName}";

            // Remove existing filters
            dataGrid.Resources.Remove(showTrueKey);
            dataGrid.Resources.Remove(showFalseKey);

            // Add new filters if specified
            if (showTrue.HasValue)
            {
                dataGrid.Resources[showTrueKey] = showTrue.Value;
            }

            if (showFalse.HasValue)
            {
                dataGrid.Resources[showFalseKey] = showFalse.Value;
            }
        }


        /// <summary>
        /// Tests whether an item passes a boolean filter.
        /// </summary>
        /// <param name="item">The item to test.</param>
        /// <param name="dataGrid">The DataGrid containing filter settings.</param>
        /// <param name="propertyName">The property name of the boolean column.</param>
        /// <returns>True if the item passes the filter, false otherwise.</returns>
        private static bool PassesBooleanFilter(object item, DataGrid dataGrid, string propertyName)
        {
            var (showTrue, showFalse) = GetCurrentBooleanFilter(dataGrid, propertyName);

            // If no boolean filter is set, show all
            if (!showTrue.HasValue && !showFalse.HasValue)
                return true;

            var itemValue = GetItemValue(item, propertyName);
            if (itemValue is bool boolValue)
            {
                if (boolValue && showTrue == true) return true;
                if (!boolValue && showFalse == true) return true;
                return false;
            }

            // Handle nullable bools or non-bool values
            return true;
        }

        #endregion
    }
}