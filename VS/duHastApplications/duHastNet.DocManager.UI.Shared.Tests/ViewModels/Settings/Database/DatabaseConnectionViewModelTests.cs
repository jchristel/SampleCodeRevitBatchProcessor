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

using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Models.Results;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.Database;
using Moq;
using NUnit.Framework;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.Database;

/// <summary>
/// Tests for DatabaseConnectionViewModel - Core functionality and initialization
/// This test class covers constructor, initialization, and core properties
/// Additional functionality is tested in partial test classes:
/// - DatabaseConnectionViewModelTests_Commands: Command execution tests
/// - DatabaseConnectionViewModelTests_CustomFields: Custom fields functionality tests
/// </summary>
[TestFixture]
public class DatabaseConnectionViewModelTests
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

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidDependencies_InitializesSuccessfully()
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
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.DatabasePath, Is.EqualTo(string.Empty));
            Assert.That(viewModel.IsConnected, Is.False);
            Assert.That(viewModel.StatusMessage, Is.EqualTo("Ready"));
            Assert.That(viewModel.IsBusy, Is.False);
        });
    }

    [Test]
    public void Constructor_WithExistingDatabasePath_LoadsPathFromApi()
    {
        // Arrange
        var existingPath = @"C:\TestData\existing.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(existingPath);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);

        // Act
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.DatabasePath, Is.EqualTo(existingPath));
            Assert.That(viewModel.IsConnected, Is.True);
        });
    }

    [Test]
    public void Constructor_WithConnectedDatabaseAndLoadedData_InitializesCustomFields()
    {
        // Arrange
        var existingPath = @"C:\TestData\connected.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(existingPath);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);
        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(new List<CustomFieldDefinition>());

        // Act
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.True);
            Assert.That(viewModel.CustomFields, Is.Not.Null);
        });
    }

    #endregion

    #region Property Tests

    [Test]
    public void DatabasePath_WhenSet_TriggersPropertyChanged()
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
            if (args.PropertyName == nameof(viewModel.DatabasePath))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.DatabasePath = @"C:\TestData\new.db";

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(propertyChangedRaised, Is.True);
            Assert.That(viewModel.DatabasePath, Is.EqualTo(@"C:\TestData\new.db"));
        });
    }

    [Test]
    public void IsConnected_WhenSet_TriggersPropertyChanged()
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
            if (args.PropertyName == nameof(viewModel.IsConnected))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.IsConnected = true;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(propertyChangedRaised, Is.True);
            Assert.That(viewModel.IsConnected, Is.True);
        });
    }

    [Test]
    public void IsBusy_WhenSet_UpdatesButtonStates()
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
        viewModel.IsBusy = true;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsBusy, Is.True);
            Assert.That(viewModel.IsCreateDatabaseEnabled, Is.False);
            Assert.That(viewModel.IsConnectDatabaseEnabled, Is.False);
            Assert.That(viewModel.IsBrowseEnabled, Is.False);
        });
    }

    #endregion

    #region Computed Property Tests

    [Test]
    public void IsDatabaseReady_ReflectsApiState()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var isDatabaseReady = viewModel.IsDatabaseReady;

        // Assert
        Assert.That(isDatabaseReady, Is.True);
        _mockDocManagerApi.Verify(x => x.IsDatabaseReady(), Times.Once);
    }

    [Test]
    public void CurrentDatabasePath_ReturnsApiDatabasePath()
    {
        // Arrange
        var expectedPath = @"C:\TestData\current.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(expectedPath);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var currentPath = viewModel.CurrentDatabasePath;

        // Assert
        Assert.That(currentPath, Is.EqualTo(expectedPath));
    }

    [Test]
    public void IsDataLoaded_ReflectsManagerState()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);
        
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        var isDataLoaded = viewModel.IsDataLoaded;

        // Assert
        Assert.That(isDataLoaded, Is.True);
    }

    #endregion

    #region Validation Tests

    [Test]
    public void Validation_WhenNotConnected_ReturnsError()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.DatabasePath = @"C:\TestData\test.db";

        // Act
        var hasErrors = viewModel.HasErrors;

        // Assert
        Assert.That(hasErrors, Is.True);
    }

    [Test]
    public void Validation_WhenConnected_PassesValidation()
    {
        // Arrange
        var validPath = @"C:\TestData\valid.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(validPath);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);
        
        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // IsConnected should be true from initialization
        viewModel.DatabasePath = validPath;

        // Act
        var hasErrors = viewModel.HasErrors;

        // Assert
        Assert.That(hasErrors, Is.False);
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
        var existingPath = @"C:\TestData\connected.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(existingPath);
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
}
