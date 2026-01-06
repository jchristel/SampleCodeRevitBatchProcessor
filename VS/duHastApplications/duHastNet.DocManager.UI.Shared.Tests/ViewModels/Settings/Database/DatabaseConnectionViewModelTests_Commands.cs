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
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Models.Results;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.Database;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.Database;

/// <summary>
/// Tests for DatabaseConnectionViewModel - Command execution
/// This partial test class covers all command-related functionality including:
/// - CreateDatabaseAsync
/// - ConnectDatabaseAsync
/// - BrowseDatabaseAsync
/// - TestDatabaseAsync
/// - ImportDocumentsAsync / ExportDocumentsAsync
/// - ImportRevisionsAsync / ExportRevisionsAsync
/// </summary>
[TestFixture]
public class DatabaseConnectionViewModelTests_Commands
{
    private Mock<DocManagerApi> _mockDocManagerApi;
    private Mock<MessageStore> _mockMessageStore;
    private Mock<Manager> _mockManager;
    private Mock<IDialogService> _mockDialogService;

    [SetUp]
    public void Setup()
    {
        _mockDocManagerApi = new Mock<DocManagerApi>();
        _mockMessageStore = new Mock<MessageStore>();
        _mockManager = new Mock<Manager>();
        _mockDialogService = new Mock<IDialogService>();
    }

    #region CreateDatabaseAsync Tests

