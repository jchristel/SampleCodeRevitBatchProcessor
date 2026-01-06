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
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CloudDocManager.CloudProviderControls;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CloudDocManager.CloudProviderControls;

/// <summary>
/// Tests for AconexMetadataControlViewModel - ListView functionality
/// Covers SelectedMapping, Add/Remove/Edit commands, and helper methods
/// </summary>
[TestFixture]
public partial class AconexMetadataControlViewModelTests
{
    #region SelectedMapping Property Tests

    [Test]
    public void SelectedMapping_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };
        var mappingViewModel = new MetaDataMapViewModel(mapping);
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.SelectedMapping))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.SelectedMapping = mappingViewModel;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void SelectedMapping_WhenSet_NotifiesEditCommandCanExecuteChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };
        var mappingViewModel = new MetaDataMapViewModel(mapping);

        // Initially should not be executable
        Assert.That(viewModel.EditMetadataMappingCommand.CanExecute(null), Is.False);

        // Act
        viewModel.SelectedMapping = mappingViewModel;

        // Assert
        Assert.That(viewModel.EditMetadataMappingCommand.CanExecute(null), Is.True);
    }

    [Test]
    public void SelectedMapping_WhenSetToNull_DisablesEditCommand()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };
        var mappingViewModel = new MetaDataMapViewModel(mapping);
        viewModel.SelectedMapping = mappingViewModel;

        // Act
        viewModel.SelectedMapping = null;

        // Assert
        Assert.That(viewModel.EditMetadataMappingCommand.CanExecute(null), Is.False);
    }

    #endregion

    #region OnMappingsChanged Event Handler Tests

    [Test]
    public void OnMappingsChanged_WhenTriggered_RefreshesMetaDataMappingsCollection()
    {
        // Arrange
        var mapping1 = new MetaDataMap { MetaFieldName = "Field1", DocumentPropertyName = "Prop1" };
        var mapping2 = new MetaDataMap { MetaFieldName = "Field2", DocumentPropertyName = "Prop2" };
        var mapping3 = new MetaDataMap { MetaFieldName = "Field3", DocumentPropertyName = "Prop3" };
        
        var initialMappings = new List<MetaDataMap> { mapping1, mapping2 };
        var updatedMappings = new List<MetaDataMap> { mapping1, mapping2, mapping3 };

        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(initialMappings);

        // Use a real CloudDocumentManager instead of a mock for event raising
        // We cannot use Moq's Raise() on the mocked CloudDocumentManager because
        // the event subscription is through a property chain (_manager.CloudDocManager.MappingsChanged)
        // and Moq cannot raise events through property expressions
        var realCloudDocManager = new duHastNet.DocManager.Core.Models.CloudDocManager.CloudDocumentManager();
        _mockManager.Setup(x => x.CloudDocManager).Returns(realCloudDocManager);

        var viewModel = CreateViewModel();

        // Verify initial state
        Assert.That(viewModel.MetaDataMappings, Has.Count.EqualTo(2));

        // Update the mock to return new mappings
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(updatedMappings);

        // Act - Simulate external change by calling RaiseMappingsChanged
        realCloudDocManager.RaiseMappingsChanged();

        // Assert
        Assert.That(viewModel.MetaDataMappings, Has.Count.EqualTo(3));
    }

    #endregion

    #region AddMetadataMapping Command Tests

    [Test]
    public void AddMetadataMappingCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act & Assert
        Assert.That(viewModel.AddMetadataMappingCommand.CanExecute(null), Is.True);
    }

    [Test]
    public void AddMetadataMappingCommand_WithNoTemplateLoaded_ShowsWarningMessage()
    {
        // Arrange
        _mockAconexMapper.Setup(x => x.AvailableFields).Returns(new List<string>());
        var viewModel = CreateViewModel();

        // Act
        viewModel.AddMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Please select and load a template file")),
            MessageTypes.Warning,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public void AddMetadataMappingCommand_WithAllFieldsMapped_ShowsInformationMessage()
    {
        // Arrange
        var availableFields = new List<string> { "Field1", "Field2" };
        var existingMappings = new List<MetaDataMap>
        {
            new MetaDataMap { MetaFieldName = "Field1", DocumentPropertyName = "Prop1" },
            new MetaDataMap { MetaFieldName = "Field2", DocumentPropertyName = "Prop2" }
        };

        _mockAconexMapper.Setup(x => x.AvailableFields).Returns(availableFields);
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(existingMappings);

        var viewModel = CreateViewModel();

        // Act
        viewModel.AddMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("All template fields are already mapped")),
            MessageTypes.Information,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public void AddMetadataMappingCommand_WithException_ShowsErrorMessage()
    {
        // Arrange
        var availableFields = new List<string> { "Field1" };
        _mockAconexMapper.Setup(x => x.AvailableFields).Returns(availableFields);
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap>());
        _mockAconexMapper.Setup(x => x.AddMapper(It.IsAny<MetaDataMap>()))
            .Throws(new InvalidOperationException("Test exception"));

        var viewModel = CreateViewModel();

        // Act
        viewModel.AddMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Error adding mapping")),
            MessageTypes.Error,
            It.IsAny<int?>()), Times.Once);
    }

    #endregion

    #region RemoveMetadataMapping Command Tests

    [Test]
    public void RemoveMetadataMappingCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act & Assert
        Assert.That(viewModel.RemoveMetadataMappingCommand.CanExecute(null), Is.True);
    }

    [Test]
    public void RemoveMetadataMappingCommand_WithNoSelection_ShowsWarningMessage()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMapping = null;

        // Act
        viewModel.RemoveMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Please select a mapping to remove")),
            MessageTypes.Warning,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public void RemoveMetadataMappingCommand_WithValidSelection_RemovesMapping()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };

        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap> { mapping });
        
        var viewModel = CreateViewModel();
        
        // Select the actual mapping from the collection
        viewModel.SelectedMapping = viewModel.MetaDataMappings[0];

        // Act
        viewModel.RemoveMetadataMappingCommand.Execute(null);

        // Assert
        _mockAconexMapper.Verify(x => x.RemoveMapper(mapping), Times.Once);
    }

    [Test]
    public void RemoveMetadataMappingCommand_WithValidSelection_RemovesFromCollection()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };

        // Setup the mapper to initially have this mapping
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap> { mapping });
        
        var viewModel = CreateViewModel();
        
        // Verify the mapping is in the collection after creation
        Assert.That(viewModel.MetaDataMappings, Has.Count.EqualTo(1));
        
        // Select the actual mapping from the collection (not a new instance)
        viewModel.SelectedMapping = viewModel.MetaDataMappings[0];

        // Act
        viewModel.RemoveMetadataMappingCommand.Execute(null);

        // Assert - Collection should now be empty
        Assert.That(viewModel.MetaDataMappings, Is.Empty);
    }

    [Test]
    public void RemoveMetadataMappingCommand_WithValidSelection_ClearsSelection()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };

        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap> { mapping });
        
        var viewModel = CreateViewModel();
        
        // Select the actual mapping from the collection
        viewModel.SelectedMapping = viewModel.MetaDataMappings[0];

        // Act
        viewModel.RemoveMetadataMappingCommand.Execute(null);

        // Assert
        Assert.That(viewModel.SelectedMapping, Is.Null);
    }

    [Test]
    public void RemoveMetadataMappingCommand_WithValidSelection_ShowsSuccessMessage()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };

        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap> { mapping });
        
        var viewModel = CreateViewModel();
        
        // Select the actual mapping from the collection
        viewModel.SelectedMapping = viewModel.MetaDataMappings[0];

        // Act
        viewModel.RemoveMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Document Number") && s.Contains("removed successfully")),
            MessageTypes.Information,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public void RemoveMetadataMappingCommand_WithException_ShowsErrorMessage()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };

        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap> { mapping });
        _mockAconexMapper.Setup(x => x.RemoveMapper(It.IsAny<MetaDataMap>()))
            .Throws(new InvalidOperationException("Test exception"));

        var viewModel = CreateViewModel();
        
        // Select the actual mapping from the collection
        viewModel.SelectedMapping = viewModel.MetaDataMappings[0];

        // Act
        viewModel.RemoveMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Failed to remove mapping")),
            MessageTypes.Error,
            It.IsAny<int?>()), Times.Once);
    }

    #endregion

    #region EditMetadataMapping Command Tests

    [Test]
    public void CanEditMetadataMapping_WithNoSelection_ReturnsFalse()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.SelectedMapping = null;

        // Act
        var canExecute = viewModel.EditMetadataMappingCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void CanEditMetadataMapping_WithSelection_ReturnsTrue()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };
        var mappingViewModel = new MetaDataMapViewModel(mapping);

        var viewModel = CreateViewModel();
        viewModel.SelectedMapping = mappingViewModel;

        // Act
        var canExecute = viewModel.EditMetadataMappingCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void EditMetadataMappingCommand_WithNoTemplateLoaded_ShowsWarningMessage()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };
        var mappingViewModel = new MetaDataMapViewModel(mapping);

        _mockAconexMapper.Setup(x => x.AvailableFields).Returns(new List<string>());

        var viewModel = CreateViewModel();
        viewModel.SelectedMapping = mappingViewModel;

        // Act
        viewModel.EditMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Please select and load a template file before editing")),
            MessageTypes.Warning,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public void EditMetadataMappingCommand_WithException_ShowsErrorMessage()
    {
        // Arrange
        var mapping = new MetaDataMap
        {
            MetaFieldName = "Document Number",
            DocumentPropertyName = "Number"
        };
        var mappingViewModel = new MetaDataMapViewModel(mapping);

        var availableFields = new List<string> { "Field1", "Field2" };
        _mockAconexMapper.Setup(x => x.AvailableFields).Returns(availableFields);
        _mockAconexMapper.Setup(x => x.RemoveMapper(It.IsAny<MetaDataMap>()))
            .Throws(new InvalidOperationException("Test exception"));

        var viewModel = CreateViewModel();
        viewModel.SelectedMapping = mappingViewModel;

        // Act
        viewModel.EditMetadataMappingCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Error editing mapping")),
            MessageTypes.Error,
            It.IsAny<int?>()), Times.Once);
    }

    #endregion

    #region LoadMappingsFromModel Helper Method Tests

    [Test]
    public void LoadMappingsFromModel_WithEmptyMappings_ClearsCollection()
    {
        // Arrange
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap>());
        
        // Use a real CloudDocumentManager instead of a mock for event raising
        var realCloudDocManager = new duHastNet.DocManager.Core.Models.CloudDocManager.CloudDocumentManager();
        _mockManager.Setup(x => x.CloudDocManager).Returns(realCloudDocManager);
        
        var viewModel = CreateViewModel();

        // Add some dummy mappings first
        viewModel.MetaDataMappings.Add(new MetaDataMapViewModel(
            new MetaDataMap { MetaFieldName = "Test", DocumentPropertyName = "Test" }));

        // Update mock to return empty list
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap>());

        // Act - Trigger reload by calling RaiseMappingsChanged
        realCloudDocManager.RaiseMappingsChanged();

        // Assert
        Assert.That(viewModel.MetaDataMappings, Is.Empty);
    }

    [Test]
    public void LoadMappingsFromModel_WithMultipleMappings_LoadsAll()
    {
        // Arrange
        var mapping1 = new MetaDataMap { MetaFieldName = "Field1", DocumentPropertyName = "Prop1" };
        var mapping2 = new MetaDataMap { MetaFieldName = "Field2", DocumentPropertyName = "Prop2" };
        var mapping3 = new MetaDataMap { MetaFieldName = "Field3", DocumentPropertyName = "Prop3" };

        var mappings = new List<MetaDataMap> { mapping1, mapping2, mapping3 };
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(mappings);

        // Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.MetaDataMappings, Has.Count.EqualTo(3));
            Assert.That(viewModel.MetaDataMappings[0].MetaFieldName, Is.EqualTo("Field1"));
            Assert.That(viewModel.MetaDataMappings[1].MetaFieldName, Is.EqualTo("Field2"));
            Assert.That(viewModel.MetaDataMappings[2].MetaFieldName, Is.EqualTo("Field3"));
        });
    }

    [Test]
    public void LoadMappingsFromModel_ClearsExistingMappingsBeforeReload()
    {
        // Arrange
        var initialMapping = new MetaDataMap { MetaFieldName = "Initial", DocumentPropertyName = "Prop" };
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap> { initialMapping });

        // Use a real CloudDocumentManager instead of a mock for event raising
        var realCloudDocManager = new duHastNet.DocManager.Core.Models.CloudDocManager.CloudDocumentManager();
        _mockManager.Setup(x => x.CloudDocManager).Returns(realCloudDocManager);

        var viewModel = CreateViewModel();
        var initialCount = viewModel.MetaDataMappings.Count;

        // Update mock with new mappings
        var newMapping = new MetaDataMap { MetaFieldName = "New", DocumentPropertyName = "NewProp" };
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap> { newMapping });

        // Act - Trigger reload by calling RaiseMappingsChanged
        realCloudDocManager.RaiseMappingsChanged();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.MetaDataMappings, Has.Count.EqualTo(1));
            Assert.That(viewModel.MetaDataMappings[0].MetaFieldName, Is.EqualTo("New"));
        });
    }

    #endregion

    #region GetAvailableDocumentProperties Helper Method Tests

    [Test]
    public void GetAvailableDocumentProperties_IncludesStandardProperties()
    {
        // Arrange
        _mockManager.Setup(x => x.GetActiveCustomFieldDefinitions())
            .Returns(new List<CustomFieldDefinition>());
        var viewModel = CreateViewModel();
        // Setup to access protected method through reflection
        var method = typeof(AconexMetadataControlViewModel).GetMethod(
            "GetAvailableDocumentProperties",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        // Act
        var result = method?.Invoke(viewModel, null) as List<string>;
        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Does.Contain("Number"));
        Assert.That(result, Does.Contain("Name"));
        Assert.That(result, Does.Contain("Revision"));
        Assert.That(result, Does.Contain("RevisionDate"));
        Assert.That(result, Does.Contain("RevisionDescription"));
    }

    [Test]
    public void GetAvailableDocumentProperties_IncludesActiveCustomFields()
    {
        // Arrange
        var customField1 = new CustomFieldDefinition
        {
            PropertyName = "CustomField1",
            IsActive = true
        };
        var customField2 = new CustomFieldDefinition
        {
            PropertyName = "CustomField2",
            IsActive = true
        };

        _mockManager.Setup(x => x.GetActiveCustomFieldDefinitions())
            .Returns(new List<CustomFieldDefinition> { customField1, customField2 });

        var viewModel = CreateViewModel();

        // Setup to access protected method through reflection
        var method = typeof(AconexMetadataControlViewModel).GetMethod(
            "GetAvailableDocumentProperties",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        // Act
        var result = method?.Invoke(viewModel, null) as List<string>;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Does.Contain("CustomField1"));
            Assert.That(result, Does.Contain("CustomField2"));
        });
    }

    [Test]
    public void GetAvailableDocumentProperties_CustomFieldsAreSorted()
    {
        // Arrange
        var customField1 = new CustomFieldDefinition
        {
            PropertyName = "ZCustomField",
            IsActive = true
        };
        var customField2 = new CustomFieldDefinition
        {
            PropertyName = "ACustomField",
            IsActive = true
        };
        var customField3 = new CustomFieldDefinition
        {
            PropertyName = "MCustomField",
            IsActive = true
        };

        _mockManager.Setup(x => x.GetActiveCustomFieldDefinitions())
            .Returns(new List<CustomFieldDefinition> 
            { 
                customField1, 
                customField2, 
                customField3 
            });

        var viewModel = CreateViewModel();

        // Setup to access protected method through reflection
        var method = typeof(AconexMetadataControlViewModel).GetMethod(
            "GetAvailableDocumentProperties",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        // Act
        var result = method?.Invoke(viewModel, null) as List<string>;

        // Assert
        Assert.That(result, Is.Not.Null);
        
        // Find the index of each custom field
        var indexA = result.IndexOf("ACustomField");
        var indexM = result.IndexOf("MCustomField");
        var indexZ = result.IndexOf("ZCustomField");

        // Verify they are in alphabetical order
        Assert.Multiple(() =>
        {
            Assert.That(indexA, Is.LessThan(indexM));
            Assert.That(indexM, Is.LessThan(indexZ));
        });
    }

    [Test]
    public void GetAvailableDocumentProperties_ExcludesInactiveCustomFields()
    {
        // Arrange
        var activeField = new CustomFieldDefinition
        {
            PropertyName = "ActiveField",
            IsActive = true
        };
        var inactiveField = new CustomFieldDefinition
        {
            PropertyName = "InactiveField",
            IsActive = false
        };

        // Setup to only return active fields (as GetActiveCustomFieldDefinitions should do)
        _mockManager.Setup(x => x.GetActiveCustomFieldDefinitions())
            .Returns(new List<CustomFieldDefinition> { activeField });

        var viewModel = CreateViewModel();

        // Setup to access protected method through reflection
        var method = typeof(AconexMetadataControlViewModel).GetMethod(
            "GetAvailableDocumentProperties",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        // Act
        var result = method?.Invoke(viewModel, null) as List<string>;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(result, Is.Not.Null);
            Assert.That(result, Does.Contain("ActiveField"));
            Assert.That(result, Does.Not.Contain("InactiveField"));
        });
    }

    #endregion
}
