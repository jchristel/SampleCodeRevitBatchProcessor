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
using Autodesk.Revit.DB.Architecture;
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

        /// <summary>
        /// Initializes application state, loads settings and data, and displays the main window for the PushIt add-in
        /// within a Revit session.
        /// This function can be called from ironpython (i.e. pyRevit)
        /// </summary>
        /// <remarks>This method should be called from within a valid Revit API context. It sets up
        /// required data models, logging, and user interface components for the PushIt workflow. The method is intended
        /// for internal use as part of the add-in's startup sequence.</remarks>
        /// <param name="uiapp">The current Revit application context used to access the active document and application services. Cannot be
        /// null.</param>
        /// <returns>A value indicating whether the operation completed successfully. Returns Result.Succeeded if initialization
        /// and window display succeed.</returns>
        public Result ExecuteInternal(UIApplication uiapp)
        {
            // Revit Async version 2.x.x
            RevitTask.Initialize(uiapp);

            //set up stores
            _navigationStore = new duHastNet.Utils.WPF.Stores.NavigationStore();
            _messageStore = new duHastNet.Utils.WPF.Stores.MessageStore();
            _stateStore = new duHastNet.Utils.WPF.Stores.StateStore();

            // set up th revit data model
            _revitDataModel = new Models.RevitDataModel();

            //set up the logger
            string logFilePath = Path.Combine(Utilities.SettingsUtils.settingsDirectory,
                "log_pushit_" + DateTime.Now.ToString("yyyy-MM-dd") + ".txt");
            _revitDataModel.InitialiseLogger(logFilePath);

            _revitDataModel.LogMessages(new List<(string, duHastNet.Utils.WPF.Stores.MessageTypes)>
                {
                    ("Starting duHastNet.PushIt.", duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                });

            //Get document
            Document doc = uiapp.ActiveUIDocument.Document;

            // store the document title so the UI can display it
            _revitDataModel.RevitDocumentTitle = doc.Title;

            // load settings from file
            Models.Settings settings = SettingsUtils.LoadSettings();
            _revitDataModel.Settings = settings;

            // load room data into model
            // Wrapped in try/catch so a data source error (e.g. incomplete drofus
            // credentials, missing CSV file) does not prevent the window from opening.
            // The error is queued into the message store and shown in the banner once
            // the UI is displayed.
            try
            {
                _revitDataModel.LoadRoomsData();
            }
            catch (Exception ex)
            {
                _messageStore.EnqueueMessage(
                    $"Could not load room data on startup: {ex.Message}",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }

            //get all supported categories
            List<Models.CategoryDataModel> supportedCategories =
                Utilities.Revit.RevitCategoryObjectsConverter.ConvertToRevitCategoryObjects(doc);
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
        /// Executes the external command using the provided command data and element set.
        /// </summary>
        /// <param name="commandData">An object that contains contextual information about the external command, including access to the
        /// application and active document.</param>
        /// <param name="message">A message that can be set by the command to provide additional information to the user if execution fails.</param>
        /// <param name="elements">A set of elements that can be used to highlight or select elements in the user interface if the command
        /// fails.</param>
        /// <returns>A Result value indicating the outcome of the command execution.</returns>
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            // call execute internal with the application as arg
            return ExecuteInternal(commandData.Application);

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
