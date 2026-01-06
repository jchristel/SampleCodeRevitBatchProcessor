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
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder;
using System.IO;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.CurrentFolder;

/// <summary>
/// Tests for FilingRuleDialogViewModel
/// Covers Add mode, Edit mode, validation, and commands
/// </summary>
[TestFixture]
public class FilingRuleDialogViewModelTests
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

        // Create test directory for target path validation
        _testDirectory = Path.Combine(Path.GetTempPath(), "FilingRuleDialogViewModelTests", Guid.NewGuid().ToString());
        Directory.CreateDirectory(_testDirectory);

        // Setup CurrentFolderManager.Settings to return a valid settings object
        var settings = new Core.Models.CurrentFolder.CurrentFolderManagerSettings
        {
            IncomingFolderPath = string.Empty,
            SupersededFolderPath = string.Empty,
            RevisionPrefix = string.Empty,
            RevisionSuffix = string.Empty,
            // Include a CatchAll rule (mimics real system behavior where a default CatchAll is created)
            FilingRules = new List<Core.Interfaces.IFilingRule>
            {
                new CatchAll(string.Empty, _testDirectory)
            },
            SupportedFileTypes = new List<Core.Models.CurrentFolder.SupportedFileType>()
        };
        _mockCurrentFolderManager.Setup(x => x.Settings).Returns(settings);

        // Create parent ViewModel with mocked dependencies
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
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Add Filing Rule"));
            Assert.That(viewModel.AvailableRuleTypes, Has.Count.EqualTo(5));
            Assert.That(viewModel.SelectedRuleType, Is.EqualTo(FilingRuleType.BeginsWith));
            Assert.That(viewModel.FilterValue, Is.EqualTo(string.Empty));
            Assert.That(viewModel.TargetPath, Is.EqualTo(string.Empty));
            Assert.That(viewModel.CreatedRule, Is.Null);
        });
    }

    [Test]
    public void Constructor_AddMode_AvailableRuleTypesContainsAllTypes()
    {
        // Arrange & Act
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.AvailableRuleTypes, NUnit.Framework.Contains.Item(FilingRuleType.BeginsWith));
            Assert.That(viewModel.AvailableRuleTypes, NUnit.Framework.Contains.Item(FilingRuleType.Contains));
            Assert.That(viewModel.AvailableRuleTypes, NUnit.Framework.Contains.Item(FilingRuleType.NotBeginsWith));
            Assert.That(viewModel.AvailableRuleTypes, NUnit.Framework.Contains.Item(FilingRuleType.NotContains));
            Assert.That(viewModel.AvailableRuleTypes, NUnit.Framework.Contains.Item(FilingRuleType.Default));
        });
    }

    #endregion

    #region Constructor Tests - Edit Mode

    [Test]
    public void Constructor_EditMode_LoadsExistingRule()
    {
        // Arrange
        var existingRule = new BeginsWith("ABC", _testDirectory);
        int editIndex = 0;

        // Act
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel,
            existingRule,
            editIndex);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Edit Filing Rule"));
            Assert.That(viewModel.SelectedRuleType, Is.EqualTo(FilingRuleType.BeginsWith));
            Assert.That(viewModel.FilterValue, Is.EqualTo("ABC"));
            Assert.That(viewModel.TargetPath, Is.EqualTo(_testDirectory));
        });
    }

    [Test]
    public void Constructor_EditMode_LoadsContainsRule()
    {
        // Arrange
        var existingRule = new Core.Models.CurrentFolder.FilingRules.Contains("Project", _testDirectory);

        // Act
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel,
            existingRule,
            0);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SelectedRuleType, Is.EqualTo(FilingRuleType.Contains));
            Assert.That(viewModel.FilterValue, Is.EqualTo("Project"));
        });
    }

    [Test]
    public void Constructor_EditMode_LoadsCatchAllRule()
    {
        // Arrange
        var existingRule = new CatchAll(string.Empty, _testDirectory);

        // Act
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel,
            existingRule,
            0);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SelectedRuleType, Is.EqualTo(FilingRuleType.Default));
            Assert.That(viewModel.FilterValue, Is.EqualTo(string.Empty));
            Assert.That(viewModel.IsFilterValueEnabled, Is.False);
        });
    }

    #endregion

    #region Property Tests

    [Test]
    public void IsFilterValueEnabled_WithBeginsWith_ReturnsTrue()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act
        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;

        // Assert
        Assert.That(viewModel.IsFilterValueEnabled, Is.True);
    }

    [Test]
    public void IsFilterValueEnabled_WithCatchAll_ReturnsFalse()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act
        viewModel.SelectedRuleType = FilingRuleType.Default;

        // Assert
        Assert.That(viewModel.IsFilterValueEnabled, Is.False);
    }

    [Test]
    public void SelectedRuleType_WhenChangedToCatchAll_ClearsFilterValue()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.FilterValue = "TestValue";

        // Act
        viewModel.SelectedRuleType = FilingRuleType.Default;

        // Assert
        Assert.That(viewModel.FilterValue, Is.EqualTo(string.Empty));
    }

    [Test]
    public void SelectedRuleType_WhenChanged_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        var propertyChangedRaised = false;
        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.SelectedRuleType))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.SelectedRuleType = FilingRuleType.Contains;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    #endregion

    #region Validation Tests - FilterValue

    [Test]
    public void Validation_FilterValue_RequiredForNonCatchAll()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;

        // Act
        viewModel.FilterValue = "Something"; // Establish validation
        viewModel.FilterValue = "";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_FilterValue_NotRequiredForCatchAll()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.Default;

        // Act
        viewModel.FilterValue = "";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_FilterValue_WithValidValue_NoError()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;

        // Act
        viewModel.FilterValue = "ABC";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    #endregion

    #region Validation Tests - TargetPath

    [Test]
    public void Validation_TargetPath_WithExistingDirectory_NoError()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act
        viewModel.TargetPath = _testDirectory;

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_TargetPath_WithNonExistingDirectory_HasError()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        var nonExistentPath = Path.Combine(_testDirectory, "NonExistent");

        // Act
        viewModel.TargetPath = "ValidPath"; // Establish validation
        viewModel.TargetPath = nonExistentPath;

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_TargetPath_WithEmptyPath_HasError()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act
        viewModel.TargetPath = _testDirectory; // Establish validation
        viewModel.TargetPath = "";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    #endregion

    #region BrowseTargetPathCommand Tests

    [Test]
    public void BrowseTargetPathCommand_WhenFolderSelected_UpdatesTargetPath()
    {
        // Arrange
        var selectedPath = _testDirectory;
        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns(selectedPath);

        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act
        viewModel.BrowseTargetPathCommand.Execute(null);

        // Assert
        Assert.That(viewModel.TargetPath, Is.EqualTo(selectedPath));
    }

    [Test]
    public void BrowseTargetPathCommand_WhenUserCancels_DoesNotChangeTargetPath()
    {
        // Arrange
        var originalPath = _testDirectory;
        _mockDialogService.Setup(x => x.ShowFolderBrowserDialog(
            It.IsAny<string>(),
            It.IsAny<string>()))
            .Returns((string)null);

        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.TargetPath = originalPath;

        // Act
        viewModel.BrowseTargetPathCommand.Execute(null);

        // Assert
        Assert.That(viewModel.TargetPath, Is.EqualTo(originalPath));
    }

    #endregion

    #region OkCommand Tests - CanExecute

    [Test]
    public void OkCommand_WithValidBeginsWith_CanExecute()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;
        viewModel.FilterValue = "ABC";
        viewModel.TargetPath = _testDirectory;

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void OkCommand_WithMissingFilterValue_CannotExecute()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;
        viewModel.FilterValue = "";
        viewModel.TargetPath = _testDirectory;

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void OkCommand_WithMissingTargetPath_CannotExecute()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;
        viewModel.FilterValue = "ABC";
        viewModel.TargetPath = "";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    #endregion

    #region OkCommand Tests - Execute

    [Test]
    public void OkCommand_Execute_CreatesBeginsWithRule()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;
        viewModel.FilterValue = "ABC";
        viewModel.TargetPath = _testDirectory;

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedRule, Is.Not.Null);
            Assert.That(viewModel.CreatedRule, Is.TypeOf<BeginsWith>());
            Assert.That(viewModel.CreatedRule.ComparisonValue, Is.EqualTo("ABC"));
            Assert.That(viewModel.CreatedRule.TargetDirectory, Is.EqualTo(_testDirectory));
        });
    }

    [Test]
    public void OkCommand_Execute_CreatesContainsRule()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.Contains;
        viewModel.FilterValue = "Project";
        viewModel.TargetPath = _testDirectory;

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedRule, Is.TypeOf<Core.Models.CurrentFolder.FilingRules.Contains>());
            Assert.That(viewModel.CreatedRule.ComparisonValue, Is.EqualTo("Project"));
        });
    }

    [Test]
    public void OkCommand_Execute_CreatesNotBeginsWithRule()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.NotBeginsWith;
        viewModel.FilterValue = "XYZ";
        viewModel.TargetPath = _testDirectory;

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedRule, Is.TypeOf<NotBeginsWith>());
    }

    [Test]
    public void OkCommand_Execute_CreatesNotContainsRule()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.NotContains;
        viewModel.FilterValue = "Test";
        viewModel.TargetPath = _testDirectory;

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedRule, Is.TypeOf<NotContains>());
    }

    #endregion

    #region CancelCommand Tests

    [Test]
    public void CancelCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act
        var canExecute = viewModel.CancelCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void CancelCommand_Execute_RaisesRequestCloseEvent()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        var eventRaised = false;
        viewModel.RequestClose += (sender, args) => eventRaised = true;

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(eventRaised, Is.True);
    }

    [Test]
    public void CancelCommand_Execute_DoesNotSetCreatedRule()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;
        viewModel.FilterValue = "ABC";
        viewModel.TargetPath = _testDirectory;

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedRule, Is.Null);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void CompleteWorkflow_AddBeginsWith_WorksCorrectly()
    {
        // Arrange
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act - Step 1: User selects rule type
        viewModel.SelectedRuleType = FilingRuleType.BeginsWith;

        // Assert - Step 1: Filter value is enabled
        Assert.That(viewModel.IsFilterValueEnabled, Is.True);

        // Act - Step 2: User enters filter value
        viewModel.FilterValue = "DOC";

        // Act - Step 3: User enters target path
        viewModel.TargetPath = _testDirectory;

        // Assert - Step 3: OK button is enabled
        Assert.That(viewModel.OkCommand.CanExecute(null), Is.True);

        // Act - Step 4: User clicks OK
        viewModel.OkCommand.Execute(null);

        // Assert - Step 4: Rule is created
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedRule, Is.Not.Null);
            Assert.That(viewModel.CreatedRule, Is.TypeOf<BeginsWith>());
            Assert.That(viewModel.CreatedRule.ComparisonValue, Is.EqualTo("DOC"));
            Assert.That(viewModel.CreatedRule.TargetDirectory, Is.EqualTo(_testDirectory));
        });
    }

    [Test]
    public void CompleteWorkflow_AddCatchAllWhenOneExists_PreventsDuplicate()
    {
        // Arrange - A CatchAll already exists in the system (created during Setup)
        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel);

        // Act - Step 1: User selects CatchAll
        viewModel.SelectedRuleType = FilingRuleType.Default;

        // Assert - Step 1: Filter value is disabled and cleared
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.IsFilterValueEnabled, Is.False);
            Assert.That(viewModel.FilterValue, Is.EqualTo(string.Empty));
        });

        // Act - Step 2: User enters target path
        viewModel.TargetPath = _testDirectory;

        // Assert - Step 2: OK button is DISABLED because a CatchAll already exists
        Assert.That(viewModel.OkCommand.CanExecute(null), Is.False, 
            "OK button should be disabled when trying to add a second CatchAll rule");
    }

    [Test]
    public void CompleteWorkflow_EditExistingRule_WorksCorrectly()
    {
        // Arrange
        var existingRule = new BeginsWith("OLD", _testDirectory);

        var viewModel = new FilingRuleDialogViewModel(
            _mockDialogService.Object,
            _parentViewModel,
            existingRule,
            0);

        // Assert - Initial state loaded from existing rule
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.SelectedRuleType, Is.EqualTo(FilingRuleType.BeginsWith));
            Assert.That(viewModel.FilterValue, Is.EqualTo("OLD"));
            Assert.That(viewModel.TargetPath, Is.EqualTo(_testDirectory));
        });

        // Act - User modifies filter value
        viewModel.FilterValue = "NEW";

        // Act - User clicks OK
        viewModel.OkCommand.Execute(null);

        // Assert - Updated rule is created
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedRule, Is.TypeOf<BeginsWith>());
            Assert.That(viewModel.CreatedRule.ComparisonValue, Is.EqualTo("NEW"));
        });
    }

    #endregion
}
