// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.Models;
using System.Collections.Generic;

namespace duHastNet.PushIt.Interfaces
{
    /// <summary>
    /// Contract for all PushIt data source providers.
    /// Implement this interface to add a new provider (CSV, drofus, Excel, etc.)
    /// then register it in DataSourceFactory and the provider is available everywhere.
    /// </summary>
    public interface IDataSource
    {
        /// <summary>
        /// Loads and returns all rooms from the data source.
        /// Must be synchronous — called inside RevitTask.RunAsync which is already
        /// on a background thread; using async here risks deadlocks in Revit context.
        /// </summary>
        List<RoomDataModel> GetRoomsData(DataSourceSettings settings);

        /// <summary>
        /// Returns the column/property definitions for this source.
        /// Used to populate the data grid header row.
        /// </summary>
        List<RoomDataProperty> GetHeaderProperties(DataSourceSettings settings);

        /// <summary>
        /// Checks prerequisites without loading data (file exists, credentials present, etc.).
        /// Returns true if the source is ready; false with a user-readable errorMessage if not.
        /// </summary>
        bool Validate(DataSourceSettings settings, out string errorMessage);
    }
}
