using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using duHast.Utils.WPF.ViewModels;

namespace WpfSandpit.ViewModels
{
    public class testViewModel :ViewModelBase
    {
        //flag to indicate if safety off mode is enabled
        private bool _safetyOffMode = false;
        //default button text for safety off mode
        private string _safetyOffButtonText = "Safety on";

        // flag indicating whether the view model is waiting for a Revit command to finish
        private bool _isWaitingForRevitCommandToFinish;
        public bool IsWaitingForRevitCommandToFinish
        {
            get => _isWaitingForRevitCommandToFinish;
            set
            {
                _isWaitingForRevitCommandToFinish = value;
                OnPropertyChanged(nameof(IsWaitingForRevitCommandToFinish));
            }
        }

        //is UI in safety off mode ? (rooms can be pushed multiple times)
        public bool SafetyOffMode
        {
            get => _safetyOffMode;
            set
            {
                _safetyOffMode = value;

                // set the button text
                _safetyOffButtonText = value ? "Safety off" : "Safety on";

                //set the revit is busy flag
                IsWaitingForRevitCommandToFinish = value;

                // notify ui of changes
                OnPropertyChanged(nameof(SafetyOffButtonText));
                OnPropertyChanged(nameof(SafetyOffMode));
            }
        }

        //button text for safety off mode
        public string SafetyOffButtonText
        {
            get => _safetyOffButtonText;
        }

    }
}
