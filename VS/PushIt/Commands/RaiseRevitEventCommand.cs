using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel;

namespace PushIt.Commands
{
    public class RaiseRevitEventCommand : CommandBase
    {
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;

        private readonly Stores.MessageStore _messageStore;
        private readonly Action _action;


        public RaiseRevitEventCommand(
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

        public override bool CanExecute(object parameter)
        {
            return true;
        }

        public override void Execute(object parameter)
        {
            
            try
            {
                _action?.Invoke();
                _messageStore.SetCurrentMessage("Data refreshed from Revit", Stores.MessageTypes.Information);

            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage($"Failed to refresh data {ex.Message}", Stores.MessageTypes.Error);
            }
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            //if (e.PropertyName == nameof(ViewModels.MakeReservationViewModel.Username) ||
            //    e.PropertyName == nameof(ViewModels.MakeReservationViewModel.FloorNumber))
            //{
            //    OnCanExecutedChanged();
            //}
        }
    }
}
