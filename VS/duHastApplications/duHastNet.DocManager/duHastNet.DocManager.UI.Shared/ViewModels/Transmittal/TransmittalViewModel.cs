//
//License:
//
//
// Revit Batch Processor Sample Code
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

using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using duHastNet.Utils.WPF.Interfaces;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Transmittal;

public partial class TransmittalViewModel : AppViewModelBase
{
    #region Private Fields

    private readonly NavigationStore _navigationStore;
    private readonly Func<Merge.MergeViewModel> _createMergeViewModel;

    #endregion

    #region Public Properties

    public GlobalMessageViewModel GlobalMessageViewModel { get; }

    #endregion

    #region Constructor

    /// <summary>
    /// Creates a new instance of TransmittalViewModel.
    /// </summary>
    /// <param name="navigationStore">Navigation store for view navigation.</param>
    /// <param name="messageStore">Message store for global messages.</param>
    /// <param name="createMergeViewModel">Factory function to create MergeViewModel for back navigation.</param>
    /// <exception cref="ArgumentNullException">Thrown when any required parameter is null.</exception>
    public TransmittalViewModel(
        NavigationStore navigationStore,
        IMessageStore messageStore,
        Func<Merge.MergeViewModel> createMergeViewModel)
    {
        ArgumentNullException.ThrowIfNull(navigationStore);
        ArgumentNullException.ThrowIfNull(messageStore);
        ArgumentNullException.ThrowIfNull(createMergeViewModel);

        _navigationStore = navigationStore;
        _createMergeViewModel = createMergeViewModel;

        GlobalMessageViewModel = new GlobalMessageViewModel(messageStore);
        RegisterChild(GlobalMessageViewModel);
    }

    #endregion

    #region Observable Properties

    [ObservableProperty]
    private string _revisionsStatusMessage = string.Empty;

    [ObservableProperty]
    private string _documentsStatusMessage = string.Empty;

    [ObservableProperty]
    private string _exportStatusMessage = string.Empty;

    #endregion

    #region Commands

    /// <summary>
    /// Navigates back to the Merge view.
    /// </summary>
    [RelayCommand]
    private void Close()
    {
        _navigationStore.NavigateTo(_createMergeViewModel);
    }

    /// <summary>
    /// Exports the documents grid to CSV. Stub — not yet implemented.
    /// </summary>
    [RelayCommand]
    private void ExportToCsv()
    {
        // TODO: implement CSV export
    }

    #endregion

    #region Lifecycle

    public override void OnClosing()
    {
        base.OnClosing();
    }

    public override void Dispose()
    {
        base.Dispose();
    }

    #endregion
}
