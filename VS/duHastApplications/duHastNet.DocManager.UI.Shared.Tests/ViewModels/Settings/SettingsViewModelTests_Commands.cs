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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.CloudDocManager;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Settings;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Settings;

/// <summary>
/// Tests for SettingsViewModel commands
/// Covers SaveSettingsCommand and NavigateToMergeCommand
/// </summary>
[TestFixture]
public class SettingsViewModelTests_Commands
{
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private MessageStore _messageStore;
    private Manager _manager;
    private NavigationStore _navigationStore;
    private CurrentFolderManager _currentFolderManager;
    private Mock<IDialogService> _mockDialogService;
    private Mock<ISettingsService> _mockSettingsService;
    private Mock<Func<duHastNet.DocManager.UI.Shared.ViewModels.Merge.MergeViewModel>> _mockCreateViewModel;

    [SetUp]
    public void Setup()
    {
        _mockDocManagerApi = new Mock<IDocManagerApi>();
        _mockDocManagerApi.Setup(x => x.IsDatabaseReady()).Returns(true);
        
        _messageStore = new MessageStore();
        _navigationStore = new NavigationStore();

        var cloudDocumentManager = new CloudDocumentManager();
        _manager = new Manager(cloudDocumentManager);

        var settings = new CurrentFolderManagerSettings();
        _currentFolderManager = new CurrentFolderManager(settings);

        _mockDialogService = new Mock<IDialogService>();
        _mockSettingsService = new Mock<ISettingsService>();
        _mockSettingsService.Setup(x => x.SettingsDirectory).Returns("C:\\TestSettings");

        _mockCreateViewModel = new Mock<Func<duHastNet.DocManager.UI.Shared.ViewModels.Merge.MergeViewModel>>();
    }

    [TearDown]
    public void TearDown()
    {
        _messageStore?.Dispose();
    }

    #region NavigateToMergeCommand Tests

    [Test]
    public void NavigateToMergeCommand_WhenExecuted_CallsFactory()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        viewModel.NavigateToMergeCommand.Execute(null);

        // Assert
        _mockCreateViewModel.Verify(x => x.Invoke(), Times.Once,
            "The merge view model factory should be called when navigating to merge view");
    }

    [Test]
    public void NavigateToMergeCommand_CanAlwaysExecute()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        var canExecute = viewModel.NavigateToMergeCommand.CanExecute(null);

        // Assert
        Assert.That(canExecute, Is.True);
    }

    #endregion

    #region Helper Methods

    private SettingsViewModel CreateViewModel()
    {
        return new SettingsViewModel(
            _mockDocManagerApi.Object,
            _manager,
            _messageStore,
            _currentFolderManager,
            _navigationStore,
            _mockDialogService.Object,
            _mockSettingsService.Object,
            _mockCreateViewModel.Object);
    }

    #endregion
}
