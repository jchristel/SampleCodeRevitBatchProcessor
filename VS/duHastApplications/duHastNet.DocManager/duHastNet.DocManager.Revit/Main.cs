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
using duHastNet.DocManager.Revit.Utilities.UISettings;
using duHastNet.DocManager.Revit.Utilities.RevitSettings;
using duHastNet.DocManager.Core.Services.Api;
using duHastNet.DocManager.Revit.Models.Database;

namespace duHastNet.DocManager.Revit
{
    public class Main : IExternalCommand
    {
        Models.Revit.RevitDataModel _revitDataModel;
        Models.Database.DatabaseDataModel _databaseDataModel;
        duHastNet.Utils.WPF.Stores.NavigationStore _navigationStore;
        duHastNet.Utils.WPF.Stores.MessageStore _messageStore;
        duHastNet.UI.DocManagerSettingsUI.Utils.Settings _revitSettings;
        Utilities.UISettings.UISettings _uiSettings;


        static Main()
        {
            //assembly resolver in order for this plugin to be used from pyRevit invoke.button
            AppDomain.CurrentDomain.AssemblyResolve += new ResolveEventHandler(AssemblyResolver.ResolveAssembly);
        }

        public Result ExecuteInternal(UIApplication uiapp, Models.Revit.RevitDataModel revitDataModel)
        {
            //set up stores
            _navigationStore = new duHastNet.Utils.WPF.Stores.NavigationStore();
            _messageStore = new duHastNet.Utils.WPF.Stores.MessageStore();
            // set up the revit data model
            // check if this is called from the Execute method (there is a data model already) or if the data model is already created and passed in (e.g. from pyRevit) and set it accordingly
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
            _uiSettings = UISettingsUtils.LoadSettings();

            //initialise the settings from the revit model settings json string,
            //this will be used in the main window and passed to the view models via the constructor,
            //so that they can access the settings as needed
            _revitSettings = RevitSettingsUtils.InitialiseRevitSettings(_revitDataModel.SettingsAsJson);

            //process each sheet: build the document number as per passed in settings
            _revitDataModel.AddFullDocumentNumber(_revitSettings.DocumentNumberBuilderString);

            // parse each revision's raw date string into a DateTime using the configured format order.
            // must run after AddFullDocumentNumber so all startup data is available, and before
            // LoadDatabaseData so that ParsedDate is set before any UI or comparison logic runs.
            Utilities.RevisionDateNormaliser.NormaliseRevisionDates(_revitDataModel, _revitSettings.DateFormatOrder);

            _revitDataModel.LogMessages(
                [
                    ($"Normalised revision dates using format order: {_revitSettings.DateFormatOrder}.", duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                ]);

            // load existing documents and revisions from the database;
            // happy/unhappy path is resolved here — the window always opens regardless of outcome
            _databaseDataModel = LoadDatabaseData();

            //set up the navigation store with the main integration view model
            _navigationStore.CurrentViewModel = CreateRevitIntegrationViewModel();

            //show the main window
            duHastNet.DocManager.Revit.Views.MainWindow mainWindow = new(_uiSettings)
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };

            mainWindow.Show();

            return Result.Succeeded;
        }

        /// <summary>
        /// Executes the external command using the provided command data and element set.
        /// </summary>
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

            // load settings from the revit model as a json string and create the data model
            string settingsAsJson = RevitSettingsUtils.LoadSettingsFromRevitModel(doc);
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
        /// Creates the <see cref="ViewModels.RevitIntegrationViewModel"/> used as the
        /// navigation target in <see cref="ExecuteInternal"/>.
        /// All required data has been collected and loaded before this method is called.
        /// </summary>
        private ViewModels.RevitIntegrationViewModel CreateRevitIntegrationViewModel()
        {
            return new ViewModels.RevitIntegrationViewModel(
                _revitDataModel,
                _databaseDataModel,
                _messageStore,
                _revitSettings);
        }

        /// <summary>
        /// Creates the proof of concept <see cref="ViewModels.PyRevitDocumentListViewModel"/>.
        /// Retained for future reference — not used in the main startup sequence.
        /// </summary>
        private ViewModels.PyRevitDocumentListViewModel CreatePOCViewModel()
        {
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMsgVm =
                new(_messageStore);

            return new ViewModels.PyRevitDocumentListViewModel(_revitSettings, _uiSettings);
        }

        #endregion

        #region database

        /// <summary>
        /// Connects to the Document Manager database and reads existing documents and revisions.
        /// <para>
        /// The database path is read from <see cref="_revitSettings"/>. All failures are
        /// enqueued to <see cref="_messageStore"/> so they surface in the UI message banner.
        /// A <see cref="DatabaseDataModel"/> is always returned — on failure it is disconnected
        /// with empty lists, allowing the window to open with operations disabled.
        /// </para>
        /// </summary>
        private DatabaseDataModel LoadDatabaseData()
        {
            string databasePath = _revitSettings?.DatabasePath ?? string.Empty;

            if (string.IsNullOrWhiteSpace(databasePath))
            {
                _messageStore.EnqueueMessage(
                    "No database path configured. Use the setup utility to configure the database path.",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Error);

                _revitDataModel.LogMessages(
                    [("Database path is not configured.", duHastNet.Utils.WPF.Stores.MessageTypes.Error)]);

                return DatabaseDataModel.CreateDisconnected();
            }

            var api = new DocManagerApi();
            try
            {
                var connectionResult = api.ConnectDatabase(databasePath);

                if (!connectionResult.Success)
                {
                    string errorMessage = $"Could not connect to database: {connectionResult.Message}";

                    _messageStore.EnqueueMessage(errorMessage, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                    _revitDataModel.LogMessages([(errorMessage, duHastNet.Utils.WPF.Stores.MessageTypes.Error)]);

                    return DatabaseDataModel.CreateDisconnected();
                }

                var documents = api.GetActiveDocuments();
                var revisions = api.GetAllRevisions();
                var customFieldDefinitions = api.GetActiveCustomFieldDefinitions();

                _revitDataModel.LogMessages(
                    [
                        ($"Loaded {documents.Count} document(s) from database.", duHastNet.Utils.WPF.Stores.MessageTypes.Information),
                        ($"Loaded {revisions.Count} revision(s) from database.", duHastNet.Utils.WPF.Stores.MessageTypes.Information),
                        ($"Loaded {customFieldDefinitions.Count} custom field definition(s) from database.", duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                    ]);

                return new DatabaseDataModel(true, documents, revisions, customFieldDefinitions, api);
            }
            catch (Exception ex)
            {
                string errorMessage = $"Failed to read database: {ex.Message}";

                _messageStore.EnqueueMessage(errorMessage, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.LogMessages([(errorMessage, duHastNet.Utils.WPF.Stores.MessageTypes.Error)]);

                return DatabaseDataModel.CreateDisconnected();
            }
        }

        #endregion database

        #region utility

        private void SetupLog()
        {
            //set up the logger
            string logFilePath = Path.Combine(UISettingsUtils.settingsDirectory,
                UISettingsUtils.settingsFileNamePrefix + DateTime.Now.ToString("yyyy-MM-dd") + ".txt");

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
                directoryPath: UISettingsUtils.settingsDirectory,
                olderThanDays: 5,
                fileNamePrefix: UISettingsUtils.settingsFileNamePrefix,
                fileExtension: "*.txt");

            if (_revitDataModel != null)
            {
                if (cleaner.ErrorMessages.Count > 0)
                {
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
