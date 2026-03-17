// BSD License - Copyright 2026, Jan Christel

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
    /// Startup action for the drofus data source. Runs synchronously on the
    /// Revit API thread in <c>Main.ExecuteInternal</c> before the main window
    /// opens, mirroring the structure of <see cref="ValidateCsvOnStartup"/>.
    /// <para>
    /// Steps (in order):
    /// <list type="number">
    ///   <item>
    ///     <b>Credential check</b> — verifies that BaseUrl, DatabaseName,
    ///     ProjectNumber and ApiToken are all present. Returns <c>Error</c>
    ///     immediately if any are missing.
    ///   </item>
    ///   <item>
    ///     <b>Connection test / field catalogue / configurations</b> — calls
    ///     <see cref="DrofusDataSource.GetFieldCatalogue"/> (OPTIONS endpoint) and
    ///     <see cref="DrofusDataSource.GetAttributeConfigurations"/>. On success,
    ///     populates the <see cref="DrofusPropertyMapper"/> and caches both results
    ///     on the settings object for the ViewModel to consume without a second
    ///     API call. Returns <c>Error</c> if the catalogue fetch fails (Gap 1).
    ///     Returns <c>Warning</c> and skips Steps 3–4 if the configurations fetch
    ///     fails or returns no room configurations (Gap 2 / Scenario 1).
    ///     Checks for a deleted configuration (Scenario 3) and clears mappings if
    ///     detected — only when the connection succeeded (Gap 9).
    ///   </item>
    ///   <item>
    ///     <b>Mapping validation</b> — skipped when no mappings are configured.
    ///     Cross-references each mapping's drofus field name against the field
    ///     catalogue and each Revit parameter GUID against
    ///     <see cref="RevitDataModel.GetAllAvailableParameters"/>. Failed mappings
    ///     are flagged (not removed) and excluded from the room load.
    ///   </item>
    ///   <item>
    ///     <b>Room data load</b> — calls <see cref="RevitDataModel.LoadRoomsData"/>
    ///     with the validated mapping set. The Revit-side room matching is handled
    ///     separately by <c>RefreshUIFromRevitModelAsyncCommand</c> after the
    ///     window opens.
    ///   </item>
    /// </list>
    /// </para>
    /// </summary>
    public class ValidateDrofusOnStartup : RevitActionBase
    {
        // ── Dependencies ──────────────────────────────────────────────────────

        private readonly RevitDataModel _revitDataModel;
        private readonly DrofusPropertyMapper _mapper;

        // ── Constructor ───────────────────────────────────────────────────────

        /// <summary>
        /// Constructs the startup action.
        /// </summary>
        /// <param name="revitDataModel">
        /// The active <see cref="RevitDataModel"/>. Room data is loaded into this
        /// instance; <see cref="RevitDataModel.GetAllAvailableParameters"/> is read
        /// for mapping validation. Must not be <c>null</c>.
        /// </param>
        /// <param name="mapper">
        /// The <see cref="DrofusPropertyMapper"/> owned by the drofus control
        /// ViewModel. Field catalogue, configurations, and validation results are
        /// written back to this instance. Must not be <c>null</c>.
        /// </param>
        public ValidateDrofusOnStartup(
            RevitDataModel revitDataModel,
            DrofusPropertyMapper mapper)
        {
            _revitDataModel = revitDataModel
                ?? throw new ArgumentNullException(nameof(revitDataModel));
            _mapper = mapper
                ?? throw new ArgumentNullException(nameof(mapper));
        }

        // ── Execute ───────────────────────────────────────────────────────────

        /// <summary>
        /// Runs the four-step drofus startup sequence synchronously.
        /// </summary>
        /// <returns>
        /// A tuple containing a human-readable summary message and a
        /// <see cref="Utils.WPF.Stores.MessageTypes"/> value:
        /// <list type="bullet">
        ///   <item><c>Information</c> — connection succeeded and rooms loaded
        ///     (or no mappings yet configured).</item>
        ///   <item><c>Warning</c> — connection succeeded but some mappings are
        ///     invalid, or no room attribute configurations are available.</item>
        ///   <item><c>Error</c> — credentials invalid, connection failed, or the
        ///     field catalogue could not be retrieved; grid will be empty.</item>
        /// </list>
        /// </returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute()
        {
            var drofusSettings = _revitDataModel.Settings.DataSource.Drofus;

            // ── Step 1: credential check ──────────────────────────────────────
            var dataSource = new DrofusDataSource();
            if (!dataSource.Validate(_revitDataModel.Settings.DataSource, out string credError))
            {
                string msg = $"drofus startup: {credError}";
                AddMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("drofus startup: aborted — credentials incomplete.");
            }

            // ── Step 2: field catalogue, configurations, scenario checks ──────

            // 2a — Field catalogue (OPTIONS endpoint). Fatal on failure (Gap 1).
            List<DrofusRoomField> fieldCatalogue;
            try
            {
                fieldCatalogue = dataSource.GetFieldCatalogue(
                    _revitDataModel.Settings.DataSource);

                _mapper.UpdateAvailableFields(fieldCatalogue);

                if (drofusSettings != null)
                    drofusSettings.StartupFieldCatalogue = fieldCatalogue;

                string catalogueMsg = fieldCatalogue.Count > 0
                    ? $"drofus startup: connected — {fieldCatalogue.Count} room fields available in catalogue."
                    : "drofus startup: connected but field catalogue is empty. " +
                      "Check that the project contains room fields.";
                AddMessage(catalogueMsg, Utils.WPF.Stores.MessageTypes.Information);
                _revitDataModel.AddStartupMessage(catalogueMsg, Utils.WPF.Stores.MessageTypes.Information);
            }
            catch (Exception ex)
            {
                // Gap 1: catalogue failure is fatal — disable everything.
                string msg = "Could not retrieve the room field catalogue from drofus. " +
                             $"Check your connection and reconnect. Detail: {ex.Message}";
                AddMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("drofus startup: aborted — field catalogue unavailable.");
            }

            // 2b — Attribute configurations. Fatal to mapping interface on failure (Gap 2).
            List<DrofusAttributeConfiguration> configurations;
            try
            {
                configurations = dataSource.GetAttributeConfigurations(
                    _revitDataModel.Settings.DataSource);

                _mapper.UpdateAvailableConfigurations(configurations);

                if (drofusSettings != null)
                    drofusSettings.StartupAttributeConfigurations = configurations;
            }
            catch (Exception ex)
            {
                // Gap 2: treat identically to Scenario 1 — no room configurations.
                string msg = "No room attribute configurations are set up in drofus. " +
                             "At least one is required to configure mappings. " +
                             "Please create a room attribute configuration in drofus and reconnect. " +
                             $"Detail: {ex.Message}";
                AddMessage(msg, Utils.WPF.Stores.MessageTypes.Warning);
                _revitDataModel.AddStartupMessage(msg, Utils.WPF.Stores.MessageTypes.Warning);
                return GetReturnValue("drofus startup: completed — mapping interface unavailable.");
            }

            // 2c — Scenario 1: no room configurations returned.
            if (configurations.Count == 0)
            {
                string noConfigMsg = "No room attribute configurations are set up in drofus. " +
                    "At least one is required to configure mappings. " +
                    "Please create a room attribute configuration in drofus and reconnect.";
                AddMessage(noConfigMsg, Utils.WPF.Stores.MessageTypes.Warning);
                _revitDataModel.AddStartupMessage(noConfigMsg, Utils.WPF.Stores.MessageTypes.Warning);
                return GetReturnValue("drofus startup: completed — mapping interface unavailable.");
            }

            // 2d — Restore selected configuration id from persisted settings.
            if (drofusSettings != null)
            {
                _mapper.SelectConfiguration(
                    drofusSettings.SelectedAttributeConfigurationId,
                    drofusSettings);
            }

            // 2e — Scenario 3: previously selected configuration was deleted in drofus.
            // Only checked when the connection succeeded and we have a positive list.
            // Must NOT be called on connection failure — absence of data is not evidence
            // of deletion (Gap 9).
            if (drofusSettings?.SelectedAttributeConfigurationId != null)
            {
                bool configStillExists = configurations.Any(
                    c => c.Id == drofusSettings.SelectedAttributeConfigurationId.Value);

                if (!configStillExists)
                {
                    string deletedMsg = _mapper.HandleDeletedConfiguration();
                    _mapper.SaveMappingsToSettings(drofusSettings);
                    _mapper.SelectConfiguration(null, drofusSettings);

                    AddMessage(deletedMsg, Utils.WPF.Stores.MessageTypes.Warning);
                    _revitDataModel.AddStartupMessage(deletedMsg, Utils.WPF.Stores.MessageTypes.Warning);

                    // Mappings have been cleared — nothing left to validate or load.
                    return GetReturnValue("drofus startup: completed — configuration deleted, mappings cleared.");
                }
            }

            // ── Step 3: mapping validation ────────────────────────────────────
            var persistedMappings = drofusSettings?.PropertyMappings
                ?? new List<DrofusPropertyMap>();

            if (persistedMappings.Count == 0)
            {
                string noMapMsg = "drofus startup: no mappings configured. " +
                    "Use Settings → Add Mapping to set up drofus ↔ Revit property mappings.";
                AddMessage(noMapMsg, Utils.WPF.Stores.MessageTypes.Information);
                _revitDataModel.AddStartupMessage(noMapMsg, Utils.WPF.Stores.MessageTypes.Information);
                return GetReturnValue("drofus startup: connected, awaiting mapping configuration.");
            }

            var revitValidationResults = new Dictionary<string, bool>(StringComparer.OrdinalIgnoreCase);
            var validMappings = new List<DrofusPropertyMap>();
            var invalidMappings = new List<(DrofusPropertyMap Map, string Reason)>();

            IReadOnlyList<AvailableParameter> availableRevitParams =
                _revitDataModel.GetAllAvailableParameters();

            // Build a set of field ids from the catalogue for O(1) lookup.
            // Using the full catalogue (not scoped to the selected configuration)
            // so that the flag-only behaviour at startup is lenient — stale detection
            // against the configuration scope happens at Connect time via
            // CleanupStaleMappings (Scenario 4).
            var catalogueIds = new HashSet<string>(
                fieldCatalogue.Select(f => f.Id),
                StringComparer.OrdinalIgnoreCase);

            foreach (DrofusPropertyMap mapping in persistedMappings)
            {
                // Catalogue id lookup replaces the old availableFields.Contains string
                // comparison — the source of truth is now the OPTIONS catalogue.
                bool drofusOk = catalogueIds.Contains(mapping.DrofusFieldName);

                bool revitOk = availableRevitParams.Any(p =>
                    string.Equals(p.ParameterGuid, mapping.RevitParameterGuid,
                        StringComparison.OrdinalIgnoreCase));

                revitValidationResults[mapping.RevitParameterGuid] = revitOk;

                if (!drofusOk || !revitOk)
                {
                    var reasons = new List<string>();
                    if (!drofusOk)
                    {
                        // Report human-readable label when available.
                        string label = _mapper.GetFieldLabel(mapping.DrofusFieldName);
                        reasons.Add($"drofus field '{label}' not found in field catalogue");
                    }
                    if (!revitOk)
                        reasons.Add($"Revit parameter '{mapping.RevitParameterName}' " +
                                    $"(GUID: {mapping.RevitParameterGuid}) not bound in document");

                    string reason = string.Join("; ", reasons);
                    invalidMappings.Add((mapping, reason));

                    // Flag only — do not remove at startup (consistent with existing
                    // startup philosophy; removal happens at Connect via CleanupStaleMappings).
                    string warnMsg = $"drofus startup: mapping flagged — {reason}.";
                    AddMessage(warnMsg, Utils.WPF.Stores.MessageTypes.Warning);
                    _revitDataModel.AddStartupMessage(warnMsg, Utils.WPF.Stores.MessageTypes.Warning);
                }
                else
                {
                    validMappings.Add(mapping);
                }
            }

            _mapper.SetRevitValidationResults(revitValidationResults);

            // ── Step 4: room data load ────────────────────────────────────────
            if (validMappings.Count == 0)
            {
                string noValidMsg = "drofus startup: no valid mappings — rooms not loaded. " +
                    "Fix mapping issues in Settings.";
                AddMessage(noValidMsg, Utils.WPF.Stores.MessageTypes.Warning);
                _revitDataModel.AddStartupMessage(noValidMsg, Utils.WPF.Stores.MessageTypes.Warning);
                return GetReturnValue("drofus startup: completed with mapping errors.");
            }

            int idCount = validMappings.Count(m => m.IsUniqueId);
            if (idCount != 1)
            {
                string idMsg = idCount == 0
                    ? "drofus startup: no valid mapping is nominated as the unique identifier " +
                      "(Is Id) — rooms not loaded."
                    : $"drofus startup: {idCount} valid mappings carry Is Id — exactly one is " +
                      $"required — rooms not loaded.";
                AddMessage(idMsg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(idMsg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("drofus startup: aborted — unique-id mapping issue.");
            }

            try
            {
                _revitDataModel.ClearAllRooms();
                _revitDataModel.LoadRoomsData();

                int skipped = drofusSettings?.LastSkippedRoomCount ?? 0;
                if (skipped > 0)
                {
                    string skipMsg = skipped == 1
                        ? "drofus startup: 1 room skipped — unique-id field was empty or null."
                        : $"drofus startup: {skipped} rooms skipped — unique-id field was empty or null.";
                    AddMessage(skipMsg, Utils.WPF.Stores.MessageTypes.Warning);
                    _revitDataModel.AddStartupMessage(skipMsg, Utils.WPF.Stores.MessageTypes.Warning);
                }

                string successMsg = invalidMappings.Count == 0
                    ? "drofus startup: all mappings valid — rooms loaded."
                    : $"drofus startup: rooms loaded with {invalidMappings.Count} invalid mapping(s) flagged.";
                AddMessage(successMsg, Utils.WPF.Stores.MessageTypes.Information);
                _revitDataModel.AddStartupMessage(successMsg, Utils.WPF.Stores.MessageTypes.Information);
                return GetReturnValue(successMsg);
            }
            catch (Exception ex)
            {
                string errMsg = $"drofus startup: room load failed — {ex.Message}";
                AddMessage(errMsg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(errMsg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("drofus startup: completed with errors.");
            }
        }
    }
}
