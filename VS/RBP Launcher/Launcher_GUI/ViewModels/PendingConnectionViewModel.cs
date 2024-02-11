using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using Launcher_GUI.ViewModels;
using System.Windows;

namespace Launcher_GUI.ViewModels
{
    public class PendingConnectionViewModel : ObservableObject
    {
        private ConnectorViewModel _source = default!;
        public ConnectorViewModel Source
        {
            get => _source;
            set => SetProperty(ref _source, value);
        }

        private ConnectorViewModel? _target;
        public ConnectorViewModel? Target
        {
            get => _target;
            set => SetProperty(ref _target, value);
        }

        private bool _isVisible;
        public bool IsVisible
        {
            get => _isVisible;
            set => SetProperty(ref _isVisible, value);
        }

        private Point _targetLocation;

        public Point TargetLocation
        {
            get => _targetLocation;
            set => SetProperty(ref _targetLocation, value);
        }
    }
}
