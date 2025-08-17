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

using duHastNet.Utils.WPF.Interfaces;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Represents the state of a DataGrid that can be saved and restored.
    /// Simplified to work with NavigationStore's single-state-per-grid pattern.
    /// </summary>
    public class DataGridState : IGridState
    {
        #region IGridState Implementation

        /// <summary>
        /// Unique identifier for this grid state
        /// </summary>
        public string GridId { get; set; }

        /// <summary>
        /// State name (always "Default" for simplified management)
        /// </summary>
        public string StateName { get; set; } = "Default";

        /// <summary>
        /// When this state was created
        /// </summary>
        public DateTime CreatedDate { get; set; }

        /// <summary>
        /// When this state was last modified
        /// </summary>
        public DateTime LastModified { get; set; }

        /// <summary>
        /// Version of the state format for compatibility
        /// </summary>
        public string Version { get; set; } = "1.0";

        /// <summary>
        /// Additional metadata for grid-specific information
        /// </summary>
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        #endregion

        #region Grid-Specific State Properties

        /// <summary>
        /// Information about each column's state
        /// </summary>
        public List<ColumnState> Columns { get; set; } = new List<ColumnState>();

        /// <summary>
        /// Active sorting configuration
        /// </summary>
        public SortState Sorting { get; set; }

        /// <summary>
        /// Active filters applied to columns
        /// </summary>
        public List<FilterState> Filters { get; set; } = new List<FilterState>();

        #endregion

        #region Constructor

        public DataGridState()
        {
            CreatedDate = DateTime.Now;
            LastModified = DateTime.Now;
        }

        #endregion

        #region IGridState Implementation Methods

        /// <summary>
        /// Gets a summary of the state for display purposes
        /// </summary>
        /// <returns>Human-readable summary of the state</returns>
        public string GetSummary()
        {
            var summary = new List<string>();

            if (Columns?.Count > 0)
            {
                var visibleColumns = Columns.Count(c => c.IsVisible);
                summary.Add($"{visibleColumns}/{Columns.Count} columns");
            }

            if (Sorting != null)
            {
                summary.Add($"Sorted by {Sorting.PropertyName}");
            }

            if (Filters?.Count > 0)
            {
                summary.Add($"{Filters.Count} filter(s)");
            }

            return summary.Count > 0 ? string.Join(", ", summary) : "No configuration";
        }

        /// <summary>
        /// Creates a deep copy of this state
        /// </summary>
        /// <returns>A new instance that is a copy of this state</returns>
        public IGridState Clone()
        {
            return new DataGridState
            {
                GridId = GridId,
                StateName = StateName,
                CreatedDate = DateTime.Now,
                LastModified = DateTime.Now,
                Version = Version,
                Columns = Columns?.Select(c => new ColumnState
                {
                    PropertyName = c.PropertyName,
                    DisplayName = c.DisplayName,
                    IsVisible = c.IsVisible,
                    DisplayIndex = c.DisplayIndex,
                    Width = c.Width,
                    IsReadOnly = c.IsReadOnly,
                    DataTypeName = c.DataTypeName
                }).ToList() ?? new List<ColumnState>(),
                Sorting = Sorting != null ? new SortState
                {
                    PropertyName = Sorting.PropertyName,
                    Direction = Sorting.Direction,
                    SortIndex = Sorting.SortIndex
                } : null,
                Filters = Filters?.Select(f => new FilterState
                {
                    PropertyName = f.PropertyName,
                    FilterType = f.FilterType,
                    FilterValues = new Dictionary<string, object>(f.FilterValues),
                    Description = f.Description
                }).ToList() ?? new List<FilterState>(),
                Metadata = new Dictionary<string, object>(Metadata)
            };
        }

        /// <summary>
        /// Serializes this state to a string for persistence
        /// </summary>
        /// <returns>Serialized string representation</returns>
        public string Serialize()
        {
            try
            {
                var settings = new JsonSerializerSettings
                {
                    DateFormatHandling = DateFormatHandling.IsoDateFormat,
                    NullValueHandling = NullValueHandling.Ignore,
                    DefaultValueHandling = DefaultValueHandling.Ignore
                };

                return JsonConvert.SerializeObject(this, Formatting.None, settings);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error serializing DataGridState: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Deserializes state from a string
        /// </summary>
        /// <param name="serializedState">Serialized state string</param>
        /// <returns>True if deserialization was successful</returns>
        public bool Deserialize(string serializedState)
        {
            try
            {
                if (string.IsNullOrEmpty(serializedState))
                    return false;

                var settings = new JsonSerializerSettings
                {
                    DateFormatHandling = DateFormatHandling.IsoDateFormat,
                    NullValueHandling = NullValueHandling.Ignore,
                    MissingMemberHandling = MissingMemberHandling.Ignore,
                    Error = (sender, args) =>
                    {
                        System.Diagnostics.Debug.WriteLine($"JSON deserialization error: {args.ErrorContext.Error.Message}");
                        args.ErrorContext.Handled = true;
                    }
                };

                var deserialized = JsonConvert.DeserializeObject<DataGridState>(serializedState, settings);
                if (deserialized != null)
                {
                    // Copy properties from deserialized object
                    GridId = deserialized.GridId;
                    StateName = deserialized.StateName ?? "Default";
                    CreatedDate = deserialized.CreatedDate;
                    LastModified = deserialized.LastModified;
                    Version = deserialized.Version ?? "1.0";
                    Columns = deserialized.Columns ?? new List<ColumnState>();
                    Sorting = deserialized.Sorting;
                    Filters = deserialized.Filters ?? new List<FilterState>();
                    Metadata = deserialized.Metadata ?? new Dictionary<string, object>();
                    return true;
                }
            }
            catch (JsonException jsonEx)
            {
                System.Diagnostics.Debug.WriteLine($"JSON error deserializing DataGridState: {jsonEx.Message}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error deserializing DataGridState: {ex.Message}");
            }

            return false;
        }

        /// <summary>
        /// Validates that this state is internally consistent
        /// </summary>
        /// <returns>List of validation errors, empty if valid</returns>
        public List<string> Validate()
        {
            var issues = new List<string>();

            if (string.IsNullOrEmpty(GridId))
                issues.Add("GridId is required");

            if (string.IsNullOrEmpty(Version))
                issues.Add("Version is required");

            // Check for duplicate column display indices
            if (Columns?.Count > 0)
            {
                var visibleColumns = Columns.Where(c => c.IsVisible).ToList();
                if (visibleColumns.Count > 0)
                {
                    var displayIndices = visibleColumns.Select(c => c.DisplayIndex).ToList();
                    var duplicateIndices = displayIndices.GroupBy(i => i)
                        .Where(g => g.Count() > 1)
                        .Select(g => g.Key)
                        .ToList();

                    if (duplicateIndices.Count > 0)
                    {
                        issues.Add($"Duplicate display indices found: {string.Join(", ", duplicateIndices)}");
                    }

                    // Check for missing display indices (should be consecutive starting from 0)
                    var expectedIndices = Enumerable.Range(0, visibleColumns.Count).ToHashSet();
                    var actualIndices = displayIndices.ToHashSet();
                    var missingIndices = expectedIndices.Except(actualIndices).ToList();

                    if (missingIndices.Count > 0)
                    {
                        issues.Add($"Missing display indices: {string.Join(", ", missingIndices)}");
                    }
                }

                // Check for columns with missing property names
                var columnsWithoutPropertyName = Columns.Where(c => string.IsNullOrEmpty(c.PropertyName)).ToList();
                if (columnsWithoutPropertyName.Count > 0)
                {
                    issues.Add($"{columnsWithoutPropertyName.Count} column(s) missing PropertyName");
                }

                // Check for columns with invalid widths
                var columnsWithInvalidWidth = Columns.Where(c => c.Width < 0).ToList();
                if (columnsWithInvalidWidth.Count > 0)
                {
                    issues.Add($"{columnsWithInvalidWidth.Count} column(s) have invalid width");
                }
            }

            // Validate sorting
            if (Sorting != null && string.IsNullOrEmpty(Sorting.PropertyName))
            {
                issues.Add("Sorting property name cannot be empty");
            }

            // Validate filters
            if (Filters?.Count > 0)
            {
                for (int i = 0; i < Filters.Count; i++)
                {
                    var filter = Filters[i];
                    if (string.IsNullOrEmpty(filter.PropertyName))
                    {
                        issues.Add($"Filter {i}: PropertyName is required");
                    }
                    if (filter.FilterValues == null)
                    {
                        issues.Add($"Filter {i}: FilterValues cannot be null");
                    }
                }
            }

            return issues;
        }

        #endregion

        #region Utility Properties

        /// <summary>
        /// Checks if this state has any filters applied
        /// </summary>
        public bool HasFilters => Filters?.Count > 0;

        /// <summary>
        /// Checks if this state has sorting applied
        /// </summary>
        public bool HasSorting => Sorting != null;

        /// <summary>
        /// Gets the names of all filtered columns
        /// </summary>
        public List<string> GetFilteredColumnNames()
        {
            return Filters?.Select(f => f.PropertyName).ToList() ?? new List<string>();
        }

        /// <summary>
        /// Gets the names of all visible columns in display order
        /// </summary>
        public List<string> GetVisibleColumnNames()
        {
            return Columns?
                .Where(c => c.IsVisible)
                .OrderBy(c => c.DisplayIndex)
                .Select(c => c.DisplayName)
                .ToList() ?? new List<string>();
        }

        /// <summary>
        /// Gets the names of all hidden columns
        /// </summary>
        public List<string> GetHiddenColumnNames()
        {
            return Columns?
                .Where(c => !c.IsVisible)
                .Select(c => c.DisplayName)
                .ToList() ?? new List<string>();
        }

        #endregion
    }
}