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
    ///     <b>Connection test / available fields</b> — calls
    ///     <see cref="DrofusDataSource.GetAvailableFields"/> which queries the
    ///     first room from the API. On success, stores the field list on the
    ///     <see cref="DrofusPropertyMapper"/> via
    ///     <see cref="DrofusPropertyMapper.UpdateAvailableFields"/>.
    ///     Returns <c>Error</c> on connection failure.
    ///   </item>
    ///   <item>
    ///     <b>Mapping validation</b> — skipped when no mappings are configured.
    ///     Otherwise cross-references each mapping's drofus field name against
    ///     <see cref="DrofusPropertyMapper.AvailableFields"/> and each Revit
    ///     parameter GUID against
    ///     <see cref="RevitDataModel.GetAllAvailableParameters"/> (populated
    ///     synchronously by <c>Main.LoadSharedParametersFromDocument</c> before
    ///     this action runs). Failed mappings are flagged and excluded from the
    ///     room load.
    ///   </item>
    ///   <item>
    ///     <b>Room data load</b> — calls <see cref="RevitDataModel.LoadRoomsData"/>
    ///     with the validated mapping set. The Revit-side room matching
    ///     (<c>UpdateRoomDataModelWithNewRooms</c> + <c>RefreshRoomDataWithRevitData</c>)
    ///     is handled separately by <c>RefreshUIFromRevitModelAsyncCommand</c>
    ///     which fires from the <c>RoomsMainViewModel</c> constructor after the
    ///     window opens — by that point rooms are already in the model.
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
        /// ViewModel. Available fields and validation results are written back to
        /// this instance. Must not be <c>null</c>.
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
        ///     invalid; valid mappings loaded rooms.</item>
        ///   <item><c>Error</c> — credentials invalid or connection failed;
        ///     grid will be empty.</item>
        /// </list>
        /// </returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute()
        {
            // ── Step 1: credential check ──────────────────────────────────────
            var dataSource = new DrofusDataSource();
            if (!dataSource.Validate(_revitDataModel.Settings.DataSource, out string credError))
            {
                string msg = $"drofus startup: {credError}";
                AddMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("drofus startup: aborted — credentials incomplete.");
            }

            // ── Step 2: connection test / available fields ────────────────────
            List<string> availableFields;
            try
            {
                availableFields = dataSource.GetAvailableFields(_revitDataModel.Settings.DataSource);
                _mapper.UpdateAvailableFields(availableFields);

                // Cache for DrofusDataSourceControlViewModel construction.
                if (_revitDataModel.Settings.DataSource.Drofus != null)
                    _revitDataModel.Settings.DataSource.Drofus.StartupAvailableFields = availableFields;

                string connMsg = availableFields.Count > 0
                    ? $"drofus startup: connected — {availableFields.Count} room properties available."
                    : "drofus startup: connected but no room properties were returned. " +
                      "Check that the project contains rooms.";
                AddMessage(connMsg, Utils.WPF.Stores.MessageTypes.Information);
                _revitDataModel.AddStartupMessage(connMsg, Utils.WPF.Stores.MessageTypes.Information);
            }
            catch (Exception ex)
            {
                string msg = $"drofus startup: connection failed — {ex.Message}";
                AddMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(msg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("drofus startup: aborted — connection failed.");
            }

            // ── Step 3: mapping validation ────────────────────────────────────
            var persistedMappings = _revitDataModel.Settings.DataSource.Drofus?.PropertyMappings
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

            foreach (DrofusPropertyMap mapping in persistedMappings)
            {
                bool drofusOk = availableFields.Contains(
                    mapping.DrofusFieldName, StringComparer.OrdinalIgnoreCase);

                bool revitOk = availableRevitParams.Any(p =>
                    string.Equals(p.ParameterGuid, mapping.RevitParameterGuid,
                        StringComparison.OrdinalIgnoreCase));

                revitValidationResults[mapping.RevitParameterGuid] = revitOk;

                if (!drofusOk || !revitOk)
                {
                    var reasons = new List<string>();
                    if (!drofusOk)
                        reasons.Add($"drofus field '{mapping.DrofusFieldName}' not found in API response");
                    if (!revitOk)
                        reasons.Add($"Revit parameter '{mapping.RevitParameterName}' " +
                                    $"(GUID: {mapping.RevitParameterGuid}) not bound in document");

                    string reason = string.Join("; ", reasons);
                    invalidMappings.Add((mapping, reason));

                    string warnMsg = $"drofus startup: mapping excluded — {reason}.";
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

                int skipped = _revitDataModel.Settings.DataSource.Drofus?.LastSkippedRoomCount ?? 0;
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
                    : $"drofus startup: rooms loaded with {invalidMappings.Count} invalid mapping(s) excluded.";
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
