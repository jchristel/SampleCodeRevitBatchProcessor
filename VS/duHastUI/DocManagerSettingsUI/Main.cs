//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2026, Jan Christel
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

using duHastNet.UI.DocManagerSettingsUI.Views;
using duHastNet.Utils.WPF.Stores;

namespace duHastNet.UI.DocManagerSettingsUI
{
    public class Main
    {
        readonly duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
        readonly Models.ExportDataModel _exportDataModel;
        readonly Utils.Settings _settings;

        /// <summary>
        /// Constructor for the Main class.
        /// </summary>
        /// <param name="currentDocumentNumberString">Current PDF export string</param>
        /// <param name="parameterNames">List of parameter names associated to sheets</param>
        /// 
        public Main(
            string currentDocumentNumberString,
            List<string> parameterNames
            )
        {
            //set up stores
            _messageStore = new MessageStore();

            //set up a setting object
            _settings = new Utils.Settings(
                documentNumberString: currentDocumentNumberString,
                databasePath: string.Empty
            );

            //set up the export data model
            _exportDataModel = new Models.ExportDataModel
            {
                //set the settings object to the data model
                Settings = _settings
            };

            // add the parameter names to the data model
            foreach (var parameterName in parameterNames)
            {
                _exportDataModel.AddParameterName(parameterName);
            }
        }

        /// <summary>
        /// Function which will display the settings window and return the pdf and dwg export settings to the caller
        /// </summary>
        public Utils.Settings Execute()
        {

            //create the settings view model
            var settingsViewModel = CreateSettingsViewModel();

            //show the main window
            MainWindow mainWindow = new(_settings)
            {
                DataContext = new ViewModels.MainWindowViewModel(settingsViewModel)
            };

            mainWindow.ShowDialog();

            // return the settings object
            return mainWindow.Settings;
        }

        /// <summary>
        /// Creates the settings view model.
        /// </summary>
        /// <returns></returns>
        private ViewModels.SettingsViewModel CreateSettingsViewModel()
        {
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel _globalMessageViewModel = new(_messageStore);

            return new ViewModels.SettingsViewModel(
                _exportDataModel,
                _globalMessageViewModel,
                _messageStore);
        }
    }
}
