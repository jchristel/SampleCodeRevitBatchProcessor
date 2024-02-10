using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Windows.Input;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Nodify;

namespace Launcher_GUI.ViewModels
{
    public class EditorViewModel
    {
        public ICommand DisconnectConnectorCommand { get; }

        public PendingConnectionViewModel PendingConnection { get; }
        public ObservableCollection<NodeViewModel> Nodes { get; } = new ObservableCollection<NodeViewModel>();
        public ObservableCollection<ConnectionViewModel> Connections { get; } = new ObservableCollection<ConnectionViewModel>();


        public EditorViewModel()
        {

            DisconnectConnectorCommand = new DelegateCommand<ConnectorViewModel>(connector =>
            {
                var connection = Connections.First(x => x.Source == connector || x.Target == connector);
                connection.Source.IsConnected = false;  // This is not correct if there are multiple connections to the same connector
                connection.Target.IsConnected = false;
                Connections.Remove(connection);
            });

            PendingConnection = new PendingConnectionViewModel(this);

            // set up nodes

            var welcome = new NodeViewModel
            {
                Title = "Welcome",
                Input = new ObservableCollection<ConnectorViewModel>
                {
                    new ConnectorViewModel
                    {
                        Title = "In"
                    }
                },
                Output = new ObservableCollection<ConnectorViewModel>
                {
                    new ConnectorViewModel
                    {
                        Title = "Out"
                    }
                }
            };

            var nodify = new NodeViewModel
            {
                Title = "To Nodify",
                Input = new ObservableCollection<ConnectorViewModel>
                {
                    new ConnectorViewModel
                    {
                        Title = "In"
                    }
                }
            };

            var thirdSample = new NodeViewModel
            {
                Title = "To Nodify or not?",
                Input = new ObservableCollection<ConnectorViewModel>
                {
                    new ConnectorViewModel
                    {
                        Title = "In"
                    }
                }
            };

            // add nodes to model
            Nodes.Add(welcome);
            Nodes.Add(nodify);
            Nodes.Add(thirdSample);

            // create a connection between nodes
            Connections.Add(new ConnectionViewModel(welcome.Output[0], nodify.Input[0]));
        }

        public void Connect(ConnectorViewModel source, ConnectorViewModel target)
        {
            Connections.Add(new ConnectionViewModel(source, target));
        }
    }
}
