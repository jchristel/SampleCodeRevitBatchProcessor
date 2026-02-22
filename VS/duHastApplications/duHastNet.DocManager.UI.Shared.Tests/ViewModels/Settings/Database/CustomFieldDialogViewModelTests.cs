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
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings.Database;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings.Database;

/// <summary>
/// Tests for CustomFieldDialogViewModel
/// Covers constructor, validation, commands, and property changes
/// </summary>
[TestFixture]
public class CustomFieldDialogViewModelTests
{
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private Mock<IMessageStore> _mockMessageStore;
    private Mock<IManager> _mockManager;
    private Mock<IDialogService> _mockDialogService;
    private DatabaseConnectionViewModel _parentViewModel;

    [SetUp]
    public void Setup()
    {
        _mockDocManagerApi = new Mock<IDocManagerApi>();
        _mockMessageStore = new Mock<IMessageStore>();
        _mockManager = new Mock<IManager>();
        _mockDialogService = new Mock<IDialogService>();

        // Create parent ViewModel with no existing custom fields
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(@"C:\Test\db.db");
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(false);
        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(new List<CustomFieldDefinition>());

        _parentViewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);
    }

    #region Constructor Tests

    [Test]
    public void Constructor_WithValidParent_InitializesSuccessfully()
    {
        // Arrange & Act
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel, Is.Not.Null);
            Assert.That(viewModel.FieldName, Is.EqualTo(string.Empty));
            Assert.That(viewModel.CreatedFieldName, Is.Null);
            Assert.That(viewModel.DialogTitle, Is.EqualTo("Add Custom Field"));
        });
    }

    #endregion

    #region Property Tests

    [Test]
    public void FieldName_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.FieldName))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.FieldName = "TestField";

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(propertyChangedRaised, Is.True);
            Assert.That(viewModel.FieldName, Is.EqualTo("TestField"));
        });
    }

    [Test]
    public void DialogTitle_ReturnsConstantValue()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        var title = viewModel.DialogTitle;

        // Assert
        Assert.That(title, Is.EqualTo("Add Custom Field"));
    }

    #endregion

    #region Validation Tests

    [Test]
    public void Validation_WithEmptyFieldName_HasError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        // Set to non-empty first to trigger validation (initial value is already empty string)
        viewModel.FieldName = "TempValue";
        viewModel.FieldName = ""; // Now set to empty to test validation

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_WithWhitespaceFieldName_HasError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        viewModel.FieldName = "   ";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_WithValidFieldName_NoError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        viewModel.FieldName = "ProjectPhase";

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_WithTooLongFieldName_HasError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        var longFieldName = new string('A', 101); // 101 characters

        // Act
        viewModel.FieldName = longFieldName;

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_WithMaxLengthFieldName_NoError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        var maxLengthFieldName = new string('A', 100); // Exactly 100 characters

        // Act
        viewModel.FieldName = maxLengthFieldName;

        // Assert
        Assert.That(viewModel.HasErrors, Is.False);
    }

    [Test]
    public void Validation_WithDoubleQuote_HasError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        viewModel.FieldName = "Field\"Name";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_WithSingleQuote_HasError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        viewModel.FieldName = "Field'Name";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_WithSemicolon_HasError()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        viewModel.FieldName = "Field;Name";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_WithDuplicateFieldName_HasError()
    {
        // Arrange
        var customFieldDefinitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition { PropertyName = "ExistingField", IsActive = true }
        };

        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(customFieldDefinitions);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);

        var parentViewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var viewModel = new CustomFieldDialogViewModel(parentViewModel);

        // Act
        viewModel.FieldName = "ExistingField";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    [Test]
    public void Validation_WithDuplicateFieldNameDifferentCase_HasError()
    {
        // Arrange
        var customFieldDefinitions = new List<CustomFieldDefinition>
        {
            new CustomFieldDefinition { PropertyName = "ExistingField", IsActive = true }
        };

        _mockManager.Setup(x => x.GetAllCustomFieldDefinitions())
            .Returns(customFieldDefinitions);
        _mockManager.Setup(x => x.IsDataLoaded).Returns(true);

        var parentViewModel = new DatabaseConnectionViewModel(
            _mockDocManagerApi.Object,
            _mockMessageStore.Object,
            _mockManager.Object,
            _mockDialogService.Object);

        var viewModel = new CustomFieldDialogViewModel(parentViewModel);

        // Act
        viewModel.FieldName = "existingfield";

        // Assert
        Assert.That(viewModel.HasErrors, Is.True);
    }

    #endregion

    #region OkCommand Tests

    [Test]
    public void OkCommand_WithValidFieldName_CanExecute()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "ValidField";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void OkCommand_WithEmptyFieldName_CannotExecute()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void OkCommand_WithInvalidFieldName_CannotExecute()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "Field\"Name";

        // Act
        var canExecute = viewModel.OkCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.False);
    }

    [Test]
    public void OkCommand_Execute_SetsCreatedFieldName()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "NewField";

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedFieldName, Is.EqualTo("NewField"));
    }

    [Test]
    public void OkCommand_Execute_TrimsFieldName()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "  NewField  ";

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedFieldName, Is.EqualTo("NewField"));
    }

    [Test]
    public void OkCommand_Execute_RaisesRequestCloseEvent()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "NewField";

        var eventRaised = false;
        viewModel.RequestClose += (sender, args) => eventRaised = true;

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.That(eventRaised, Is.True);
    }

    [Test]
    public void OkCommand_ExecuteWithErrors_DoesNotSetCreatedFieldName()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "Field\"Invalid";

        // Act
        viewModel.OkCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedFieldName, Is.Null);
    }

    #endregion

    #region CancelCommand Tests

    [Test]
    public void CancelCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act
        var canExecute = viewModel.CancelCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    [Test]
    public void CancelCommand_Execute_RaisesRequestCloseEvent()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        var eventRaised = false;
        viewModel.RequestClose += (sender, args) => eventRaised = true;

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(eventRaised, Is.True);
    }

    [Test]
    public void CancelCommand_Execute_DoesNotSetCreatedFieldName()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        viewModel.FieldName = "SomeField";

        // Act
        viewModel.CancelCommand.Execute(null);

        // Assert
        Assert.That(viewModel.CreatedFieldName, Is.Null);
    }

    #endregion

    #region Integration Tests

    [Test]
    public void CompleteWorkflow_ValidFieldName_WorksCorrectly()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);
        var closeEventRaised = false;
        viewModel.RequestClose += (sender, args) => closeEventRaised = true;

        // Act - Step 1: User types field name
        viewModel.FieldName = "  ProjectPhase  ";

        // Assert - Step 1: Validation passes
        Assert.That(viewModel.HasErrors, Is.False);

        // Act - Step 2: User clicks OK
        Assert.That(viewModel.OkCommand.CanExecute(null), Is.True);
        viewModel.OkCommand.Execute(null);

        // Assert - Step 2: Field is created and dialog closes
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CreatedFieldName, Is.EqualTo("ProjectPhase"));
            Assert.That(closeEventRaised, Is.True);
        });
    }

    [Test]
    public void CompleteWorkflow_InvalidFieldName_PreventsOk()
    {
        // Arrange
        var viewModel = new CustomFieldDialogViewModel(_parentViewModel);

        // Act - Step 1: User types invalid field name
        viewModel.FieldName = "Invalid\"Field";

        // Assert - Step 1: OK button is disabled
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.HasErrors, Is.True);
            Assert.That(viewModel.OkCommand.CanExecute(null), Is.False);
        });
    }

    #endregion
}
