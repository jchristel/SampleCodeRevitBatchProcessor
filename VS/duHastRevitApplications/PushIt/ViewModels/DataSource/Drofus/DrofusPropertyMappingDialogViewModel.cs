// BSD License - Copyright 2025, Jan Christel

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Models.Drofus;
using duHastNet.PushIt.Utilities.Drofus;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace duHastNet.PushIt.ViewModels.DataSource.Drofus
{
    /// <summary>
    /// ViewModel for the Add / Edit drofus property mapping dialog.
    /// Two constructors support Add mode and Edit mode.
    /// When confirmed, <see cref="CreatedMapping"/> is set and
    /// <see cref="RequestClose"/> is raised.
    /// </summary>
    public partial class DrofusPropertyMappingDialogViewModel : ObservableObject
    {
        // ── Private state ─────────────────────────────────────────────────────

        private readonly bool _isEditMode;
        private readonly DrofusPropertyMap? _existingMapping;

        /// <summary>
        /// <c>true</c> when another mapping already carries <c>IsUniqueId = true</c>
        /// and this dialog is not editing that mapping. Used to disable the Is Id
        /// checkbox so only one mapping can hold the unique-id flag at a time.
        /// </summary>
        private readonly bool _anotherMappingIsAlreadyId;

        /// <summary>
        /// Lookup from parameter Name -> AvailableParameter so that selecting a
        /// parameter name in the ComboBox can immediately resolve its GUID.
        /// </summary>
        private readonly Dictionary<string, AvailableParameter> _revitParamsByName;

        /// <summary>
        /// The mapper service, used to call <see cref="DrofusPropertyMapper.GetElementForField"/>
        /// for direction pre-population when a field is selected. May be <c>null</c>
        /// when no mapper is available (legacy construction path).
        /// </summary>
        private readonly DrofusPropertyMapper? _mapper;

        /// <summary>
        /// The id of the currently active attribute configuration, passed in from
        /// the parent ViewModel. Used together with <see cref="_mapper"/> to resolve
        /// the <see cref="DrofusAttributeConfigurationElement"/> for a selected field
        /// and pre-populate direction and IsUniqueId automatically.
        /// <c>null</c> means no configuration is active — no auto-population.
        /// </summary>
        private readonly int? _activeConfigurationId;

        // ── Observable collections ────────────────────────────────────────────

        /// <summary>
        /// drofus room fields available for the first ComboBox, scoped to the
        /// currently selected attribute configuration (or the full catalogue when
        /// no configuration is selected). The ComboBox binds
        /// <c>DisplayMemberPath="Name"</c> so the user sees the human-readable label;
        /// the selected item is a <see cref="DrofusRoomField"/> instance.
        /// </summary>
        public ObservableCollection<DrofusRoomField> AvailableDrofusFields { get; }

        /// <summary>
        /// Revit shared parameter names available for the second ComboBox.
        /// Populated from the available parameters at construction.
        /// </summary>
        public ObservableCollection<string> AvailableRevitParameterNames { get; }

        /// <summary>
        /// Flow direction values for the direction ComboBox.
        /// </summary>
        public MappingFlowDirection[] AvailableFlowDirections { get; } =
            (MappingFlowDirection[])Enum.GetValues(typeof(MappingFlowDirection));

        // ── Observable properties ─────────────────────────────────────────────

        /// <summary>
        /// The selected drofus room field. Required for OK to be enabled.
        /// When changed, triggers direction and IsUniqueId pre-population from
        /// the active configuration element (if available).
        /// </summary>
        [ObservableProperty]
        private DrofusRoomField? _selectedDrofusField;

        /// <summary>
        /// Selected Revit parameter name from the ComboBox.
        /// Changing this automatically updates <see cref="RevitParameterGuid"/>.
        /// </summary>
        [ObservableProperty]
        private string? _selectedRevitParameterName;

        /// <summary>
        /// Revit shared parameter GUID. Read-only in the UI — auto-populated
        /// when a parameter is selected from the ComboBox.
        /// </summary>
        [ObservableProperty]
        private string _revitParameterGuid = string.Empty;

        /// <summary>
        /// Selected flow direction. May be auto-populated from the active
        /// configuration element when a drofus field is selected.
        /// </summary>
        [ObservableProperty]
        private MappingFlowDirection _selectedFlowDirection = MappingFlowDirection.DrofusToRevit;

        /// <summary>
        /// Whether this mapping is nominated as the unique identifier.
        /// Only one mapping in the list may carry this flag — the checkbox is
        /// disabled when another mapping already holds it (unless this dialog is
        /// editing that exact mapping). May be auto-populated from the active
        /// configuration element when a drofus field is selected.
        /// </summary>
        [ObservableProperty]
        private bool _isUniqueId;

        /// <summary>
        /// <c>true</c> when the Is Id checkbox should be interactive.
        /// <c>false</c> when another mapping already holds the unique-id flag
        /// and this dialog is not editing that mapping — prevents a second mapping
        /// from being nominated as the unique identifier.
        /// </summary>
        public bool IsUniqueIdEnabled => !_anotherMappingIsAlreadyId;

        /// <summary>
        /// The mapping produced on OK. Null until OK fires, and null after Cancel.
        /// </summary>
        [ObservableProperty]
        private DrofusPropertyMap? _createdMapping;

        /// <summary>
        /// Dialog title — "Add Mapping" or "Edit Mapping".
        /// </summary>
        public string DialogTitle => _isEditMode ? "Edit Mapping" : "Add Mapping";

        // ── Events ────────────────────────────────────────────────────────────

        /// <summary>Raised when the dialog should close.</summary>
        public event EventHandler? RequestClose;

        // ── Constructors ──────────────────────────────────────────────────────

        /// <summary>
        /// Add mode constructor.
        /// </summary>
        /// <param name="availableFields">
        /// drofus room fields scoped to the active configuration (or the full
        /// catalogue when no configuration is selected). Supplied by
        /// <c>DrofusPropertyMapper.GetFieldsForSelectedConfiguration()</c>.
        /// </param>
        /// <param name="availableRevitParameters">
        /// Revit shared parameters available in the document.
        /// </param>
        /// <param name="hasExistingId">
        /// <c>true</c> when another mapping in the list already carries
        /// <c>IsUniqueId = true</c>. Disables the Is Id checkbox.
        /// </param>
        /// <param name="mapper">
        /// The mapper service, used for direction pre-population. May be <c>null</c>.
        /// </param>
        /// <param name="activeConfigurationId">
        /// The id of the active attribute configuration, used to look up the
        /// <see cref="DrofusAttributeConfigurationElement"/> for a selected field.
        /// <c>null</c> when no configuration is active.
        /// </param>
        public DrofusPropertyMappingDialogViewModel(
            IReadOnlyList<DrofusRoomField> availableFields,
            IReadOnlyList<AvailableParameter> availableRevitParameters,
            bool hasExistingId = false,
            DrofusPropertyMapper? mapper = null,
            int? activeConfigurationId = null)
        {
            if (availableFields is null)
                throw new ArgumentNullException(nameof(availableFields));
            if (availableRevitParameters is null)
                throw new ArgumentNullException(nameof(availableRevitParameters));

            _isEditMode = false;
            _existingMapping = null;
            _anotherMappingIsAlreadyId = hasExistingId;
            _mapper = mapper;
            _activeConfigurationId = activeConfigurationId;

            AvailableDrofusFields = new ObservableCollection<DrofusRoomField>(availableFields);
            AvailableRevitParameterNames = new ObservableCollection<string>(
                availableRevitParameters.Select(p => p.ParameterName));

            _revitParamsByName = availableRevitParameters
                .GroupBy(p => p.ParameterName)
                .ToDictionary(g => g.Key, g => g.First());

            // Pre-select first items via the property setters so WPF bindings
            // are notified correctly (backing-field assignment in constructors
            // does NOT raise PropertyChanged).
            if (AvailableDrofusFields.Count > 0)
                SelectedDrofusField = AvailableDrofusFields[0];

            if (AvailableRevitParameterNames.Count > 0)
                SelectedRevitParameterName = AvailableRevitParameterNames[0];
        }

        /// <summary>
        /// Edit mode constructor.
        /// </summary>
        /// <param name="availableFields">
        /// drofus room fields scoped to the active configuration (or the full
        /// catalogue). Supplied by
        /// <c>DrofusPropertyMapper.GetFieldsForSelectedConfiguration()</c>.
        /// </param>
        /// <param name="availableRevitParameters">
        /// Revit shared parameters available in the document.
        /// </param>
        /// <param name="existingMapping">The mapping being edited.</param>
        /// <param name="hasExistingId">
        /// <c>true</c> when another mapping (not this one) already carries
        /// <c>IsUniqueId = true</c>. Pass <c>false</c> when editing the mapping
        /// that is itself the current unique identifier so its checkbox stays enabled.
        /// </param>
        /// <param name="mapper">
        /// The mapper service, used for direction pre-population. May be <c>null</c>.
        /// </param>
        /// <param name="activeConfigurationId">
        /// The id of the active attribute configuration. <c>null</c> when none active.
        /// </param>
        public DrofusPropertyMappingDialogViewModel(
            IReadOnlyList<DrofusRoomField> availableFields,
            IReadOnlyList<AvailableParameter> availableRevitParameters,
            DrofusPropertyMap existingMapping,
            bool hasExistingId = false,
            DrofusPropertyMapper? mapper = null,
            int? activeConfigurationId = null)
            : this(availableFields, availableRevitParameters, hasExistingId, mapper, activeConfigurationId)
        {
            _isEditMode = true;
            _existingMapping = existingMapping
                ?? throw new ArgumentNullException(nameof(existingMapping));

            // Override defaults with existing mapping values — via property setters
            // so PropertyChanged fires and WPF ComboBoxes resolve correctly.
            // Look up the DrofusRoomField by Id so the ComboBox selected-item binding
            // resolves to the correct object reference rather than a string comparison.
            SelectedDrofusField = AvailableDrofusFields
                .FirstOrDefault(f => string.Equals(
                    f.Id, existingMapping.DrofusFieldName,
                    StringComparison.OrdinalIgnoreCase));

            SelectedRevitParameterName = existingMapping.RevitParameterName;
            _revitParameterGuid        = existingMapping.RevitParameterGuid; // read-only; set backing field directly
            SelectedFlowDirection      = existingMapping.FlowDirection;
            IsUniqueId                 = existingMapping.IsUniqueId;
        }

        // ── Partial property callbacks ────────────────────────────────────────

        partial void OnSelectedDrofusFieldChanged(DrofusRoomField? value)
        {
            OkCommand.NotifyCanExecuteChanged();

            // Direction / IsUniqueId pre-population from the active configuration
            // element. Only fires when a mapper and active configuration are present.
            // In edit mode the existing mapping values are already loaded by the
            // constructor — we still allow the auto-population to fire so that if the
            // user changes the field selection the direction updates accordingly.
            if (value is null || _mapper is null || _activeConfigurationId is null)
                return;

            DrofusAttributeConfigurationElement? element =
                _mapper.GetElementForField(_activeConfigurationId.Value, value.Id);

            if (element is null)
            {
                // Field is from the full catalogue with no active configuration
                // element — leave direction and IsUniqueId at their current values.
                return;
            }

            // Map the raw direction string to PushIt concepts and update both
            // observable properties so the UI reflects the pre-populated state.
            MappingFlowDirection direction =
                DrofusPropertyMapper.MapDirection(element.Direction, out bool isUniqueId);

            SelectedFlowDirection = direction;

            // Only override IsUniqueId when the checkbox is not locked.
            // If _anotherMappingIsAlreadyId is true the checkbox is disabled anyway,
            // but we should not silently set IsUniqueId = true on a locked dialog.
            if (!_anotherMappingIsAlreadyId)
                IsUniqueId = isUniqueId;
        }

        partial void OnSelectedRevitParameterNameChanged(string? value)
        {
            // Auto-populate GUID from the parameter lookup.
            if (value != null && _revitParamsByName.TryGetValue(value, out AvailableParameter? param))
                RevitParameterGuid = param.ParameterGuid;
            else
                RevitParameterGuid = string.Empty;

            OkCommand.NotifyCanExecuteChanged();
        }

        // ── Commands ──────────────────────────────────────────────────────────

        [RelayCommand(CanExecute = nameof(CanExecuteOk))]
        private void Ok()
        {
            // Write the field Id (not Name) into DrofusFieldName so the persisted
            // format is the stable JSON key, not the human-readable label.
            CreatedMapping = new DrofusPropertyMap
            {
                DrofusFieldName    = SelectedDrofusField!.Id.Trim(),
                RevitParameterName = SelectedRevitParameterName!.Trim(),
                RevitParameterGuid = RevitParameterGuid.Trim(),
                FlowDirection      = SelectedFlowDirection,
                IsUniqueId         = IsUniqueId,
            };

            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        private bool CanExecuteOk()
            => SelectedDrofusField is not null
            && !string.IsNullOrWhiteSpace(SelectedRevitParameterName);

        [RelayCommand]
        private void Cancel()
        {
            CreatedMapping = null;
            RequestClose?.Invoke(this, EventArgs.Empty);
        }
    }
}
