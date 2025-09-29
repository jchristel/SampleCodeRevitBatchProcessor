using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using duHastNet.DocManager.UI.Shared.Stores;

namespace duHastNet.DocManager.UI.Shared.ViewModels;

public partial class GlobalMessageViewModel : ObservableObject
{
    private readonly MessageStore _messageStore;

    public string CurrentMessage => _messageStore.CurrentMessage;
    public bool IsErrorMessage => _messageStore.CurrentMessageType == MessageTypes.Error;
    public bool IsInformationMessage => _messageStore.CurrentMessageType == MessageTypes.Information;
    public bool HasMessage => _messageStore.HasCurrentMessage;
    public double ProgressPercentage => _messageStore.ProgressPercentage;
    public bool IsTimerActive => _messageStore.IsTimerActive;

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

    private void OnStorePropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        // Forward all property changes from store to ViewModel
        if (e.PropertyName == nameof(MessageStore.CurrentMessage))
        {
            OnPropertyChanged(nameof(CurrentMessage));
            OnPropertyChanged(nameof(HasMessage));
        }
        else if (e.PropertyName == nameof(MessageStore.CurrentMessageType))
        {
            OnPropertyChanged(nameof(IsErrorMessage));
            OnPropertyChanged(nameof(IsInformationMessage));
        }
        else if (e.PropertyName == nameof(MessageStore.ProgressPercentage))
        {
            OnPropertyChanged(nameof(ProgressPercentage));
        }
        else if (e.PropertyName == nameof(MessageStore.IsTimerActive))
        {
            OnPropertyChanged(nameof(IsTimerActive));
        }
    }

    public GlobalMessageViewModel(MessageStore messageStore)
    {
        _messageStore = messageStore;
        _messageStore.PropertyChanged += OnStorePropertyChanged;
    }

    public void Dispose()
    {
        _messageStore.PropertyChanged -= OnStorePropertyChanged;
    }
}