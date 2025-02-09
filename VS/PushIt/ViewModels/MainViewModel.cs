using PushIt.Utilities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace PushIt.ViewModels
{
    public class MainViewModel:ViewModelBase
    {

        private readonly Stores.NavigationStore _navigationStore;
        private readonly RevitExternalEventHandlerManager _eventManager;
        public ViewModelBase CurrentViewModel => _navigationStore.CurrentViewModel;

        public MainViewModel(Stores.NavigationStore navigationStore, RevitExternalEventHandlerManager eventManager)
        {
            _navigationStore = navigationStore;
            _navigationStore.CurrentViewModelChanged += OnCurrentViewModelChanged;
            _eventManager = eventManager;
        }

        private void OnCurrentViewModelChanged()
        {
            OnPropertyChanged(nameof(CurrentViewModel));
        }

        public override void OnClosing()
        {
            // Custom closing logic for RoomsSelectionViewModel
            _eventManager.DisposeEvents();
            base.OnClosing();
        }
    }
}