    [Test]
    public async Task CreateDatabaseAsync_WithValidPath_CreatesSuccessfully()
    {
        // Arrange
        var selectedPath = @"C:\TestData\new.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockDialogService.Setup(x => x.ShowSaveFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns(selectedPath);

        var setupResult = SetupResult.CreateSuccess(selectedPath);
        _mockDocManagerApi.Setup(x => x.SetupDatabaseAsync(
            It.Is<string>(s => s == selectedPath),
            It.IsAny<List<string>>(),
            It.Is<bool>(b => b == true)))
            .ReturnsAsync(setupResult);

        var loadResult = SetupResult.CreateSuccess(selectedPath);
        _mockDocManagerApi.Setup(x => x.LoadDataIntoManagerAsync(_mockManager.Object))
            .ReturnsAsync(loadResult);

        _mockManager.Setup(x => x.GetAllCustomPropertyNames())
            .Returns(new List<string>());

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        await viewModel.CreateDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.True);
            Assert.That(viewModel.DatabasePath, Is.EqualTo(selectedPath));
            Assert.That(viewModel.IsBusy, Is.False);
        });

        _mockDocManagerApi.Verify(x => x.SetupDatabaseAsync(
            It.Is<string>(s => s == selectedPath),
            It.IsAny<List<string>>(),
            It.Is<bool>(b => b == true)), Times.Once);
        _mockDocManagerApi.Verify(x => x.LoadDataIntoManagerAsync(_mockManager.Object), Times.Once);
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(msg => msg.Contains("Creating database")),
            MessageTypes.Information,
            It.IsAny<int>()), Times.Once);
    }

    [Test]
    public async Task CreateDatabaseAsync_WhenUserCancels_DoesNotCreateDatabase()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockDialogService.Setup(x => x.ShowSaveFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns((string)null); // User cancelled

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        await viewModel.CreateDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.False);
            Assert.That(viewModel.IsBusy, Is.False);
        });

        _mockDocManagerApi.Verify(x => x.SetupDatabaseAsync(
            It.IsAny<string>(),
            It.IsAny<List<string>>(),
            It.IsAny<bool>()), Times.Never);
    }

    [Test]
    public async Task CreateDatabaseAsync_WhenSetupFails_ShowsErrorMessage()
    {
        // Arrange
        var selectedPath = @"C:\TestData\invalid.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockDialogService.Setup(x => x.ShowSaveFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns(selectedPath);

        var setupResult = SetupResult.CreateFailure("Database path is invalid");
        _mockDocManagerApi.Setup(x => x.SetupDatabaseAsync(
            It.Is<string>(s => s == selectedPath),
            It.IsAny<List<string>>(),
            It.Is<bool>(b => b == true)))
            .ReturnsAsync(setupResult);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        await viewModel.CreateDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.False);
            Assert.That(viewModel.IsBusy, Is.False);
        });

        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(msg => msg.Contains("Failed to create database")),
            MessageTypes.Error,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public async Task CreateDatabaseAsync_WhenDataLoadFails_StillShowsConnected()
    {
        // Arrange
        var selectedPath = @"C:\TestData\new.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockDialogService.Setup(x => x.ShowSaveFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns(selectedPath);

        var setupResult = SetupResult.CreateSuccess(selectedPath);
        _mockDocManagerApi.Setup(x => x.SetupDatabaseAsync(
            It.Is<string>(s => s == selectedPath),
            It.IsAny<List<string>>(),
            It.Is<bool>(b => b == true)))
            .ReturnsAsync(setupResult);

        var loadResult = SetupResult.CreateFailure("Data load failed");
        _mockDocManagerApi.Setup(x => x.LoadDataIntoManagerAsync(_mockManager.Object))
            .ReturnsAsync(loadResult);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        await viewModel.CreateDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.True);
            Assert.That(viewModel.DatabasePath, Is.EqualTo(selectedPath));
        });
    }

    [Test]
    public async Task CreateDatabaseAsync_SetsBusyStateDuringOperation()
    {
        // Arrange
        var selectedPath = @"C:\TestData\new.db";
        var busyStateChanges = new List<bool>();

        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockDialogService.Setup(x => x.ShowSaveFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns(selectedPath);

        var setupResult = SetupResult.CreateSuccess(selectedPath);
        _mockDocManagerApi.Setup(x => x.SetupDatabaseAsync(
            It.Is<string>(s => s == selectedPath),
            It.IsAny<List<string>>(),
            It.Is<bool>(b => b == true)))
            .ReturnsAsync(setupResult);

        var loadResult = SetupResult.CreateSuccess(selectedPath);
        _mockDocManagerApi.Setup(x => x.LoadDataIntoManagerAsync(_mockManager.Object))
            .ReturnsAsync(loadResult);

        _mockManager.Setup(x => x.GetAllCustomPropertyNames())
            .Returns(new List<string>());

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.IsBusy))
                busyStateChanges.Add(viewModel.IsBusy);
        };

        // Act
        await viewModel.CreateDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(busyStateChanges, Has.Count.GreaterThanOrEqualTo(2));
            Assert.That(busyStateChanges[0], Is.True); // Set to true at start
            Assert.That(busyStateChanges[^1], Is.False); // Set to false at end
            Assert.That(viewModel.IsBusy, Is.False); // Final state is false
        });
    }

    #endregion

    #region ConnectDatabaseAsync Tests

    [Test]
    public async Task ConnectDatabaseAsync_WithValidPath_ConnectsSuccessfully()
    {
        // Arrange
        var databasePath = @"C:\TestData\existing.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var connectResult = SetupResult.CreateSuccess(databasePath);
        _mockDocManagerApi.Setup(x => x.ConnectDatabaseAsync(It.Is<string>(s => s == databasePath)))
            .ReturnsAsync(connectResult);

        var loadResult = SetupResult.CreateSuccess(databasePath);
        _mockDocManagerApi.Setup(x => x.LoadDataIntoManagerAsync(_mockManager.Object))
            .ReturnsAsync(loadResult);

        _mockManager.Setup(x => x.GetAllCustomPropertyNames())
            .Returns(new List<string>());

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.DatabasePath = databasePath;

        // Act
        await viewModel.ConnectDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.True);
            Assert.That(viewModel.IsBusy, Is.False);
        });

        _mockDocManagerApi.Verify(x => x.ConnectDatabaseAsync(It.Is<string>(s => s == databasePath)), Times.Once);
        _mockDocManagerApi.Verify(x => x.LoadDataIntoManagerAsync(_mockManager.Object), Times.Once);
    }

    [Test]
    public async Task ConnectDatabaseAsync_WhenConnectionFails_ShowsErrorMessage()
    {
        // Arrange
        var databasePath = @"C:\TestData\nonexistent.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var connectResult = SetupResult.CreateFailure("Database file does not exist");
        _mockDocManagerApi.Setup(x => x.ConnectDatabaseAsync(It.Is<string>(s => s == databasePath)))
            .ReturnsAsync(connectResult);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.DatabasePath = databasePath;

        // Act
        await viewModel.ConnectDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.False);
            Assert.That(viewModel.IsBusy, Is.False);
        });

        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(msg => msg.Contains("Failed to connect")),
            MessageTypes.Error,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public async Task ConnectDatabaseAsync_InitializesCustomFieldsAfterSuccess()
    {
        // Arrange
        var databasePath = @"C:\TestData\existing.db";
        var customFields = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition { PropertyName = "DisciplineCode", IsActive = true },
            new CustomFieldDefinition { PropertyName = "ProjectPhase", IsActive = true }
        };

        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var connectResult = SetupResult.CreateSuccess(databasePath);
        _mockDocManagerApi.Setup(x => x.ConnectDatabaseAsync(It.Is<string>(s => s == databasePath)))
            .ReturnsAsync(connectResult);

        var loadResult = SetupResult.CreateSuccess(databasePath);
        _mockDocManagerApi.Setup(x => x.LoadDataIntoManagerAsync(_mockManager.Object))
            .ReturnsAsync(loadResult);

        _mockManager.Setup(x => x.GetAllCustomPropertyNames())
            .Returns(new List<string> { "DisciplineCode", "ProjectPhase" });
        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(customFields);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.DatabasePath = databasePath;

        // Act
        await viewModel.ConnectDatabaseCommand.ExecuteAsync(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsConnected, Is.True);
            Assert.That(viewModel.CustomFields, Has.Count.EqualTo(2));
        });
    }

    #endregion

    #region BrowseDatabaseAsync Tests

    [Test]
    public void BrowseDatabase_WhenFileSelected_UpdatesDatabasePath()
    {
        // Arrange
        var selectedPath = @"C:\TestData\selected.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockDialogService.Setup(x => x.ShowOpenFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<bool>()))
            .Returns(new[] { selectedPath });

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        viewModel.BrowseDatabaseCommand.Execute(null);

        // Assert
        Assert.That(viewModel.DatabasePath, Is.EqualTo(selectedPath));
    }

    [Test]
    public void BrowseDatabase_WhenUserCancels_DoesNotChangePath()
    {
        // Arrange
        var originalPath = @"C:\TestData\original.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);
        _mockDialogService.Setup(x => x.ShowOpenFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<bool>()))
            .Returns((string[])null); // User cancelled

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        viewModel.DatabasePath = originalPath;

        // Act
        viewModel.BrowseDatabaseCommand.Execute(null);

        // Assert
        Assert.That(viewModel.DatabasePath, Is.EqualTo(originalPath));
    }

    #endregion

    #region TestDatabaseAsync Tests

    [Test]
    public async Task TestDatabaseAsync_WhenSuccessful_ShowsSuccessMessage()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var testResult = SetupResult.CreateSuccess("TestPath");
        testResult.Message = "Database test successful. Revisions: 10, Documents: 25";
        _mockDocManagerApi.Setup(x => x.TestDatabaseAsync())
            .ReturnsAsync(testResult);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        await viewModel.TestDatabaseCommand.ExecuteAsync(null);

        // Assert
        _mockDocManagerApi.Verify(x => x.TestDatabaseAsync(), Times.Once);
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(msg => msg.Contains("Database test successful")),
            MessageTypes.Information,
            It.IsAny<int>()), Times.Once);
    }

    [Test]
    public async Task TestDatabaseAsync_WhenFails_ShowsErrorMessage()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns((string)null);
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(false);

        var testResult = SetupResult.CreateFailure("Database not initialized");
        _mockDocManagerApi.Setup(x => x.TestDatabaseAsync())
            .ReturnsAsync(testResult);

        var viewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        // Act
        await viewModel.TestDatabaseCommand.ExecuteAsync(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(msg => msg.Contains("Database test failed")),
            MessageTypes.Error,
            It.IsAny<int?>()), Times.Once);
    }

    #endregion
}