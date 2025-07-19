//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//


using duHastNet.Utils.WPF.Interfaces;
using System.Collections.Generic;
using System.ComponentModel;


namespace duHastNet.Utils.WPF.ViewModels
{
    public class ViewModelBase : INotifyPropertyChanged, duHastNet.Utils.WPF.Interfaces.ICloseable
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


        /// <summary>
        /// list of nested view models
        /// </summary>
        protected List<ICloseable> _childViewModels = [];

        protected void RegisterChild(ICloseable child)
        {
            _childViewModels.Add(child);
        }
        public virtual void OnClosing()
        {
            // Override this method in derived classes to perform clean-up operations

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
    }
}
