// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models
{
    /// <summary>
    /// Holds the active data source type and all per-provider configuration.
    /// Replaces the bare <c>Settings.DataPath</c> string.
    /// <para>
    /// Migration: if DataSource is null on load, or SourceType is None, or
    /// SourceType is Csv but CsvConfig is null (i.e. default-constructed with
    /// no real data), SettingsUtils promotes any legacy DataPath value into
    /// CsvConfig automatically.
    /// </para>
    /// </summary>
    public class DataSourceSettings
    {
        /// <summary>
        /// Which provider is currently active.
        /// Defaults to <see cref="DataSourceType.None"/> so that a freshly
        /// default-constructed instance is distinguishable from one that has
        /// been explicitly configured by the user or migrated from a legacy file.
        /// </summary>
        public DataSourceType SourceType { get; set; } = DataSourceType.None;

        /// <summary>
        /// CSV-specific configuration — populated when SourceType == Csv.
        /// Null for any other active provider.
        /// </summary>
        public CsvDataSourceConfig? CsvConfig { get; set; }

        /// <summary>
        /// drofus connection details — populated when SourceType == Drofus.
        /// Null for any other active provider.
        /// </summary>
        public DrofusDataSourceSettings? Drofus { get; set; }
    }
}