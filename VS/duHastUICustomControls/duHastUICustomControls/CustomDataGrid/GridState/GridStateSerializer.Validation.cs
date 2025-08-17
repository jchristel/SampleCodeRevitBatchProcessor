//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

using duHastNet.UI.CustomControls.CustomDataGrid;
using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Extensions to GridStateSerializer for validation and diagnostics
    /// </summary>
    public static partial class GridStateSerializer
    {
        #region Validation Methods

        /// <summary>
        /// Validates that a DataGridState is compatible with a specific DynamicDataGrid
        /// </summary>
        /// <param name="dataGrid">The target DynamicDataGrid</param>
        /// <param name="state">The state to validate</param>
        /// <returns>Validation result with any errors or warnings</returns>
        public static GridStateValidationResult ValidateState(DynamicDataGrid dataGrid, DataGridState state)
        {
            var result = new GridStateValidationResult();

            if (dataGrid == null)
            {
                result.AddError("DataGrid is null");
                return result;
            }

            if (state == null)
            {
                result.AddError("State is null");
                return result;
            }

            try
            {
                // Validate basic state integrity
                ValidateStateIntegrity(state, result);

                // Validate compatibility with current grid
                ValidateGridCompatibility(dataGrid, state, result);

                // Validate column states
                ValidateColumnStates(dataGrid, state, result);

                // Validate filter states
                ValidateFilterStates(dataGrid, state, result);

                // Validate sorting state
                ValidateSortingState(dataGrid, state, result);
            }
            catch (Exception ex)
            {
                result.AddError($"Validation failed with exception: {ex.Message}");
            }

            return result;
        }

        private static void ValidateStateIntegrity(DataGridState state, GridStateValidationResult result)
        {
            // Use the state's built-in validation
            var stateErrors = state.Validate();
            foreach (var error in stateErrors)
            {
                result.AddError($"State integrity: {error}");
            }

            // Additional checks
            if (string.IsNullOrEmpty(state.GridId))
            {
                result.AddError("State has no GridId");
            }

            if (state.Version != "1.0")
            {
                result.AddWarning($"State version '{state.Version}' may not be fully compatible");
            }
        }

        private static void ValidateGridCompatibility(DynamicDataGrid dataGrid, DataGridState state, GridStateValidationResult result)
        {
            // Check if state was created from a compatible grid type
            if (state.Metadata.TryGetValue("GridType", out var gridType) &&
                gridType?.ToString() != "DynamicDataGrid")
            {
                result.AddWarning($"State was created from {gridType}, not DynamicDataGrid");
            }

            // Check ViewModel compatibility
            if (dataGrid.DataContext != null &&
                state.Metadata.TryGetValue("ViewModelType", out var vmType))
            {
                var currentVMType = dataGrid.DataContext.GetType().FullName;
                if (vmType?.ToString() != currentVMType)
                {
                    result.AddWarning($"State was created from ViewModel '{vmType}', current is '{currentVMType}'");
                }
            }
        }

        private static void ValidateColumnStates(DynamicDataGrid dataGrid, DataGridState state, GridStateValidationResult result)
        {
            if (state.Columns?.Count == 0)
            {
                result.AddWarning("State contains no column information");
                return;
            }

            // Get available columns from the grid's ViewModel
            var availableColumns = GridStateHelpers.GetAvailableColumns(dataGrid);
            var availablePropertyNames = availableColumns.Select(ac => ac.PropertyName).ToHashSet();

            foreach (var columnState in state.Columns ?? Enumerable.Empty<ColumnState>())
            {
                if (!availablePropertyNames.Contains(columnState.PropertyName))
                {
                    result.AddError($"Column '{columnState.PropertyName}' from state is not available in current grid");
                }

                if (columnState.Width < 0)
                {
                    result.AddWarning($"Column '{columnState.PropertyName}' has invalid width: {columnState.Width}");
                }
            }

            // Check for missing columns
            var statePropertyNames = state.Columns?.Select(cs => cs.PropertyName).ToHashSet() ?? new HashSet<string>();
            var currentColumns = dataGrid.ColumnDefinitions?.Select(cd => cd.PropertyName).ToHashSet() ?? new HashSet<string>();

            foreach (var currentColumn in currentColumns)
            {
                if (!statePropertyNames.Contains(currentColumn))
                {
                    result.AddWarning($"Current column '{currentColumn}' is not present in saved state");
                }
            }
        }

        private static void ValidateFilterStates(DynamicDataGrid dataGrid, DataGridState state, GridStateValidationResult result)
        {
            if (state.Filters?.Count == 0)
                return; // No filters to validate

            var availableColumns = GridStateHelpers.GetAvailableColumns(dataGrid);
            var availablePropertyNames = availableColumns.Select(ac => ac.PropertyName).ToHashSet();

            foreach (var filterState in state.Filters ?? Enumerable.Empty<FilterState>())
            {
                if (!availablePropertyNames.Contains(filterState.PropertyName))
                {
                    result.AddError($"Filter for '{filterState.PropertyName}' cannot be applied - column not available");
                    continue;
                }

                // Validate filter values based on type
                ValidateFilterValues(filterState, result);
            }
        }

        private static void ValidateFilterValues(FilterState filterState, GridStateValidationResult result)
        {
            switch (filterState.FilterType)
            {
                case FilterType.Text:
                    if (!filterState.FilterValues.ContainsKey("FilterText"))
                    {
                        result.AddError($"Text filter for '{filterState.PropertyName}' missing FilterText value");
                    }
                    break;

                case FilterType.Boolean:
                    if (!filterState.FilterValues.ContainsKey("ShowTrue") &&
                        !filterState.FilterValues.ContainsKey("ShowFalse"))
                    {
                        result.AddError($"Boolean filter for '{filterState.PropertyName}' missing show values");
                    }
                    break;

                case FilterType.Numeric:
                    if (!filterState.FilterValues.ContainsKey("Operation"))
                    {
                        result.AddError($"Numeric filter for '{filterState.PropertyName}' missing Operation");
                    }
                    break;

                case FilterType.DateTime:
                    if (!filterState.FilterValues.ContainsKey("Operation"))
                    {
                        result.AddError($"DateTime filter for '{filterState.PropertyName}' missing Operation");
                    }
                    break;

                case FilterType.DropDown:
                    if (!filterState.FilterValues.ContainsKey("SelectedValue"))
                    {
                        result.AddError($"DropDown filter for '{filterState.PropertyName}' missing SelectedValue");
                    }
                    break;

                default:
                    result.AddWarning($"Unknown filter type '{filterState.FilterType}' for '{filterState.PropertyName}'");
                    break;
            }
        }

        private static void ValidateSortingState(DynamicDataGrid dataGrid, DataGridState state, GridStateValidationResult result)
        {
            if (state.Sorting == null)
                return; // No sorting to validate

            var availableColumns = GridStateHelpers.GetAvailableColumns(dataGrid);
            var availablePropertyNames = availableColumns.Select(ac => ac.PropertyName).ToHashSet();

            if (!availablePropertyNames.Contains(state.Sorting.PropertyName))
            {
                result.AddError($"Sort on '{state.Sorting.PropertyName}' cannot be applied - column not available");
            }
        }

        #endregion

        #region Diagnostics Methods

        /// <summary>
        /// Gets comprehensive diagnostic information about a DynamicDataGrid and its state
        /// </summary>
        /// <param name="dataGrid">The DynamicDataGrid to analyze</param>
        /// <param name="state">Optional state to compare against</param>
        /// <returns>Detailed diagnostic information</returns>
        public static string GetDiagnostics(DynamicDataGrid dataGrid, DataGridState state = null)
        {
            var diagnostics = new StringBuilder();

            try
            {
                diagnostics.AppendLine("=== DYNAMICDATAGRID STATE DIAGNOSTICS ===");
                diagnostics.AppendLine($"Timestamp: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
                diagnostics.AppendLine();

                // Basic grid information
                AddBasicGridInfo(dataGrid, diagnostics);

                // Column information
                AddColumnInfo(dataGrid, diagnostics);

                // Current state information
                AddCurrentStateInfo(dataGrid, diagnostics);

                // State comparison if provided
                if (state != null)
                {
                    AddStateComparisonInfo(dataGrid, state, diagnostics);
                }

                // Filter information
                AddFilterInfo(dataGrid, diagnostics);

                // ViewModel information
                AddViewModelInfo(dataGrid, diagnostics);
            }
            catch (Exception ex)
            {
                diagnostics.AppendLine($"Error generating diagnostics: {ex.Message}");
            }

            return diagnostics.ToString();
        }

        private static void AddBasicGridInfo(DynamicDataGrid dataGrid, StringBuilder diagnostics)
        {
            diagnostics.AppendLine("=== BASIC GRID INFORMATION ===");
            diagnostics.AppendLine($"Grid Name: {dataGrid.Name ?? "Unnamed"}");
            diagnostics.AppendLine($"Grid Type: {dataGrid.GetType().Name}");
            diagnostics.AppendLine($"Current Columns: {dataGrid.Columns?.Count ?? 0}");
            diagnostics.AppendLine($"Column Definitions: {dataGrid.ColumnDefinitions?.Count ?? 0}");
            diagnostics.AppendLine($"Items Count: {dataGrid.Items?.Count ?? 0}");
            diagnostics.AppendLine($"Has DataContext: {dataGrid.DataContext != null}");
            diagnostics.AppendLine($"ItemsSource Type: {dataGrid.ItemsSource?.GetType().Name ?? "None"}");
            diagnostics.AppendLine();
        }

        private static void AddColumnInfo(DynamicDataGrid dataGrid, StringBuilder diagnostics)
        {
            diagnostics.AppendLine("=== COLUMN INFORMATION ===");

            if (dataGrid.ColumnDefinitions?.Count > 0)
            {
                diagnostics.AppendLine("Column Definitions:");
                foreach (var colDef in dataGrid.ColumnDefinitions)
                {
                    diagnostics.AppendLine($"  - {colDef.PropertyName} ({colDef.DataType.Name}) - '{colDef.DisplayName}' [Width: {colDef.Width}, ReadOnly: {colDef.IsReadOnly}]");
                }
            }

            if (dataGrid.Columns?.Count > 0)
            {
                diagnostics.AppendLine("Actual Columns (by display order):");
                var orderedColumns = dataGrid.Columns.OrderBy(c => c.DisplayIndex);
                foreach (var column in orderedColumns)
                {
                    var propName = GridStateHelpers.GetColumnPropertyName(column);
                    diagnostics.AppendLine($"  [{column.DisplayIndex}] {column.Header} (Property: {propName}, Width: {column.ActualWidth:F1}, Visible: {column.Visibility})");
                }
            }

            var availableColumns = GridStateHelpers.GetAvailableColumns(dataGrid);
            diagnostics.AppendLine($"Available Columns: {availableColumns.Count}");
            foreach (var ac in availableColumns.Take(10)) // Show first 10
            {
                diagnostics.AppendLine($"  - {ac.PropertyName} ({ac.DataType.Name}) - '{ac.DisplayName}' [{ac.Category}]");
            }
            if (availableColumns.Count > 10)
            {
                diagnostics.AppendLine($"  ... and {availableColumns.Count - 10} more");
            }

            diagnostics.AppendLine();
        }

        private static void AddCurrentStateInfo(DynamicDataGrid dataGrid, StringBuilder diagnostics)
        {
            diagnostics.AppendLine("=== CURRENT STATE INFORMATION ===");

            // Sorting
            var collectionView = System.Windows.Data.CollectionViewSource.GetDefaultView(dataGrid.ItemsSource);
            if (collectionView?.SortDescriptions?.Count > 0)
            {
                var sort = collectionView.SortDescriptions.First();
                diagnostics.AppendLine($"Sorting: {sort.PropertyName} {sort.Direction}");
            }
            else
            {
                diagnostics.AppendLine("Sorting: None");
            }

            // Filters
            var filterCounts = FilterStateCapture.GetFilterCountsByType(dataGrid);
            var activeFilters = filterCounts.Where(kvp => kvp.Value > 0).ToList();
            if (activeFilters.Any())
            {
                diagnostics.AppendLine("Active Filters:");
                foreach (var kvp in activeFilters)
                {
                    diagnostics.AppendLine($"  - {kvp.Key}: {kvp.Value}");
                }
            }
            else
            {
                diagnostics.AppendLine("Active Filters: None");
            }

            diagnostics.AppendLine();
        }

        private static void AddStateComparisonInfo(DynamicDataGrid dataGrid, DataGridState state, StringBuilder diagnostics)
        {
            diagnostics.AppendLine("=== STATE COMPARISON ===");
            diagnostics.AppendLine($"State GridId: {state.GridId}");
            diagnostics.AppendLine($"State Created: {state.CreatedDate:yyyy-MM-dd HH:mm:ss}");
            diagnostics.AppendLine($"State Modified: {state.LastModified:yyyy-MM-dd HH:mm:ss}");
            diagnostics.AppendLine($"State Version: {state.Version}");

            // Validate the state
            var validation = ValidateState(dataGrid, state);
            diagnostics.AppendLine($"State Compatibility: {(validation.IsValid ? "VALID" : "INVALID")}");

            if (!validation.IsValid)
            {
                diagnostics.AppendLine("Validation Errors:");
                foreach (var error in validation.Errors)
                {
                    diagnostics.AppendLine($"  - {error}");
                }
            }

            if (validation.HasWarnings)
            {
                diagnostics.AppendLine("Validation Warnings:");
                foreach (var warning in validation.Warnings)
                {
                    diagnostics.AppendLine($"  - {warning}");
                }
            }

            diagnostics.AppendLine();
        }

        private static void AddFilterInfo(DynamicDataGrid dataGrid, StringBuilder diagnostics)
        {
            diagnostics.AppendLine("=== DETAILED FILTER INFORMATION ===");

            var allFilters = FilterStateCapture.CaptureAllFilterStates(dataGrid);
            if (allFilters.Count > 0)
            {
                foreach (var filter in allFilters)
                {
                    diagnostics.AppendLine($"Filter: {filter.PropertyName} ({filter.FilterType})");
                    diagnostics.AppendLine($"  Description: {filter.Description}");
                    diagnostics.AppendLine($"  Values: {string.Join(", ", filter.FilterValues.Select(kvp => $"{kvp.Key}={kvp.Value}"))}");
                }
            }
            else
            {
                diagnostics.AppendLine("No active filters");
            }

            diagnostics.AppendLine();
        }

        private static void AddViewModelInfo(DynamicDataGrid dataGrid, StringBuilder diagnostics)
        {
            diagnostics.AppendLine("=== VIEWMODEL INFORMATION ===");

            if (dataGrid.DataContext != null)
            {
                var vm = dataGrid.DataContext;
                diagnostics.AppendLine($"ViewModel Type: {vm.GetType().FullName}");
                diagnostics.AppendLine($"Assembly: {vm.GetType().Assembly.GetName().Name}");

                // Check if it supports state management
                if (vm is duHastNet.Utils.WPF.Interfaces.IGridStateSupport stateSupport)
                {
                    diagnostics.AppendLine($"State Management Enabled: {stateSupport.StateManagementEnabled}");
                    diagnostics.AppendLine($"Grid State ID: {stateSupport.GetGridStateId()}");
                }
                else
                {
                    diagnostics.AppendLine("State Management: Not supported");
                }
            }
            else
            {
                diagnostics.AppendLine("No ViewModel (DataContext is null)");
            }

            diagnostics.AppendLine();
        }

        #endregion
    }
}