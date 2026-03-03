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
        private readonly List<string> _availableFields;

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
        /// The live drofus field names derived from the most recent successful
        /// API response. Empty until <see cref="UpdateAvailableFields"/> has been
        /// called at least once (either from the Connect button or from the
        /// startup validation pass).
        /// </summary>
        public IReadOnlyList<string> AvailableFields => _availableFields;

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
            _availableFields = new List<string>();
            _revitValidationResults = new Dictionary<string, bool>(StringComparer.OrdinalIgnoreCase);
        }

        // ── Field management ──────────────────────────────────────────────────

        /// <summary>
        /// Replaces the internal available-fields list with the field names
        /// extracted from the first room object in a live drofus API response.
        /// <para>
        /// Called after every successful HTTP connection — both from the Connect
        /// button and from the startup validation pass.
        /// </para>
        /// </summary>
        /// <param name="fieldNames">
        /// The JSON property names present on the first room returned by the
        /// drofus rooms endpoint. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="fieldNames"/> is <c>null</c>.
        /// </exception>
        public void UpdateAvailableFields(List<string> fieldNames)
        {
            if (fieldNames is null)
                throw new ArgumentNullException(nameof(fieldNames));

            _availableFields.Clear();
            _availableFields.AddRange(fieldNames);
        }

        // ── Mapping mutations ─────────────────────────────────────────────────

        /// <summary>
        /// Adds a new mapping to the list.
        /// </summary>
        /// <param name="map">The mapping to add. Must not be <c>null</c>.</param>
        /// <returns>
        /// <c>true</c> if the mapping was added; <c>false</c> if a mapping with
        /// the same <see cref="DrofusPropertyMap.DrofusFieldName"/> already exists
        /// (case-insensitive comparison).
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
        /// is not present in <see cref="AvailableFields"/>.
        /// <para>
        /// This method is only called after a successful explicit Connect — never
        /// during the startup validation pass (where stale mappings are flagged,
        /// not removed).
        /// </para>
        /// </summary>
        /// <returns>
        /// The list of <see cref="DrofusPropertyMap.DrofusFieldName"/> values that
        /// were removed, so the caller can report them to the user.
        /// Returns an empty list if <see cref="AvailableFields"/> is empty (i.e.
        /// no connection has been made yet) or if no stale mappings existed.
        /// </returns>
        public List<string> CleanupStaleMappings()
        {
            // If we have no live field data yet, we cannot determine what is stale.
            if (_availableFields.Count == 0)
                return new List<string>();

            var stale = _mappings
                .Where(m => !_availableFields.Contains(
                    m.DrofusFieldName, StringComparer.OrdinalIgnoreCase))
                .ToList();

            var removedNames = new List<string>();
            foreach (var mapping in stale)
            {
                _mappings.Remove(mapping);
                removedNames.Add(mapping.DrofusFieldName);
            }

            return removedNames;
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
        /// Called by <c>ValidateDrofusMappingsOnStartup</c> after querying
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
        /// absent from the live API response.
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
                    if (_availableFields.Count > 0 &&
                        !_availableFields.Contains(
                            mapping.DrofusFieldName, StringComparer.OrdinalIgnoreCase))
                    {
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
            if (_availableFields.Count > 0 &&
                !_availableFields.Contains(
                    map.DrofusFieldName, StringComparer.OrdinalIgnoreCase))
            {
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
