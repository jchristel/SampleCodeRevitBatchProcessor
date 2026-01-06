//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using NUnit.Framework;
using Moq;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.CloudProviderControls;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CloudDocManager.CloudProviderControls;

/// <summary>
/// Tests for MetaDataMappingDialogViewModel
/// Covers Add mode, Edit mode, conditional validation, and mapping creation
/// </summary>
[TestFixture]
public class MetaDataMappingDialogViewModelTests
{
    private Mock<MessageStore> _mockMessageStore;
    private List<string> _availableMetaFields;
    private List<string> _availableDocumentProperties;

    [SetUp]
    public void Setup()
    {
        _mockMessageStore = new Mock<MessageStore>();

        _availableMetaFields = new List<string>
        {
            "ProjectNumber",
            "ProjectName",
            "Discipline",
            "Status"
        };

        _availableDocumentProperties = new List<string>
        {
            "Number",
            "Name",
            "Revision",
            "CustomField1",
            "CustomField2"
        };
    }

    #region Constructor Tests - Add Mode

    [Test]
    public void Constructor_AddMode_InitializesSuccessfully()
    {
        // Arrange & Act
        var viewModel = new MetaDataMappingDialogViewModel(
            _availableMetaFields,
            _availableDocumentProperties,
            _mockMessageStore.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Add Metadata Mapping"));
            Assert.That(viewModel.AvailableMetaFields, Has.Count.EqualTo(4));
            Assert.That(viewModel.AvailableDocumentProperties, Has.Count.EqualTo(5));
            Assert.That(viewModel.AvailableFileProperties, Has.Count.GreaterThan(0));
            Assert.That(viewModel.SelectedMappingSource, Is.EqualTo(MappingSourceType.DocumentProperty));
            Assert.That(viewModel.CreatedMapping, Is.Null);
        });
    }

    [Test]
    public void Constructor_AddMode_SelectsDefaultValues()
    {
        // Arrange & Act
        var viewModel = new MetaDataMappingDialogViewModel(
            _availableMetaFields,
            _availableDocumentProperties,
            _mockMessageStore.Object);

        // Assert - Should select first items as defaults
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SelectedMetaFieldName, Is.EqualTo("ProjectNumber"));
            Assert.That(viewModel.SelectedDocumentProperty, Is.EqualTo("Number"));
            Assert.That(viewModel.SelectedFileProperty, Is.Not.Null);
        });
    }

    [Test]
    public void Constructor_AddMode_WithNullParameters_ThrowsException()
    {
        // Arrange & Act & Assert
        Assert.Multiple(() =>
        {
            Assert.Throws<ArgumentNullException>(() => new MetaDataMappingDialogViewModel(
                null,
                _availableDocumentProperties,
                _mockMessageStore.Object));

            Assert.Throws<ArgumentNullException>(() => new MetaDataMappingDialogViewModel(
                _availableMetaFields,
                null,
                _mockMessageStore.Object));

            Assert.Throws<ArgumentNullException>(() => new MetaDataMappingDialogViewModel(
                _availableMetaFields,
                _availableDocumentProperties,
                null));
        });
    }

    #endregion

    #region Constructor Tests - Edit Mode

    [Test]
    public void Constructor_EditMode_LoadsExistingMapping()
    {
        // Arrange
        var existingMapping = new MetaDataMap
        {
            MetaFieldName = "ProjectNumber",
            DocumentPropertyName = "Number",
            CloudServiceProviderName = "Aconex"
        };

        // Act
        var viewModel = new MetaDataMappingDialogViewModel(
            _availableMetaFields,
            _availableDocumentProperties,
            existingMapping,
            _mockMessageStore.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Edit Metadata Mapping"));
            Assert.That(viewModel.SelectedMetaFieldName, Is.EqualTo("ProjectNumber"));
            Assert.That(viewModel.SelectedMappingSource, Is.EqualTo(MappingSourceType.DocumentProperty));
            Assert.That(viewModel.SelectedDocumentProperty, Is.EqualTo("Number"));
        });
    }

    [Test]
    public void Constructor_EditMode_LoadsStaticValueMapping()
    {
        // Arrange
        var existingMapping = new MetaDataMap
        {
            MetaFieldName = "Status",
            MetaFieldValue = "Draft",
            CloudServiceProviderName = "Aconex"
        };

        // Act
        var viewModel = new MetaDataMappingDialogViewModel(
            _availableMetaFields,
            _availableDocumentProperties,
            existingMapping,
            _mockMessageStore.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SelectedMappingSource, Is.EqualTo(MappingSourceType.StaticValue));
            Assert.That(viewModel.StaticValue, Is.EqualTo("Draft"));
        });
    }

    [Test]
    public void Constructor_EditMode_LoadsFilePropertyMapping()
    {
        // Arrange
        var existingMapping = new MetaDataMap
        {
            MetaFieldName = "FileName",
            FilePropertyName = "FileName",
            CloudServiceProviderName = "Aconex"
        };

        // Act
        var viewModel = new MetaDataMappingDialogViewModel(
            _availableMetaFields,
            _availableDocumentProperties,
            existingMapping,
            _mockMessageStore.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SelectedMappingSource, Is.EqualTo(MappingSourceType.FileProperty));
            Assert.That(viewModel.SelectedFileProperty, Is.EqualTo("FileName"));
        });
    }

    #endregion

    #region Property Change Tests

    [Test]
    public void SelectedMappingSource_WhenChanged_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.SelectedMappingSource))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void SelectedMappingSource_WhenChanged_ClearsOtherFieldErrors()
    {
        // Arrange
        var viewModel = CreateViewModel();
        
        // Set to StaticValue and make it invalid
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;
        viewModel.StaticValue = "";
        
        Assert.That(viewModel.HasErrors, Is.True, "Should have errors for empty static value");

        // Act - Switch to DocumentProperty
        viewModel.SelectedMappingSource = MappingSourceType.DocumentProperty;

        // Assert - Errors should be cleared (DocumentProperty is already selected from default)
        Assert.That(viewModel.HasErrors, Is.False, "Errors should be cleared when switching source types");
    }

    #endregion

    #region Validation Tests - DocumentProperty Mode

    [Test]
    public void Validation_DocumentPropertyMode_WithValidSelection_NoError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.DocumentProperty;

        // Act
        viewModel.SelectedDocumentProperty = "Number";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_DocumentPropertyMode_WithEmptySelection_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.DocumentProperty;

        // Act
        viewModel.SelectedDocumentProperty = "Something";
        viewModel.SelectedDocumentProperty = null;

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_DocumentPropertyMode_StaticValueNotRequired()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.DocumentProperty;

        // Act
        viewModel.StaticValue = ""; // Empty but shouldn't cause error in DocumentProperty mode

        // Assert
        Assert.That(viewModel.HasErrors, Is.False, "StaticValue should not be validated in DocumentProperty mode");
    }

    #endregion

    #region Validation Tests - StaticValue Mode

    [Test]
    public void Validation_StaticValueMode_WithValidValue_NoError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;

        // Act
        viewModel.StaticValue = "Draft";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_StaticValueMode_WithEmptyValue_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;

        // Act
        viewModel.StaticValue = "Something";
        viewModel.StaticValue = "";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_StaticValueMode_DocumentPropertyNotRequired()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;
        viewModel.StaticValue = "Draft";

        // Act
        viewModel.SelectedDocumentProperty = null;

        // Assert
        Assert.That(viewModel.HasErrors, Is.False, "DocumentProperty should not be validated in StaticValue mode");
    }

    #endregion

    #region Validation Tests - FileProperty Mode

    [Test]
    public void Validation_FilePropertyMode_WithValidSelection_NoError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.FileProperty;

        // Act
        viewModel.SelectedFileProperty = "FileName";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_FilePropertyMode_WithEmptySelection_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.FileProperty;

        // Act
        viewModel.SelectedFileProperty = "Something";
        viewModel.SelectedFileProperty = null;

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    #endregion

    #region OkCommand Tests - CanExecute

    [Test]
    public void OkCommand_DocumentPropertyMode_WithValidData_CanExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.DocumentProperty;
        viewModel.SelectedMetaFieldName = "ProjectNumber";
        viewModel.SelectedDocumentProperty = "Number";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void OkCommand_StaticValueMode_WithValidData_CanExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;
        viewModel.SelectedMetaFieldName = "Status";
        viewModel.StaticValue = "Draft";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void OkCommand_FilePropertyMode_WithValidData_CanExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.FileProperty;
        viewModel.SelectedMetaFieldName = "FileName";
        viewModel.SelectedFileProperty = "FileName";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void OkCommand_WithNoMetaFieldSelected_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMetaFieldName = null;

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void OkCommand_DocumentPropertyMode_WithNoPropertySelected_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.DocumentProperty;
        viewModel.SelectedMetaFieldName = "ProjectNumber";
        viewModel.SelectedDocumentProperty = null;

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void OkCommand_StaticValueMode_WithEmptyValue_CannotExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;
        viewModel.SelectedMetaFieldName = "Status";
        viewModel.StaticValue = "";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    #endregion

    #region OkCommand Tests - Execute

    [Test]
    public void OkCommand_Execute_CreatesDocumentPropertyMapping()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.DocumentProperty;
        viewModel.SelectedMetaFieldName = "ProjectNumber";
        viewModel.SelectedDocumentProperty = "Number";

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedMapping, Is.Not.Null);
            Assert.That(viewModel.CreatedMapping.MetaFieldName, Is.EqualTo("ProjectNumber"));
            Assert.That(viewModel.CreatedMapping.DocumentPropertyName, Is.EqualTo("Number"));
            Assert.That(viewModel.CreatedMapping.MetaFieldValue, Is.Null);
            Assert.That(viewModel.CreatedMapping.FilePropertyName, Is.Null);
            Assert.That(viewModel.CreatedMapping.CloudServiceProviderName, Is.EqualTo("Aconex"));
        });
    }

    [Test]
    public void OkCommand_Execute_CreatesStaticValueMapping()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;
        viewModel.SelectedMetaFieldName = "Status";
        viewModel.StaticValue = "Draft";

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedMapping, Is.Not.Null);
            Assert.That(viewModel.CreatedMapping.MetaFieldName, Is.EqualTo("Status"));
            Assert.That(viewModel.CreatedMapping.MetaFieldValue, Is.EqualTo("Draft"));
            Assert.That(viewModel.CreatedMapping.DocumentPropertyName, Is.Null);
            Assert.That(viewModel.CreatedMapping.FilePropertyName, Is.Null);
        });
    }

    [Test]
    public void OkCommand_Execute_CreatesFilePropertyMapping()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMappingSource = MappingSourceType.FileProperty;
        viewModel.SelectedMetaFieldName = "FileName";
        viewModel.SelectedFileProperty = "FileName";

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedMapping, Is.Not.Null);
            Assert.That(viewModel.CreatedMapping.MetaFieldName, Is.EqualTo("FileName"));
            Assert.That(viewModel.CreatedMapping.FilePropertyName, Is.EqualTo("FileName"));
            Assert.That(viewModel.CreatedMapping.DocumentPropertyName, Is.Null);
            Assert.That(viewModel.CreatedMapping.MetaFieldValue, Is.Null);
        });
    }

    #endregion

    #region CancelCommand Tests

    [Test]
    public void CancelCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        var canExecute = viewModel.CancelCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void CancelCommand_Execute_ClearsCreatedMapping()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedMapping, Is.Null);
    }

    [Test]
    public void CancelCommand_Execute_RaisesRequestCloseEvent()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var eventRaised = false;
        viewModel.RequestClose += (sender, args) => eventRaised = true;

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(eventRaised, Is.True);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void CompleteWorkflow_AddDocumentPropertyMapping_WorksCorrectly()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act - Step 1: Select metadata field
        viewModel.SelectedMetaFieldName = "ProjectName";

        // Act - Step 2: Select mapping source (already DocumentProperty by default)
        Assert.That(viewModel.SelectedMappingSource, Is.EqualTo(MappingSourceType.DocumentProperty));

        // Act - Step 3: Select document property
        viewModel.SelectedDocumentProperty = "Name";

        // Assert - Step 3: OK button should be enabled
        Assert.That(viewModel.OkCommand.CanExecute(null), Is.True);

        // Act - Step 4: Click OK
        viewModel.OkCommand.Execute(null);

        // Assert - Step 4: Mapping is created correctly
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedMapping, Is.Not.Null);
            Assert.That(viewModel.CreatedMapping.MetaFieldName, Is.EqualTo("ProjectName"));
            Assert.That(viewModel.CreatedMapping.DocumentPropertyName, Is.EqualTo("Name"));
        });
    }

    [Test]
    public void CompleteWorkflow_AddStaticValueMapping_WorksCorrectly()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act - Step 1: Select metadata field
        viewModel.SelectedMetaFieldName = "Status";

        // Act - Step 2: Switch to static value
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;

        // Note: HasErrors will be true here because StaticValue is empty
        // This is expected behavior - validation happens on mode switch

        // Act - Step 3: Enter static value
        viewModel.StaticValue = "For Review";

        // Assert - Step 3: OK button enabled and no errors
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.HasErrors, Is.False, "Should have no errors after entering value");
            Assert.That(viewModel.OkCommand.CanExecute(null), Is.True);
        });

        // Act - Step 4: Click OK
        viewModel.OkCommand.Execute(null);

        // Assert - Step 4: Mapping created
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedMapping.MetaFieldName, Is.EqualTo("Status"));
            Assert.That(viewModel.CreatedMapping.MetaFieldValue, Is.EqualTo("For Review"));
        });
    }

    [Test]
    public void CompleteWorkflow_SwitchBetweenMappingTypes_WorksCorrectly()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMetaFieldName = "ProjectNumber";

        // Act - Start with DocumentProperty (default)
        Assert.That(viewModel.SelectedMappingSource, Is.EqualTo(MappingSourceType.DocumentProperty));

        // Act - Switch to StaticValue
        viewModel.SelectedMappingSource = MappingSourceType.StaticValue;
        viewModel.StaticValue = "PRJ-001";

        // Assert - Can execute with static value
        Assert.That(viewModel.OkCommand.CanExecute(null), Is.True);

        // Act - Switch to FileProperty
        viewModel.SelectedMappingSource = MappingSourceType.FileProperty;
        
        // Assert - Static value errors cleared, file property selected
        Assert.That(viewModel.HasErrors, Is.False);
        Assert.That(viewModel.SelectedFileProperty, Is.Not.Null);
        Assert.That(viewModel.OkCommand.CanExecute(null), Is.True);
    }

    #endregion

    #region Helper Methods

    private MetaDataMappingDialogViewModel CreateViewModel()
    {
        return new MetaDataMappingDialogViewModel(
            _availableMetaFields,
            _availableDocumentProperties,
            _mockMessageStore.Object);
    }

    #endregion
}
