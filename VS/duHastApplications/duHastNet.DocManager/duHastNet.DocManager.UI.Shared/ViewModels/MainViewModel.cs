using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using duHastNet.DocManager.Core.Services.Api;

namespace duHastNet.DocManager.UI.Shared.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        private readonly DocManagerApi _docManagerApi;
        private readonly duHastNet.DocManager.Core.Models.Manager _manager;
        private readonly duHastNet.DocManager.UI.Shared.Stores.MessageStore _messageStore;
        ObservableObject _currentViewModel;
        
        private ObservableObject CurrentViewModel 
        { 
            get => _currentViewModel; 
        }

        public MainViewModel(DocManagerApi docManagerApi, Core.Models.Manager manager, Stores.MessageStore messageStore)
        {
            _docManagerApi = docManagerApi;
            _manager = manager;
            _messageStore = messageStore;

            _currentViewModel = new SettingsViewModel(_docManagerApi, _manager, messageStore: _messageStore);
        }
    }
}
