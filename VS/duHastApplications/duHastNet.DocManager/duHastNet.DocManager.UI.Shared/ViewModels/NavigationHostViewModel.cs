using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.UI.Shared.Stores;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    public partial class NavigationHostViewModel : ObservableObject
    {
        private readonly DocManagerApi _docManagerApi;
        private readonly Manager _manager;
        private readonly MessageStore _messageStore;

        [ObservableProperty]
        private ObservableObject _currentViewModel;

        public NavigationHostViewModel(DocManagerApi docManagerApi, Manager manager, MessageStore messageStore)
        {
            _docManagerApi = docManagerApi;
            _manager = manager;
            _messageStore = messageStore;

            // Initialize with SettingsViewModel as the default view
            _currentViewModel = new SettingsViewModel(_docManagerApi, _manager, _messageStore);
        }
    }
}