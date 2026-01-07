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
using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CloudDocManager;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Merge;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Merge;

/// <summary>
/// Tests for MergeViewModel
/// Covers constructor, properties, commands, and property change handlers
/// </summary>
[TestFixture]
public class MergeViewModelTests
{
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private MessageStore _messageStore;
    private NavigationStore _navigationStore;
    private Manager _manager;
    private CurrentFolderManager _currentFolderManager;
    private Mock<IDialogService> _mockDialogService;
    private Mock<Func<duHastNet.DocManager.UI.Shared.ViewModels.Settings.SettingsViewModel>> _mockCreateViewModel;

    [SetUp]
    public void Setup()
    {
        _mockDocManagerApi = new Mock<IDocManagerApi>();
        _messageStore = new MessageStore();
        _navigationStore = new NavigationStore();
        
        var cloudDocumentManager = new CloudDocumentManager();
        _manager = new Manager(cloudDocumentManager);
        
        var settings = new CurrentFolderManagerSettings();
        _currentFolderManager = new CurrentFolderManager(settings);
        
        _mockDialogService = new Mock<IDialogService>();
        _mockCreateViewModel = new Mock<Func<duHastNet.DocManager.UI.Shared.ViewModels.Settings.SettingsViewModel>>();
    }

    [TearDown]
    public void TearDown()
    {
        _messageStore?.Dispose();
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
            Assert.That(viewModel.MessageViewModel, Is.Not.Null);
            Assert.That(viewModel.DocumentMatchViewModel, Is.Not.Null);
            Assert.That(viewModel.FilteredRevisionDescriptions, Is.Not.Null);
            Assert.That(viewModel.StatusMessage, Is.EqualTo("Ready"));
            Assert.That(viewModel.IsConnected, Is.False);
            Assert.That(viewModel.IsBusy, Is.False);
        });
    }

    [Test]
    public void Constructor_WithNullManager_ThrowsException()
    {
        // Arrange & Act & Assert
        Assert.Throws<ArgumentNullException>(() => new MergeViewModel(
            _mockDocManagerApi.Object,
            _messageStore,
            _navigationStore,
            null,
            _currentFolderManager,
            _mockDialogService.Object,
            _mockCreateViewModel.Object));
    }

    [Test]
    public void Constructor_WithNullCurrentFolderManager_ThrowsException()
    {
        // Arrange & Act & Assert
        Assert.Throws<ArgumentNullException>(() => new MergeViewModel(
            _mockDocManagerApi.Object,
            _messageStore,
            _navigationStore,
            _manager,
            null,
            _mockDialogService.Object,
            _mockCreateViewModel.Object));
    }

    [Test]
    public void Constructor_WithNullDialogService_ThrowsException()
    {
        // Arrange & Act & Assert
        Assert.Throws<ArgumentNullException>(() => new MergeViewModel(
            _mockDocManagerApi.Object,
            _messageStore,
            _navigationStore,
            _manager,
            _currentFolderManager,
            null,
            _mockCreateViewModel.Object));
    }

    #endregion

    #region Property Tests

    [Test]
    public void StatusMessage_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.StatusMessage))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.StatusMessage = "Test Status";

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void IsConnected_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.IsConnected))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.IsConnected = true;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void IsBusy_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.IsBusy))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.IsBusy = true;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void RevisionDescription_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.RevisionDescription))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.RevisionDescription = "Test Description";

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    [Test]
    public void RevisionDate_WhenSet_TriggersPropertyChanged()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChangedRaised = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.RevisionDate))
                propertyChangedRaised = true;
        };

        // Act
        viewModel.RevisionDate = DateTime.Now;

        // Assert
        Assert.That(propertyChangedRaised, Is.True);
    }

    #endregion

    #region Computed Properties Tests

    [Test]
    public void IsDatabaseReady_ReturnsValueFromApi()
    {
        // Arrange
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        var viewModel = CreateViewModel();

        // Act
        var result = viewModel.IsDatabaseReady;

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void CurrentDatabasePath_ReturnsValueFromApi()
    {
        // Arrange
        var testPath = "C:\\TestDatabase.db";
        _mockDocManagerApi.Setup(x => x.GetDatabasePath()).Returns(testPath);
        var viewModel = CreateViewModel();

        // Act
        var result = viewModel.CurrentDatabasePath;

        // Assert
        Assert.That(result, Is.EqualTo(testPath));
    }

    #endregion

    #region NavigateToSettingsCommand Tests

    [Test]
    public void NavigateToSettingsCommand_WhenExecuted_NavigatesToSettings()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.NavigateToSettingsCommand.Execute(null);

        // Assert
        // Verify that the factory was invoked, which means NavigateTo was called
        _mockCreateViewModel.Verify(x => x.Invoke(), Times.Once,
            "The settings view model factory should be called when navigating to settings");
    }

    [Test]
    public void NavigateToSettingsCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        var canExecute = viewModel.NavigateToSettingsCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    #endregion

    #region SelectRevisionDescriptionCommand Tests

    [Test]
    public void SelectRevisionDescriptionCommand_WithValidDescription_SetsRevisionDescription()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var testDescription = "Test Revision";

        // Act
        viewModel.SelectRevisionDescriptionCommand.Execute(testDescription);

        // Assert
        Assert.That(viewModel.RevisionDescription, Is.EqualTo(testDescription));
    }

    [Test]
    public void SelectRevisionDescriptionCommand_WhenExecuted_ClosesPopup()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.IsRevisionSuggestionsPopupOpen = true;

        // Act
        viewModel.SelectRevisionDescriptionCommand.Execute("Test");

        // Assert
        Assert.That(viewModel.IsRevisionSuggestionsPopupOpen, Is.False);
    }

    [Test]
    public void SelectRevisionDescriptionCommand_WhenExecuted_ClearsFilteredDescriptions()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.FilteredRevisionDescriptions.Add("Item 1");
        viewModel.FilteredRevisionDescriptions.Add("Item 2");

        // Act
        viewModel.SelectRevisionDescriptionCommand.Execute("Test");

        // Assert
        Assert.That(viewModel.FilteredRevisionDescriptions, Is.Empty);
    }

    [Test]
    public void SelectRevisionDescriptionCommand_WithEmptyDescription_DoesNothing()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.RevisionDescription = "Original";

        // Act
        viewModel.SelectRevisionDescriptionCommand.Execute(string.Empty);

        // Assert
        Assert.That(viewModel.RevisionDescription, Is.EqualTo("Original"));
    }

    #endregion

    #region RevisionDescription Property Change Tests

    [Test]
    public void RevisionDescription_WhenSetToEmpty_ClearsSuggestions()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.RevisionDescription = "Some Value"; // Set to non-empty first
        viewModel.FilteredRevisionDescriptions.Add("Item");

        // Act
        viewModel.RevisionDescription = string.Empty; // Now this is actually a change

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.FilteredRevisionDescriptions, Is.Empty);
            Assert.That(viewModel.IsRevisionSuggestionsPopupOpen, Is.False);
        });
    }

    [Test]
    public void RevisionDescription_WhenSetToWhitespace_ClearsSuggestions()
    {
        // Arrange
        var viewModel = CreateViewModel();
        viewModel.RevisionDescription = "Some Value"; // Set to non-empty first
        viewModel.FilteredRevisionDescriptions.Add("Item");

        // Act
        viewModel.RevisionDescription = "   "; // Whitespace should also clear (IsNullOrWhiteSpace)

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.FilteredRevisionDescriptions, Is.Empty);
            Assert.That(viewModel.IsRevisionSuggestionsPopupOpen, Is.False);
        });
    }

    [Test]
    public void RevisionDescription_WhenSetWithNoMatches_ShowsNoSuggestions()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.RevisionDescription = "NoMatch";

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.FilteredRevisionDescriptions, Is.Empty);
            Assert.That(viewModel.IsRevisionSuggestionsPopupOpen, Is.False);
        });
    }

    #endregion

    #region Helper Methods

    private MergeViewModel CreateViewModel()
    {
        return new MergeViewModel(
            _mockDocManagerApi.Object,
            _messageStore,
            _navigationStore,
            _manager,
            _currentFolderManager,
            _mockDialogService.Object,
            _mockCreateViewModel.Object);
    }

    #endregion
}
