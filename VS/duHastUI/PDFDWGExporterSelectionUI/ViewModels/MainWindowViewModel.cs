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
using duHastNet.Utils.WPF.Stores;
using duHastNet.Utils.WPF.ViewModels;
using System.ComponentModel;

namespace duHastNet.UI.PDFDWGExporterSelectionUI.ViewModels
{
    public class MainWindowViewModel : ViewModelBase
    {
        private readonly duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;
        public ObservableObject? CurrentViewModel => _navigationStore.CurrentViewModel;

        public MainWindowViewModel(duHastNet.Utils.WPF.Stores.NavigationStore navigationStore)
        {
            _navigationStore = navigationStore;
            _navigationStore.PropertyChanged += OnNavigationStorePropertyChanged;
        }

        private void OnNavigationStorePropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(NavigationStore.CurrentViewModel))
            {
                OnPropertyChanged(nameof(CurrentViewModel));
            }
        }

        public override void OnClosing()
        {
            System.Diagnostics.Debug.WriteLine("MainWindowViewModel.OnClosing() called");

            // Notify the navigation store to close current view model
            _navigationStore.NotifyClosing();

            // Event cleanup moved to DisposeManaged()
            base.OnClosing();
        }

        public override void Dispose()
        {
            System.Diagnostics.Debug.WriteLine("MainWindowViewModel.Dispose() called");

            // Unsubscribe from navigation store events
            if (_navigationStore != null)
            {
                _navigationStore.PropertyChanged -= OnNavigationStorePropertyChanged;
            }

            base.Dispose();
        }
    }
}
