// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.Models.Drofus;
using duHastNet.PushIt.Utilities.Drofus;
using System;

namespace duHastNet.PushIt.ViewModels.DataSource.Drofus
{
    /// <summary>
    /// ViewModel wrapper for a single <see cref="DrofusPropertyMap"/> entry.
    /// Provides display properties for the three columns of the mapping
    /// <c>ListView</c> and exposes the runtime validation flags that drive the
    /// warning indicator shown on invalid rows.
    /// <para>
    /// Mirrors <c>MetaDataMapViewModel</c> in <c>duHastNet.DocManager</c>.
    /// This class is intentionally simple — it holds no commands and raises no
    /// events. All mutations (Add, Remove, Edit) are handled by the parent
    /// <c>DrofusDataSourceControlViewModel</c>.
    /// </para>
    /// </summary>
    public class DrofusPropertyMapViewModel
    {
        // ── Private state ─────────────────────────────────────────────────────

        private MappingValidationState _validationState;

        /// <summary>
        /// Resolves the human-readable display label for a drofus field id.
        /// Backed by <see cref="DrofusPropertyMapper.GetFieldLabel"/> — returns
        /// the catalogue <c>Name</c> when available, or the raw field id as fallback.
        /// </summary>
        private readonly Func<string, string> _fieldLabelResolver;

        // ── Public model reference ────────────────────────────────────────────

        /// <summary>
        /// The underlying serialisable mapping model.
        /// Exposed so the parent ViewModel can pass this instance directly to
        /// <see cref="DrofusPropertyMapper.RemoveMapping"/> or to the edit dialog
        /// constructor without an additional lookup.
        /// </summary>
        public DrofusPropertyMap Model { get; }

        // ── ListView column display properties ────────────────────────────────

        /// <summary>
        /// The human-readable drofus field label shown in the first ListView column.
        /// Resolved via <see cref="_fieldLabelResolver"/> from the catalogue —
        /// e.g. <c>"Room Function Number"</c> instead of <c>"room_func_no"</c>.
        /// Falls back to the raw <see cref="DrofusPropertyMap.DrofusFieldName"/> JSON
        /// key when the catalogue has not been loaded or the id is not found.
        /// </summary>
        public string DrofusFieldLabel => _fieldLabelResolver(Model.DrofusFieldName);

        /// <summary>
        /// The raw drofus JSON field id stored in the mapping model.
        /// Not displayed in the primary ListView column (use <see cref="DrofusFieldLabel"/>
        /// for display) but retained for tooltip or debug use.
        /// </summary>
        public string DrofusFieldName => Model.DrofusFieldName;

        /// <summary>
        /// The Revit shared parameter name shown in the second ListView column.
        /// e.g. <c>"RDS_RoomFunctionNumber"</c>.
        /// </summary>
        public string RevitParameterName => Model.RevitParameterName;

        /// <summary>
        /// Human-readable representation of <see cref="DrofusPropertyMap.FlowDirection"/>
        /// shown in the third ListView column.
        /// Returns <c>"drofus → Revit"</c> or <c>"Revit → drofus (future)"</c>.
        /// </summary>
        public string FlowDirectionDisplay => Model.FlowDirection switch
        {
            MappingFlowDirection.DrofusToRevit => "drofus → Revit",
            MappingFlowDirection.RevitToDrofus => "Revit → drofus (future)",
            _ => Model.FlowDirection.ToString()
        };

        /// <summary>
        /// <c>true</c> when this mapping is the nominated unique identifier.
        /// Passed through directly from the underlying model.
        /// </summary>
        public bool IsUniqueId => Model.IsUniqueId;

        /// <summary>
        /// Returns <c>Bold</c> for the unique-id mapping so it stands out in the
        /// ListView, and <c>Normal</c> for all other rows.
        /// </summary>
        public System.Windows.FontWeight RowFontWeight =>
            Model.IsUniqueId
                ? System.Windows.FontWeights.Bold
                : System.Windows.FontWeights.Normal;

        // ── Validation state properties ───────────────────────────────────────

