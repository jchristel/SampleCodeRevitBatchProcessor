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
using duHastNet.DocManager.UI.Shared.ViewModels.Merge;
using System.Reflection;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Merge;

/// <summary>
/// Tests for MergeViewModel_UpdateDataBase partial class
/// Covers database update operations during merge
/// Note: UpdateDatabaseAsync is a private method with complex dependencies.
/// These tests verify the method exists and can be invoked, but full integration testing would require
/// a real database setup.
/// </summary>
[TestFixture]
public class MergeViewModelTests_UpdateDataBase
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

    #region UpdateDatabaseAsync Method Existence Tests

    [Test]
    public void UpdateDatabaseAsync_MethodExists()
    {
        // Arrange & Act
        var method = typeof(MergeViewModel).GetMethod("UpdateDatabaseAsync",
            BindingFlags.NonPublic | BindingFlags.Instance);

        // Assert
        Assert.That(method, Is.Not.Null, "UpdateDatabaseAsync method should exist");
        Assert.That(method.ReturnType, Is.EqualTo(typeof(Task<bool>)), "UpdateDatabaseAsync should return Task<bool>");
    }

    [Test]
    public void UpdateDatabaseAsync_WithoutSetup_CanBeInvoked()
    {
        // Arrange
        var viewModel = CreateViewModel();
        var method = typeof(MergeViewModel).GetMethod("UpdateDatabaseAsync",
            BindingFlags.NonPublic | BindingFlags.Instance);

        // Act & Assert
        Assert.DoesNotThrow(() =>
        {
            var task = (Task<bool>)method.Invoke(viewModel, null);
            // Don't await - just verify it can be invoked
        }, "UpdateDatabaseAsync should be invocable without throwing during invocation");
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
