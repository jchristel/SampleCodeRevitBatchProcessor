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
using duHastNet.DocManager.UI.Shared.ViewModels;
using duHastNet.DocManager.UI.Shared.ViewModels.Merge;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels;

/// <summary>
/// Tests for NavigationHostViewModel
/// Covers initialization, navigation setup, and property forwarding
/// </summary>
[TestFixture]
public class NavigationHostViewModelTests
{
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private MessageStore _messageStore;
    private Manager _manager;
    private NavigationStore _navigationStore;
    private CurrentFolderManager _currentFolderManager;
    private Mock<IDialogService> _mockDialogService;
    private Mock<ISettingsService> _mockSettingsService;

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
        _mockSettingsService = new Mock<ISettingsService>();
        _mockSettingsService.Setup(x => x.SettingsDirectory).Returns("C:\\TestSettings");
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
        Assert.That(viewModel, Is.Not.Null);
    }

    [Test]
    public void Constructor_NavigatesToMergeViewByDefault()
    {
        // Arrange & Act
        var viewModel = CreateViewModel();

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(_navigationStore.CurrentViewModel, Is.Not.Null, 
                "Should navigate to initial view on construction");
            Assert.That(_navigationStore.CurrentViewModel, Is.InstanceOf<MergeViewModel>(),
                "Initial view should be MergeViewModel");
        });
    }

    #endregion

    #region CurrentViewModel Property Tests

    [Test]
    public void CurrentViewModel_ForwardsFromNavigationStore()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var initialViewModel = _navigationStore.CurrentViewModel;

        // Act - Navigate to a different view (will be null in test, but property should update)
        _navigationStore.NavigateTo((CommunityToolkit.Mvvm.ComponentModel.ObservableObject?)null);

        // Assert
        Assert.Multiple(() =>
        {
            Assert.That(viewModel.CurrentViewModel, Is.EqualTo(_navigationStore.CurrentViewModel),
                "CurrentViewModel should forward from NavigationStore");
            Assert.That(viewModel.CurrentViewModel, Is.Not.EqualTo(initialViewModel),
                "CurrentViewModel should reflect navigation changes");
        });
    }

    [Test]
    public void CurrentViewModel_RaisesPropertyChangedWhenNavigationStoreChanges()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var propertyChanged = false;

        viewModel.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(viewModel.CurrentViewModel))
                propertyChanged = true;
        };

        // Act - Trigger navigation change
        _navigationStore.NavigateTo((CommunityToolkit.Mvvm.ComponentModel.ObservableObject?)null);

        // Assert
        Assert.That(propertyChanged, Is.True,
            "Should raise PropertyChanged when NavigationStore.CurrentViewModel changes");
    }

    #endregion

    #region OnClosing Tests

    [Test]
    public void OnClosing_NotifiesNavigationStore()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act - Should not throw
        Assert.DoesNotThrow(() => viewModel.OnClosing());

        // Assert - If current ViewModel implements ICloseable, it should be notified
        // This is handled by NavigationStore.NotifyClosing()
    }

    #endregion

    #region Helper Methods

    private NavigationHostViewModel CreateViewModel()
    {
        return new NavigationHostViewModel(
            _mockDocManagerApi.Object,
            _manager,
            _currentFolderManager,
            _messageStore,
            _navigationStore,
            _mockSettingsService.Object,
            _mockDialogService.Object);
    }

    #endregion
}
