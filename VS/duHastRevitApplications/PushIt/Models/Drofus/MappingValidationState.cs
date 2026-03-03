// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models.Drofus
{
    /// <summary>
    /// Runtime-only validation flags for a single <see cref="DrofusPropertyMap"/> entry.
    /// <para>
    /// Populated during the startup validation pass and refreshed after each
    /// successful Connect. Carried by the ViewModel layer and never serialised
    /// to disk — it must not appear in the PushIt settings JSON file.
    /// </para>
    /// <para>
    /// A mapping whose flags indicate a problem is shown with a warning indicator
    /// in the mapping ListView. Invalid mappings are never removed automatically;
    /// the user must choose to remove or fix them.
    /// </para>
    /// </summary>
    public class MappingValidationState
    {
        /// <summary>
        /// <c>true</c> when the Revit shared parameter referenced by
        /// <see cref="DrofusPropertyMap.RevitParameterGuid"/> (or
        /// <see cref="DrofusPropertyMap.RevitParameterName"/> when the GUID is
        /// empty) could not be found in the active Revit document during the
        /// most recent validation pass.
        /// <para>
        /// Remains <c>false</c> when no validation pass has been run yet, or
        /// when the mapping has an empty GUID and name-based lookup has not been
        /// attempted.
        /// </para>
        /// </summary>
        public bool RevitParameterMissing { get; set; }

        /// <summary>
        /// <c>true</c> when <see cref="DrofusPropertyMap.DrofusFieldName"/> was
        /// not present in the field list returned by the drofus API during the
        /// most recent validation pass.
        /// <para>
        /// Remains <c>false</c> when no successful drofus connection has been
        /// made yet — a connection failure means field validity is unknown, not
        /// that the field is absent.
        /// </para>
        /// </summary>
        public bool DrofusFieldMissing { get; set; }

        /// <summary>
        /// Convenience property. Returns <c>true</c> when either flag is set,
        /// indicating that this mapping has at least one unresolved issue.
        /// </summary>
        public bool HasWarning => RevitParameterMissing || DrofusFieldMissing;
    }
}
