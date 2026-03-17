// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models.Drofus
{
    /// <summary>
    /// Represents one element within a drofus attribute configuration, as returned
    /// by <c>GET /api/{db}/{pr}/attributeconfigurations</c>.
    /// <para>
    /// This class is runtime-only and is never serialised to the settings file.
    /// </para>
    /// </summary>
    public class DrofusAttributeConfigurationElement
    {
        /// <summary>
        /// The drofus attribute id for this element. Corresponds to
        /// <see cref="DrofusRoomField.Id"/> in the field catalogue.
        /// Used to resolve which catalogue field this element refers to.
        /// </summary>
        public string DrofusAttributeId { get; set; } = string.Empty;

        /// <summary>
        /// The display label for this element as defined in the attribute
        /// configuration. May differ from <see cref="DrofusRoomField.Name"/>
        /// in the catalogue — the configuration label is project-specific.
        /// </summary>
        public string DrofusAttributeLabel { get; set; } = string.Empty;

        /// <summary>
        /// The raw direction string as returned by the drofus API.
        /// Known values: <c>"Key"</c>, <c>"ToExternalApplication"</c>,
        /// <c>"ToDrofus"</c>.
        /// <para>
        /// PushIt mapping:
        /// <list type="bullet">
        ///   <item><c>"Key"</c> — unique identifier field; sets
        ///     <c>IsUniqueId = true</c> with direction
        ///     <see cref="MappingFlowDirection.DrofusToRevit"/>.</item>
        ///   <item><c>"ToExternalApplication"</c> — drofus → Revit;
        ///     maps to <see cref="MappingFlowDirection.DrofusToRevit"/>.</item>
        ///   <item><c>"ToDrofus"</c> — Revit → drofus;
        ///     maps to <see cref="MappingFlowDirection.RevitToDrofus"/>.</item>
        /// </list>
        /// Any unrecognised value defaults to
        /// <see cref="MappingFlowDirection.DrofusToRevit"/> with
        /// <c>IsUniqueId = false</c> (see Gap 4 in the implementation spec).
        /// </para>
        /// <para>
        /// <c>external_attribute_id</c> and <c>external_attribute_label</c>
        /// from the API response are intentionally ignored — they reference
        /// Revit built-in parameters which PushIt does not use (PushIt uses
        /// shared parameters selected manually by the user).
        /// </para>
        /// </summary>
        public string Direction { get; set; } = string.Empty;
    }
}
