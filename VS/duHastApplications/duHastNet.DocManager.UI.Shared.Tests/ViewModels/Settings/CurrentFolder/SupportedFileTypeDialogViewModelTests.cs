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
using duHastNet.DocManager.Core.Models.CurrentFolder.DocumentNumberModifiers;
using duHastNet.DocManager.Core.Models.CurrentFolder.FilingRules;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CurrentFolder;

/// <summary>
/// Tests for SupportedFileTypeDialogViewModel
/// Covers Add mode, Edit mode, validation, modifier selection, and commands
/// </summary>
[TestFixture]
public class SupportedFileTypeDialogViewModelTests
{
    private Mock<IDialogService> _mockDialogService;
    private Mock<IMessageStore> _mockMessageStore;
    private Mock<IManager> _mockManager;
    private Mock<ICurrentFolderManager> _mockCurrentFolderManager;
    private CurrentFolderViewModel _parentViewModel;
    private string _testDirectory;

    [SetUp]
    public void Setup()
    {
        _mockDialogService = new Mock<IDialogService>();
        _mockMessageStore = new Mock<IMessageStore>();
        _mockManager = new Mock<IManager>();
        _mockCurrentFolderManager = new Mock<ICurrentFolderManager>();

        // Create test directory
        _testDirectory = Path.Combine(Path.GetTempPath(), "SupportedFileTypeDialogViewModelTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);

        // Setup CurrentFolderManager.Settings
        var settings = new CurrentFolderManagerSettings
        {
            IncomingFolderPath = string.Empty,
            SupersededFolderPath = string.Empty,
            RevisionPrefix = string.Empty,
            RevisionSuffix = string.Empty,
            FilingRules = new List<IFilingRule>
            {
                new CatchAll(string.Empty, _testDirectory)
            },
            SupportedFileTypes = new List<SupportedFileType>()
        };
        _mockCurrentFolderManager.Setup(x => x.Settings).Returns(settings);

        // Create parent ViewModel
        _parentViewModel = new CurrentFolderViewModel(
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockCurrentFolderManager.Object,
            _mockDialogService.Object);
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, true);
        }
    }

    #region Constructor Tests - Add Mode

    [Test]
    public void Constructor_AddMode_InitializesSuccessfully()
    {
        // Arrange & Act
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Add File Type"));
            Assert.That(viewModel.AvailableModifierTypes, Has.Count.EqualTo(5));
            Assert.That(viewModel.SelectedModifierType, Is.EqualTo(ModifierType.None));
            Assert.That(viewModel.FileExtension, Is.EqualTo(string.Empty));
            Assert.That(viewModel.Description, Is.EqualTo(string.Empty));
            Assert.That(viewModel.CurrentModifierControl, Is.Null);
            Assert.That(viewModel.CreatedFileType, Is.Null);
            Assert.That(viewModel.IsFileExtensionEnabled, Is.True);
        });
    }

    [Test]
    public void Constructor_AddMode_AvailableModifierTypesContainsAllTypes()
    {
        // Arrange & Act
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.AvailableModifierTypes, NUnit.Framework.Contains.Item(ModifierType.None));
            Assert.That(viewModel.AvailableModifierTypes, NUnit.Framework.Contains.Item(ModifierType.AddSuffix));
            Assert.That(viewModel.AvailableModifierTypes, NUnit.Framework.Contains.Item(ModifierType.AddPrefix));
            Assert.That(viewModel.AvailableModifierTypes, NUnit.Framework.Contains.Item(ModifierType.AddAtIndex));
            Assert.That(viewModel.AvailableModifierTypes, NUnit.Framework.Contains.Item(ModifierType.Replace));
        });
    }

    #endregion

    #region Constructor Tests - Edit Mode

    [Test]
    public void Constructor_EditMode_LoadsExistingFileType()
    {
        // Arrange
        var existingFileType = new SupportedFileType(".dwg", "AutoCAD Drawing", null);
        int editIndex = 0;

        // Act
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object,
            existingFileType,
            editIndex);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Edit File Type"));
            Assert.That(viewModel.FileExtension, Is.EqualTo(".dwg"));
            Assert.That(viewModel.Description, Is.EqualTo("AutoCAD Drawing"));
            Assert.That(viewModel.SelectedModifierType, Is.EqualTo(ModifierType.None));
            // Note: IsFileExtensionEnabled depends on whether we're editing PDF,
            // which requires the parent to have the file type in its collection
        });
    }

    [Test]
    public void Constructor_EditMode_LoadsFileTypeWithSuffixModifier()
    {
        // Arrange
        var modifier = new AddToEnd("-COPY");
        var existingFileType = new SupportedFileType(".pdf", "PDF Document", modifier);

        // Act
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object,
            existingFileType,
            0);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SelectedModifierType, Is.EqualTo(ModifierType.AddSuffix));
            Assert.That(viewModel.CurrentModifierControl, Is.Not.Null);
        });
    }

    #endregion

    #region Property Tests

    [Test]
    public void SelectedModifierType_WhenChanged_UpdatesCurrentModifierControl()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.SelectedModifierType = ModifierType.AddSuffix;

        // Assert
        Assert.That(viewModel.CurrentModifierControl, Is.Not.Null);
    }

    [Test]
    public void SelectedModifierType_WhenChangedToNone_ClearsModifierControl()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.SelectedModifierType = ModifierType.AddSuffix;
        Assert.That(viewModel.CurrentModifierControl, Is.Not.Null);

        // Act
        viewModel.SelectedModifierType = ModifierType.None;

        // Assert
        Assert.That(viewModel.CurrentModifierControl, Is.Null);
    }

    [Test]
    public void SelectedModifierType_WhenChanged_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        var propertyChangedRaised = false;
        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.SelectedModifierType))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.SelectedModifierType = ModifierType.AddPrefix;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    #endregion

    #region Validation Tests - FileExtension

    [Test]
    public void Validation_FileExtension_WithValidExtension_NoError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Set Description to valid to avoid unrelated errors
        viewModel.Description = "Test Document";

        // Act
        viewModel.FileExtension = ".txt";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_FileExtension_WithEmptyValue_HasError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.FileExtension = ".pdf"; // Establish validation
        viewModel.FileExtension = "";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_FileExtension_WithoutPeriod_HasError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.FileExtension = "pdf";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_FileExtension_WithPeriodOnly_HasError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.FileExtension = ".";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_FileExtension_WithInvalidCharacters_HasError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.FileExtension = ".pdf@#";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_FileExtension_WithSpaces_HasError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.FileExtension = ".p df";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_FileExtension_WithValidAlphanumeric_NoError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.FileExtension = ".dwg2023";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    #endregion

    #region Validation Tests - Description

    [Test]
    public void Validation_Description_WithValidValue_NoError()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        viewModel.Description = "PDF Document";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    #endregion

    #region OkCommand Tests - CanExecute

    [Test]
    public void OkCommand_WithValidFileTypeNoModifier_CanExecute()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.FileExtension = ".xlsx";
        viewModel.Description = "Excel Spreadsheet";
        viewModel.SelectedModifierType = ModifierType.None;

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void OkCommand_WithMissingFileExtension_CannotExecute()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.FileExtension = "";
        viewModel.Description = "PDF Document";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void OkCommand_WithMissingDescription_CannotExecute()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.FileExtension = ".docx";
        viewModel.Description = "";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void OkCommand_WithInvalidFileExtension_CannotExecute()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.FileExtension = "pdf"; // Missing period
        viewModel.Description = "PDF Document";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    #endregion

    #region OkCommand Tests - Execute

    [Test]
    public void OkCommand_Execute_CreatesFileTypeWithNoModifier()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.FileExtension = ".dwg";
        viewModel.Description = "AutoCAD Drawing";
        viewModel.SelectedModifierType = ModifierType.None;

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedFileType, Is.Not.Null);
            Assert.That(viewModel.CreatedFileType.FileExtension, Is.EqualTo(".dwg"));
            Assert.That(viewModel.CreatedFileType.Description, Is.EqualTo("AutoCAD Drawing"));
            Assert.That(viewModel.CreatedFileType.DocumentNumberModifier, Is.Null);
        });
    }

    [Test]
    public void OkCommand_Execute_CreatesFileTypeWithDifferentExtensions()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.FileExtension = ".dwg";
        viewModel.Description = "AutoCAD Drawing";

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedFileType.FileExtension, Is.EqualTo(".dwg"));
            Assert.That(viewModel.CreatedFileType.Description, Is.EqualTo("AutoCAD Drawing"));
        });
    }

    #endregion

    #region CancelCommand Tests

    [Test]
    public void CancelCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act
        var canExecute = viewModel.CancelCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void CancelCommand_Execute_RaisesRequestCloseEvent()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        var eventRaised = false;
        viewModel.RequestClose += (sender, args) => eventRaised = true;

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(eventRaised, Is.True);
    }

    [Test]
    public void CancelCommand_Execute_DoesNotSetCreatedFileType()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        viewModel.FileExtension = ".txt";
        viewModel.Description = "Text File";

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedFileType, Is.Null);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void CompleteWorkflow_AddFileTypeWithoutModifier_WorksCorrectly()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act - Step 1: User enters file extension
        viewModel.FileExtension = ".xlsx";

        // Assert - Step 1: Validation passes
        Assert.That(viewModel.HasErrors, Is.False);

        // Act - Step 2: User enters description
        viewModel.Description = "Excel Spreadsheet";

        // Act - Step 3: User leaves modifier as None
        viewModel.SelectedModifierType = ModifierType.None;

        // Assert - Step 3: OK button is enabled
        Assert.That(viewModel.OkCommand.CanExecute(null), Is.True);

        // Act - Step 4: User clicks OK
        viewModel.OkCommand.Execute(null);

        // Assert - Step 4: File type is created
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedFileType, Is.Not.Null);
            Assert.That(viewModel.CreatedFileType.FileExtension, Is.EqualTo(".xlsx"));
            Assert.That(viewModel.CreatedFileType.Description, Is.EqualTo("Excel Spreadsheet"));
            Assert.That(viewModel.CreatedFileType.DocumentNumberModifier, Is.Null);
        });
    }

    [Test]
    public void CompleteWorkflow_EditExistingFileType_WorksCorrectly()
    {
        // Arrange
        var existingFileType = new SupportedFileType(".dwg", "Old Description", null);

        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object,
            existingFileType,
            0);

        // Assert - Initial state loaded
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.FileExtension, Is.EqualTo(".dwg"));
            Assert.That(viewModel.Description, Is.EqualTo("Old Description"));
        });

        // Act - User modifies description
        viewModel.Description = "AutoCAD Drawing File";

        // Act - User clicks OK
        viewModel.OkCommand.Execute(null);

        // Assert - Updated file type is created
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedFileType, Is.Not.Null);
            Assert.That(viewModel.CreatedFileType.FileExtension, Is.EqualTo(".dwg"));
            Assert.That(viewModel.CreatedFileType.Description, Is.EqualTo("AutoCAD Drawing File"));
        });
    }

    [Test]
    public void CompleteWorkflow_InvalidFileExtension_PreventsOk()
    {
        // Arrange
        var viewModel = new SupportedFileTypeDialogViewModel(
            _parentViewModel,
            _mockDialogService.Object);

        // Act - User enters invalid file extension
        viewModel.FileExtension = "pdf"; // Missing period
        viewModel.Description = "PDF Document";

        // Assert - OK button is disabled
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.HasErrors, Is.True);
            Assert.That(viewModel.OkCommand.CanExecute(null), Is.False);
        });
    }

    #endregion
}
