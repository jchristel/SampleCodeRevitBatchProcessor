using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Commands
{
    public class PushSingleRoomDataToRevit: CommandBase
    {
        private readonly Models.RevitDataModel _revitDataModel;
        private readonly ViewModels.RoomsSelectionViewModel _roomsSelectionViewModel;
        //private readonly Services.NavigationService _reservationViewNavigationService;

        private readonly Stores.MessageStore _messageStore;
        private readonly Action _action;


        public override bool CanExecute(object parameter)
        {
            // check if IsMatchingRevitRoomsEmpty is true and call the base CanExecute method
            return _roomsSelectionViewModel.IsMatchingRevitRoomsEmpty && base.CanExecute(parameter);
        }

        public override void Execute(object parameter)
        {
            try
            {
                _action?.Invoke();
                _messageStore.SetCurrentMessage("Pushed data into Revit room", Stores.MessageTypes.Information);

            }
            catch (Exception ex)
            {
                _messageStore.SetCurrentMessage($"Failed to push data into Revit room {ex.Message}", Stores.MessageTypes.Error);
            }
        }

        private void OnViewModelPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            // check if the property that changed is the one that we are interested in
            if (e.PropertyName == nameof(ViewModels.RoomsSelectionViewModel.IsMatchingRevitRoomsEmpty))
            {
                OnCanExecutedChanged();
            }
        }

        public PushSingleRoomDataToRevit(
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
