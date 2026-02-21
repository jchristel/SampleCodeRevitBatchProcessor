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

using CommunityToolkit.Mvvm.ComponentModel;
using System.ComponentModel;

namespace duHastNet.AtTheLibrary.ViewModels
{
    public class MainViewModel : Utils.WPF.ViewModels.ViewModelBase
    {

        private readonly Utils.WPF.Stores.NavigationStore _navigationStore;

        // Return type changed from ViewModelBase to ObservableObject?
        // NavigationStore.CurrentViewModel is now typed ObservableObject? (Community Toolkit)
        public ObservableObject? CurrentViewModel => _navigationStore.CurrentViewModel;

        public MainViewModel(Utils.WPF.Stores.NavigationStore navigationStore)
        {
            _navigationStore = navigationStore;
            // CurrentViewModelChanged event no longer exists on NavigationStore.
            // Subscribe to PropertyChanged and filter by property name instead.
            _navigationStore.PropertyChanged += OnNavigationStorePropertyChanged;
        }

        private void OnNavigationStorePropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(_navigationStore.CurrentViewModel))
            {
                OnPropertyChanged(nameof(CurrentViewModel));
            }
        }

        public override void OnClosing()
        {
            // Notify the navigation store to close current view model
            _navigationStore.NotifyClosing();
            // Unsubscribe from PropertyChanged (was CurrentViewModelChanged before migration)
            _navigationStore.PropertyChanged -= OnNavigationStorePropertyChanged;
            base.OnClosing();
        }
    }
}