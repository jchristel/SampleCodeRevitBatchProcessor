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

using duHastNet.DocManager.Revit;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using System.Reflection;
using System.IO;
using duHastNet.Utils;

namespace duHastNet.DocManager.Revit
{
    public class Main : IExternalCommand
    {
        Models.Revit.RevitDataModel _revitDataModel;
        duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;
        duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
        duHastNet.Utils.WPF.Stores.StateStore _stateStore;

        Revit.Models.Settings _settings;

        static Main()
        {
            //assembly resolver in order for this plugin to be used form pyRevit invoke.button
            AppDomain.CurrentDomain.AssemblyResolve += new ResolveEventHandler(AssemblyResolver.ResolveAssembly);
        }

        public Result ExecuteInternal(UIApplication uiapp, Models.Revit.RevitDataModel revitDataModel)
        {
            //set up stores
            _navigationStore = new duHastNet.Utils.WPF.Stores.NavigationStore();
            _messageStore = new duHastNet.Utils.WPF.Stores.MessageStore();
            _stateStore = new duHastNet.Utils.WPF.Stores.StateStore();

            // set up the revit data model
            // check if this is called from the Execute method ( there is a data model allready) or if the data model is already created and passed in (e.g. from pyRevit) and set it accordingly
            _revitDataModel ??= revitDataModel;
               
            //setup logger and delete old log files 
            //needs to happen after data model is created so that we can display log messages in the banner
            SetupLog();

            // log the start of the command execution
            // log the loaded revisions and sheets counts
            _revitDataModel.LogMessages(
                [
                    ("Starting duHastNet.DocManager.Revit.", duHastNet.Utils.WPF.Stores.MessageTypes.Information),
                    ($"Loaded {_revitDataModel.GetRevisions().Count} revision(s) from Revit model: {_revitDataModel.ModelName}.", duHastNet.Utils.WPF.Stores.MessageTypes.Information),
                    ($"Loaded {_revitDataModel.GetSheets().Count} sheet(s) from Revit model: {_revitDataModel.ModelName}.", duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                ]);


            // load settings from file, these are purely UI related and not the same as the settings stored in the revit model which are part of the data model, but we need them to set up the main window
            _settings = duHastNet.DocManager.Revit.Utilities.SettingsUtils.LoadSettings();
            //store the json string from the data model in the settings for now, so that we can pass it to the main window and then to the viewmodels
            _settings.JsonString = _revitDataModel.SettingsAsJson;

            //process each sheet: build the document number as per past in settings
            _revitDataModel.AddFullDocumentNumber(_settings.DocumentNumberingJsonString);

            //set up the navigation store
            ViewModels.PyRevitDocumentListViewModel pocVm = CreatePOCViewModel();
            _navigationStore.CurrentViewModel = pocVm;

            //show the main window
            duHastNet.DocManager.Revit.Views.MainWindow mainWindow = new(_settings)
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };

            mainWindow.Show();

            return Result.Succeeded;
        }

        /// <summary>
        /// Executes the external command using the provided command data and element set.
        /// </summary>
        /// <param name="commandData">
        /// An object that contains contextual information about the external command, including
        /// access to the application and active document.
        /// </param>
        /// <param name="message">
        /// A message that can be set by the command to provide additional information to the user
        /// if execution fails.
        /// </param>
        /// <param name="elements">
        /// A set of elements that can be used to highlight or select elements in the user interface
        /// if the command fails.
        /// </param>
        /// <returns>A <see cref="Result"/> value indicating the outcome of the command execution.</returns>
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            //get the active document
            Autodesk.Revit.DB.Document doc = commandData.Application.ActiveUIDocument.Document;

            // check if we have an active document, if not, we cannot proceed and should inform the user
            if (doc == null)
            {
                message = "No active document found.";
                return Result.Failed;
            }

            // load settings from the revit model a json string and create the data model
            string settingsAsJson = Utilities.SettingsUtils.LoadSettingsFromRevitModel(doc);
            _revitDataModel = new Models.Revit.RevitDataModel(doc.Title, settingsAsJson);

