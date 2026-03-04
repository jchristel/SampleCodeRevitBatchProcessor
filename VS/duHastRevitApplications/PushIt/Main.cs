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
using duHastNet.PushIt.Models.Drofus;
using duHastNet.PushIt.RevitActions;
using duHastNet.PushIt.RevitActions.Drofus;
using duHastNet.PushIt.Utilities;
using duHastNet.PushIt.Utilities.Drofus;
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

            //set up the navigation store
            ViewModels.RoomsMainViewModel roomsVm = CreateRoomsSelectionViewModel();
            _navigationStore.CurrentViewModel = roomsVm;

            //show the main window
            MainWindow mainWindow = new MainWindow(settings)
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };

            mainWindow.Show();

            // ── Phase 2: source-specific startup (fire-and-forget) ───────────
            // Both helpers guard on their own SourceType so only one executes.
            // Each writes results to _revitDataModel.StartupMessages; the
            // message store relay happens inside each helper after Execute().
            FireDrofusStartupValidationIfRequired(settings, roomsVm);
            FireCsvStartupLoadIfRequired(settings);

            return Result.Succeeded;
        }

        // ── Private helpers ───────────────────────────────────────────────────

        /// <summary>
        /// Reads all shared parameters bound in the Revit document and loads them
        /// into <see cref="Models.RevitDataModel"/> via
        /// <see cref="Models.RevitDataModel.AddParameter"/>.
        /// <para>
        /// Called synchronously on the Revit API thread before the main window
        /// opens, so the parameter list is always available regardless of which
        /// data source is selected.
        /// </para>
        /// </summary>
        private void LoadSharedParametersFromDocument(Autodesk.Revit.DB.Document doc)
        {
            try
            {
                // GetSharedParameterIdsByGUID returns Dictionary<GUID string, ElementId>.
                // Each ElementId resolves to a SharedParameterElement whose Name
                // gives the display name used in the mapping dialog ComboBox.
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

                    // Only register parameters that are actually bound to at
                    // least one enabled category — parameters bound only to
                    // categories the user has not enabled are not relevant.
                    List<string>? bindingsId =
                        duHastNet.RevitUtils.Parameters.SharedParaUtils
                            .ParameterBindingsByGUID(doc, guid);

                    //check if any bindings found, there should be some
                    if (bindingsId == null)
                    {
                        continue;
                    }

                    bool isBoundToEnabledCategory = true;
                    // check if parameter is bound to enabled categories
                    foreach (var supportedCategory in _revitDataModel.GetAllEnabledCategories())
                    {
                        if (supportedCategory.Enabled)
                        {
                            if (!bindingsId.Contains(supportedCategory.Name))
                            {
                                isBoundToEnabledCategory = false;
                            }
                        }
                    }

                    // if the parameter is not bound to any enabled category, skip it
                    if (!isBoundToEnabledCategory)
                    {
                        continue;
                    }

                    // if we get here, the parameter is shared and bound to categories, so we add it to the model
                    _revitDataModel.AddParameter(new Models.RoomDataProperty(
                        name: spElem.Name,
                        parameterGUID: guid,
                        parameterName: spElem.Name,
                        value: string.Empty,
                        showInUI: true,
                        isReadOnly: false,
                        isUniqueId: false));
                }
            }
            catch (Exception ex)
            {
                // Non-fatal — parameters will be empty but the app still opens.
                _messageStore.EnqueueMessage(
                    $"Could not read shared parameters from Revit document: {ex.Message}",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Warning);
            }
        }

        /// <summary>
        /// Fires a fire-and-forget <c>RevitTask.RunAsync</c> block that validates
        /// existing drofus property mappings against the live Revit document and
        /// drofus API. Skipped when the active source is not drofus, no mappings
        /// are configured, or credentials are incomplete.
        /// <para>
        /// Messages generated by the action are written to
        /// <see cref="Models.RevitDataModel.AddStartupMessage"/> inside the action
        /// itself, and are also forwarded to <c>_messageStore</c> here so they
        /// appear in the UI banner.
        /// </para>
        /// </summary>
        private void FireDrofusStartupValidationIfRequired(
            Models.Settings settings,
            ViewModels.RoomsMainViewModel roomsVm)
        {
            if (settings.DataSource?.SourceType != Models.DataSourceType.Drofus)
                return;

            DrofusDataSourceControlViewModel? drofusControlVm =
                roomsVm.DataSourceViewModel.CurrentSourceControlViewModel
                    as DrofusDataSourceControlViewModel;

            if (drofusControlVm is null)
                return;

            // Shared parameters were loaded into _revitDataModel synchronously
            // before the window opened. Inject them into the control ViewModel
            // now so the Add/Edit dialog ComboBox is populated.
            drofusControlVm.AvailableRevitParameters = _revitDataModel.GetAllParameters();

            DrofusDataSourceSettings? drofusSettings = settings.DataSource.Drofus;
            if (drofusSettings is null || drofusSettings.PropertyMappings.Count == 0)
                return;

            var dataSource = new DrofusDataSource();
            if (!dataSource.Validate(settings.DataSource, out _))
                return;

            _ = RevitTask.RunAsync(app =>
            {
                Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;

                try
                {
                    var action = new ValidateDrofusMappingsOnStartup(
                        drofusControlVm.Mapper,
                        settings.DataSource);

                    (string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType) =
                        action.Execute(doc);

                    _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                    // Forward detail messages into the durable startup list
                    foreach (var entry in action.GetLogMessagesAndLogTypes())
                    {
                        _revitDataModel.AddStartupMessage(entry.Item1, entry.Item2);
                    }

                    if (messageType != duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                        _messageStore.EnqueueMessage(message, messageType);

                    System.Windows.Application.Current?.Dispatcher.Invoke(
                        () => drofusControlVm.OnStartupValidationCompleted());
                }
                catch (Exception ex)
                {
                    string errMsg = $"drofus mapping validation failed unexpectedly: {ex.Message}";
                    _revitDataModel.AddStartupMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Warning);
                    _messageStore.EnqueueMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Warning);
                }

                return (string.Empty, duHastNet.Utils.WPF.Stores.MessageTypes.Information);
            });
        }

        /// <summary>
        /// Fires a fire-and-forget <c>RevitTask.RunAsync</c> block that validates
        /// CSV settings and — if valid — loads header parameters, verifies them
        /// against the Revit document, and loads all room records into the model.
        /// Skipped when the active source is not CSV, or when CSV settings fail
        /// basic validation (missing or non-existent file path).
        /// <para>
        /// Mirrors the drofus startup pattern: validation first, then data load,
        /// all on the RevitTask background thread so the window is visible when
        /// any error banner appears.
        /// </para>
        /// </summary>
        private void FireCsvStartupLoadIfRequired(Models.Settings settings)
        {
            if (settings.DataSource?.SourceType != Models.DataSourceType.Csv)
                return;

            // Validate settings synchronously before firing the async block.
            // A missing or invalid file path is reported immediately without
            // entering RevitTask.RunAsync.
            var csvDataSource = new Utilities.CsvDataSource();
            if (!csvDataSource.Validate(settings.DataSource, out string validationError))
            {
                string errMsg = $"CSV startup: {validationError}";
                _revitDataModel.AddStartupMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                _messageStore.EnqueueMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                return;
            }

            _ = RevitTask.RunAsync(app =>
            {
                Autodesk.Revit.DB.Document doc = app.ActiveUIDocument.Document;

                try
                {
                    var action = new ValidateCsvOnStartup(_revitDataModel);
                    (string message, duHastNet.Utils.WPF.Stores.MessageTypes messageType) =
                        action.Execute(doc);

                    _revitDataModel.LogMessages(action.GetLogMessagesAndLogTypes());

                    // Non-information results (warnings or errors) are surfaced
                    // in the banner. Information is silent — rooms loaded cleanly.
                    if (messageType != duHastNet.Utils.WPF.Stores.MessageTypes.Information)
                        _messageStore.EnqueueMessage(message, messageType);
                }
                catch (Exception ex)
                {
                    string errMsg = $"CSV startup failed unexpectedly: {ex.Message}";
                    _revitDataModel.AddStartupMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                    _messageStore.EnqueueMessage(errMsg, duHastNet.Utils.WPF.Stores.MessageTypes.Error);
                }

                return (string.Empty, duHastNet.Utils.WPF.Stores.MessageTypes.Information);
            });
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
