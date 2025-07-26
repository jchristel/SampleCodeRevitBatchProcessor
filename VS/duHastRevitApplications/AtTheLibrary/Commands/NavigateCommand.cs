using System;

namespace duHastNet.AtTheLibrary.Commands
{
    public class NavigateCommand : Utils.WPF.Commands.CommandBase
    {
        private readonly duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;
        private readonly Func<Utils.WPF.ViewModels.ViewModelBase> _createViewModel;

        public NavigateCommand(
            duHastNet.Utils.WPF.Stores.NavigationStore navigationStore,
            Func<Utils.WPF.ViewModels.ViewModelBase> createViewModel
        )
        {
            _navigationStore = navigationStore;
            _createViewModel = createViewModel;
        }

        public override void Execute(object parameter)
        {
            _navigationStore.CurrentViewModel = _createViewModel();
        }
    }
}
