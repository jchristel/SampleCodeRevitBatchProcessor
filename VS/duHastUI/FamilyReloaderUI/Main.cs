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

using System;
using System.IO;
using System.Collections.Generic;
using duHastNet.Utils.WPF.Stores;

namespace duHastNet.UI.FamilyReloaderUI
{
    public class Main
    {
        duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
        duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;

        Models.FamiliesDataModel _familiesDataModel;
        Models.Settings _settings;

        public Main(List<Models.RevitFamily> revitFamilies)
        {
            // do some sanity checking before proceeding:
            // do we have any families?
            if (revitFamilies == null || revitFamilies.Count == 0)
            { throw new System.Exception("No families supplied."); }

            //set up stores
            _navigationStore = new NavigationStore();
            _messageStore = new MessageStore();

            //set up a setting object
            //load settings from file is done in the view model
            _settings = new Models.Settings();

            //set up the families data model
            _familiesDataModel = new Models.FamiliesDataModel(
                revitFamilies: revitFamilies,
                settings: _settings
            );

            // build a file path for the log file using the settings directory and the current date
            string logFilePath = Path.Combine(Utils.SettingsUtils.settingsDirectory, "log_familyReloader_" + DateTime.Now.ToString("yyyy-MM-dd") + ".txt");
            // set up the logger
            _familiesDataModel.InitialiseLogger(logFilePath);

        }

        // <summary>
        /// Function which will display the families reload selection window and return the selected families to the caller
        /// </summary>
        public duHastNet.UI.FamilyReloaderUI.Utils.ReloadSelection Execute()
        {
            //create the settings view model
            var settingsViewModel = CreateFamiliesSelectionViewModel();

            //set the current view model to the settings view model
            _navigationStore.CurrentViewModel = settingsViewModel;

            //show the main window
            Views.MainWindow mainWindow = new Views.MainWindow(_settings)
            {
                DataContext = new ViewModels.MainWindowViewModel(_navigationStore)
            };

            mainWindow.ShowDialog();

            //store settings
            Utils.SettingsUtils.SaveSettings(_familiesDataModel.Settings);

            // get families to reload
            var familiesToRelaod = _familiesDataModel.GetFamiliesToReload();
            var reloadSelection = new Utils.ReloadSelection();
           
            if (familiesToRelaod != null)
            {
                foreach (var family in familiesToRelaod)
                {
                    reloadSelection.AddFamily(family);
                }
            }

            // determine whether all types have to be reloaded
            reloadSelection.LoadAllFamilyTypesOnReload = _familiesDataModel.Settings.LoadAllFamilyTypesOnReload;

            return reloadSelection;
        }


        /// <summary>
        /// Creates the document selection view model.
        /// </summary>
        /// <returns></returns>
        private ViewModels.FamiliesSelectionViewModel CreateFamiliesSelectionViewModel()
        {
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel _globalMessageViewModel = new duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel(_messageStore);

            return new ViewModels.FamiliesSelectionViewModel(
                _familiesDataModel,
                //_navigationStore,
                _globalMessageViewModel,
                _messageStore);
        }
    }
}
