// BSD License - Copyright 2025, Jan Christel

using Autodesk.Revit.DB;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Models.Drofus;
using duHastNet.PushIt.Utilities;
using duHastNet.PushIt.Utilities.Drofus;
using System;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.PushIt.RevitActions.Drofus
{
    /// <summary>
    /// Startup validation action that checks the persisted drofus ↔ Revit
    /// property mappings against both the live Revit document and the live
    /// drofus API.
    /// <para>
    /// Must be executed inside <c>RevitTask.RunAsync</c> — the Revit-side check
    /// requires the Revit API, and the drofus-side check makes a synchronous
    /// HTTP call that must not block the UI thread.
    /// </para>
    /// <para>
    /// This action never removes mappings. Its sole purpose is to populate
    /// validation state on the <see cref="DrofusPropertyMapper"/> so that the
    /// mapping UI can indicate which entries need attention. The user decides
    /// whether to remove or fix them.
    /// </para>
    /// </summary>
    public class ValidateDrofusMappingsOnStartup : RevitActionBase,
        duHastNet.RevitUtils.RevitActions.IRevitAction
    {
        // ── Dependencies ──────────────────────────────────────────────────────

        private readonly DrofusPropertyMapper _mapper;
        private readonly DataSourceSettings _dataSourceSettings;

        // ── Counters used for the return message ──────────────────────────────

        private int _revitMissingCount;
        private int _drofusMissingCount;
        private bool _drofusConnectionFailed;

        // ── Constructor ───────────────────────────────────────────────────────

        /// <summary>
        /// Constructs the validation action.
        /// </summary>
        /// <param name="mapper">
        /// The <see cref="DrofusPropertyMapper"/> instance owned by
        /// <c>DrofusDataSourceControlViewModel</c>. Validation results are
        /// written back to this instance. Must not be <c>null</c>.
        /// </param>
        /// <param name="dataSourceSettings">
        /// The active <see cref="DataSourceSettings"/>. Used to supply
        /// credentials to the drofus HTTP call and to read the mappings list for
        /// the Revit-side GUID check. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when either argument is <c>null</c>.
        /// </exception>
        public ValidateDrofusMappingsOnStartup(
            DrofusPropertyMapper mapper,
            DataSourceSettings dataSourceSettings)
        {
            _mapper = mapper
                ?? throw new ArgumentNullException(nameof(mapper));
            _dataSourceSettings = dataSourceSettings
                ?? throw new ArgumentNullException(nameof(dataSourceSettings));
        }

        // ── IRevitAction ──────────────────────────────────────────────────────

        /// <summary>
        /// Runs both validation checks and writes results back to the mapper.
        /// The two checks are independent — a failure in one does not prevent
        /// the other from running.
        /// </summary>
        /// <param name="doc">The active Revit document.</param>
        /// <returns>
        /// A tuple containing a human-readable summary message and a
        /// <see cref="Utils.WPF.Stores.MessageTypes"/> value:
        /// <list type="bullet">
        ///   <item><c>Information</c> — both checks passed with no issues.</item>
        ///   <item><c>Warning</c> — at least one mapping has a validation problem,
        ///     or the drofus connection failed at startup (non-fatal).</item>
        /// </list>
        /// Individual issue details are also recorded via <c>AddMessage</c> for
        /// the session log.
        /// </returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(
            Document doc)
        {
            _revitMissingCount = 0;
            _drofusMissingCount = 0;
            _drofusConnectionFailed = false;

            RunRevitParameterCheck(doc);
            RunDrofusFieldCheck();

            return BuildReturnValue();
        }

        // ── Check 1: Revit shared parameter existence ─────────────────────────

        /// <summary>
        /// For every mapping that carries a non-empty
        /// <see cref="DrofusPropertyMap.RevitParameterGuid"/>, queries
        /// <c>SharedParaUtils.ParameterBindingsByGUID</c> to confirm the
        /// parameter still exists and is bound in the active document.
        /// Results are written to the mapper via
        /// <see cref="DrofusPropertyMapper.SetRevitValidationResults"/>.
        /// </summary>
        private void RunRevitParameterCheck(Document doc)
        {
            try
            {
                var results = new Dictionary<string, bool>(StringComparer.OrdinalIgnoreCase);

                var mappingsWithGuid = _mapper.Mappings
                    .Where(m => !string.IsNullOrWhiteSpace(m.RevitParameterGuid))
                    .ToList();

                foreach (DrofusPropertyMap mapping in mappingsWithGuid)
                {
                    List<string>? bindings = duHastNet.RevitUtils.Parameters.SharedParaUtils
                        .ParameterBindingsByGUID(doc, mapping.RevitParameterGuid);

                    bool exists = bindings != null;
                    results[mapping.RevitParameterGuid] = exists;

                    if (!exists)
                    {
                        _revitMissingCount++;
                        AddMessage(
                            $"drofus mapping validation: Revit shared parameter " +
                            $"'{mapping.RevitParameterName}' (GUID: {mapping.RevitParameterGuid}) " +
                            $"mapped to drofus field '{mapping.DrofusFieldName}' " +
                            $"does not exist in the active document.",
                            Utils.WPF.Stores.MessageTypes.Warning);
                    }
                }

                _mapper.SetRevitValidationResults(results);
            }
            catch (Exception ex)
            {
                // Log but do not propagate — the drofus check must still run.
                AddMessage(
                    $"drofus mapping validation: Revit parameter check failed with an " +
                    $"unexpected error: {ex.Message}",
                    Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        // ── Check 2: drofus field existence ───────────────────────────────────

        /// <summary>
        /// Calls <see cref="DrofusDataSource.GetAvailableFields"/> to retrieve
        /// the live field list from the drofus API, then passes it to
        /// <see cref="DrofusPropertyMapper.UpdateAvailableFields"/>.
        /// <para>
        /// Unlike the Connect flow, <c>CleanupStaleMappings</c> is NOT called —
        /// stale fields are flagged by the mapper's
        /// <see cref="DrofusPropertyMapper.HasValidationWarnings"/> property, not
        /// removed.
        /// </para>
        /// <para>
        /// If the HTTP call fails for any reason (network, credentials, server
        /// error), the failure is logged as a warning and
        /// <see cref="AvailableFields"/> is left empty. An empty
        /// <c>AvailableFields</c> means "unknown", not "all fields missing".
        /// </para>
        /// </summary>
        private void RunDrofusFieldCheck()
        {
            try
            {
                var dataSource = new DrofusDataSource();
                List<string> fields = dataSource.GetAvailableFields(_dataSourceSettings);
                _mapper.UpdateAvailableFields(fields);

                // Count mappings whose drofus field is absent from the live response.
                // GetValidationState reads directly from AvailableFields so this is
                // always consistent with what the UI will show.
                foreach (DrofusPropertyMap mapping in _mapper.Mappings)
                {
                    MappingValidationState state = _mapper.GetValidationState(mapping);
                    if (state.DrofusFieldMissing)
                    {
                        _drofusMissingCount++;
                        AddMessage(
                            $"drofus mapping validation: drofus field '{mapping.DrofusFieldName}' " +
                            $"mapped to Revit parameter '{mapping.RevitParameterName}' " +
                            $"was not found in the current API response.",
                            Utils.WPF.Stores.MessageTypes.Warning);
                    }
                }
            }
            catch (Exception ex)
            {
                // A connection failure at startup is non-fatal. Log as a warning
                // so the banner informs the user, but do not block the window.
                _drofusConnectionFailed = true;
                AddMessage(
                    $"drofus mapping validation: could not connect to drofus at startup " +
                    $"to verify field mappings. drofus field validity is unknown until " +
                    $"Connect is pressed. Detail: {ex.Message}",
                    Utils.WPF.Stores.MessageTypes.Warning);
            }
        }

        // ── Return value construction ─────────────────────────────────────────

        /// <summary>
        /// Builds the top-level return tuple from the counters accumulated during
        /// the two checks. Returns <c>Warning</c> if any problem was found or if
        /// the drofus connection failed; <c>Information</c> if everything passed.
        /// </summary>
        private (string message, Utils.WPF.Stores.MessageTypes messageType) BuildReturnValue()
        {
            bool hasIssues = _revitMissingCount > 0
                          || _drofusMissingCount > 0
                          || _drofusConnectionFailed;

            if (!hasIssues)
            {
                return (
                    "drofus mapping validation: all mappings are valid.",
                    Utils.WPF.Stores.MessageTypes.Information);
            }

            var parts = new List<string>();

            if (_revitMissingCount > 0)
            {
                parts.Add(_revitMissingCount == 1
                    ? "1 mapping references a Revit shared parameter that no longer exists in the document."
                    : $"{_revitMissingCount} mappings reference Revit shared parameters that no longer exist in the document.");
            }

            if (_drofusMissingCount > 0)
            {
                parts.Add(_drofusMissingCount == 1
                    ? "1 mapping references a drofus field that was not found in the current API response."
                    : $"{_drofusMissingCount} mappings reference drofus fields that were not found in the current API response.");
            }

            if (_drofusConnectionFailed)
            {
                parts.Add("Could not connect to drofus at startup — drofus field validity is unknown until Connect is pressed.");
            }

            return (
                string.Join(" ", parts),
                Utils.WPF.Stores.MessageTypes.Warning);
        }
    }
}
