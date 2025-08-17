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
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, even if advised of the possibility of such damage.
//
//
//

using System;
using System.ComponentModel;
using System.Linq;
using System.Windows.Data;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Handles capturing the complete state of a DynamicDataGrid control.
    /// Orchestrates capture of columns, sorting, filters, and DynamicDataGrid-specific metadata.
    /// This class focuses purely on state capture - NavigationStore handles lifecycle management.
    /// </summary>
    internal static class GridStateCapture
    {
        #region Main Capture Method

        /// <summary>
        /// Captures the complete current state of a DynamicDataGrid.
        /// Creates a DataGridState with all column, sorting, filter, and metadata information.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture state from.</param>
        /// <param name="gridId">Unique identifier for this grid state.</param>
        /// <returns>Complete DataGridState representing the current grid configuration.</returns>
        internal static DataGridState CaptureCompleteState(DynamicDataGrid dataGrid, string gridId)
        {
            if (dataGrid == null)
                throw new ArgumentNullException(nameof(dataGrid));

            if (string.IsNullOrEmpty(gridId))
                throw new ArgumentException("GridId cannot be null or empty", nameof(gridId));

            var state = new DataGridState
            {
                GridId = gridId,
                CreatedDate = DateTime.Now,
                LastModified = DateTime.Now
            };

            try
            {
                // Capture column states
                state.Columns = CaptureColumnStates(dataGrid);

                // Capture sorting state
                state.Sorting = CaptureSortingState(dataGrid);

                // Capture filter states
                state.Filters = FilterStateCapture.CaptureAllFilterStates(dataGrid);

                // Capture DynamicDataGrid-specific metadata
                CaptureDynamicDataGridMetadata(dataGrid, state);

                System.Diagnostics.Debug.WriteLine($"Captured state for DynamicDataGrid '{gridId}': {state.Columns.Count} columns, {state.Filters.Count} filters, sorting: {state.Sorting != null}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error capturing state for DynamicDataGrid '{gridId}': {ex.Message}");

                // Return partial state rather than failing completely
                state.Metadata["CaptureError"] = ex.Message;
                state.Metadata["CaptureTime"] = DateTime.Now;
            }

            return state;
        }

        #endregion

        #region Column State Capture

        /// <summary>
        /// Captures the state of all columns in the DynamicDataGrid.
        /// Includes visibility, order, width, and read-only status for each column.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture column states from.</param>
        /// <returns>List of ColumnState objects representing each column's configuration.</returns>
        internal static System.Collections.Generic.List<ColumnState> CaptureColumnStates(DynamicDataGrid dataGrid)
        {
            var columnStates = new System.Collections.Generic.List<ColumnState>();

            if (dataGrid.Columns == null)
                return columnStates;

            try
            {
                // Process columns in their current display order
                foreach (var column in dataGrid.Columns.OrderBy(c => c.DisplayIndex))
                {
                    var propertyName = GridStateHelpers.GetColumnPropertyName(column);
                    if (string.IsNullOrEmpty(propertyName))
                        continue;

                    // Validate that this property exists in available columns
                    if (!GridStateHelpers.IsValidProperty(dataGrid, propertyName))
                    {
                        System.Diagnostics.Debug.WriteLine($"Skipping column for unknown property: {propertyName}");
                        continue;
                    }

                    var columnState = new ColumnState
                    {
                        PropertyName = propertyName,
                        DisplayName = column.Header?.ToString() ?? propertyName,
                        IsVisible = column.Visibility == System.Windows.Visibility.Visible,
                        DisplayIndex = column.DisplayIndex,
                        Width = column.ActualWidth > 0 ? column.ActualWidth : column.Width.Value,
                        IsReadOnly = column.IsReadOnly
                    };

                    // Get data type from DynamicDataGrid's available columns
                    var columnDefinition = GridStateHelpers.GetColumnDefinition(dataGrid, propertyName);
                    columnState.DataTypeName = columnDefinition?.DataType?.FullName ?? typeof(string).FullName;

                    columnStates.Add(columnState);
                }

                System.Diagnostics.Debug.WriteLine($"Captured {columnStates.Count} column states from DynamicDataGrid");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error capturing column states: {ex.Message}");
            }

            return columnStates;
        }

        #endregion

        #region Sorting State Capture

        /// <summary>
        /// Captures the current sorting state of the DynamicDataGrid.
        /// Only supports single-column sorting as per current implementation.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture sorting state from.</param>
        /// <returns>SortState representing the current sort configuration, or null if no sorting is active.</returns>
        internal static SortState CaptureSortingState(DynamicDataGrid dataGrid)
        {
            try
            {
                var collectionView = CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
                if (collectionView?.SortDescriptions?.Count > 0)
                {
                    var sortDesc = collectionView.SortDescriptions.First();

                    // Validate that the sorted property exists in available columns
                    if (!GridStateHelpers.IsValidProperty(dataGrid, sortDesc.PropertyName))
                    {
                        System.Diagnostics.Debug.WriteLine($"Skipping sort for unknown property: {sortDesc.PropertyName}");
                        return null;
                    }

                    var sortState = new SortState
                    {
                        PropertyName = sortDesc.PropertyName,
                        Direction = sortDesc.Direction,
                        SortIndex = 0 // Single column sorting only
                    };

                    System.Diagnostics.Debug.WriteLine($"Captured sort state: {sortState.PropertyName} {sortState.Direction}");
                    return sortState;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error capturing sorting state: {ex.Message}");
            }

            return null;
        }

        #endregion

        #region DynamicDataGrid-Specific Metadata Capture

        /// <summary>
        /// Captures DynamicDataGrid-specific metadata including available columns information.
        /// This metadata is essential for proper state restoration in DynamicDataGrid contexts.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to capture metadata from.</param>
        /// <param name="state">The DataGridState to store metadata in.</param>
        internal static void CaptureDynamicDataGridMetadata(DynamicDataGrid dataGrid, DataGridState state)
        {
            try
            {
                // Store basic grid information
                state.Metadata["GridType"] = "DynamicDataGrid";
                state.Metadata["CaptureTimestamp"] = DateTime.Now;

                // Capture available columns information from ViewModel
                var availableColumns = GridStateHelpers.GetAvailableColumns(dataGrid);
                if (availableColumns.Count > 0)
                {
                    var availableColumnsMetadata = availableColumns.Select(ac => new
                    {
                        PropertyName = ac.PropertyName,
                        DisplayName = ac.DisplayName,
                        DataType = ac.DataType.FullName,
                        Category = ac.Category,
                        Description = ac.Description,
                        UIType = ac.UIType.ToString(),
                        DropDownValues = ac.DropDownValues?.ToList() // Create a copy
                    }).ToList();

                    state.Metadata["AvailableColumns"] = availableColumnsMetadata;
                    state.Metadata["AvailableColumnsCount"] = availableColumns.Count;

                    System.Diagnostics.Debug.WriteLine($"Captured metadata for {availableColumns.Count} available columns");
                }

                // Capture current column definitions from the DynamicDataGrid
                if (dataGrid.ColumnDefinitions?.Count > 0)
                {
                    var currentColumnDefs = dataGrid.ColumnDefinitions.Select(cd => new
                    {
                        PropertyName = cd.PropertyName,
                        DisplayName = cd.DisplayName,
                        DataType = cd.DataType.FullName,
                        Width = cd.Width,
                        IsReadOnly = cd.IsReadOnly
                    }).ToList();

                    state.Metadata["CurrentColumnDefinitions"] = currentColumnDefs;
                    state.Metadata["CurrentColumnsCount"] = dataGrid.ColumnDefinitions.Count;
                }

                // Capture ViewModel type information for restoration context
                if (dataGrid.DataContext != null)
                {
                    state.Metadata["ViewModelType"] = dataGrid.DataContext.GetType().FullName;
                }

                // Store grid configuration options
                state.Metadata["AutoGenerateColumns"] = dataGrid.AutoGenerateColumns;
                state.Metadata["CanUserAddRows"] = dataGrid.CanUserAddRows;
                state.Metadata["CanUserDeleteRows"] = dataGrid.CanUserDeleteRows;
                state.Metadata["CanUserReorderColumns"] = dataGrid.CanUserReorderColumns;
                state.Metadata["CanUserResizeColumns"] = dataGrid.CanUserResizeColumns;
                state.Metadata["CanUserSortColumns"] = dataGrid.CanUserSortColumns;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error capturing DynamicDataGrid metadata: {ex.Message}");
                state.Metadata["MetadataError"] = ex.Message;
            }
        }

        #endregion

        #region Validation and Diagnostics

        /// <summary>
        /// Validates that a captured state is complete and consistent for a DynamicDataGrid.
        /// Performs post-capture validation to ensure state integrity.
        /// </summary>
        /// <param name="state">The captured DataGridState to validate.</param>
        /// <returns>List of validation issues found, empty if state is valid.</returns>
        internal static System.Collections.Generic.List<string> ValidateCapturedState(DataGridState state)
        {
            var issues = new System.Collections.Generic.List<string>();

            if (state == null)
            {
                issues.Add("State is null");
                return issues;
            }

            try
            {
                // Use the state's built-in validation
                var stateIssues = state.Validate();
                issues.AddRange(stateIssues);

                // Additional DynamicDataGrid-specific validation
                if (!state.Metadata.ContainsKey("GridType") ||
                    state.Metadata["GridType"]?.ToString() != "DynamicDataGrid")
                {
                    issues.Add("State was not captured from a DynamicDataGrid");
                }

                if (!state.Metadata.ContainsKey("AvailableColumns"))
                {
                    issues.Add("Missing AvailableColumns metadata - may affect restoration");
                }

                // Validate that all column states reference valid properties
                if (state.Columns?.Count > 0 && state.Metadata.ContainsKey("AvailableColumns"))
                {
                    var availableProps = new System.Collections.Generic.HashSet<string>();

                    if (state.Metadata["AvailableColumns"] is System.Collections.IEnumerable availableColumns)
                    {
                        foreach (var column in availableColumns)
                        {
                            var propName = column.GetType().GetProperty("PropertyName")?.GetValue(column)?.ToString();
                            if (!string.IsNullOrEmpty(propName))
                            {
                                availableProps.Add(propName);
                            }
                        }
                    }

                    foreach (var columnState in state.Columns)
                    {
                        if (!availableProps.Contains(columnState.PropertyName))
                        {
                            issues.Add($"Column state references unknown property: {columnState.PropertyName}");
                        }
                    }
                }

                // Validate filters reference valid properties
                if (state.Filters?.Count > 0 && state.Metadata.ContainsKey("AvailableColumns"))
                {
                    var availableProps = new System.Collections.Generic.HashSet<string>();

                    if (state.Metadata["AvailableColumns"] is System.Collections.IEnumerable availableColumns)
                    {
                        foreach (var column in availableColumns)
                        {
                            var propName = column.GetType().GetProperty("PropertyName")?.GetValue(column)?.ToString();
                            if (!string.IsNullOrEmpty(propName))
                            {
                                availableProps.Add(propName);
                            }
                        }
                    }

                    foreach (var filterState in state.Filters)
                    {
                        if (!availableProps.Contains(filterState.PropertyName))
                        {
                            issues.Add($"Filter state references unknown property: {filterState.PropertyName}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                issues.Add($"Error during validation: {ex.Message}");
            }

            return issues;
        }

        /// <summary>
        /// Gets diagnostic information about the capture operation.
        /// Useful for debugging state capture issues.
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to get diagnostics for.</param>
        /// <returns>Diagnostic information string.</returns>
        internal static string GetCaptureDiagnostics(DynamicDataGrid dataGrid)
        {
            var diagnostics = new System.Text.StringBuilder();

            try
            {
                diagnostics.AppendLine("=== DYNAMICDATAGRID CAPTURE DIAGNOSTICS ===");
                diagnostics.AppendLine($"Grid Name: {dataGrid.Name ?? "Unnamed"}");
                diagnostics.AppendLine($"Columns Count: {dataGrid.Columns?.Count ?? 0}");
                diagnostics.AppendLine($"Column Definitions Count: {dataGrid.ColumnDefinitions?.Count ?? 0}");
                diagnostics.AppendLine($"Has DataContext: {dataGrid.DataContext != null}");
                diagnostics.AppendLine($"ItemsSource: {dataGrid.ItemsSource?.GetType().Name ?? "None"}");

                // Available columns info
                var availableColumns = GridStateHelpers.GetAvailableColumns(dataGrid);
                diagnostics.AppendLine($"Available Columns: {availableColumns.Count}");

                foreach (var ac in availableColumns.Take(5)) // Show first 5
                {
                    diagnostics.AppendLine($"  - {ac.PropertyName} ({ac.DataType.Name}) - {ac.DisplayName}");
                }

                if (availableColumns.Count > 5)
                {
                    diagnostics.AppendLine($"  ... and {availableColumns.Count - 5} more");
                }

                // Current filters info
                var filterCounts = FilterStateCapture.GetFilterCountsByType(dataGrid);
                diagnostics.AppendLine("Active Filters:");
                foreach (var kvp in filterCounts)
                {
                    if (kvp.Value > 0)
                    {
                        diagnostics.AppendLine($"  - {kvp.Key}: {kvp.Value}");
                    }
                }

                // Sorting info
                var collectionView = CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
                if (collectionView?.SortDescriptions?.Count > 0)
                {
                    var sort = collectionView.SortDescriptions.First();
                    diagnostics.AppendLine($"Sorting: {sort.PropertyName} {sort.Direction}");
                }
                else
                {
                    diagnostics.AppendLine("Sorting: None");
                }
            }
            catch (Exception ex)
            {
                diagnostics.AppendLine($"Error getting diagnostics: {ex.Message}");
            }

            return diagnostics.ToString();
        }

        #endregion
    }
}