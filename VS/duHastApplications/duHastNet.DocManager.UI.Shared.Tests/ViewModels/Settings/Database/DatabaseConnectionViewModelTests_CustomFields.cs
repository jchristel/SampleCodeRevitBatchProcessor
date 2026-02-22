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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Models.Results;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.Database;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.Database;

/// <summary>
/// Tests for DatabaseConnectionViewModel - Custom Fields functionality
/// This partial test class covers custom field-related functionality including:
/// - Custom field initialization
/// - Custom field collection management
/// - AddCustomFieldCommand CanExecute logic
/// - RemoveCustomFieldCommand CanExecute logic
/// - ToggleCustomFieldActiveCommand CanExecute logic
/// - UpdateDatabaseSchemaCommand CanExecute logic
/// - Pending changes tracking
/// - Duplicate field detection
/// </summary>
[TestFixture]
public class DatabaseConnectionViewModelTests_CustomFields
{
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private Mock<IMessageStore> _mockMessageStore;
    private Mock<IManager> _mockManager;
    private Mock<IDialogService> _mockDialogService;

    [SetUp]
    public void Setup()
    {
        _mockDocManagerApi = new Mock<IDocManagerApi>();
        _mockMessageStore = new Mock<IMessageStore>();
        _mockManager = new Mock<IManager>();
        _mockDialogService = new Mock<IDialogService>();
    }

    #region Custom Fields Initialization Tests

    [Test]
    public void CustomFields_WhenNotConnected_CollectionIsEmpty()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        // Act
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Assert
        Assert.That(viewModel.CustomFields, Is.Empty);
    }

    [Test]
    public void CustomFields_WhenConnectedWithData_LoadsFromManager()
    {
        // Arrange
        var customFieldDefinitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition { PropertyName = "DisciplineCode", IsActive = true },
            new CustomFieldDefinition { PropertyName = "ProjectPhase", IsActive = true },
            new CustomFieldDefinition { PropertyName = "Contractor", IsActive = false }
        };

        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);
        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(customFieldDefinitions);

        // Act
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CustomFields, Has.Count.EqualTo(3));
            Assert.That(viewModel.CustomFields[0].PropertyName, Is.EqualTo("DisciplineCode"));
            Assert.That(viewModel.CustomFields[1].PropertyName, Is.EqualTo("ProjectPhase"));
            Assert.That(viewModel.CustomFields[2].PropertyName, Is.EqualTo("Contractor"));
        });
    }

    #endregion

    #region IsCustomFieldsExpanded Tests

    [Test]
    public void IsCustomFieldsExpanded_WhenNotConnected_ReturnsFalse()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var isExpanded = viewModel.IsCustomFieldsExpanded;

        // Assert
        Assert.That(isExpanded, Is.False);
    }

    [Test]
    public void IsCustomFieldsExpanded_WhenConnected_ReturnsTrue()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var isExpanded = viewModel.IsCustomFieldsExpanded;

        // Assert
        Assert.That(isExpanded, Is.True);
    }

    #endregion

    #region HasPendingCustomFieldChanges Tests

    [Test]
    public void HasPendingCustomFieldChanges_InitiallyFalse()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        // Act
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Assert
        Assert.That(viewModel.HasPendingCustomFieldChanges, Is.False);
    }

    [Test]
    public void HasPendingCustomFieldChanges_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var propertyChangedRaised = false;
        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.HasPendingCustomFieldChanges))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.HasPendingCustomFieldChanges = true;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(propertyChangedRaised, Is.True);
            Assert.That(viewModel.HasPendingCustomFieldChanges, Is.True);
        });
    }

    #endregion

    #region AddCustomFieldCommand CanExecute Tests

    [Test]
    public void AddCustomFieldCommand_WhenNotConnected_CannotExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var canExecute = viewModel.AddCustomFieldCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void AddCustomFieldCommand_WhenConnected_CanExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var canExecute = viewModel.AddCustomFieldCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    #endregion

    #region RemoveCustomFieldCommand CanExecute Tests

    [Test]
    public void RemoveCustomFieldCommand_WhenNotConnected_CannotExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var canExecute = viewModel.RemoveCustomFieldCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void RemoveCustomFieldCommand_WhenConnectedButNoSelection_CannotExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // SelectedCustomField is null by default

        // Act
        var canExecute = viewModel.RemoveCustomFieldCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    #endregion

    #region ToggleCustomFieldActiveCommand CanExecute Tests

    [Test]
    public void ToggleCustomFieldActiveCommand_WhenNotConnected_CannotExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var canExecute = viewModel.ToggleCustomFieldActiveCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void ToggleCustomFieldActiveCommand_WhenConnectedButNoSelection_CannotExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // SelectedCustomField is null by default

        // Act
        var canExecute = viewModel.ToggleCustomFieldActiveCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    #endregion

    #region UpdateDatabaseSchemaCommand CanExecute Tests

    [Test]
    public void UpdateDatabaseSchemaCommand_WhenNotConnected_CannotExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var canExecute = viewModel.UpdateDatabaseSchemaCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void UpdateDatabaseSchemaCommand_WhenConnectedButNoPendingChanges_CannotExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // HasPendingCustomFieldChanges is false by default

        // Act
        var canExecute = viewModel.UpdateDatabaseSchemaCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void UpdateDatabaseSchemaCommand_WhenConnectedWithPendingChanges_CanExecute()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.HasPendingCustomFieldChanges = true;

        // Act
        var canExecute = viewModel.UpdateDatabaseSchemaCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    #endregion

    #region IsDuplicateCustomField Tests

    [Test]
    public void IsDuplicateCustomField_WithNoDuplicates_ReturnsFalse()
    {
        // Arrange
        var customFieldDefinitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition { PropertyName = "DisciplineCode", IsActive = true },
            new CustomFieldDefinition { PropertyName = "ProjectPhase", IsActive = true }
        };

        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);
        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(customFieldDefinitions);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var isDuplicate = viewModel.IsDuplicateCustomField("NewField");

        // Assert
        Assert.That(isDuplicate, Is.False);
    }

    [Test]
    public void IsDuplicateCustomField_WithDuplicate_ReturnsTrue()
    {
        // Arrange
        var customFieldDefinitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition { PropertyName = "DisciplineCode", IsActive = true },
            new CustomFieldDefinition { PropertyName = "ProjectPhase", IsActive = true }
        };

        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);
        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(customFieldDefinitions);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var isDuplicate = viewModel.IsDuplicateCustomField("DisciplineCode");

        // Assert
        Assert.That(isDuplicate, Is.True);
    }

    [Test]
    public void IsDuplicateCustomField_CaseInsensitive_ReturnsTrue()
    {
        // Arrange
        var customFieldDefinitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition { PropertyName = "DisciplineCode", IsActive = true }
        };

        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);
        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(customFieldDefinitions);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var isDuplicate = viewModel.IsDuplicateCustomField("disciplinecode");

        // Assert
        Assert.That(isDuplicate, Is.True);
    }

    #endregion
}
