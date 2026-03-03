// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models.Drofus
{
    /// <summary>
    /// A single serialisable mapping entry that links a drofus room API field
    /// to a Revit shared parameter.
    /// <para>
    /// Instances are stored as a <c>List&lt;DrofusPropertyMap&gt;</c> on
    /// <see cref="DrofusDataSourceSettings.PropertyMappings"/> and round-trip
    /// through the PushIt settings JSON file via Newtonsoft.Json without any
    /// additional attributes.
    /// </para>
    /// </summary>
    public class DrofusPropertyMap
    {
        /// <summary>
        /// The JSON field name returned by the drofus rooms API endpoint,
        /// e.g. <c>"room_func_no"</c>, <c>"name"</c>, <c>"programmed_area"</c>.
        /// <para>
        /// Field names are derived dynamically from the first room object in the
        /// API response — they are not hardcoded. This value is the primary key
        /// used to detect duplicate and stale mappings.
        /// </para>
        /// </summary>
        public string DrofusFieldName { get; set; } = string.Empty;

        /// <summary>
        /// The display name of the Revit shared parameter to read from or write to,
        /// e.g. <c>"RDS_RoomFunctionNumber"</c>.
        /// <para>
        /// Used as a human-readable label in the mapping UI and as a fallback
        /// lookup when <see cref="RevitParameterGuid"/> is empty.
        /// </para>
        /// </summary>
        public string RevitParameterName { get; set; } = string.Empty;

        /// <summary>
        /// The GUID of the Revit shared parameter, formatted as a plain string
        /// without braces, e.g. <c>"a1b2c3d4-e5f6-7890-abcd-ef1234567890"</c>.
        /// <para>
        /// Preferred over <see cref="RevitParameterName"/> for all Revit API
        /// lookups — GUIDs are stable across document copies; names are not.
        /// May be left empty if the GUID is not known, in which case name-based
        /// lookup is used as a fallback.
        /// </para>
        /// </summary>
        public string RevitParameterGuid { get; set; } = string.Empty;

        /// <summary>
        /// The direction of data flow for this mapping.
        /// Defaults to <see cref="MappingFlowDirection.DrofusToRevit"/>.
        /// </summary>
        public MappingFlowDirection FlowDirection { get; set; } = MappingFlowDirection.DrofusToRevit;
    }
}
