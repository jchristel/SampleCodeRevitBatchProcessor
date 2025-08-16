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
using System.ComponentModel;

namespace duHastNet.UI.CustomControls.CustomDataGrid.GridState
{
    /// <summary>
    /// Represents the complete state of a DataGrid that can be saved and restored
    /// </summary>
    public class DataGridState
    {
        /// <summary>
        /// Unique identifier for this grid state (e.g., ViewModel name + grid identifier)
        /// </summary>
        public string GridId { get; set; }

        /// <summary>
        /// Human-readable name for this state
        /// </summary>
        public string StateName { get; set; }

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

        /// <summary>
        /// Additional metadata that can be used by specific implementations
        /// </summary>
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        public DataGridState()
        {
            CreatedDate = DateTime.Now;
            LastModified = DateTime.Now;
        }
    }

    /// <summary>
    /// Represents the state of a single column
    /// </summary>
    public class ColumnState
    {
        /// <summary>
        /// Property name that identifies this column
        /// </summary>
        public string PropertyName { get; set; }

        /// <summary>
        /// Display name of the column
        /// </summary>
        public string DisplayName { get; set; }

        /// <summary>
        /// Whether this column is currently visible
        /// </summary>
        public bool IsVisible { get; set; } = true;

        /// <summary>
        /// Display order of the column (0-based)
        /// </summary>
        public int DisplayIndex { get; set; }

        /// <summary>
        /// Width of the column
        /// </summary>
        public double Width { get; set; }

        /// <summary>
        /// Whether this column is read-only
        /// </summary>
        public bool IsReadOnly { get; set; }

        /// <summary>
        /// Data type of the column for restoration purposes
        /// </summary>
        public string DataTypeName { get; set; }
    }

    /// <summary>
    /// Represents the sorting state of the grid
    /// </summary>
    public class SortState
    {
        /// <summary>
        /// Property name of the column being sorted
        /// </summary>
        public string PropertyName { get; set; }

        /// <summary>
        /// Direction of the sort
        /// </summary>
        public ListSortDirection Direction { get; set; }

        /// <summary>
        /// Index for multi-column sorting (future enhancement)
        /// </summary>
        public int SortIndex { get; set; } = 0;
    }

    /// <summary>
    /// Represents a filter applied to a column
    /// </summary>
    public class FilterState
    {
        /// <summary>
        /// Property name of the filtered column
        /// </summary>
        public string PropertyName { get; set; }

        /// <summary>
        /// Type of filter (Text, Boolean, Numeric, DateTime, DropDown)
        /// </summary>
        public FilterType FilterType { get; set; }

        /// <summary>
        /// Filter values stored as key-value pairs to handle different filter types
        /// </summary>
        public Dictionary<string, object> FilterValues { get; set; } = new Dictionary<string, object>();

        /// <summary>
        /// Human-readable description of the filter for display purposes
        /// </summary>
        public string Description { get; set; }
    }

    /// <summary>
    /// Types of filters supported by the grid
    /// </summary>
    public enum FilterType
    {
        Text,
        Boolean,
        Numeric,
        DateTime,
        DropDown
    }

    /// <summary>
    /// Options for saving and loading grid states
    /// </summary>
    public class GridStateOptions
    {
        /// <summary>
        /// Default location for saving grid states
        /// </summary>
        public string DefaultSaveLocation { get; set; }

        /// <summary>
        /// Whether to automatically save state when grid is modified
        /// </summary>
        public bool AutoSave { get; set; } = false;

        /// <summary>
        /// Delay in milliseconds before auto-saving after a change
        /// </summary>
        public int AutoSaveDelay { get; set; } = 2000;

        /// <summary>
        /// Whether to include filter states when saving
        /// </summary>
        public bool IncludeFilters { get; set; } = true;

        /// <summary>
        /// Whether to include sorting state when saving
        /// </summary>
        public bool IncludeSorting { get; set; } = true;

        /// <summary>
        /// Whether to include column visibility when saving
        /// </summary>
        public bool IncludeVisibility { get; set; } = true;

        /// <summary>
        /// Whether to include column order when saving
        /// </summary>
        public bool IncludeColumnOrder { get; set; } = true;

        /// <summary>
        /// Whether to include column widths when saving
        /// </summary>
        public bool IncludeColumnWidths { get; set; } = true;

        /// <summary>
        /// Maximum number of states to keep per grid
        /// </summary>
        public int MaxStatesPerGrid { get; set; } = 10;

        /// <summary>
        /// File extension for state files
        /// </summary>
        public string FileExtension { get; set; } = ".gridstate";
    }

    /// <summary>
    /// Event arguments for grid state events
    /// </summary>
    public class GridStateEventArgs : EventArgs
    {
        public string GridId { get; set; }
        public string StateName { get; set; }
        public DataGridState State { get; set; }
        public Exception Exception { get; set; }
        public bool Success { get; set; }

        public GridStateEventArgs(string gridId, string stateName, DataGridState state = null)
        {
            GridId = gridId;
            StateName = stateName;
            State = state;
            Success = true;
        }

        public GridStateEventArgs(string gridId, string stateName, Exception exception)
        {
            GridId = gridId;
            StateName = stateName;
            Exception = exception;
            Success = false;
        }
    }
}