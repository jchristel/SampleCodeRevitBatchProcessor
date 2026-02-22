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
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CurrentFolder;

/// <summary>
/// Tests for CurrentFolderViewModel - Main functionality
/// Covers constructor, properties, validation, and browse commands
/// </summary>
[TestFixture]
public partial class CurrentFolderViewModelTests
{
    private Mock<IDialogService> _mockDialogService;
    private Mock<IMessageStore> _mockMessageStore;
    private Mock<IManager> _mockManager;
    private Mock<ICurrentFolderManager> _mockCurrentFolderManager;
    private CurrentFolderManagerSettings _settings;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _mockDialogService = new Mock<IDialogService>();
        _mockMessageStore = new Mock<IMessageStore>();
        _mockManager = new Mock<IManager>();
        _mockCurrentFolderManager = new Mock<ICurrentFolderManager>();

        // Create test directory
        _testDirectory = Path.Combine(Path.GetTempPath(), "CurrentFolderViewModelTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);

        // Setup settings
        _settings = new CurrentFolderManagerSettings
        {
            IncomingFolderPath = _testDirectory,  // Set to valid existing directory
            SupersededFolderPath = _testDirectory,  // Set to valid existing directory
            RevisionPrefix = "[",  // Set to valid value to avoid validation errors
            RevisionSuffix = "]",  // Set to valid value to avoid validation errors
            FilingRules = new List<IFilingRule>
            {
                new CatchAll(string.Empty, _testDirectory)
            },
            SupportedFileTypes = new List<SupportedFileType>()
        };
        _mockCurrentFolderManager.Setup(x => x.Settings).Returns(_settings);
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidDependencies_InitializesSuccessfully()
    {
        // Arrange & Act
        var viewModel = new CurrentFolderViewModel(
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockCurrentFolderManager.Object,
            _mockDialogService.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.IncomingFolderPath, Is.EqualTo(_testDirectory));
            Assert.That(viewModel.ArchiveFolderPath, Is.EqualTo(_testDirectory));
            Assert.That(viewModel.RevisionPrefix, Is.EqualTo("["));
            Assert.That(viewModel.RevisionSuffix, Is.EqualTo("]"));
        });
    }

    [Test]
    public void Constructor_WithValidSettings_HasNoErrors()
    {
        // Arrange & Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.That(viewModel.HasErrors, Is.False, 
            "ViewModel should have no validation errors after construction with valid settings");
    }

    [Test]
    public void Constructor_LoadsSettingsFromCurrentFolderManager()
    {
        // Arrange
        _settings.IncomingFolderPath = _testDirectory;
        _settings.SupersededFolderPath = Path.Combine(_testDirectory, "Archive");
        _settings.RevisionPrefix = "[";
        _settings.RevisionSuffix = "]";

        // Act
        var viewModel = new CurrentFolderViewModel(
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockCurrentFolderManager.Object,
            _mockDialogService.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IncomingFolderPath, Is.EqualTo(_testDirectory));
            Assert.That(viewModel.ArchiveFolderPath, Is.EqualTo(Path.Combine(_testDirectory, "Archive")));
            Assert.That(viewModel.RevisionPrefix, Is.EqualTo("["));
            Assert.That(viewModel.RevisionSuffix, Is.EqualTo("]"));
        });
    }

    #endregion

    #region Property Tests

    [Test]
    public void IncomingFolderPath_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.IncomingFolderPath))
                propertyChangedRaised = true;
        };

        // Create a different valid directory
        var differentDirectory = Path.Combine(_testDirectory, "SubFolder");
        Directory.CreateDirectory(differentDirectory);

        // Act - Set to a DIFFERENT value than initial
        viewModel.IncomingFolderPath = differentDirectory;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void IncomingFolderPath_WhenSet_SyncsToSettings()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.IncomingFolderPath = _testDirectory;

        // Assert
        Assert.That(_settings.IncomingFolderPath, Is.EqualTo(_testDirectory));
    }

    [Test]
    public void ArchiveFolderPath_WhenSet_SyncsToSettings()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var archivePath = Path.Combine(_testDirectory, "Archive");

        // Act
        viewModel.ArchiveFolderPath = archivePath;

        // Assert
        Assert.That(_settings.SupersededFolderPath, Is.EqualTo(archivePath));
    }

    [Test]
    public void RevisionPrefix_WhenSet_SyncsToSettings()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.RevisionPrefix = "[";

        // Assert
        Assert.That(_settings.RevisionPrefix, Is.EqualTo("["));
    }

    [Test]
    public void RevisionSuffix_WhenSet_SyncsToSettings()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.RevisionSuffix = "]";

        // Assert
        Assert.That(_settings.RevisionSuffix, Is.EqualTo("]"));
    }

    #endregion

    #region Validation Tests

    [Test]
    public void Validation_IncomingFolderPath_WithExistingFolder_NoError()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.IncomingFolderPath = _testDirectory;

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_IncomingFolderPath_WithNonExistentFolder_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var nonExistentPath = Path.Combine(_testDirectory, "NonExistent");

        // Act
        viewModel.IncomingFolderPath = nonExistentPath;

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_ArchiveFolderPath_WithExistingFolder_NoError()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.ArchiveFolderPath = _testDirectory;

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_ArchiveFolderPath_WithNonExistentFolder_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var nonExistentPath = Path.Combine(_testDirectory, "NonExistent");

        // Act
        viewModel.ArchiveFolderPath = nonExistentPath;

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    #endregion

    #region BrowseIncomingFolderCommand Tests

    [Test]
    public void BrowseIncomingFolderCommand_WhenFolderSelected_UpdatesPath()
    {
        // Arrange
        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns(_testDirectory);

        var viewModel = CreateViewModel();

        // Act
        viewModel.BrowseIncomingFolderCommand.Execute(null);

        // Assert
        Assert.That(viewModel.IncomingFolderPath, Is.EqualTo(_testDirectory));
    }

    [Test]
    public void BrowseIncomingFolderCommand_WhenUserCancels_DoesNotChangePath()
    {
        // Arrange
        var originalPath = _testDirectory;
        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns((string)null);

        var viewModel = CreateViewModel();
        viewModel.IncomingFolderPath = originalPath;

        // Act
        viewModel.BrowseIncomingFolderCommand.Execute(null);

        // Assert
        Assert.That(viewModel.IncomingFolderPath, Is.EqualTo(originalPath));
    }

    [Test]
    public void BrowseIncomingFolderCommand_OnException_EnqueuesErrorMessage()
    {
        // Arrange
        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Throws(new Exception("Test exception"));

        var viewModel = CreateViewModel();

        // Act
        viewModel.BrowseIncomingFolderCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Error selecting incoming folder")),
            It.IsAny<MessageTypes>(),
            It.IsAny<int?>()),
            Times.Once);
    }

    #endregion

    #region BrowseArchiveFolderCommand Tests

    [Test]
    public void BrowseArchiveFolderCommand_WhenFolderSelected_UpdatesPath()
    {
        // Arrange
        var archivePath = Path.Combine(_testDirectory, "Archive");
        Directory.CreateDirectory(archivePath);

        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns(archivePath);

        var viewModel = CreateViewModel();

        // Act
        viewModel.BrowseArchiveFolderCommand.Execute(null);

        // Assert
        Assert.That(viewModel.ArchiveFolderPath, Is.EqualTo(archivePath));
    }

    [Test]
    public void BrowseArchiveFolderCommand_WhenUserCancels_DoesNotChangePath()
    {
        // Arrange
        var originalPath = _testDirectory;
        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns((string)null);

        var viewModel = CreateViewModel();
        viewModel.ArchiveFolderPath = originalPath;

        // Act
        viewModel.BrowseArchiveFolderCommand.Execute(null);

        // Assert
        Assert.That(viewModel.ArchiveFolderPath, Is.EqualTo(originalPath));
    }

    [Test]
    public void BrowseArchiveFolderCommand_OnException_EnqueuesErrorMessage()
    {
        // Arrange
        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Throws(new Exception("Test exception"));

        var viewModel = CreateViewModel();

        // Act
        viewModel.BrowseArchiveFolderCommand.Execute(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Error selecting archive folder")),
            It.IsAny<MessageTypes>(),
            It.IsAny<int?>()),
            Times.Once);
    }

    #endregion

    #region Helper Methods

    private CurrentFolderViewModel CreateViewModel()
    {
        return new CurrentFolderViewModel(
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockCurrentFolderManager.Object,
            _mockDialogService.Object);
    }

    #endregion
}
