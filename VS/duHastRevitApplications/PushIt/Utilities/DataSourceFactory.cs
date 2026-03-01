// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.Models;
using duHastNet.PushIt.Interfaces;
using System;

namespace duHastNet.PushIt.Utilities
{
    /// <summary>
    /// Maps <see cref="DataSourceType"/> to the correct <see cref="IDataSource"/> implementation.
    /// Add new providers here — nothing else needs to change.
    /// </summary>
    public static class DataSourceFactory
    {
        public static IDataSource Create(DataSourceType type) => type switch
        {
            DataSourceType.Csv    => new CsvDataSource(),
            DataSourceType.Drofus => new DrofusDataSource(),
            _ => throw new NotSupportedException($"Unknown data source type: {type}")
        };
    }
}
