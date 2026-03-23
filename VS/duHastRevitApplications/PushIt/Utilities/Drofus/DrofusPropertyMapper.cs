// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.Models.Drofus;
using System;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.PushIt.Utilities.Drofus
{
    /// <summary>
    /// Service layer that owns the runtime state of the drofus ↔ Revit property
    /// mapping list for a single session.
    /// <para>
    /// Mirrors <c>MetaDataMapperAconex</c> in <c>duHastNet.DocManager</c>.
    /// Constructed once from the persisted <see cref="DrofusDataSourceSettings.PropertyMappings"/>
    /// list and kept alive for the duration of the PushIt session.
    /// </para>
    /// <para>
    /// This class has no dependency on the Revit API or on any ViewModel — it
    /// operates purely on the model layer and can be unit-tested in isolation.
    /// </para>
    /// </summary>
    public class DrofusPropertyMapper
    {
        // ── Private state ─────────────────────────────────────────────────────

        private readonly List<DrofusPropertyMap> _mappings;
        private readonly List<DrofusRoomField> _availableFields;
        private readonly List<DrofusAttributeConfiguration> _availableConfigurations;

        /// <summary>
        /// Keyed on <see cref="DrofusPropertyMap.RevitParameterGuid"/>.
        /// <c>true</c> = parameter exists in the document; <c>false</c> = missing.
        /// Only populated after a validation pass; absent key = not yet checked.
        /// </summary>
        private readonly Dictionary<string, bool> _revitValidationResults;

        // ── Public read-only views ────────────────────────────────────────────

        /// <summary>
        /// The current list of mappings. Treat as read-only from outside this
        /// class — mutations must go through <see cref="AddMapping"/> and
        /// <see cref="RemoveMapping"/> so internal state stays consistent.
        /// </summary>
        public IReadOnlyList<DrofusPropertyMap> Mappings => _mappings;

        /// <summary>
        /// The complete room field catalogue fetched from the drofus OPTIONS endpoint.
        /// Empty until <see cref="UpdateAvailableFields"/> has been called at least
        /// once (either from the Connect button or from the startup validation pass).
        /// </summary>
        public IReadOnlyList<DrofusRoomField> AvailableFields => _availableFields;

        /// <summary>
        /// The list of room attribute configurations fetched from drofus.
        /// Empty until <see cref="UpdateAvailableConfigurations"/> has been called.
        /// </summary>
        public IReadOnlyList<DrofusAttributeConfiguration> AvailableConfigurations
            => _availableConfigurations;

        /// <summary>
        /// The id of the currently selected attribute configuration, or <c>null</c>
        /// when no configuration is selected (the full catalogue is used).
        /// Synced to <see cref="DrofusDataSourceSettings.SelectedAttributeConfigurationId"/>
        /// via <see cref="SelectConfiguration"/>.
        /// </summary>
        public int? SelectedConfigurationId { get; private set; }

        // ── Constructor ───────────────────────────────────────────────────────

        /// <summary>
        /// Constructs a mapper pre-populated from the persisted settings.
        /// </summary>
        /// <param name="persistedMappings">
        /// The <see cref="DrofusDataSourceSettings.PropertyMappings"/> list loaded
        /// from the settings file. May be empty but must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="persistedMappings"/> is <c>null</c>.
        /// </exception>
        public DrofusPropertyMapper(List<DrofusPropertyMap> persistedMappings)
        {
            if (persistedMappings is null)
                throw new ArgumentNullException(nameof(persistedMappings));

            // Defensive copy — we own our list; callers own theirs.
            _mappings = new List<DrofusPropertyMap>(persistedMappings);
            _availableFields = new List<DrofusRoomField>();
            _availableConfigurations = new List<DrofusAttributeConfiguration>();
            _revitValidationResults = new Dictionary<string, bool>(StringComparer.OrdinalIgnoreCase);
        }

        // ── Field catalogue management ────────────────────────────────────────

        /// <summary>
        /// Replaces the internal available-fields list with the full room field
        /// catalogue fetched from the drofus OPTIONS endpoint.
        /// <para>
        /// Called after every successful HTTP connection — both from the Connect
        /// button and from the startup validation pass.
        /// </para>
        /// </summary>
        /// <param name="fields">
        /// The complete catalogue of room fields returned by
        /// <c>DrofusDataSource.GetFieldCatalogue</c>. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="fields"/> is <c>null</c>.
        /// </exception>
        public void UpdateAvailableFields(List<DrofusRoomField> fields)
        {
            if (fields is null)
                throw new ArgumentNullException(nameof(fields));

            _availableFields.Clear();
            _availableFields.AddRange(fields);
        }

        // ── Configuration management ──────────────────────────────────────────

        /// <summary>
        /// Replaces the internal available-configurations list with those fetched
        /// from <c>GET /attributeconfigurations</c>, filtered to <c>config_type == "room"</c>.
        /// <para>
        /// Called after every successful HTTP connection and at startup.
        /// </para>
        /// </summary>
        /// <param name="configurations">
        /// The room attribute configurations returned by
        /// <c>DrofusDataSource.GetAttributeConfigurations</c>. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="configurations"/> is <c>null</c>.
        /// </exception>
        public void UpdateAvailableConfigurations(List<DrofusAttributeConfiguration> configurations)
        {
            if (configurations is null)
                throw new ArgumentNullException(nameof(configurations));

            _availableConfigurations.Clear();
            _availableConfigurations.AddRange(configurations);
        }

        /// <summary>
        /// Sets the active attribute configuration and syncs the id back to the
        /// provided settings object so it is persisted on the next save.
        /// </summary>
        /// <param name="configurationId">
        /// The <see cref="DrofusAttributeConfiguration.Id"/> of the configuration
        /// to select, or <c>null</c> to deselect (full catalogue shown).
        /// </param>
        /// <param name="settings">
        /// The settings object to sync the selection to. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="settings"/> is <c>null</c>.
        /// </exception>
        public void SelectConfiguration(int? configurationId, DrofusDataSourceSettings settings)
        {
            if (settings is null)
                throw new ArgumentNullException(nameof(settings));

            // The UI sentinel (NoneId) must never reach the mapper or settings —
            // normalise it to null so all downstream logic treats it as "no selection".
            if (configurationId == DrofusAttributeConfiguration.NoneId)
                configurationId = null;

            SelectedConfigurationId = configurationId;
            settings.SelectedAttributeConfigurationId = configurationId;
        }

        /// <summary>
        /// Returns the fields that should appear in the mapping dialog dropdown,
        /// scoped to the currently selected attribute configuration.
        /// <para>
        /// When a configuration is selected, only catalogue fields whose
        /// <see cref="DrofusRoomField.Id"/> appears as a
        /// <see cref="DrofusAttributeConfigurationElement.DrofusAttributeId"/>
        /// in that configuration's elements are returned.
        /// </para>
        /// <para>
        /// When no configuration is selected (<see cref="SelectedConfigurationId"/>
        /// is <c>null</c>), the full catalogue is returned.
        /// </para>
        /// </summary>
        /// <returns>
        /// A read-only snapshot of the fields available for mapping under the
        /// current configuration. Changes to the returned list do not affect
        /// internal state.
        /// </returns>
        public IReadOnlyList<DrofusRoomField> GetFieldsForSelectedConfiguration()
        {
            if (SelectedConfigurationId is null)
                return _availableFields;

            DrofusAttributeConfiguration? config = _availableConfigurations
                .FirstOrDefault(c => c.Id == SelectedConfigurationId.Value);

            if (config is null)
                return _availableFields;

            var configFieldIds = new HashSet<string>(
                config.Elements.Select(e => e.DrofusAttributeId),
                StringComparer.OrdinalIgnoreCase);

            return _availableFields
                .Where(f => configFieldIds.Contains(f.Id))
                .ToList();
        }

        /// <summary>
        /// Returns the <see cref="DrofusAttributeConfigurationElement"/> from the
        /// specified configuration whose
        /// <see cref="DrofusAttributeConfigurationElement.DrofusAttributeId"/>
        /// matches <paramref name="fieldId"/>, or <c>null</c> if no match is found.
        /// <para>
        /// Used by <c>DrofusPropertyMappingDialogViewModel</c> to pre-populate
        /// <see cref="DrofusPropertyMap.FlowDirection"/> and
        /// <see cref="DrofusPropertyMap.IsUniqueId"/> when the user selects a field
        /// that originates from a configuration element, saving manual entry.
        /// </para>
        /// </summary>
        /// <param name="configurationId">The id of the configuration to search within.</param>
        /// <param name="fieldId">The <see cref="DrofusRoomField.Id"/> to look up.</param>
        /// <returns>
        /// The matching element, or <c>null</c> when the configuration is not found
        /// or the field is not part of it.
        /// </returns>
        public DrofusAttributeConfigurationElement? GetElementForField(int configurationId, string fieldId)
        {
            if (string.IsNullOrWhiteSpace(fieldId))
                return null;

            DrofusAttributeConfiguration? config = _availableConfigurations
                .FirstOrDefault(c => c.Id == configurationId);

            if (config is null)
                return null;

            return config.Elements.FirstOrDefault(e =>
                string.Equals(e.DrofusAttributeId, fieldId, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Maps a raw <see cref="DrofusAttributeConfigurationElement.Direction"/>
        /// string from the drofus API to the corresponding
        /// <see cref="MappingFlowDirection"/> and <c>IsUniqueId</c> flag.
        /// </summary>
        /// <param name="direction">
        /// The raw direction string from the API element:
        /// <c>"Key"</c>, <c>"ToExternalApplication"</c>, or <c>"ToDrofus"</c>.
        /// </param>
        /// <param name="isUniqueId">
        /// Set to <c>true</c> when <paramref name="direction"/> is <c>"Key"</c>;
        /// <c>false</c> otherwise.
        /// </param>
        /// <returns>
        /// The <see cref="MappingFlowDirection"/> for this element.
        /// Unknown direction values default to
        /// <see cref="MappingFlowDirection.DrofusToRevit"/> with
        /// <c>isUniqueId = false</c> — this is intentional future-proofing
        /// against new API direction values (Gap 4 / Gap 8).
        /// </returns>
        public static MappingFlowDirection MapDirection(string direction, out bool isUniqueId)
        {
            switch (direction)
            {
                case "Key":
                    isUniqueId = true;
                    return MappingFlowDirection.DrofusToRevit;

                case "ToExternalApplication":
                    isUniqueId = false;
                    return MappingFlowDirection.DrofusToRevit;

                case "ToDrofus":
                    isUniqueId = false;
                    return MappingFlowDirection.RevitToDrofus;

                default:
                    // Intentional future-proofing: any direction value not recognised
                    // above defaults to DrofusToRevit with IsUniqueId = false.
                    // This is the safe, non-destructive fallback — data flows into
                    // Revit rather than overwriting drofus (Gap 4 / Gap 8).
                    isUniqueId = false;
                    return MappingFlowDirection.DrofusToRevit;
            }
        }

        /// <summary>
        /// Resolves the human-readable display label for a drofus field id by
        /// looking it up in the current field catalogue.
        /// </summary>
        /// <param name="fieldId">
        /// The <see cref="DrofusRoomField.Id"/> (JSON key) to resolve.
        /// </param>
        /// <returns>
        /// The <see cref="DrofusRoomField.Name"/> for the matching catalogue entry,
        /// or the raw <paramref name="fieldId"/> string as a fallback when the
        /// catalogue has not been loaded or the id is not found.
        /// </returns>
        public string GetFieldLabel(string fieldId)
        {
            if (string.IsNullOrWhiteSpace(fieldId))
                return fieldId ?? string.Empty;

            DrofusRoomField? field = _availableFields
                .FirstOrDefault(f => string.Equals(f.Id, fieldId, StringComparison.OrdinalIgnoreCase));

            return field?.Name ?? fieldId;
        }

        /// <summary>
        /// Handles the case where the previously selected attribute configuration
        /// has been deleted from drofus (Scenario 3).
        /// <para>
        /// Clears all current mappings, resets
        /// <see cref="SelectedConfigurationId"/> to <c>null</c>, and returns a
        /// warning message for the caller to surface in the UI. The caller is
        /// responsible for immediately calling
        /// <see cref="SaveMappingsToSettings"/> and
        /// <see cref="SelectConfiguration"/> with <c>null</c> to persist the reset.
        /// </para>
        /// <para>
        /// This method must only be called when a Connect or startup sequence has
        /// <b>successfully</b> retrieved the configuration list and positively
        /// confirmed the previously selected id is absent. It must <b>not</b> be
        /// called on connection failure — absence of data is not evidence of
        /// deletion (Gap 9).
        /// </para>
        /// </summary>
        /// <returns>
        /// A warning message string ready to surface in the UI.
        /// </returns>
        public string HandleDeletedConfiguration()
        {
            _mappings.Clear();
            SelectedConfigurationId = null;

            return "The previously selected attribute configuration no longer exists " +
                   "in drofus. All mappings have been cleared. Please select a " +
                   "configuration and reconfigure your mappings.";
        }

        // ── Mapping mutations ─────────────────────────────────────────────────

        /// <summary>
        /// Removes all mappings unconditionally.
        /// <para>
        /// Called when the user confirms switching to the "None" sentinel
        /// configuration, where every mapping must be dropped regardless of
        /// whether the field still exists in the catalogue.
        /// </para>
        /// </summary>
        /// <returns>
        /// The human-readable labels of all mappings that were removed, so the
        /// caller can surface a meaningful status message.
        /// </returns>
        public List<string> ClearAllMappings()
        {
            var removedLabels = _mappings
                .Select(m => GetFieldLabel(m.DrofusFieldName))
                .ToList();

            _mappings.Clear();
            _revitValidationResults.Clear();
            return removedLabels;
        }

        /// <summary>
        /// Replaces the entire mapping list with a defensive copy of
        /// <paramref name="mappings"/> and clears any previously stored
        /// Revit validation results (since they relate to the old list).
        /// <para>
        /// Used when a settings file is loaded at runtime so the mapper's
        /// internal state is fully replaced without constructing a new instance.
        /// </para>
        /// </summary>
        /// <param name="mappings">
        /// The new mappings list. Must not be <c>null</c>; may be empty.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="mappings"/> is <c>null</c>.
        /// </exception>
        public void ReplaceMappings(List<DrofusPropertyMap> mappings)
        {
            if (mappings is null)
                throw new ArgumentNullException(nameof(mappings));

            _mappings.Clear();
            _mappings.AddRange(mappings);

            // Validation results belong to the old mapping set — clear them so
            // the UI does not show stale warning indicators against new mappings.
            _revitValidationResults.Clear();
        }

        /// <summary>
        /// Adds a new mapping to the list.
        /// <para>
        /// A drofus field may appear in more than one mapping (fan-out) — the same
        /// field value will be written to each mapped Revit parameter on push.
        /// The uniqueness constraint is therefore on the <b>(drofus field, Revit
        /// parameter)</b> pair: the identical combination twice would produce
        /// redundant writes with no useful effect.
        /// </para>
        /// </summary>
        /// <param name="map">The mapping to add. Must not be <c>null</c>.</param>
        /// <returns>
        /// <c>true</c> if the mapping was added; <c>false</c> if a mapping with
        /// the same <see cref="DrofusPropertyMap.DrofusFieldName"/> <b>and</b>
        /// <see cref="DrofusPropertyMap.RevitParameterName"/> pair already exists
        /// (case-insensitive comparison on both).
        /// </returns>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="map"/> is <c>null</c>.
        /// </exception>
        public bool AddMapping(DrofusPropertyMap map)
        {
            if (map is null)
                throw new ArgumentNullException(nameof(map));

            bool duplicate = _mappings.Any(m =>
                string.Equals(m.DrofusFieldName, map.DrofusFieldName,
                    StringComparison.OrdinalIgnoreCase)
                && string.Equals(m.RevitParameterName, map.RevitParameterName,
                    StringComparison.OrdinalIgnoreCase));

            if (duplicate)
                return false;

            _mappings.Add(map);
            return true;
        }

        /// <summary>
        /// Removes the specified mapping from the list by reference equality.
        /// </summary>
        /// <param name="map">The mapping instance to remove. Must not be <c>null</c>.</param>
        /// <returns>
        /// <c>true</c> if the mapping was found and removed; <c>false</c> if it
        /// was not present in the list.
        /// </returns>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="map"/> is <c>null</c>.
        /// </exception>
        public bool RemoveMapping(DrofusPropertyMap map)
        {
            if (map is null)
                throw new ArgumentNullException(nameof(map));

            return _mappings.Remove(map);
        }

        /// <summary>
        /// Removes all mappings whose <see cref="DrofusPropertyMap.DrofusFieldName"/>
        /// does not match any <see cref="DrofusRoomField.Id"/> in
        /// <see cref="GetFieldsForSelectedConfiguration"/>.
        /// <para>
        /// When a configuration is active, this method compares against that
        /// configuration's field ids — so a field removed from the configuration
        /// will be caught even if it still exists in the full catalogue (Scenario 4).
        /// When no configuration is active, the full catalogue is used.
        /// </para>
        /// <para>
        /// This method is only called after a successful explicit Connect — never
        /// during the startup validation pass (where stale mappings are flagged,
        /// not removed).
        /// </para>
        /// </summary>
        /// <returns>
        /// The list of <see cref="DrofusPropertyMap.DrofusFieldName"/> values that
        /// were removed (as human-readable labels via <see cref="GetFieldLabel"/>),
        /// so the caller can report them to the user.
        /// Returns an empty list when the available field set is empty (i.e. no
        /// connection has been made yet) or if no stale mappings existed.
        /// </returns>
        public List<string> CleanupStaleMappings()
        {
            // If we have no live field data yet, we cannot determine what is stale.
            if (_availableFields.Count == 0)
                return new List<string>();

            IReadOnlyList<DrofusRoomField> scopedFields = GetFieldsForSelectedConfiguration();

            var scopedIds = new HashSet<string>(
                scopedFields.Select(f => f.Id),
                StringComparer.OrdinalIgnoreCase);

            var stale = _mappings
                .Where(m => !scopedIds.Contains(m.DrofusFieldName))
                .ToList();

            var removedLabels = new List<string>();
            foreach (var mapping in stale)
            {
                _mappings.Remove(mapping);
                // Report human-readable label so the caller can surface a meaningful
                // message rather than raw JSON field ids.
                removedLabels.Add(GetFieldLabel(mapping.DrofusFieldName));
            }

            return removedLabels;
        }

        // ── Filtering ─────────────────────────────────────────────────────────

        /// <summary>
        /// Returns only the mappings whose <see cref="DrofusPropertyMap.FlowDirection"/>
        /// matches <paramref name="direction"/>.
        /// </summary>
        /// <param name="direction">The flow direction to filter by.</param>
        /// <returns>
        /// A new list containing the matching mappings. The returned list is a
        /// snapshot — changes to it do not affect the mapper's internal state.
        /// </returns>
        public List<DrofusPropertyMap> GetMappingsForDirection(MappingFlowDirection direction)
        {
            return _mappings
                .Where(m => m.FlowDirection == direction)
                .ToList();
        }

        // ── Revit validation results ──────────────────────────────────────────

        /// <summary>
        /// Stores the outcome of the Revit-side shared parameter existence check.
        /// <para>
        /// Called by <c>ValidateDrofusOnStartup</c> after querying
        /// <c>SharedParaUtils.ParameterBindingsByGUID</c> for each mapping GUID.
        /// Also called after a successful Connect to refresh the state.
        /// </para>
        /// </summary>
        /// <param name="resultsByGuid">
        /// Dictionary keyed on <see cref="DrofusPropertyMap.RevitParameterGuid"/>.
        /// A value of <c>true</c> means the parameter was found in the document;
        /// <c>false</c> means it was not. GUIDs not present in the dictionary are
        /// treated as "not yet checked" rather than missing.
        /// Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="resultsByGuid"/> is <c>null</c>.
        /// </exception>
        public void SetRevitValidationResults(Dictionary<string, bool> resultsByGuid)
        {
            if (resultsByGuid is null)
                throw new ArgumentNullException(nameof(resultsByGuid));

            _revitValidationResults.Clear();

            foreach (var kvp in resultsByGuid)
            {
                _revitValidationResults[kvp.Key] = kvp.Value;
            }
        }

        /// <summary>
        /// Returns the stored Revit parameter existence result for the given GUID.
        /// </summary>
        /// <param name="guid">
        /// The <see cref="DrofusPropertyMap.RevitParameterGuid"/> to look up.
        /// </param>
        /// <returns>
        /// <c>true</c> if the parameter was confirmed present; <c>false</c> if it
        /// was confirmed missing; <c>null</c> if no validation result has been
        /// recorded for this GUID yet (i.e. the validation pass has not run, or
        /// the GUID was not included in the last pass).
        /// </returns>
        public bool? GetRevitValidationResult(string guid)
        {
            if (string.IsNullOrWhiteSpace(guid))
                return null;

            if (_revitValidationResults.TryGetValue(guid, out bool result))
                return result;

            return null;
        }

        // ── Aggregate validation state ────────────────────────────────────────

        /// <summary>
        /// <c>true</c> when at least one mapping has a known validation problem —
        /// either a Revit parameter confirmed missing, or a drofus field confirmed
        /// absent from the catalogue (or the active configuration's fields).
        /// <para>
        /// Returns <c>false</c> when no validation pass has run yet (i.e. both
        /// <see cref="AvailableFields"/> is empty and no Revit results have been
        /// stored) — absence of evidence is not evidence of a problem.
        /// </para>
        /// </summary>
        public bool HasValidationWarnings
        {
            get
            {
                foreach (var mapping in _mappings)
                {
                    // Check Revit-side: a stored false means confirmed missing.
                    bool? revitResult = GetRevitValidationResult(mapping.RevitParameterGuid);
                    if (revitResult == false)
                        return true;

                    // Check drofus-side: only flag as missing when we have live
                    // field data — an empty AvailableFields means unknown, not absent.
                    if (_availableFields.Count > 0)
                    {
                        IReadOnlyList<DrofusRoomField> scopedFields =
                            GetFieldsForSelectedConfiguration();

                        bool fieldPresent = scopedFields.Any(f =>
                            string.Equals(f.Id, mapping.DrofusFieldName,
                                StringComparison.OrdinalIgnoreCase));

                        if (!fieldPresent)
                            return true;
                    }
                }

                return false;
            }
        }

        /// <summary>
        /// Builds a <see cref="MappingValidationState"/> for the given mapping
        /// based on the most recently stored validation results.
        /// <para>
        /// Intended for use by <c>DrofusPropertyMapViewModel</c> when constructing
        /// or refreshing its display state.
        /// </para>
        /// </summary>
        /// <param name="map">The mapping to evaluate. Must not be <c>null</c>.</param>
        /// <returns>
        /// A new <see cref="MappingValidationState"/> instance reflecting the
        /// current known validation state for <paramref name="map"/>.
        /// </returns>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="map"/> is <c>null</c>.
        /// </exception>
        public MappingValidationState GetValidationState(DrofusPropertyMap map)
        {
            if (map is null)
                throw new ArgumentNullException(nameof(map));

            bool revitMissing = false;
            bool? revitResult = GetRevitValidationResult(map.RevitParameterGuid);
            if (revitResult == false)
                revitMissing = true;

            bool drofusMissing = false;
            if (_availableFields.Count > 0)
            {
                IReadOnlyList<DrofusRoomField> scopedFields =
                    GetFieldsForSelectedConfiguration();

                bool fieldPresent = scopedFields.Any(f =>
                    string.Equals(f.Id, map.DrofusFieldName,
                        StringComparison.OrdinalIgnoreCase));

                if (!fieldPresent)
                    drofusMissing = true;
            }

            return new MappingValidationState
            {
                RevitParameterMissing = revitMissing,
                DrofusFieldMissing = drofusMissing,
            };
        }

        // ── Settings sync ─────────────────────────────────────────────────────

        /// <summary>
        /// Writes the current in-memory mapping list back to the provided
        /// <see cref="DrofusDataSourceSettings"/> so that the caller can persist
        /// it to disk via the normal settings save path.
        /// <para>
        /// Called after every Add, Remove, or CleanupStaleMappings operation,
        /// and before the settings file is written.
        /// </para>
        /// </summary>
        /// <param name="settings">
        /// The settings object to update. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="settings"/> is <c>null</c>.
        /// </exception>
        public void SaveMappingsToSettings(DrofusDataSourceSettings settings)
        {
            if (settings is null)
                throw new ArgumentNullException(nameof(settings));

            settings.PropertyMappings.Clear();
            settings.PropertyMappings.AddRange(_mappings);
        }
    }
}
