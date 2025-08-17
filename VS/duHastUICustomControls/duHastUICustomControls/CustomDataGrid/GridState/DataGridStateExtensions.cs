using duHastNet.UI.CustomControls.CustomDataGrid.GridState;
using duHastNet.Utils.WPF.Interfaces;

using System.Collections.Generic;

/// <summary>
/// Extension methods for DataGridState to provide additional utility methods
/// </summary>
public static class DataGridStateExtensions
{
    /// <summary>
    /// Converts a DataGridState to IGridState (no conversion needed since it implements the interface)
    /// </summary>
    /// <param name="state">The DataGridState to convert</param>
    /// <returns>The same state as IGridState</returns>
    public static IGridState AsIGridState(this DataGridState state)
    {
        return state;
    }

    /// <summary>
    /// Safely casts an IGridState back to DataGridState
    /// </summary>
    /// <param name="state">The IGridState to cast</param>
    /// <returns>DataGridState if cast is valid, null otherwise</returns>
    public static DataGridState AsDataGridState(this IGridState state)
    {
        return state as DataGridState;
    }

    /// <summary>
    /// Creates a DataGridState from an IGridState if it's not already one
    /// </summary>
    /// <param name="state">The IGridState to convert</param>
    /// <returns>DataGridState representation</returns>
    public static DataGridState ToDataGridState(this IGridState state)
    {
        if (state is DataGridState dataGridState)
            return dataGridState;

        // Create a new DataGridState and try to deserialize from the source
        var newState = new DataGridState
        {
            GridId = state.GridId,
            StateName = state.StateName,
            CreatedDate = state.CreatedDate,
            LastModified = state.LastModified,
            Version = state.Version,
            Metadata = new Dictionary<string, object>(state.Metadata)
        };

        // Try to deserialize additional data
        var serialized = state.Serialize();
        if (!string.IsNullOrEmpty(serialized))
        {
            newState.Deserialize(serialized);
        }

        return newState;
    }

    /// <summary>
    /// Compares two DataGridStates for equality based on their content
    /// </summary>
    /// <param name="state1">First state to compare</param>
    /// <param name="state2">Second state to compare</param>
    /// <returns>True if states are equivalent</returns>
    public static bool IsEquivalentTo(this DataGridState state1, DataGridState state2)
    {
        if (state1 == null && state2 == null) return true;
        if (state1 == null || state2 == null) return false;

        // Compare basic properties
        if (state1.GridId != state2.GridId) return false;
        if (state1.Version != state2.Version) return false;

        // Compare serialized representations for deep comparison
        try
        {
            var serialized1 = state1.Serialize();
            var serialized2 = state2.Serialize();
            return serialized1 == serialized2;
        }
        catch
        {
            return false;
        }
    }
}