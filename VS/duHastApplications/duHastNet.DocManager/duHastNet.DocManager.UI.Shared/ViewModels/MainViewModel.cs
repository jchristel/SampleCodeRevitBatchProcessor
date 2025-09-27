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

        ObservableObject _currentViewModel;
        
        private ObservableObject CurrentViewModel 
        { 
            get => _currentViewModel; 
        }

        public MainViewModel(DocManagerApi docManagerApi)
        {
            _docManagerApi = docManagerApi;
            _currentViewModel = new SettingsViewModel(_docManagerApi);
        }
    }
}
