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


using System;
using System.Collections.Generic;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHast.PushIt.Views;
using duHast.PushIt.Utilities;
using System.IO;
using System.Reflection;
using Revit.Async;


namespace duHast.PushIt
{
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class Main : IExternalCommand
    {
        Models.RevitDataModel _revitDataModel;
        duHast.Utils.WPF.Stores.NavigationStore _navigationStore;
        duHast.Utils.WPF.Stores.MessageStore _messageStore;
        
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
            _navigationStore = new duHast.Utils.WPF.Stores.NavigationStore();
            _messageStore = new duHast.Utils.WPF.Stores.MessageStore();
           
            // set up th revit data model
            _revitDataModel = new Models.RevitDataModel();

            //set up the logger
            //Utils.LoggerUtility.setupLogger();

            // Example log entry
            //Log.Information("Starting duHast.PushIt.");

            //Get application and document objects
            UIApplication uiapp = commandData.Application;
            Document doc = uiapp.ActiveUIDocument.Document;

            // load settings from file
            Models.Settings settings = SettingsUtils.LoadSettings();
            _revitDataModel.Settings = settings;

            //load room data into model
            _revitDataModel.LoadRoomsData();

            //get supported categories and load into the data model
            List<Models.CategoryDataModel> supportedCategories = Utilities.Revit.RevitCategoryObjectsConverter.ConvertToRevitCategoryObjects(doc);
            _revitDataModel.LoadCategoryData(supportedCategories);

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

        private ViewModels.RoomsSelectionViewModel CreateRoomsSelectionViewModel()
        {
            duHast.Utils.WPF.ViewModels.GlobalMessageViewModel _globa = new duHast.Utils.WPF.ViewModels.GlobalMessageViewModel(_messageStore);

            return new ViewModels.RoomsSelectionViewModel(
                _revitDataModel,
                _navigationStore,
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
