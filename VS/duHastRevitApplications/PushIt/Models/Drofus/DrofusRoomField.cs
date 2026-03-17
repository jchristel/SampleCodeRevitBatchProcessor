// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models.Drofus
{
    /// <summary>
    /// Represents one entry in the drofus room field catalogue, as returned by
    /// <c>OPTIONS /api/{db}/{pr}/rooms</c>.
    /// <para>
    /// This class is runtime-only and is never serialised to the settings file.
    /// The stable <see cref="Id"/> value (the JSON key) is what gets persisted
    /// inside <see cref="DrofusPropertyMap.DrofusFieldName"/>; the human-readable
    /// <see cref="Name"/> is resolved at display time from the live catalogue.
    /// </para>
    /// </summary>
    public class DrofusRoomField
    {
        /// <summary>
        /// The JSON property key returned by the drofus rooms endpoint,
        /// e.g. <c>"room_func_no"</c>, <c>"programmed_area"</c>,
        /// <c>"room_data_10151910"</c>.
        /// <para>
        /// This is the stable identifier stored in
        /// <see cref="DrofusPropertyMap.DrofusFieldName"/>. It is used for all
        /// internal comparisons and catalogue lookups.
        /// </para>
        /// </summary>
        public string Id { get; set; } = string.Empty;

        /// <summary>
        /// Human-readable display label for this field, as supplied by the drofus
        /// API, e.g. <c>"Room Function Number"</c>, <c>"Programmed Area"</c>.
        /// Shown in the mapping dialog dropdown in place of the raw JSON key.
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// The logical group this field belongs to within the drofus data model,
        /// e.g. <c>"Base"</c>, <c>"RoomData"</c>, <c>"Measurement"</c>.
        /// Used for optional grouping in the mapping dialog UI.
        /// </summary>
        public string PropertyGroup { get; set; } = string.Empty;

        /// <summary>
        /// The data type of this field as reported by the drofus API,
        /// e.g. <c>"string"</c>, <c>"number"</c>, <c>"integer"</c>,
        /// <c>"boolean"</c>, <c>"array"</c>.
        /// </summary>
        public string DataType { get; set; } = string.Empty;

        /// <summary>
        /// The unit associated with this field, e.g. <c>"SquareMeters"</c>,
        /// <c>"Undefined"</c>. Empty string when no unit applies.
        /// </summary>
        public string Unit { get; set; } = string.Empty;
    }
}
