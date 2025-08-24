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


using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHastNet.PushIt.Utilities;
using duHastNet.PushIt.Views;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;


namespace duHastNet.PushIt
{
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class Main : IExternalCommand
    {
        Models.RevitDataModel _revitDataModel;
        duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;
        duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
        duHastNet.Utils.WPF.Stores.StateStore _stateStore;

        static Main()
        {
            //assembly resolver in order for this plugin to be used form pyRevit invoke.button
            AppDomain.CurrentDomain.AssemblyResolve += new ResolveEventHandler(AssemblyResolver.ResolveAssembly);
        }


        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {

            // Revit Async version 2.x.x
            RevitTask.Initialize(commandData.Application);

            //set up stores
            _navigationStore = new duHastNet.Utils.WPF.Stores.NavigationStore();
            _messageStore = new duHastNet.Utils.WPF.Stores.MessageStore();
            _stateStore = new duHastNet.Utils.WPF.Stores.StateStore();

            // set up th revit data model
            _revitDataModel = new Models.RevitDataModel();

            //set up the logger
            // build a file path for the log file using the settings directory and the current date
            string logFilePath = Path.Combine(Utilities.SettingsUtils.settingsDirectory, "log_pushit_" + DateTime.Now.ToString("yyyy-MM-dd") + ".txt");
            _revitDataModel.InitialiseLogger(logFilePath);

            // Example log entry
            _revitDataModel.LogMessages(new List<(string, duHastNet.Utils.WPF.Stores.MessageTypes)> { ("Starting duHastNet.PushIt.", duHastNet.Utils.WPF.Stores.MessageTypes.Log) });

            //Get application and document objects
            UIApplication uiapp = commandData.Application;
            Document doc = uiapp.ActiveUIDocument.Document;

            // load settings from file
            Models.Settings settings = SettingsUtils.LoadSettings();
            //  settings in data model, this will automatically add enables categories to the category container in the 
            // data model
            _revitDataModel.Settings = settings;

            //load room data into model
            _revitDataModel.LoadRoomsData();

            //get all supported categories and load into the data model ( a supported category is not an enabled category!)
            List<Models.CategoryDataModel> supportedCategories = Utilities.Revit.RevitCategoryObjectsConverter.ConvertToRevitCategoryObjects(doc);
            _revitDataModel.LoadSupportedCategoryData(supportedCategories);

            //set up the navigation store
            _navigationStore.CurrentViewModel = CreateRoomsSelectionViewModel();

            //show the main window
            MainWindow mainWindow = new MainWindow(settings)
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };

            mainWindow.Show();

            return Result.Succeeded;

        }

        /// <summary>
        /// create the RoomsSelectionViewModel
        /// </summary>
        private ViewModels.RoomsMainViewModel CreateRoomsSelectionViewModel()
        {
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel _globa = new duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel(_messageStore);

            return new ViewModels.RoomsMainViewModel(
                _revitDataModel,
                _navigationStore,
                _stateStore,
                _messageStore,
                _globa);
        }

        //assembly resolver static method
        /// <summary>
        /// attempts to resolve the assembly from the local app data/duhast/bin directory
        /// </summary>
        public static class AssemblyResolver
        {
            public static System.Reflection.Assembly ResolveAssembly(object sender, ResolveEventArgs args)
            {
                try
                {
                    //get the local app data path
                    string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                    string duHastBinDirectory = Path.Combine(localAppDataPath, "duHast", "bin");

                    string assemblyName = new AssemblyName(args.Name).Name;

                    // Check if the assembly name ends with ".resources"
                    if (assemblyName.EndsWith(".resources"))
                    {
                        // Strip the ".resources" suffix
                        assemblyName = assemblyName.Substring(0, assemblyName.Length - ".resources".Length);
                    }

                    string assemblyPath = Path.Combine(duHastBinDirectory, new AssemblyName(args.Name).Name + ".dll");
                    return File.Exists(assemblyPath) ? System.Reflection.Assembly.LoadFrom(assemblyPath) : null;

                }
                catch (Exception)
                {
                    return null;
                }
            }
        }
    }
}