            // get the revision and sheet data from the revit model using the utility method and store it in the data model
            // stubs for now only
            bool revisionsLoaded = Utilities.RevitDataFactory.GetRevisionDataFromRevitModel(doc, _revitDataModel);

            // if loading the revisions failed, we cannot proceed, so we should inform the user and not open the main window
            if (!revisionsLoaded)
            {
                message = "Failed to load revisions from model.";
                return Result.Failed;
            }

            // get the sheet data from the revit model using the utility method and store it in the data model
            bool sheetsLoaded = Utilities.RevitDataFactory.GetSheetDataFromRevitModel(doc, _revitDataModel);

            // if loading the sheets failed, we cannot proceed, so we should inform the user and not open the main window
            if (!sheetsLoaded)
            {
                message = "Failed to load sheets from model.";
                return Result.Failed;
            }

            // execute the main logic of the command in a separate method, passing the application and the data model
            return ExecuteInternal(commandData.Application, _revitDataModel);
        }

        #region viewmodel setup

        /// <summary>
        /// Creates the <see cref="ViewModels.RoomsMainViewModel"/> used as the
        /// initial navigation target.
        /// </summary>
        private ViewModels.PyRevitDocumentListViewModel CreatePOCViewModel()
        {
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMsgVm =
                new duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel(_messageStore);

            return new ViewModels.PyRevitDocumentListViewModel();
        }
        #endregion

        #region utility

        private void SetupLog()
        {
            //set up the logger
            string logFilePath = Path.Combine(Utilities.SettingsUtils.settingsDirectory,
                Utilities.SettingsUtils.settingsFileNamePrefix + DateTime.Now.ToString("yyyy-MM-dd") + ".txt");

            if (_revitDataModel != null)
            {
                _revitDataModel.InitialiseLogger(logFilePath);

                _revitDataModel.LogMessages(
                    [
                        ("Starting duHastNet.PushIt.", duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                    ]);
            }

            //delete old log files
            duHastNet.Utils.Logging.LogFileCleanup cleaner = new();
            cleaner.DeleteOldLogFilesFireAndForget(
                directoryPath: Utilities.SettingsUtils.settingsDirectory, 
                olderThanDays: 5, 
                fileNamePrefix: Utilities.SettingsUtils.settingsFileNamePrefix, 
                fileExtension: "*.txt");

            if (_revitDataModel != null)
            {
                if (cleaner.ErrorMessages.Count > 0)
                {
                    // Log any errors encountered during log file cleanup, but do not fail startup — the main window still opens and the user can see the messages in the banner.
                    List<(string, duHastNet.Utils.WPF.Stores.MessageTypes)> e = [];
                    foreach (var err in cleaner.ErrorMessages)
                    {
                        e.Add(($"Error during log file cleanup: {err}", duHastNet.Utils.WPF.Stores.MessageTypes.Warning));
                    }
                    _revitDataModel.LogMessages(e);
                }
            }
        }

        #endregion utility
    }

    //assembly resolver static method
    /// <summary>
    /// Attempts to resolve the assembly from the local app data/duhast/bin directory.
    /// </summary>
    public static class AssemblyResolver
    {
        public static System.Reflection.Assembly? ResolveAssembly(object sender, ResolveEventArgs args)
        {
            try
            {
                string localAppDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string duHastBinDirectory = Path.Combine(localAppDataPath, "duHast", "bin");

                string? assemblyName = new AssemblyName(args.Name).Name;

                if (assemblyName is null)
                    return null;

                // Strip the ".resources" suffix if present.
                if (assemblyName.EndsWith(".resources"))
                    assemblyName = assemblyName[..^".resources".Length];

                string assemblyPath = Path.Combine(duHastBinDirectory, assemblyName + ".dll");
                return File.Exists(assemblyPath)
                    ? System.Reflection.Assembly.LoadFrom(assemblyPath)
                    : null;
            }
            catch (Exception)
            {
                return null;
            }
        }
    }
}
