using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Commands
{
    public class ReloadDataCommand : CommandBase
    {
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;

        private readonly Stores.MessageStore _messageStore;
        private readonly Action _action;


        public override bool CanExecute(object parameter)
        {
            // check if DataFilePath is a valid path and call the base CanExecute method
            bool isValidFilePath = true;
            try
            {
                System.IO.Path.GetFullPath(_roomsSelectionViewModel.DataFilePath);
            }
            catch (Exception)
            {
                isValidFilePath = false;
            }

            return isValidFilePath && base.CanExecute(parameter);
        }

        public override void Execute(object parameter)
        {
            try
            {
                _action?.Invoke();
                _messageStore.SetCurrentMessage("Reloaded data", Stores.MessageTypes.Information);

            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage($"Failed to reload data {ex.Message}", Stores.MessageTypes.Error);
            }
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.DataFilePath))
            {
                OnCanExecutedChanged();
            }
        }

        public ReloadDataCommand(
            ViewModels.RoomsSelectionViewModel roomsSelectionViewModel,
            Models.RevitDataModel revitDataModel,
            Stores.MessageStore messageStore,
            Action action
            )
        {
            _revitDataModel = revitDataModel;
            _roomsSelectionViewModel = roomsSelectionViewModel;
            _messageStore = messageStore;
            _action = action;
            _roomsSelectionViewModel.PropertyChanged += OnViewModelPropertyChanged;
        }
    }
}
