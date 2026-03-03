// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models.Drofus
{
    /// <summary>
    /// Defines the direction of data flow for a single drofus ↔ Revit property mapping.
    /// </summary>
    public enum MappingFlowDirection
    {
        /// <summary>
        /// drofus is the source; the mapped Revit shared parameter is the write target.
        /// This is the primary direction used by PushIt.
        /// </summary>
        DrofusToRevit,

        /// <summary>
        /// Revit is the source; the mapped drofus field is the write target.
        /// <para>
        /// NOTE: This direction is stubbed for future use. The drofus REST API
        /// write endpoints are not yet implemented in PushIt. Mappings may be
        /// configured and persisted with this direction, but no data will be
        /// written to drofus until the write path is implemented.
        /// </para>
        /// </summary>
        RevitToDrofus,
    }
}
