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
using duHastNet.DocManager.Core.Models.Results;
using duHastNet.DocManager.Core.Models.CloudDocManager;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CloudDocManager.CloudProviderControls;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CloudDocManager.CloudProviderControls;

/// <summary>
/// Tests for AconexMetadataControlViewModel - Main functionality
/// Covers constructor, template file path, validation, and commands
/// </summary>
[TestFixture]
public partial class AconexMetadataControlViewModelTests
{
    protected Mock<IMessageStore> _mockMessageStore;
    protected Mock<IDialogService> _mockDialogService;
    protected Mock<ICloudMetaData> _mockAconexMapper;
    protected Mock<IMetaDataTemplateService> _mockTemplateService;
    protected Mock<IManager> _mockManager;
    protected Mock<CloudDocumentManager> _mockCloudDocumentManager;
    protected string _testDirectory;
    protected string _testCsvFilePath;

    [SetUp]
    public void Setup()
    {
        _mockMessageStore = new Mock<IMessageStore>();
        _mockDialogService = new Mock<IDialogService>();
        _mockAconexMapper = new Mock<ICloudMetaData>();
        _mockTemplateService = new Mock<IMetaDataTemplateService>();
        _mockCloudDocumentManager = new Mock<CloudDocumentManager>();
        _mockManager = new Mock<IManager>();

        // Setup Manager to return CloudDocumentManager
        _mockManager.Setup(x => x.CloudDocManager).Returns(_mockCloudDocumentManager.Object);

        // Create test directory and CSV file
        _testDirectory = Path.Combine(Path.GetTempPath(), "AconexMetadataControlViewModelTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);

        _testCsvFilePath = Path.Combine(_testDirectory, "template.csv");
        File.WriteAllText(_testCsvFilePath, "Header1,Header2,Header3");

        // Setup default mock behavior
        _mockAconexMapper.Setup(x => x.MetadataTemplateFilePath).Returns(string.Empty);
        _mockAconexMapper.Setup(x => x.MetaDataMap).Returns(new List<MetaDataMap>());
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
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.TemplateMetaDataFilePath, Is.EqualTo(string.Empty));
            Assert.That(viewModel.IsBrowseTemplateFileEnabled, Is.True);
            Assert.That(viewModel.IsRefreshTemplateEnabled, Is.False);
            Assert.That(viewModel.MetaDataMappings, Is.Not.Null);
        });
    }

    [Test]
    public void Constructor_WithNullParameters_ThrowsException()
    {
        // Arrange & Act & Assert
        Assert.Multiple(() =>
        {
            Assert.Throws<ArgumentNullException>(() => new AconexMetadataControlViewModel(
                null,
                _mockDialogService.Object,
                _mockAconexMapper.Object,
                _mockTemplateService.Object,
                _mockManager.Object));

            Assert.Throws<ArgumentNullException>(() => new AconexMetadataControlViewModel(
                _mockMessageStore.Object,
                null,
                _mockAconexMapper.Object,
                _mockTemplateService.Object,
                _mockManager.Object));

            Assert.Throws<ArgumentNullException>(() => new AconexMetadataControlViewModel(
                _mockMessageStore.Object,
                _mockDialogService.Object,
                null,
                _mockTemplateService.Object,
                _mockManager.Object));

            Assert.Throws<ArgumentNullException>(() => new AconexMetadataControlViewModel(
                _mockMessageStore.Object,
                _mockDialogService.Object,
                _mockAconexMapper.Object,
                null,
                _mockManager.Object));

            Assert.Throws<ArgumentNullException>(() => new AconexMetadataControlViewModel(
                _mockMessageStore.Object,
                _mockDialogService.Object,
                _mockAconexMapper.Object,
                _mockTemplateService.Object,
                null));
        });
    }

    [Test]
    public void Constructor_LoadsExistingTemplatePathFromMapper()
    {
        // Arrange
        _mockAconexMapper.Setup(x => x.MetadataTemplateFilePath).Returns(_testCsvFilePath);

        // Setup template service to return success
        var result = new MetaDataTemplateResult
        {
            IsReadSuccessful = true,
            ColumnHeaders = new List<string> { "Header1", "Header2" }
        };
        _mockTemplateService.Setup(x => x.ReadColumnHeadersAsync(_testCsvFilePath))
            .ReturnsAsync(result);

        // Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.That(viewModel.TemplateMetaDataFilePath, Is.EqualTo(_testCsvFilePath));
    }

    #endregion

    #region Property Tests

    [Test]
    public void TemplateMetaDataFilePath_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.TemplateMetaDataFilePath))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void TemplateMetaDataFilePath_WhenSetToValidFile_UpdatesMapper()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Assert
        _mockAconexMapper.VerifySet(x => x.MetadataTemplateFilePath = _testCsvFilePath, Times.Once);
    }

    [Test]
    public void TemplateMetaDataFilePath_WhenSetToValidFile_EnablesRefreshButton()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Setup template service to return success
        var result = new MetaDataTemplateResult
        {
            IsReadSuccessful = true,
            ColumnHeaders = new List<string> { "Header1" }
        };
        _mockTemplateService.Setup(x => x.ReadColumnHeadersAsync(_testCsvFilePath))
            .ReturnsAsync(result);

        // Act
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Give async operation time to complete
        System.Threading.Thread.Sleep(100);

        // Assert
        Assert.That(viewModel.IsRefreshTemplateEnabled, Is.True);
    }

    [Test]
    public void TemplateMetaDataFilePath_WhenSetToInvalidFile_DisablesRefreshButton()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.TemplateMetaDataFilePath = "nonexistent.csv";

        // Assert
        Assert.That(viewModel.IsRefreshTemplateEnabled, Is.False);
    }

    #endregion

    #region Validation Tests

    [Test]
    public void Validation_TemplateFilePath_WithExistingCsvFile_NoError()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_TemplateFilePath_WithNonExistentFile_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.TemplateMetaDataFilePath = "nonexistent.csv";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_TemplateFilePath_WithNonCsvFile_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var txtFilePath = Path.Combine(_testDirectory, "template.txt");
        File.WriteAllText(txtFilePath, "test content");

        // Act
        viewModel.TemplateMetaDataFilePath = txtFilePath;

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_TemplateFilePath_WithEmptyPath_HasError()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.TemplateMetaDataFilePath = "something";
        viewModel.TemplateMetaDataFilePath = "";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    #endregion

    #region BrowseTemplateFileCommand Tests

    [Test]
    public void BrowseTemplateFileCommand_WhenFileSelected_UpdatesPath()
    {
        // Arrange
        _mockDialogService.Setup(x => x.ShowOpenFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string?>(),
            It.IsAny<bool>()))
            .Returns(new[] { _testCsvFilePath });

        var viewModel = CreateViewModel();

        // Act
        viewModel.BrowseTemplateFileCommand.Execute(null);

        // Assert
        Assert.That(viewModel.TemplateMetaDataFilePath, Is.EqualTo(_testCsvFilePath));
    }

    [Test]
    public void BrowseTemplateFileCommand_WhenUserCancels_DoesNotChangePath()
    {
        // Arrange
        var originalPath = "";
        _mockDialogService.Setup(x => x.ShowOpenFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string?>(),
            It.IsAny<bool>()))
            .Returns((string[])null);

        var viewModel = CreateViewModel();
        viewModel.TemplateMetaDataFilePath = originalPath;

        // Act
        viewModel.BrowseTemplateFileCommand.Execute(null);

        // Assert
        Assert.That(viewModel.TemplateMetaDataFilePath, Is.EqualTo(originalPath));
    }

    [Test]
    public void BrowseTemplateFileCommand_DisablesThenEnablesBrowseButton()
    {
        // Arrange
        _mockDialogService.Setup(x => x.ShowOpenFileDialog(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string?>(),
            It.IsAny<bool>()))
            .Returns(new[] { _testCsvFilePath });

        var viewModel = CreateViewModel();

        // Act
        viewModel.BrowseTemplateFileCommand.Execute(null);

        // Assert - Button should be re-enabled after operation
        Assert.That(viewModel.IsBrowseTemplateFileEnabled, Is.True);
    }

    #endregion

    #region RefreshTemplateCommand Tests

    [Test]
    public async Task RefreshTemplateCommand_WithValidFile_LoadsHeaders()
    {
        // Arrange
        var result = new MetaDataTemplateResult
        {
            IsReadSuccessful = true,
            ColumnHeaders = new List<string> { "Header1", "Header2", "Header3" }
        };
        _mockTemplateService.Setup(x => x.ReadColumnHeadersAsync(_testCsvFilePath))
            .ReturnsAsync(result);

        var viewModel = CreateViewModel();
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Act
        await viewModel.RefreshTemplateCommand.ExecuteAsync(null);

        // Assert
        _mockAconexMapper.Verify(x => x.UpdateAvailableFields(result.ColumnHeaders), Times.Once);
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("3 column headers")),
            MessageTypes.Information,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public async Task RefreshTemplateCommand_WithNoFilePath_ShowsWarning()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.TemplateMetaDataFilePath = "";

        // Act
        await viewModel.RefreshTemplateCommand.ExecuteAsync(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("No template file selected")),
            MessageTypes.Warning,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public async Task RefreshTemplateCommand_WithFailedRead_ShowsError()
    {
        // Arrange
        var result = new MetaDataTemplateResult
        {
            IsReadSuccessful = false,
            Message = "Failed to read file",
            Errors = new List<string> { "Error detail 1" }
        };
        _mockTemplateService.Setup(x => x.ReadColumnHeadersAsync(_testCsvFilePath))
            .ReturnsAsync(result);

        var viewModel = CreateViewModel();
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Act
        await viewModel.RefreshTemplateCommand.ExecuteAsync(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            It.Is<string>(s => s.Contains("Failed to refresh template")),
            MessageTypes.Error,
            It.IsAny<int?>()), Times.Once);
    }

    [Test]
    public async Task RefreshTemplateCommand_WithWarnings_DisplaysWarnings()
    {
        // Arrange
        var result = new MetaDataTemplateResult
        {
            IsReadSuccessful = true,
            ColumnHeaders = new List<string> { "Header1" },
            Warnings = new List<string> { "Duplicate header found" }
        };
        _mockTemplateService.Setup(x => x.ReadColumnHeadersAsync(_testCsvFilePath))
            .ReturnsAsync(result);

        var viewModel = CreateViewModel();
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Act
        await viewModel.RefreshTemplateCommand.ExecuteAsync(null);

        // Assert
        _mockMessageStore.Verify(x => x.EnqueueMessage(
            "Duplicate header found",
            MessageTypes.Warning,
            It.IsAny<int?>()), Times.Once);
    }

    #endregion

    #region Helper Method Tests

    [Test]
    public void IsValid_WithValidState_ReturnsTrue()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.TemplateMetaDataFilePath = _testCsvFilePath;

        // Act
        var isValid = viewModel.IsValid();

        // Assert
        Assert.That(isValid, Is.True);
    }

    [Test]
    public void IsValid_WithInvalidState_ReturnsFalse()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.TemplateMetaDataFilePath = ""; // Invalid

        // Act
        var isValid = viewModel.IsValid();

        // Assert
        Assert.That(isValid, Is.False);
    }

    #endregion

    #region Helper Methods

    protected AconexMetadataControlViewModel CreateViewModel()
    {
        return new AconexMetadataControlViewModel(
            _mockMessageStore.Object,
            _mockDialogService.Object,
            _mockAconexMapper.Object,
            _mockTemplateService.Object,
            _mockManager.Object);
    }

    #endregion
}