        /// <summary>
        /// <c>true</c> when the Revit shared parameter referenced by this mapping
        /// was confirmed absent from the active document during the most recent
        /// validation pass.
        /// <para>
        /// Drives the warning indicator in the ListView row template.
        /// Remains <c>false</c> when no validation pass has run yet.
        /// </para>
        /// </summary>
        public bool RevitParameterMissing => _validationState.RevitParameterMissing;

        /// <summary>
        /// <c>true</c> when the drofus field referenced by this mapping was not
        /// found in the field catalogue (or the active configuration's fields)
        /// during the most recent validation pass.
        /// <para>
        /// Drives the warning indicator in the ListView row template.
        /// Remains <c>false</c> when no successful drofus connection has been made
        /// yet — unknown is distinct from confirmed missing.
        /// </para>
        /// </summary>
        public bool DrofusFieldMissing => _validationState.DrofusFieldMissing;

        /// <summary>
        /// <c>true</c> when either <see cref="RevitParameterMissing"/> or
        /// <see cref="DrofusFieldMissing"/> is set.
        /// Convenience property for binding a single warning visibility trigger
        /// in the row template.
        /// </summary>
        public bool HasWarning => _validationState.HasWarning;

        /// <summary>
        /// When <c>true</c>, the value written to Revit on the first split-room push
        /// is treated as authoritative on all subsequent pushes. The SoA/drofus value
        /// is ignored for this property from that point forward.
        /// <para>
        /// Bound to the checkbox in the per-parameter row of the drofus UI panel.
        /// Persisted via <see cref="DrofusDataSourceSettings.RevitPrecedencePropertyNames"/>.
        /// </para>
        /// </summary>
        public bool RevitTakesPrecedenceAfterInitialPush { get; set; }

        // ── Constructor ───────────────────────────────────────────────────────

        /// <summary>
        /// Constructs the row ViewModel, resolves the initial validation state,
        /// and captures the field-label resolver from the mapper.
        /// </summary>
        /// <param name="model">
        /// The underlying mapping model. Must not be <c>null</c>.
        /// </param>
        /// <param name="mapper">
        /// The active <see cref="DrofusPropertyMapper"/> instance. Used to derive
        /// the initial <see cref="MappingValidationState"/> for this row and to
        /// supply the <see cref="DrofusFieldLabel"/> resolver.
        /// Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when either argument is <c>null</c>.
        /// </exception>
        public DrofusPropertyMapViewModel(DrofusPropertyMap model, DrofusPropertyMapper mapper)
        {
            Model = model ?? throw new ArgumentNullException(nameof(model));

            if (mapper is null)
                throw new ArgumentNullException(nameof(mapper));

            // Capture the label resolver as a delegate so this ViewModel has no
            // direct dependency on the mapper beyond construction time.
            _fieldLabelResolver = mapper.GetFieldLabel;

            _validationState = mapper.GetValidationState(model);
        }

        // ── Validation refresh ────────────────────────────────────────────────

        /// <summary>
        /// Refreshes the validation state from the mapper.
        /// <para>
        /// Called by the parent <c>DrofusDataSourceControlViewModel</c> after
        /// each event that may change validation state: a successful Connect, a
        /// completed startup validation pass, or a manual Remove followed by
        /// re-add. The parent rebuilds or refreshes all row ViewModels at those
        /// points so that the ListView reflects the latest known state.
        /// </para>
        /// </summary>
        /// <param name="mapper">
        /// The mapper to read updated state from. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="mapper"/> is <c>null</c>.
        /// </exception>
        public void RefreshValidationState(DrofusPropertyMapper mapper)
        {
            if (mapper is null)
                throw new ArgumentNullException(nameof(mapper));

            _validationState = mapper.GetValidationState(Model);
        }

        // ── Debugging ─────────────────────────────────────────────────────────

        /// <summary>
        /// Returns a concise string representation for use in debugger watch
        /// windows and log output. Uses the human-readable label where available.
        /// </summary>
        public override string ToString()
        {
            string warning = HasWarning ? " [WARNING]" : string.Empty;
            return $"{DrofusFieldLabel} → {RevitParameterName} ({FlowDirectionDisplay}){warning}";
        }
    }
}
