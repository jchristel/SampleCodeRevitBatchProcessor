using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel;
using PushIt.Utilities;

namespace PushIt.ViewModels
{
    public class ViewModelBase : INotifyPropertyChanged, ICloseable
    {

        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        public void RaisePropertyChanged(string name)
        {
            OnPropertyChanged(name);
        }

        public virtual void OnClosing()
        {
            // Override this method in derived classes to perform clean-up operations
        }
    }
}
