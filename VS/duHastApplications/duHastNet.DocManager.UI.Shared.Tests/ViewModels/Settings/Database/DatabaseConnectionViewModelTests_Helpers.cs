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
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.Database;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.Database;

/// <summary>
/// Tests for DatabaseConnectionViewModel - Helper methods and validation
/// This partial test class covers helper method functionality including:
/// - UpdateButtonStates
/// - Property change handlers (OnDatabasePathChanged, OnIsConnectedChanged, OnIsBusyChanged)
/// - Button state management
/// </summary>
[TestFixture]
public class DatabaseConnectionViewModelTests_Helpers
{
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private Mock<IMessageStore> _mockMessageStore;
    private Mock<IManager> _mockManager;
    private Mock<IDialogService> _mockDialogService;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _mockDocManagerApi = new Mock<IDocManagerApi>();
        _mockMessageStore = new Mock<IMessageStore>();
        _mockManager = new Mock<IManager>();
        _mockDialogService = new Mock<IDialogService>();

        // Create unique test directory
        _testDirectory = Path.Combine(Path.GetTempPath(), "DatabaseConnectionViewModelTests_Helpers", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region UpdateButtonStates Tests

    [Test]
    public void UpdateButtonStates_WithNoDatabasePath_DisablesConnectAndImportExport()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act - setting DatabasePath to empty triggers UpdateButtonStates
        viewModel.DatabasePath = "";

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnectDatabaseEnabled, Is.False, "Connect should be disabled - no file exists");
            Assert.That(viewModel.IsBrowseEnabled, Is.True, "Browse should always be enabled when not busy");
            Assert.That(viewModel.IsImportExportEnabled, Is.False, "ImportExport should be disabled - not connected");
        });
    }

    [Test]
    public void UpdateButtonStates_WithValidPathButFileDoesNotExist_EnablesCreateOnly()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var nonExistentPath = Path.Combine(_testDirectory, "nonexistent.db");

        // Act
        viewModel.DatabasePath = nonExistentPath;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsCreateDatabaseEnabled, Is.True);
            Assert.That(viewModel.IsConnectDatabaseEnabled, Is.False);
            Assert.That(viewModel.IsBrowseEnabled, Is.True);
        });
    }

    [Test]
    public void UpdateButtonStates_WithExistingFile_EnablesBothCreateAndConnect()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var existingFilePath = Path.Combine(_testDirectory, "existing.db");
        File.WriteAllText(existingFilePath, "test content");

        // Act
        viewModel.DatabasePath = existingFilePath;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsCreateDatabaseEnabled, Is.True);
            Assert.That(viewModel.IsConnectDatabaseEnabled, Is.True);
            Assert.That(viewModel.IsBrowseEnabled, Is.True);
        });
    }

    [Test]
    public void UpdateButtonStates_WhenBusy_DisablesAllButtons()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var existingFilePath = Path.Combine(_testDirectory, "existing.db");
        File.WriteAllText(existingFilePath, "test content");
        viewModel.DatabasePath = existingFilePath;

        // Act
        viewModel.IsBusy = true;

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsCreateDatabaseEnabled, Is.False);
            Assert.That(viewModel.IsConnectDatabaseEnabled, Is.False);
            Assert.That(viewModel.IsBrowseEnabled, Is.False);
            Assert.That(viewModel.IsImportExportEnabled, Is.False);
        });
    }

    [Test]
    public void UpdateButtonStates_WhenConnected_EnablesImportExport()
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

        // IsConnected is true from initialization

        // Act - trigger UpdateButtonStates
        viewModel.DatabasePath = @"C:\Test\db.db";

        // Assert
        Assert.That(viewModel.IsImportExportEnabled, Is.True);
    }

    #endregion

    #region OnDatabasePathChanged Tests

    [Test]
    public void OnDatabasePathChanged_TriggersValidation()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var validationTriggered = false;
        viewModel.ErrorsChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.DatabasePath))
                validationTriggered = true;
        };

        // Act
        viewModel.DatabasePath = @"C:\Test\new.db";

        // Assert
        Assert.That(validationTriggered, Is.True);
    }

    #endregion

    #region OnIsConnectedChanged Tests

    [Test]
    public void OnIsConnectedChanged_RevalidatesDatabasePath()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.DatabasePath = @"C:\Test\db.db";

        var validationTriggered = false;
        viewModel.ErrorsChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.DatabasePath))
                validationTriggered = true;
        };

        // Act
        viewModel.IsConnected = true;

        // Assert
        Assert.That(validationTriggered, Is.True);
    }

    [Test]
    public void OnIsConnectedChanged_UpdatesButtonStates()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.DatabasePath = @"C:\Test\db.db";

        // Initially not connected, ImportExport disabled
        Assert.That(viewModel.IsImportExportEnabled, Is.False);

        // Act
        viewModel.IsConnected = true;

        // Assert - ImportExport now enabled
        Assert.That(viewModel.IsImportExportEnabled, Is.True);
    }

    [Test]
    public void OnIsConnectedChanged_NotifiesIsDatabaseReady()
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
            if (args.PropertyName == nameof(viewModel.IsDatabaseReady))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.IsConnected = true;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    #endregion

    #region OnIsBusyChanged Tests

    [Test]
    public void OnIsBusyChanged_UpdatesButtonStates()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var existingFilePath = Path.Combine(_testDirectory, "existing.db");
        File.WriteAllText(existingFilePath, "test content");
        viewModel.DatabasePath = existingFilePath;

        // Initially not busy, buttons enabled
        Assert.That(viewModel.IsCreateDatabaseEnabled, Is.True);
        Assert.That(viewModel.IsBrowseEnabled, Is.True);

        // Act
        viewModel.IsBusy = true;

        // Assert - buttons disabled during busy
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsCreateDatabaseEnabled, Is.False);
            Assert.That(viewModel.IsBrowseEnabled, Is.False);
        });
    }

    [Test]
    public void OnIsBusyChanged_WhenSetToFalse_ReEnablesButtons()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var existingFilePath = Path.Combine(_testDirectory, "existing.db");
        File.WriteAllText(existingFilePath, "test content");
        viewModel.DatabasePath = existingFilePath;

        viewModel.IsBusy = true;
        Assert.That(viewModel.IsCreateDatabaseEnabled, Is.False);

        // Act
        viewModel.IsBusy = false;

        // Assert - buttons re-enabled
        Assert.That(viewModel.IsCreateDatabaseEnabled, Is.True);
    }

    #endregion

    #region Button State Integration Tests

    [Test]
    public void ButtonStates_CompleteWorkflow_UpdatesCorrectly()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var testDbPath = Path.Combine(_testDirectory, "workflow.db");

        // Act & Assert - Step 1: Set path (file doesn't exist yet)
        viewModel.DatabasePath = testDbPath;
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsCreateDatabaseEnabled, Is.True, "Should enable Create when path set");
            Assert.That(viewModel.IsConnectDatabaseEnabled, Is.False, "Should disable Connect when file doesn't exist");
        });

        // Act & Assert - Step 2: Simulate busy state
        viewModel.IsBusy = true;
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsCreateDatabaseEnabled, Is.False, "Should disable all when busy");
            Assert.That(viewModel.IsBrowseEnabled, Is.False, "Should disable browse when busy");
        });

        // Act & Assert - Step 3: Complete operation
        viewModel.IsBusy = false;
        Assert.That(viewModel.IsCreateDatabaseEnabled, Is.True, "Should re-enable after busy");

        // Act & Assert - Step 4: Simulate connection
        viewModel.IsConnected = true;
        Assert.That(viewModel.IsImportExportEnabled, Is.True, "Should enable ImportExport when connected");
    }

    #endregion
}
