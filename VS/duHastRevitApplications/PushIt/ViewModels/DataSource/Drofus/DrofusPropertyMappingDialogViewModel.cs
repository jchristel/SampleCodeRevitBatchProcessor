// BSD License - Copyright 2025, Jan Christel

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Models.Drofus;
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

        // ── Observable collections ────────────────────────────────────────────

        /// <summary>
        /// drofus JSON field names available for the first ComboBox.
        /// Populated from DrofusPropertyMapper.AvailableFields at construction.
        /// </summary>
        public ObservableCollection<string> AvailableDrofusFields { get; }

        /// <summary>
        /// Revit shared parameter names available for the second ComboBox.
        /// Populated from RevitDataModel.GetAllParameters() at construction.
        /// </summary>
        public ObservableCollection<string> AvailableRevitParameterNames { get; }

        /// <summary>
        /// Flow direction values for the direction ComboBox.
        /// </summary>
        public MappingFlowDirection[] AvailableFlowDirections { get; } =
            (MappingFlowDirection[])Enum.GetValues(typeof(MappingFlowDirection));

        // ── Observable properties ─────────────────────────────────────────────

        /// <summary>
        /// Selected drofus field name. Required for OK to be enabled.
        /// </summary>
        [ObservableProperty]
        private string? _selectedDrofusField;

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
        /// Selected flow direction.
        /// </summary>
        [ObservableProperty]
        private MappingFlowDirection _selectedFlowDirection = MappingFlowDirection.DrofusToRevit;

        /// <summary>
        /// Whether this mapping is nominated as the unique identifier.
        /// Only one mapping in the list may carry this flag — the checkbox is
        /// disabled when another mapping already holds it (unless this dialog is
        /// editing that exact mapping).
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

        /// <summary>Add mode constructor.</summary>
        /// <param name="availableFields">drofus JSON field names from the live API response.</param>
        /// <param name="availableRevitParameters">Revit shared parameters available in the document.</param>
        /// <param name="hasExistingId">
        /// <c>true</c> when another mapping in the list already carries
        /// <c>IsUniqueId = true</c>. Disables the Is Id checkbox so only one
        /// mapping can be the unique identifier at a time.
        /// </param>
        public DrofusPropertyMappingDialogViewModel(
            IReadOnlyList<string> availableFields,
            IReadOnlyList<AvailableParameter> availableRevitParameters,
            bool hasExistingId = false)
        {
            if (availableFields is null)
                throw new ArgumentNullException(nameof(availableFields));
            if (availableRevitParameters is null)
                throw new ArgumentNullException(nameof(availableRevitParameters));

            _isEditMode  = false;
            _existingMapping = null;
            _anotherMappingIsAlreadyId = hasExistingId;

            AvailableDrofusFields       = new ObservableCollection<string>(availableFields);
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

        /// <summary>Edit mode constructor.</summary>
        /// <param name="availableFields">drofus JSON field names from the live API response.</param>
        /// <param name="availableRevitParameters">Revit shared parameters available in the document.</param>
        /// <param name="existingMapping">The mapping being edited.</param>
        /// <param name="hasExistingId">
        /// <c>true</c> when another mapping (not this one) already carries
        /// <c>IsUniqueId = true</c>. Pass <c>false</c> when editing the mapping
        /// that is itself the current unique identifier so its checkbox stays enabled.
        /// </param>
        public DrofusPropertyMappingDialogViewModel(
            IReadOnlyList<string> availableFields,
            IReadOnlyList<AvailableParameter> availableRevitParameters,
            DrofusPropertyMap existingMapping,
            bool hasExistingId = false)
            : this(availableFields, availableRevitParameters, hasExistingId)
        {
            _isEditMode      = true;
            _existingMapping = existingMapping
                ?? throw new ArgumentNullException(nameof(existingMapping));

            // Override defaults with existing mapping values — again via property
            // setters so PropertyChanged fires and WPF ComboBoxes resolve correctly.
            SelectedDrofusField        = existingMapping.DrofusFieldName;
            SelectedRevitParameterName = existingMapping.RevitParameterName;
            _revitParameterGuid        = existingMapping.RevitParameterGuid; // GUID is read-only so set backing field directly
            SelectedFlowDirection      = existingMapping.FlowDirection;
            IsUniqueId                 = existingMapping.IsUniqueId;
        }

        // ── Partial property callbacks ────────────────────────────────────────

        partial void OnSelectedDrofusFieldChanged(string? value)
            => OkCommand.NotifyCanExecuteChanged();

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
            CreatedMapping = new DrofusPropertyMap
            {
                DrofusFieldName      = SelectedDrofusField!.Trim(),
                RevitParameterName   = SelectedRevitParameterName!.Trim(),
                RevitParameterGuid   = RevitParameterGuid.Trim(),
                FlowDirection        = SelectedFlowDirection,
                IsUniqueId           = IsUniqueId,
            };

            RequestClose?.Invoke(this, EventArgs.Empty);
        }

        private bool CanExecuteOk()
            => !string.IsNullOrWhiteSpace(SelectedDrofusField)
            && !string.IsNullOrWhiteSpace(SelectedRevitParameterName);

        [RelayCommand]
        private void Cancel()
        {
            CreatedMapping = null;
            RequestClose?.Invoke(this, EventArgs.Empty);
        }
    }
}
