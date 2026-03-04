// BSD License - Copyright 2025, Jan Christel

using Autodesk.Revit.DB;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Utilities;
using System;
using System.Collections.Generic;

namespace duHastNet.PushIt.RevitActions
{
    /// <summary>
    /// Startup action that validates the CSV data source and loads parameters
    /// and rooms into the <see cref="RevitDataModel"/> in the correct sequence.
    /// <para>
    /// The three steps run in order and abort on the first failure:
    /// <list type="number">
    ///   <item>Read header parameters from the CSV file into the parameter store.</item>
    ///   <item>
    ///     Cross-reference each CSV parameter GUID against the pre-built
    ///     <see cref="RevitDataModel.GetAllAvailableParameters"/> list. This list
    ///     was populated at startup from the live Revit document by
    ///     <c>Main.LoadSharedParametersFromDocument</c>, so no further Revit API
    ///     call is required here.
    ///   </item>
    ///   <item>Load all room records into the model.</item>
    /// </list>
    /// </para>
    /// <para>
    /// Must be executed inside <c>RevitTask.RunAsync</c> so that it runs on a
    /// background thread and the UI remains responsive. The Revit API
    /// <paramref name="doc"/> argument is accepted to satisfy the
    /// <c>IRevitAction</c> contract but is not used by this action.
    /// </para>
    /// <para>
    /// All messages are written to both the action's own log (via
    /// <c>AddMessage</c>) and to
    /// <see cref="RevitDataModel.AddStartupMessage"/> so they survive the async
    /// boundary and can be forwarded to the UI message store by
    /// <c>Main.ExecuteInternal</c> after the action completes.
    /// </para>
    /// </summary>
    public class ValidateCsvOnStartup : RevitActionBase,
        duHastNet.RevitUtils.RevitActions.IRevitAction
    {
        // ── Dependencies ──────────────────────────────────────────────────────

        private readonly RevitDataModel _revitDataModel;

        // ── Constructor ───────────────────────────────────────────────────────

        /// <summary>
        /// Constructs the startup action.
        /// </summary>
        /// <param name="revitDataModel">
        /// The active <see cref="RevitDataModel"/>. Parameters and rooms are
        /// loaded into this instance. Must not be <c>null</c>.
        /// </param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="revitDataModel"/> is <c>null</c>.
        /// </exception>
        public ValidateCsvOnStartup(RevitDataModel revitDataModel)
        {
            _revitDataModel = revitDataModel
                ?? throw new ArgumentNullException(nameof(revitDataModel));
        }

        // ── IRevitAction ──────────────────────────────────────────────────────

        /// <summary>
        /// Runs the three-step CSV startup sequence.
        /// </summary>
        /// <param name="doc">
        /// The active Revit document. Accepted to satisfy the
        /// <c>IRevitAction</c> contract; not used by this action.
        /// </param>
        /// <returns>
        /// A tuple containing a human-readable summary message and a
        /// <see cref="Utils.WPF.Stores.MessageTypes"/> value:
        /// <list type="bullet">
        ///   <item><c>Information</c> — all steps passed; rooms are loaded.</item>
        ///   <item><c>Error</c> — a step failed; rooms are not loaded.</item>
        /// </list>
        /// </returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(
            Document doc)
        {
            try
            {
                // ── Step A: read CSV header parameters ────────────────────────
                // Replaces any parameters left over from a previous load attempt.
                _revitDataModel.ClearParameters();
                _revitDataModel.LoadParameterData();

                var csvParameters = _revitDataModel.GetAllParameters();

                if (csvParameters.Count == 0)
                {
                    string noParamsMsg =
                        "CSV startup: no parameters were read from the CSV file headers. " +
                        "Check that the CSV file is present and correctly formatted.";
                    AddMessage(noParamsMsg, Utils.WPF.Stores.MessageTypes.Error);
                    _revitDataModel.AddStartupMessage(noParamsMsg, Utils.WPF.Stores.MessageTypes.Error);
                    return GetReturnValue("CSV startup: aborted — no CSV parameters.");
                }

                // ── Step B: cross-reference against available parameters ───────
                // Available parameters were read from the live Revit document by
                // Main.LoadSharedParametersFromDocument before this action ran.
                // Each CSV parameter that carries a GUID must match an entry in
                // that list. Parameters without a GUID (standard non-shared
                // parameters) are checked by name only.
                IReadOnlyList<AvailableParameter> availableParameters =
                    _revitDataModel.GetAllAvailableParameters();

                if (availableParameters.Count == 0)
                {
                    string noAvailMsg =
                        "CSV startup: no shared parameters are registered as available in the " +
                        "Revit document. Ensure shared parameters are bound to all enabled " +
                        "categories before loading.";
                    AddMessage(noAvailMsg, Utils.WPF.Stores.MessageTypes.Error);
                    _revitDataModel.AddStartupMessage(noAvailMsg, Utils.WPF.Stores.MessageTypes.Error);
                    return GetReturnValue("CSV startup: aborted — no available parameters.");
                }

                bool allMatched = true;

                foreach (var csvParam in csvParameters)
                {
                    if (!string.IsNullOrWhiteSpace(csvParam.ParameterGUID))
                    {
                        // GUID-based match: authoritative, order-independent.
                        if (!_revitDataModel.AvailableParameterExistsByGuid(csvParam.ParameterGUID))
                        {
                            string missMsg =
                                $"CSV startup: parameter '{csvParam.Name}' " +
                                $"(GUID: {csvParam.ParameterGUID}) is specified in the CSV " +
                                $"but was not found as a shared parameter bound to all " +
                                $"enabled categories in the Revit document.";
                            AddMessage(missMsg, Utils.WPF.Stores.MessageTypes.Error);
                            _revitDataModel.AddStartupMessage(
                                missMsg, Utils.WPF.Stores.MessageTypes.Error);
                            allMatched = false;
                        }
                    }
                    else
                    {
                        // Name-based fallback for standard (non-shared) parameters.
                        if (!_revitDataModel.AvailableParameterExistsByName(csvParam.Name))
                        {
                            string missMsg =
                                $"CSV startup: parameter '{csvParam.Name}' is specified in " +
                                $"the CSV but was not found in the available parameters list " +
                                $"for the Revit document.";
                            AddMessage(missMsg, Utils.WPF.Stores.MessageTypes.Error);
                            _revitDataModel.AddStartupMessage(
                                missMsg, Utils.WPF.Stores.MessageTypes.Error);
                            allMatched = false;
                        }
                    }
                }

                if (!allMatched)
                {
                    // One or more parameters are missing — do not load rooms
                    // against an invalid parameter set.
                    return GetReturnValue("CSV startup: aborted — parameter mismatch.");
                }

                // ── Step C: load rooms ────────────────────────────────────────
                _revitDataModel.ClearAllRooms();
                _revitDataModel.LoadRoomsData();

                string successMsg =
                    "CSV startup: all parameters matched and rooms loaded successfully.";
                _revitDataModel.AddStartupMessage(
                    successMsg, Utils.WPF.Stores.MessageTypes.Information);
                return GetReturnValue(successMsg);
            }
            catch (Exception ex)
            {
                string errorMsg =
                    $"CSV startup: an unexpected error occurred: {ex.Message}";
                AddMessage(errorMsg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(
                    errorMsg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("CSV startup: completed with errors.");
            }
        }
    }
}
