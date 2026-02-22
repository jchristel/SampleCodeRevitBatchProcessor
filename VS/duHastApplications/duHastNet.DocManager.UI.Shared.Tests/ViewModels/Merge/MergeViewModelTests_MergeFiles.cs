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
/// Tests for MergeViewModel_MergeFiles partial class
/// Covers file merging and superseding operations
/// </summary>
[TestFixture]
public class MergeViewModelTests_MergeFiles
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

    #region MergeFilesAsync Tests

    [Test]
    public void MergeFilesAsync_MethodExists()
    {
        // Arrange & Act
        var method = typeof(MergeViewModel).GetMethod("MergeFilesAsync",
            BindingFlags.NonPublic | BindingFlags.Instance);

        // Assert
        Assert.That(method, Is.Not.Null, "MergeFilesAsync method should exist");
        Assert.That(method.ReturnType, Is.EqualTo(typeof(Task)), "MergeFilesAsync should return Task");
    }

    [Test]
    public void MergeFilesAsync_WithNoDocumentsToMerge_CanBeInvoked()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act & Assert
        Assert.DoesNotThrowAsync(async () => await InvokeMergeFilesAsync(viewModel));
    }

    #endregion

    #region ShowMergeLog Tests

    [Test]
    public void ShowMergeLog_WhenCalled_ShowsDialog()
    {
        // Arrange
        var viewModel = CreateViewModel();

        // Act
        InvokeShowMergeLog(viewModel);

        // Assert
        _mockDialogService.Verify(x => x.ShowDialog(It.IsAny<object>()), Times.Once);
    }

    [Test]
    public void ShowMergeLog_WithException_ShowsErrorMessage()
    {
        // Arrange
        var viewModel = CreateViewModel();
        _mockDialogService.Setup(x => x.ShowDialog(It.IsAny<object>()))
            .Throws(new Exception("Test exception"));
        
        var messageCount = 0;
        _messageStore.PropertyChanged += (sender, args) =>
        {
            if (args.PropertyName == nameof(_messageStore.CurrentMessage) && !string.IsNullOrEmpty(_messageStore.CurrentMessage))
            {
                messageCount++;
            }
        };

        // Act
        InvokeShowMergeLog(viewModel);

        // Assert
        Assert.That(messageCount, Is.GreaterThan(0));
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

    private async Task InvokeMergeFilesAsync(MergeViewModel viewModel)
    {
        var method = typeof(MergeViewModel).GetMethod("MergeFilesAsync",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        if (method == null)
            throw new InvalidOperationException("MergeFilesAsync method not found");

        var task = (Task)method.Invoke(viewModel, null);
        await task;
    }

    private void InvokeShowMergeLog(MergeViewModel viewModel)
    {
        var method = typeof(MergeViewModel).GetMethod("ShowMergeLog",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        if (method == null)
            throw new InvalidOperationException("ShowMergeLog method not found");

        method.Invoke(viewModel, null);
    }

    private void AddMatchedDocumentToViewModel(MergeViewModel viewModel, DocumentMatchStatus status, int documentId, bool hasMatch)
    {
        var matchedDoc = new duHastNet.DocManager.UI.Shared.ViewModels.Merge.MatchedDocs.MatchedDocumentViewModel
        {
            MatchStatus = status,
            MatchedDocumentId = hasMatch ? documentId : null,
            IncomingRevision = "B",
            IncomingFilePath = "C:\\Test\\file.pdf",
            MatchedDocumentNumber = hasMatch ? "DOC-001" : null
        };
        
        viewModel.DocumentMatchViewModel.MatchedDocuments.Add(matchedDoc);
    }

    #endregion
}
