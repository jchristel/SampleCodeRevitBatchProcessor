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
using duHastNet.DocManager.UI.Shared.Interfaces;
using duHastNet.DocManager.UI.Shared.Stores;
using System.ComponentModel;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

public partial class GlobalMessageViewModel : ObservableObject, ICloseable, IDisposable
{
    private readonly IMessageStore _messageStore;

    public string CurrentMessage => _messageStore.CurrentMessage;
    public bool IsErrorMessage => _messageStore.CurrentMessageType == MessageTypes.Error;
    public bool IsInformationMessage => _messageStore.CurrentMessageType == MessageTypes.Information;
    public bool IsWarningMessage => _messageStore.CurrentMessageType == MessageTypes.Warning;
    public bool HasMessage => _messageStore.HasCurrentMessage;
    public double ProgressPercentage => _messageStore.ProgressPercentage;
    public bool IsTimerActive => _messageStore.IsTimerActive;
    public int PendingMessageCount => _messageStore.PendingMessageCount;
    public bool HasPendingMessages => _messageStore.HasPendingMessages;

    [RelayCommand]
    private void ClearMessage()
    {
        _messageStore.ClearCurrentMessage();
    }

    [RelayCommand]
    private void PauseTimer()
    {
        _messageStore.PauseDismissTimer();
    }

    [RelayCommand]
    private void ResumeTimer()
    {
        _messageStore.ResumeDismissTimer(5); // Resume with default 5 seconds
    }

    private void OnStorePropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        // Forward all property changes from store to ViewModel
        if (e.PropertyName == nameof(_messageStore.CurrentMessage))
        {
            OnPropertyChanged(nameof(CurrentMessage));
            OnPropertyChanged(nameof(HasMessage));
        }
        else if (e.PropertyName == nameof(_messageStore.CurrentMessageType))
        {
            OnPropertyChanged(nameof(IsErrorMessage));
            OnPropertyChanged(nameof(IsInformationMessage));
            OnPropertyChanged(nameof(IsWarningMessage));
        }
        else if (e.PropertyName == nameof(_messageStore.ProgressPercentage))
        {
            OnPropertyChanged(nameof(ProgressPercentage));
        }
        else if (e.PropertyName == nameof(_messageStore.IsTimerActive))
        {
            OnPropertyChanged(nameof(IsTimerActive));
        }
        else if (e.PropertyName == nameof(_messageStore.PendingMessageCount))
        {
            OnPropertyChanged(nameof(PendingMessageCount));
            OnPropertyChanged(nameof(HasPendingMessages));
        }
    }

    public GlobalMessageViewModel(IMessageStore messageStore)
    {
        _messageStore = messageStore;
        
        // Subscribe to property changes if the store implements INotifyPropertyChanged
        if (_messageStore is INotifyPropertyChanged notifyPropertyChanged)
        {
            notifyPropertyChanged.PropertyChanged += OnStorePropertyChanged;
        }
    }

    public void OnClosing()
    {
        // Save any message state if needed
        // Stop any timers that should stop when navigating away
        _messageStore.PauseDismissTimer();
    }

    public void Dispose()
    {
        // Unsubscribe from property changes if we subscribed
        if (_messageStore is INotifyPropertyChanged notifyPropertyChanged)
        {
            notifyPropertyChanged.PropertyChanged -= OnStorePropertyChanged;
        }
    }
}
