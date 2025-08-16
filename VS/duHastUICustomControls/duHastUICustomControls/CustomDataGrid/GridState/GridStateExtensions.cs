//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// Written by Claude
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

using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Controls;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Extension methods to make working with grid state easier
    /// </summary>
    public static class GridStateExtensions
    {
        #region DataGrid Extensions

        /// <summary>
        /// Saves the current state of the DataGrid with a simple method call
        /// </summary>
        public static async Task<bool> SaveStateAsync(this DataGrid dataGrid, string stateName)
        {
            return await GridStateBehavior.SaveStateAsync(dataGrid, stateName);
        }

        /// <summary>
        /// Loads a saved state into the DataGrid
        /// </summary>
        public static async Task<bool> LoadStateAsync(this DataGrid dataGrid, string stateName)
        {
            return await GridStateBehavior.LoadStateAsync(dataGrid, stateName);
        }

        /// <summary>
        /// Gets all available saved states for this DataGrid
        /// </summary>
        public static async Task<List<string>> GetAvailableStatesAsync(this DataGrid dataGrid)
        {
            return await GridStateBehavior.GetAvailableStatesAsync(dataGrid);
        }

        /// <summary>
        /// Deletes a saved state
        /// </summary>
        public static async Task<bool> DeleteStateAsync(this DataGrid dataGrid, string stateName)
        {
            return await GridStateBehavior.DeleteStateAsync(dataGrid, stateName);
        }

        /// <summary>
        /// Gets detailed information about all saved states
        /// </summary>
        public static async Task<List<DataGridState>> GetStateInfoAsync(this DataGrid dataGrid)
        {
            return await GridStateBehavior.GetStateInfoAsync(dataGrid);
        }

        /// <summary>
        /// Captures the current state without saving it
        /// </summary>
        public static DataGridState CaptureCurrentState(this DataGrid dataGrid, string stateName = "Current")
        {
            var gridId = GridStateBehavior.GetGridId(dataGrid) ?? dataGrid.Name ?? "UnnamedGrid";

            if (dataGrid is DynamicDataGrid dynamicGrid)
            {
                return GridStateSerializer.CaptureState(dynamicGrid, gridId, stateName);
            }
            else
            {
                return GridStateSerializer.CaptureState(dataGrid, gridId, stateName);
            }
        }

        /// <summary>
        /// Applies a state to the DataGrid
        /// </summary>
        public static bool ApplyState(this DataGrid dataGrid, DataGridState state, GridStateOptions options = null)
        {
            if (dataGrid is DynamicDataGrid dynamicGrid)
            {
                return GridStateSerializer.ApplyState(dynamicGrid, state, options);
            }
            else
            {
                return GridStateSerializer.ApplyState(dataGrid, state, options);
            }
        }

        /// <summary>
        /// Checks if state management is enabled for this DataGrid
        /// </summary>
        public static bool IsStateManagementEnabled(this DataGrid dataGrid)
        {
            return GridStateBehavior.GetEnableStateManagement(dataGrid);
        }

        /// <summary>
        /// Enables state management for this DataGrid with default settings
        /// </summary>
        public static void EnableStateManagement(this DataGrid dataGrid, string gridId = null, GridStateOptions options = null)
        {
            if (string.IsNullOrEmpty(gridId))
            {
                gridId = dataGrid.Name ?? $"{dataGrid.GetType().Name}_{dataGrid.GetHashCode()}";
            }

            GridStateBehavior.SetGridId(dataGrid, gridId);

            if (options != null)
            {
                GridStateBehavior.SetStateOptions(dataGrid, options);
            }

            GridStateBehavior.SetEnableStateManagement(dataGrid, true);
        }

        /// <summary>
        /// Enables state management with auto-save and auto-load
        /// </summary>
        public static void EnableStateManagementWithAuto(this DataGrid dataGrid, string gridId = null,
            string autoStateName = "Default", GridStateOptions options = null)
        {
            dataGrid.EnableStateManagement(gridId, options);
            GridStateBehavior.SetAutoSaveStateName(dataGrid, autoStateName);
            GridStateBehavior.SetAutoLoadStateName(dataGrid, autoStateName);
        }

        #endregion

        #region DataGridState Extensions

        /// <summary>
        /// Creates a deep copy of a DataGridState
        /// </summary>
        public static DataGridState Clone(this DataGridState state)
        {
            return new DataGridState
            {
                GridId = state.GridId,
                StateName = state.StateName + "_Copy",
                CreatedDate = DateTime.Now,
                LastModified = DateTime.Now,
                Version = state.Version,
                Columns = state.Columns.Select(c => new ColumnState
                {
                    PropertyName = c.PropertyName,
                    DisplayName = c.DisplayName,
                    IsVisible = c.IsVisible,
                    DisplayIndex = c.DisplayIndex,
                    Width = c.Width,
                    IsReadOnly = c.IsReadOnly,
                    DataTypeName = c.DataTypeName
                }).ToList(),
                Sorting = state.Sorting != null ? new SortState
                {
                    PropertyName = state.Sorting.PropertyName,
                    Direction = state.Sorting.Direction,
                    SortIndex = state.Sorting.SortIndex
                } : null,
                Filters = state.Filters.Select(f => new FilterState
                {
                    PropertyName = f.PropertyName,
                    FilterType = f.FilterType,
                    FilterValues = new Dictionary<string, object>(f.FilterValues),
                    Description = f.Description
                }).ToList(),
                Metadata = new Dictionary<string, object>(state.Metadata)
            };
        }

        /// <summary>
        /// Gets a summary of the state for display purposes
        /// </summary>
        public static string GetSummary(this DataGridState state)
        {
            var summary = new List<string>();

            if (state.Columns?.Count > 0)
            {
                var visibleColumns = state.Columns.Count(c => c.IsVisible);
                summary.Add($"{visibleColumns}/{state.Columns.Count} columns");
            }

            if (state.Sorting != null)
            {
                summary.Add($"Sorted by {state.Sorting.PropertyName}");
            }

            if (state.Filters?.Count > 0)
            {
                summary.Add($"{state.Filters.Count} filter(s)");
            }

            return string.Join(", ", summary);
        }

        /// <summary>
        /// Checks if this state has any filters applied
        /// </summary>
        public static bool HasFilters(this DataGridState state)
        {
            return state.Filters?.Count > 0;
        }

        /// <summary>
        /// Checks if this state has sorting applied
        /// </summary>
        public static bool HasSorting(this DataGridState state)
        {
            return state.Sorting != null;
        }

        /// <summary>
        /// Gets the names of all filtered columns
        /// </summary>
        public static List<string> GetFilteredColumnNames(this DataGridState state)
        {
            return state.Filters?.Select(f => f.PropertyName).ToList() ?? new List<string>();
        }

        /// <summary>
        /// Gets the names of all visible columns in display order
        /// </summary>
        public static List<string> GetVisibleColumnNames(this DataGridState state)
        {
            return state.Columns?
                .Where(c => c.IsVisible)
                .OrderBy(c => c.DisplayIndex)
                .Select(c => c.DisplayName)
                .ToList() ?? new List<string>();
        }

        /// <summary>
        /// Gets the names of all hidden columns
        /// </summary>
        public static List<string> GetHiddenColumnNames(this DataGridState state)
        {
            return state.Columns?
                .Where(c => !c.IsVisible)
                .Select(c => c.DisplayName)
                .ToList() ?? new List<string>();
        }

        /// <summary>
        /// Merges another state into this one, with options for what to merge
        /// </summary>
        public static DataGridState MergeWith(this DataGridState baseState, DataGridState otherState,
            bool mergeColumns = true, bool mergeSorting = true, bool mergeFilters = true)
        {
            var merged = baseState.Clone();
            merged.StateName = $"{baseState.StateName}_Merged";
            merged.LastModified = DateTime.Now;

            if (mergeColumns && otherState.Columns?.Count > 0)
            {
                // Replace column states
                merged.Columns = otherState.Columns.Select(c => new ColumnState
                {
                    PropertyName = c.PropertyName,
                    DisplayName = c.DisplayName,
                    IsVisible = c.IsVisible,
                    DisplayIndex = c.DisplayIndex,
                    Width = c.Width,
                    IsReadOnly = c.IsReadOnly,
                    DataTypeName = c.DataTypeName
                }).ToList();
            }

            if (mergeSorting && otherState.Sorting != null)
            {
                merged.Sorting = new SortState
                {
                    PropertyName = otherState.Sorting.PropertyName,
                    Direction = otherState.Sorting.Direction,
                    SortIndex = otherState.Sorting.SortIndex
                };
            }

            if (mergeFilters && otherState.Filters?.Count > 0)
            {
                merged.Filters = otherState.Filters.Select(f => new FilterState
                {
                    PropertyName = f.PropertyName,
                    FilterType = f.FilterType,
                    FilterValues = new Dictionary<string, object>(f.FilterValues),
                    Description = f.Description
                }).ToList();
            }

            return merged;
        }

        #endregion

        #region GridStateOptions Extensions

        /// <summary>
        /// Creates a copy of GridStateOptions with auto-save enabled
        /// </summary>
        public static GridStateOptions WithAutoSave(this GridStateOptions options, int delayMs = 2000)
        {
            return new GridStateOptions
            {
                DefaultSaveLocation = options.DefaultSaveLocation,
                AutoSave = true,
                AutoSaveDelay = delayMs,
                IncludeFilters = options.IncludeFilters,
                IncludeSorting = options.IncludeSorting,
                IncludeVisibility = options.IncludeVisibility,
                IncludeColumnOrder = options.IncludeColumnOrder,
                IncludeColumnWidths = options.IncludeColumnWidths,
                MaxStatesPerGrid = options.MaxStatesPerGrid,
                FileExtension = options.FileExtension
            };
        }

        /// <summary>
        /// Creates a copy of GridStateOptions with selective inclusion
        /// </summary>
        public static GridStateOptions Including(this GridStateOptions options,
            bool? filters = null, bool? sorting = null, bool? visibility = null,
            bool? columnOrder = null, bool? columnWidths = null)
        {
            return new GridStateOptions
            {
                DefaultSaveLocation = options.DefaultSaveLocation,
                AutoSave = options.AutoSave,
                AutoSaveDelay = options.AutoSaveDelay,
                IncludeFilters = filters ?? options.IncludeFilters,
                IncludeSorting = sorting ?? options.IncludeSorting,
                IncludeVisibility = visibility ?? options.IncludeVisibility,
                IncludeColumnOrder = columnOrder ?? options.IncludeColumnOrder,
                IncludeColumnWidths = columnWidths ?? options.IncludeColumnWidths,
                MaxStatesPerGrid = options.MaxStatesPerGrid,
                FileExtension = options.FileExtension
            };
        }

        /// <summary>
        /// Creates options that only save/restore columns and their order
        /// </summary>
        public static GridStateOptions ColumnsOnly()
        {
            return new GridStateOptions
            {
                IncludeFilters = false,
                IncludeSorting = false,
                IncludeVisibility = true,
                IncludeColumnOrder = true,
                IncludeColumnWidths = true
            };
        }

        /// <summary>
        /// Creates options that only save/restore filters and sorting
        /// </summary>
        public static GridStateOptions FiltersAndSortingOnly()
        {
            return new GridStateOptions
            {
                IncludeFilters = true,
                IncludeSorting = true,
                IncludeVisibility = false,
                IncludeColumnOrder = false,
                IncludeColumnWidths = false
            };
        }

        #endregion
    }

    /// <summary>
    /// Utility class for common grid state operations
    /// </summary>
    public static class GridStateUtility
    {
        /// <summary>
        /// Creates a default GridStateManager with sensible defaults
        /// </summary>
        public static GridStateManager CreateDefaultManager(string saveLocation = null)
        {
            var options = new GridStateOptions
            {
                DefaultSaveLocation = saveLocation,
                AutoSave = true,
                AutoSaveDelay = 2000,
                IncludeFilters = true,
                IncludeSorting = true,
                IncludeVisibility = true,
                IncludeColumnOrder = true,
                IncludeColumnWidths = true,
                MaxStatesPerGrid = 10
            };

            return new GridStateManager(options);
        }

        /// <summary>
        /// Initializes grid state management for an application
        /// </summary>
        public static void InitializeForApplication(string appName, GridStateOptions options = null)
        {
            var defaultSaveLocation = System.IO.Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                appName,
                "GridStates"
            );

            options = options ?? new GridStateOptions();
            options.DefaultSaveLocation = options.DefaultSaveLocation ?? defaultSaveLocation;

            var manager = new GridStateManager(options);
            GridStateBehavior.SetDefaultStateManager(manager);
        }

        /// <summary>
        /// Compares two grid states and returns differences
        /// </summary>
        public static GridStateDifference CompareStates(DataGridState state1, DataGridState state2)
        {
            var diff = new GridStateDifference();

            // Compare columns
            if (state1.Columns?.Count != state2.Columns?.Count)
            {
                diff.ColumnCountChanged = true;
            }

            if (state1.Columns != null && state2.Columns != null)
            {
                for (int i = 0; i < Math.Min(state1.Columns.Count, state2.Columns.Count); i++)
                {
                    var col1 = state1.Columns[i];
                    var col2 = state2.Columns.FirstOrDefault(c => c.PropertyName == col1.PropertyName);

                    if (col2 == null)
                    {
                        diff.ColumnsAdded.Add(col1.PropertyName);
                    }
                    else
                    {
                        if (col1.IsVisible != col2.IsVisible)
                            diff.ColumnVisibilityChanged.Add(col1.PropertyName);
                        if (col1.DisplayIndex != col2.DisplayIndex)
                            diff.ColumnOrderChanged.Add(col1.PropertyName);
                        if (Math.Abs(col1.Width - col2.Width) > 1)
                            diff.ColumnWidthChanged.Add(col1.PropertyName);
                    }
                }
            }

            // Compare sorting
            if ((state1.Sorting == null) != (state2.Sorting == null))
            {
                diff.SortingChanged = true;
            }
            else if (state1.Sorting != null && state2.Sorting != null)
            {
                if (state1.Sorting.PropertyName != state2.Sorting.PropertyName ||
                    state1.Sorting.Direction != state2.Sorting.Direction)
                {
                    diff.SortingChanged = true;
                }
            }

            // Compare filters
            var filters1 = state1.Filters?.Select(f => f.PropertyName).ToHashSet() ?? new HashSet<string>();
            var filters2 = state2.Filters?.Select(f => f.PropertyName).ToHashSet() ?? new HashSet<string>();

            diff.FiltersAdded = filters1.Except(filters2).ToList();
            diff.FiltersRemoved = filters2.Except(filters1).ToList();

            return diff;
        }

        /// <summary>
        /// Validates a grid state for consistency
        /// </summary>
        public static List<string> ValidateState(DataGridState state)
        {
            var issues = new List<string>();

            if (string.IsNullOrEmpty(state.GridId))
                issues.Add("GridId is required");

            if (string.IsNullOrEmpty(state.StateName))
                issues.Add("StateName is required");

            // Check for duplicate column display indices
            if (state.Columns?.Count > 0)
            {
                var visibleColumns = state.Columns.Where(c => c.IsVisible).ToList();
                var displayIndices = visibleColumns.Select(c => c.DisplayIndex).ToList();
                var duplicateIndices = displayIndices.GroupBy(i => i)
                    .Where(g => g.Count() > 1)
                    .Select(g => g.Key)
                    .ToList();

                if (duplicateIndices.Count > 0)
                {
                    issues.Add($"Duplicate display indices found: {string.Join(", ", duplicateIndices)}");
                }

                // Check for missing display indices
                var expectedIndices = Enumerable.Range(0, visibleColumns.Count).ToHashSet();
                var actualIndices = displayIndices.ToHashSet();
                var missingIndices = expectedIndices.Except(actualIndices).ToList();

                if (missingIndices.Count > 0)
                {
                    issues.Add($"Missing display indices: {string.Join(", ", missingIndices)}");
                }
            }

            return issues;
        }
    }

    /// <summary>
    /// Represents differences between two grid states
    /// </summary>
    public class GridStateDifference
    {
        public bool ColumnCountChanged { get; set; }
        public List<string> ColumnsAdded { get; set; } = new List<string>();
        public List<string> ColumnsRemoved { get; set; } = new List<string>();
        public List<string> ColumnVisibilityChanged { get; set; } = new List<string>();
        public List<string> ColumnOrderChanged { get; set; } = new List<string>();
        public List<string> ColumnWidthChanged { get; set; } = new List<string>();
        public bool SortingChanged { get; set; }
        public List<string> FiltersAdded { get; set; } = new List<string>();
        public List<string> FiltersRemoved { get; set; } = new List<string>();

        public bool HasChanges => ColumnCountChanged || SortingChanged ||
                                 ColumnsAdded.Count > 0 || ColumnsRemoved.Count > 0 ||
                                 ColumnVisibilityChanged.Count > 0 || ColumnOrderChanged.Count > 0 ||
                                 ColumnWidthChanged.Count > 0 || FiltersAdded.Count > 0 ||
                                 FiltersRemoved.Count > 0;
    }
}