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

using System;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Extension methods for simplified grid state management
    /// </summary>
    public static class GridStateExtensions
    {
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
                Columns = state.Columns?.Select(c => new ColumnState
                {
                    PropertyName = c.PropertyName,
                    DisplayName = c.DisplayName,
                    IsVisible = c.IsVisible,
                    DisplayIndex = c.DisplayIndex,
                    Width = c.Width,
                    IsReadOnly = c.IsReadOnly,
                    DataTypeName = c.DataTypeName
                }).ToList() ?? new List<ColumnState>(),
                Sorting = state.Sorting != null ? new SortState
                {
                    PropertyName = state.Sorting.PropertyName,
                    Direction = state.Sorting.Direction,
                    SortIndex = state.Sorting.SortIndex
                } : null,
                Filters = state.Filters?.Select(f => new FilterState
                {
                    PropertyName = f.PropertyName,
                    FilterType = f.FilterType,
                    FilterValues = new Dictionary<string, object>(f.FilterValues),
                    Description = f.Description
                }).ToList() ?? new List<FilterState>(),
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

            return summary.Count > 0 ? string.Join(", ", summary) : "No configuration";
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

        #endregion

        #region GridStateOptions Extensions

        /// <summary>
        /// Creates a copy of GridStateOptions with selective inclusion
        /// </summary>
        public static GridStateOptions Including(this GridStateOptions options,
            bool? filters = null, bool? sorting = null, bool? visibility = null,
            bool? columnOrder = null, bool? columnWidths = null)
        {
            return new GridStateOptions
            {
                IncludeFilters = filters ?? options.IncludeFilters,
                IncludeSorting = sorting ?? options.IncludeSorting,
                IncludeVisibility = visibility ?? options.IncludeVisibility,
                IncludeColumnOrder = columnOrder ?? options.IncludeColumnOrder,
                IncludeColumnWidths = columnWidths ?? options.IncludeColumnWidths
            };
        }

        #endregion
    }
}