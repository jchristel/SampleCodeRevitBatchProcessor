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
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, even if advised of the possibility of such damage.
//
//
//


using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.RevitActions.Drofus;
using duHastNet.PushIt.Utilities;
using duHastNet.PushIt.ViewModels.DataSource;
using duHastNet.PushIt.Views;
using Revit.Async;
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Reflection.Metadata;


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
        /// Initializes application state, loads settings and data, and displays the main window
        /// for the PushIt add-in within a Revit session.
        /// This function can be called from ironpython (i.e. pyRevit).
        /// </summary>
        /// <remarks>
        /// This method should be called from within a valid Revit API context. It sets up required
        /// data models, logging, and user interface components for the PushIt workflow. The method is
        /// intended for internal use as part of the add-in's startup sequence.
        /// </remarks>
        /// <param name="uiapp">
        /// The current Revit application context used to access the active document and application
        /// services. Cannot be null.
        /// </param>
        /// <returns>
        /// A value indicating whether the operation completed successfully.
        /// Returns <see cref="Result.Succeeded"/> if initialization and window display succeed.
        /// </returns>
        public Result ExecuteInternal(UIApplication uiapp)
        {
            // Revit Async version 2.x.x
            RevitTask.Initialize(uiapp);

            //set up stores
            _navigationStore = new duHastNet.Utils.WPF.Stores.NavigationStore();
            _messageStore = new duHastNet.Utils.WPF.Stores.MessageStore();
            _stateStore = new duHastNet.Utils.WPF.Stores.StateStore();

            // set up the revit data model
            _revitDataModel = new Models.RevitDataModel();

            //set up the logger
            string logFilePath = Path.Combine(Utilities.SettingsUtils.settingsDirectory,
                "log_pushit_" + DateTime.Now.ToString("yyyy-MM-dd") + ".txt");
            _revitDataModel.InitialiseLogger(logFilePath);

            _revitDataModel.LogMessages(new List<(string, duHastNet.Utils.WPF.Stores.MessageTypes)>
                {
                    ("Starting duHastNet.PushIt.", duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                });

            //delete old log files
            duHastNet.Utils.Logging.LogFileCleanup cleaner = new();
            cleaner.DeleteOldLogFilesFireAndForget(directoryPath: Utilities.SettingsUtils.settingsDirectory,olderThanDays: 5,fileNamePrefix: "log_pushit_", fileExtension: "*.txt");
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

            //Get document
            Autodesk.Revit.DB.Document doc = uiapp.ActiveUIDocument.Document;

            // store the document title so the UI can display it
            _revitDataModel.RevitDocumentTitle = doc.Title;

            // load settings from file
            Models.Settings settings = SettingsUtils.LoadSettings();
            _revitDataModel.Settings = settings;

            // Clear any startup messages left from a previous run before the
            // startup sequence begins. Each source-specific helper writes its own
            // messages; Main forwards them to the banner after Show().
            _revitDataModel.ClearStartupMessages();

            //get all supported categories
            List<Models.CategoryDataModel> supportedCategories =
                Utilities.Revit.RevitCategoryObjectsConverter.ConvertToRevitCategoryObjects(doc);
            _revitDataModel.LoadSupportedCategoryData(supportedCategories);

            // ── Phase 1b: read shared parameters from the Revit document ─────
            // Still on the Revit API thread — doc is directly accessible.
            // Parameters are a property of the document, not the data source,
            // so we always read them regardless of which source is selected.
            LoadSharedParametersFromDocument(doc);

            // ── Phase 2: source-specific startup (sync) ───────────────────────
            // Validation, connection test, mapping validation and room data load
            // all run synchronously here on the Revit API thread before the
            // window opens. The RoomsMainViewModel constructor then fires
            // _raiseRefreshGUICommand which handles the Revit-side room matching
            // (UpdateRoomDataModelWithNewRooms + RefreshRoomDataWithRevitData)
            // asynchronously — by that point rooms are already in the model.
            RunDrofusStartupIfRequired(settings);
            RunCsvStartupIfRequired(settings);

            //set up the navigation store
            ViewModels.RoomsMainViewModel roomsVm = CreateRoomsSelectionViewModel();
            _navigationStore.CurrentViewModel = roomsVm;

            // After creating the RoomsMainViewModel, notify the drofus control VM
            // that startup is complete so mapping-row indicators and the Add Mapping
            // button reflect the validation results written during Phase 2.
            if (settings.DataSource?.SourceType == Models.DataSourceType.Drofus)
            {
                if (roomsVm.DataSourceViewModel.CurrentSourceControlViewModel
                        is ViewModels.DataSource.DrofusDataSourceControlViewModel drofusVm)
                {
                    drofusVm.OnStartupCompleted();
                }
            }

            //show the main window
            MainWindow mainWindow = new MainWindow(settings)
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };

            mainWindow.Show();

            return Result.Succeeded;
        }

        // ── Private helpers ───────────────────────────────────────────────────

        /// <summary>
        /// Reads all shared parameters bound in the Revit document and registers
        /// them in <see cref="Models.RevitDataModel"/> as
        /// <see cref="Models.AvailableParameter"/> entries via
        /// <see cref="Models.RevitDataModel.AddAvailableParameter"/>.
        /// <para>
        /// Only parameters that are bound to every currently-enabled category are
        /// registered — parameters bound only to categories the user has not
        /// enabled are not relevant for matching or mapping.
        /// </para>
        /// <para>
        /// Called synchronously on the Revit API thread before the main window
        /// opens, so the available-parameter list is always populated regardless
        /// of which data source is active.
        /// </para>
        /// </summary>
        private void LoadSharedParametersFromDocument(Autodesk.Revit.DB.Document doc)
        {
            try
            {
                // Ensure the list is empty before populating — guards against
                // the method being called more than once in a session.
                _revitDataModel.ClearAvailableParameters();

                // GetSharedParameterIdsByGUID returns Dictionary<GUID string, ElementId>.
                // Each ElementId resolves to a SharedParameterElement whose Name
                // gives the human-readable display name.
                var sharedParamIds = duHastNet.RevitUtils.Parameters.SharedParaUtils
                    .GetSharedParameterIdsByGUID(doc);

                if (sharedParamIds == null) return;

                foreach (var kvp in sharedParamIds)
                {
                    string guid = kvp.Key;
                    Autodesk.Revit.DB.ElementId elemId = kvp.Value;

                    var spElem = doc.GetElement(elemId)
                        as Autodesk.Revit.DB.SharedParameterElement;

                    if (spElem == null) continue;

                    // Only register parameters that are bound to every enabled
                    // category — parameters bound only to disabled categories
                    // cannot be used in any push or mapping operation.
                    List<string>? bindingsId =
                        duHastNet.RevitUtils.Parameters.SharedParaUtils
                            .ParameterBindingsByGUID(doc, guid);

                    if (bindingsId == null) continue;

                    bool isBoundToAllEnabledCategories = true;
                    foreach (var enabledCategory in _revitDataModel.GetAllEnabledCategories())
                    {
                        if (!bindingsId.Contains(enabledCategory.Name))
                        {
                            isBoundToAllEnabledCategories = false;
                            break;
                        }
                    }

                    if (!isBoundToAllEnabledCategories) continue;

                    // Register as a lightweight AvailableParameter — name and
                    // GUID only. No value, no UI flags, no read-only state.
                    _revitDataModel.AddAvailableParameter(
                        new Models.AvailableParameter(
                            parameterName: spElem.Name,
                            parameterGuid: guid));
                }
            }
            catch (Exception ex)
            {
                // Non-fatal — available parameters will be empty but the app
                // still opens. The source-specific startup steps will fail
                // gracefully when they find no parameters to match against.
                _messageStore.EnqueueMessage(
                    $"Could not read shared parameters from Revit document: {ex.Message}",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Warning);
            }
        }

        /// <summary>
        /// Runs <see cref="ValidateDrofusOnStartup"/> synchronously on the Revit
        /// API thread before the main window opens. Skipped when the active source
        /// is not drofus or drofus settings are absent.
        /// <para>
        /// The <see cref="DrofusPropertyMapper"/> is constructed here from the
        /// persisted mappings. Available fields and validation results written into
        /// it are then visible to <c>RoomsMainViewModel</c>'s own
        /// <c>DrofusDataSourceControlViewModel</c> after construction via
        /// <see cref="DrofusDataSourceControlViewModel.OnStartupCompleted"/>.
        /// </para>
        /// </summary>
        private void RunDrofusStartupIfRequired(Models.Settings settings)
        {
            if (settings.DataSource?.SourceType != Models.DataSourceType.Drofus)
                return;

            if (settings.DataSource.Drofus is null)
                return;

            var mapper = new Utilities.Drofus.DrofusPropertyMapper(
                settings.DataSource.Drofus.PropertyMappings);

            try
            {
                var action = new ValidateDrofusOnStartup(_revitDataModel, mapper);
                (string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType) =
                    action.Execute();

                _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                if (messageType != duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                    _messageStore.EnqueueMessage(message, messageType);
            }
            catch (Exception ex)
            {
                string errMsg = $"drofus startup failed unexpectedly: {ex.Message}";
                _revitDataModel.AddStartupMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                _messageStore.EnqueueMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        /// <summary>
        /// Runs <see cref="ValidateCsvOnStartup"/> synchronously on the Revit
        /// API thread before the main window opens. Skipped when the active source
        /// is not CSV or when CSV settings fail basic validation.
        /// </summary>
        private void RunCsvStartupIfRequired(Models.Settings settings)
        {
            if (settings.DataSource?.SourceType != Models.DataSourceType.Csv)
                return;

            var csvDataSource = new Utilities.CsvDataSource();
            if (!csvDataSource.Validate(settings.DataSource, out string validationError))
            {
                string errMsg = $"CSV startup: {validationError}";
                _revitDataModel.AddStartupMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                _messageStore.EnqueueMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                return;
            }

            try
            {
                var action = new ValidateCsvOnStartup(_revitDataModel);
                (string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType) =
                    action.Execute();

                _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                if (messageType != duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                    _messageStore.EnqueueMessage(message, messageType);
            }
            catch (Exception ex)
            {
                string errMsg = $"CSV startup failed unexpectedly: {ex.Message}";
                _revitDataModel.AddStartupMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                _messageStore.EnqueueMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
            }
        }

        /// <summary>
        /// Creates the <see cref="ViewModels.RoomsMainViewModel"/> used as the
        /// initial navigation target.
        /// </summary>
        private ViewModels.RoomsMainViewModel CreateRoomsSelectionViewModel()
        {
            duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel globalMsgVm =
                new duHastNet.Utils.WPF.ViewModels.GlobalMessageViewModel(_messageStore);

            return new ViewModels.RoomsMainViewModel(
                _revitDataModel,
                _navigationStore,
                _stateStore,
                _messageStore,
                globalMsgVm);
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
            return ExecuteInternal(commandData.Application);
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
}