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
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;
using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.Utils.WPF.Interfaces;
using duHastNet.Utils.WPF.Stores;
using duHastNet.DocManager.UI.Shared.ViewModels.Merge;
using System.Reflection;

namespace duHastNet.DocManager.UI.Shared.Tests.ViewModels.Merge;

/// <summary>
/// Tests for MergeViewModel_ExportMetData partial class
/// Covers metadata export operations during merge
/// </summary>
[TestFixture]
public class MergeViewModelTests_ExportMetData
{
    private Mock<IDocManagerApi> _mockDocManagerApi;
    private MessageStore _messageStore;
    private NavigationStore _navigationStore;
    private Manager _manager;
    private CurrentFolderManager _currentFolderManager;
    private Mock<IDialogService> _mockDialogService;
    private Mock<Func<duHastNet.DocManager.UI.Shared.ViewModels.Settings.SettingsViewModel>> _mockCreateViewModel;
    private CloudDocumentManager _cloudDocumentManager;

    [SetUp]
    public void Setup()
    {
        _mockDocManagerApi = new Mock<IDocManagerApi>();
        _messageStore = new MessageStore();
        _navigationStore = new NavigationStore();
        
        _cloudDocumentManager = new CloudDocumentManager();
        _manager = new Manager(_cloudDocumentManager);
        
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

    #region ExportMetadataAsync Tests

    [Test]
    public void ExportMetadataAsync_MethodExists()
    {
        // Arrange & Act
        var method = typeof(MergeViewModel).GetMethod("ExportMetadataAsync",
            BindingFlags.NonPublic | BindingFlags.Instance);

        // Assert
        Assert.That(method, Is.Not.Null, "ExportMetadataAsync method should exist");
        Assert.That(method.ReturnType, Is.EqualTo(typeof(Task)), "ExportMetadataAsync should return Task");
    }

    [Test]
    public void ExportMetadataAsync_WithCloudManagerDisabled_CanBeInvoked()
    {
        // Arrange
        var viewModel = CreateViewModel();
        _cloudDocumentManager.CloudDocumentManagerEnabled = false;

        // Act & Assert
        Assert.DoesNotThrowAsync(async () => await InvokeExportMetadataAsync(viewModel));
    }

    [Test]
    public void ExportMetadataAsync_WithNoMetaDataMapper_CanBeInvoked()
    {
        // Arrange
        var viewModel = CreateViewModel();
        _cloudDocumentManager.CloudDocumentManagerEnabled = true;
        _cloudDocumentManager.MetaDataMapper = null;

        // Act & Assert
        Assert.DoesNotThrowAsync(async () => await InvokeExportMetadataAsync(viewModel));
    }

    [Test]
    public void ExportMetadataAsync_WithNoMappings_CanBeInvoked()
    {
        // Arrange
        var viewModel = CreateViewModel();
        _cloudDocumentManager.CloudDocumentManagerEnabled = true;
        _cloudDocumentManager.MetaDataMapper = new MetaDataMapperAconex();

        // Act & Assert
        Assert.DoesNotThrowAsync(async () => await InvokeExportMetadataAsync(viewModel));
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

    private async Task InvokeExportMetadataAsync(MergeViewModel viewModel)
    {
        var method = typeof(MergeViewModel).GetMethod("ExportMetadataAsync",
            BindingFlags.NonPublic | BindingFlags.Instance);
        
        if (method == null)
            throw new InvalidOperationException("ExportMetadataAsync method not found");

        var task = (Task)method.Invoke(viewModel, null);
        await task;
    }

    private void SetupForExport(MergeViewModel viewModel)
    {
        _cloudDocumentManager.CloudDocumentManagerEnabled = true;
        var mapper = new MetaDataMapperAconex();
        mapper.MetaDataMap.Add(new MetaDataMap 
        { 
            MetaFieldName = "Test Field",
            DocumentPropertyName = "Number"
        });
        _cloudDocumentManager.MetaDataMapper = mapper;
    }

    #endregion
}
