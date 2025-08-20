using duHastNet.Utils.WPF.Interfaces;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;

    namespace duHastNet.Utils.WPF.ViewModels
    {
        /// <summary>
        /// Base class for ViewModels - simple and focused on core ViewModel functionality
        /// </summary>
        public class ViewModelBase : INotifyPropertyChanged, ICloseable
        {
            #region INotifyPropertyChanged

            public event PropertyChangedEventHandler PropertyChanged;

            protected void OnPropertyChanged(string propertyName)
            {
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
            }

            public void RaisePropertyChanged(string name)
            {
                OnPropertyChanged(name);
            }

            #endregion

            #region ICloseable

            /// <summary>
            /// list of nested view models
            /// </summary>
            protected List<ICloseable> _childViewModels = new List<ICloseable>();

            protected void RegisterChild(ICloseable child)
            {
                _childViewModels.Add(child);
            }

            public virtual void OnClosing()
            {
                // Close all children first
                foreach (var child in _childViewModels)
                {
                    child.OnClosing();
                }
                _childViewModels.Clear();
            }

            public virtual void Dispose()
            {
            }

            #endregion
        }
    }