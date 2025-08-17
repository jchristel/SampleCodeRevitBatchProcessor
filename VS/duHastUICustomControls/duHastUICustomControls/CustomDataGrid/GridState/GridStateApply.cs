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
using System.ComponentModel;
using System.Linq;
using System.Windows.Controls;
using System.Windows.Data;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Handles applying state configurations to DynamicDataGrid controls.
    /// Contains logic for restoring columns, sorting, and DynamicDataGrid-specific features.
    /// </summary>
    internal static class GridStateApply
    {
        #region Column State Application

        /// <summary>
        /// Applies column state configurations to a DynamicDataGrid.
        /// Restores visibility, order, width, and other column properties based on options.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply column states to.</param>
        /// <param name="columnStates">List of column states to apply.</param>
        /// <param name="options">Options controlling which aspects of column state to apply.</param>
        /// <returns>True if column states were successfully applied, false otherwise.</returns>
        internal static bool ApplyColumnStates(DynamicDataGrid dataGrid, List<ColumnState> columnStates, GridStateOptions options)
        {
            if (dataGrid == null || columnStates == null || columnStates.Count == 0)
                return false;

            try
            {
                // Create a mapping of current columns by property name
                var currentColumns = dataGrid.Columns.ToDictionary(
                    col => GridStateHelpers.GetColumnPropertyName(col),
                    col => col
                );

                // Apply states in display order
                var sortedStates = columnStates.OrderBy(cs => cs.DisplayIndex).ToList();

                for (int i = 0; i < sortedStates.Count; i++)
                {
                    var columnState = sortedStates[i];

                    // Skip columns that don't exist in the current grid
                    if (!currentColumns.TryGetValue(columnState.PropertyName, out var column))
                    {
                        System.Diagnostics.Debug.WriteLine($"Skipping column state for unknown property: {columnState.PropertyName}");
                        continue;
                    }

                    // Apply visibility
                    if (options.IncludeVisibility)
                    {
                        column.Visibility = columnState.IsVisible ?
                            System.Windows.Visibility.Visible :
                            System.Windows.Visibility.Collapsed;
                    }

                    // Apply display order
                    if (options.IncludeColumnOrder)
                    {
                        column.DisplayIndex = i;
                    }

                    // Apply width
                    if (options.IncludeColumnWidths && columnState.Width > 0)
                    {
                        column.Width = new DataGridLength(columnState.Width);
                    }

                    // Note: IsReadOnly is typically set by the ViewModel/ColumnDefinitions
                    // and shouldn't be changed during state restoration
                }

                System.Diagnostics.Debug.WriteLine($"Applied column states for {sortedStates.Count} columns");
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying column states: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Sorting State Application

        /// <summary>
        /// Applies sorting state to a DynamicDataGrid.
        /// Restores the sort column and direction.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply sorting to.</param>
        /// <param name="sortState">The sorting state to apply.</param>
        /// <returns>True if sorting was successfully applied, false otherwise.</returns>
        internal static bool ApplySortingState(DynamicDataGrid dataGrid, SortState sortState)
        {
            if (dataGrid == null || sortState == null || string.IsNullOrEmpty(sortState.PropertyName))
                return false;

            try
            {
                // Validate that the sort property exists in the grid
                if (!GridStateHelpers.IsValidProperty(dataGrid, sortState.PropertyName))
                {
                    System.Diagnostics.Debug.WriteLine($"Cannot apply sort for unknown property: {sortState.PropertyName}");
                    return false;
                }

                var collectionView = CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
                if (collectionView == null)
                {
                    System.Diagnostics.Debug.WriteLine("Cannot apply sorting: CollectionView is null");
                    return false;
                }

                // Clear existing sort descriptions
                collectionView.SortDescriptions.Clear();

                // Add the new sort description
                collectionView.SortDescriptions.Add(new SortDescription(sortState.PropertyName, sortState.Direction));

                System.Diagnostics.Debug.WriteLine($"Applied sorting: {sortState.PropertyName} {sortState.Direction}");
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying sorting state: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region DynamicDataGrid-Specific State Application

        /// <summary>
        /// Applies DynamicDataGrid-specific state restoration.
        /// Handles restoration of available columns and other DynamicDataGrid features.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to apply specific state to.</param>
        /// <param name="state">The complete DataGridState containing metadata.</param>
        /// <returns>True if DynamicDataGrid-specific state was successfully applied, false otherwise.</returns>
        internal static bool ApplyDynamicDataGridSpecificState(DynamicDataGrid dataGrid, DataGridState state)
        {
            if (dataGrid == null || state == null)
                return false;

            try
            {
                bool success = true;

                // Restore available columns metadata if needed
                if (state.Metadata.ContainsKey("AvailableColumns"))
                {
                    success &= RestoreAvailableColumnsMetadata(dataGrid, state);
                }

                // Restore column definitions if they differ from current
                if (state.Metadata.ContainsKey("CurrentColumnDefinitions"))
                {
                    success &= RestoreColumnDefinitions(dataGrid, state);
                }

                // Apply any DynamicDataGrid configuration options
                if (state.Metadata.ContainsKey("CanUserReorderColumns"))
                {
                    if (state.Metadata["CanUserReorderColumns"] is bool canReorder)
                    {
                        dataGrid.CanUserReorderColumns = canReorder;
                    }
                }

                if (state.Metadata.ContainsKey("CanUserResizeColumns"))
                {
                    if (state.Metadata["CanUserResizeColumns"] is bool canResize)
                    {
                        dataGrid.CanUserResizeColumns = canResize;
                    }
                }

                if (state.Metadata.ContainsKey("CanUserSortColumns"))
                {
                    if (state.Metadata["CanUserSortColumns"] is bool canSort)
                    {
                        dataGrid.CanUserSortColumns = canSort;
                    }
                }

                return success;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error applying DynamicDataGrid-specific state: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Restores available columns metadata to the DynamicDataGrid's ViewModel.
        /// This is primarily for validation and ensuring compatibility.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to restore metadata to.</param>
        /// <param name="state">The state containing available columns metadata.</param>
        /// <returns>True if metadata was successfully restored, false otherwise.</returns>
        private static bool RestoreAvailableColumnsMetadata(DynamicDataGrid dataGrid, DataGridState state)
        {
            try
            {
                // Get current available columns for comparison
                var currentAvailableColumns = GridStateHelpers.GetAvailableColumns(dataGrid);
                var currentPropertyNames = new HashSet<string>(currentAvailableColumns.Select(ac => ac.PropertyName));

                // Extract saved available columns metadata
                if (state.Metadata["AvailableColumns"] is System.Collections.IEnumerable savedColumns)
                {
                    var savedPropertyNames = new HashSet<string>();

                    foreach (var column in savedColumns)
                    {
                        var propName = column.GetType().GetProperty("PropertyName")?.GetValue(column)?.ToString();
                        if (!string.IsNullOrEmpty(propName))
                        {
                            savedPropertyNames.Add(propName);
                        }
                    }

                    // Check for compatibility issues
                    var missingInCurrent = savedPropertyNames.Except(currentPropertyNames).ToList();
                    var extraInCurrent = currentPropertyNames.Except(savedPropertyNames).ToList();

                    if (missingInCurrent.Count > 0)
                    {
                        System.Diagnostics.Debug.WriteLine($"Warning: Saved state references columns not available in current grid: {string.Join(", ", missingInCurrent)}");
                    }

                    if (extraInCurrent.Count > 0)
                    {
                        System.Diagnostics.Debug.WriteLine($"Info: Current grid has additional columns not in saved state: {string.Join(", ", extraInCurrent)}");
                    }
                }

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error restoring available columns metadata: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Restores column definitions to match the saved state.
        /// This could involve adding/removing columns to match the saved configuration.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to restore column definitions to.</param>
        /// <param name="state">The state containing column definitions.</param>
        /// <returns>True if column definitions were successfully restored, false otherwise.</returns>
        private static bool RestoreColumnDefinitions(DynamicDataGrid dataGrid, DataGridState state)
        {
            try
            {
                // This is a placeholder for more advanced column management
                // In a full implementation, this might:
                // 1. Add missing columns to the ViewModel
                // 2. Remove extra columns
                // 3. Reorder columns to match saved state
                // 4. Update column properties

                // For now, we just log what would need to be done
                if (state.Metadata["CurrentColumnDefinitions"] is System.Collections.IEnumerable savedColumnDefs)
                {
                    var savedCount = 0;
                    foreach (var _ in savedColumnDefs)
                    {
                        savedCount++;
                    }

                    var currentCount = dataGrid.ColumnDefinitions?.Count ?? 0;

                    if (savedCount != currentCount)
                    {
                        System.Diagnostics.Debug.WriteLine($"Column definition count mismatch: Current={currentCount}, Saved={savedCount}");
                        System.Diagnostics.Debug.WriteLine("Advanced column restoration not implemented - consider adding missing columns to ViewModel");
                    }
                }

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error restoring column definitions: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Validates that all states are compatible with the target DynamicDataGrid before applying.
        /// Performs pre-application validation to prevent errors.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to validate against.</param>
        /// <param name="state">The complete state to validate.</param>
        /// <returns>True if all states are compatible, false if there are issues.</returns>
        internal static bool ValidateStateCompatibility(DynamicDataGrid dataGrid, DataGridState state)
        {
            if (dataGrid == null || state == null)
                return false;

            try
            {
                var availableProperties = new HashSet<string>(GridStateHelpers.GetAllPropertyNames(dataGrid));

                // Check column state compatibility
                if (state.Columns?.Count > 0)
                {
                    foreach (var columnState in state.Columns)
                    {
                        if (!availableProperties.Contains(columnState.PropertyName))
                        {
                            System.Diagnostics.Debug.WriteLine($"Column state incompatible: {columnState.PropertyName} not available");
                            return false;
                        }
                    }
                }

                // Check sorting compatibility
                if (state.Sorting != null && !availableProperties.Contains(state.Sorting.PropertyName))
                {
                    System.Diagnostics.Debug.WriteLine($"Sort state incompatible: {state.Sorting.PropertyName} not available");
                    return false;
                }

                // Check filter compatibility
                if (state.Filters?.Count > 0)
                {
                    foreach (var filterState in state.Filters)
                    {
                        if (!availableProperties.Contains(filterState.PropertyName))
                        {
                            System.Diagnostics.Debug.WriteLine($"Filter state incompatible: {filterState.PropertyName} not available");
                            return false;
                        }
                    }
                }

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error validating state compatibility: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Forces a refresh of the DynamicDataGrid after state application.
        /// Ensures that all visual changes are properly applied.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to refresh.</param>
        internal static void RefreshGridAfterStateApplication(DynamicDataGrid dataGrid)
        {
            if (dataGrid == null)
                return;

            try
            {
                // Force layout update
                dataGrid.UpdateLayout();

                // Refresh the items if there's a collection view
                var collectionView = CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
                collectionView?.Refresh();

                // Refresh filters
                GridStateHelpers.RefreshDataGridFilters(dataGrid);

                System.Diagnostics.Debug.WriteLine("Refreshed DynamicDataGrid after state application");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error refreshing DynamicDataGrid: {ex.Message}");
            }
        }

        #endregion
    }
}