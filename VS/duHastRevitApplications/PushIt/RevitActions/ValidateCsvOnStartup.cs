// BSD License - Copyright 2025, Jan Christel

using Autodesk.Revit.DB;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Utilities;
using System;

namespace duHastNet.PushIt.RevitActions
{
    /// <summary>
    /// Startup action that validates the CSV data source and loads parameters
    /// and rooms into the <see cref="RevitDataModel"/> in the correct sequence.
    /// <para>
    /// The three steps run in order and abort on the first failure:
    /// <list type="number">
    ///   <item>Load header parameters from the CSV file.</item>
    ///   <item>Verify those parameters exist and are bound in the active Revit document.</item>
    ///   <item>Load all room records into the model.</item>
    /// </list>
    /// </para>
    /// <para>
    /// Must be executed inside <c>RevitTask.RunAsync</c> — step 2 requires the
    /// Revit API. Steps 1 and 3 only perform file I/O but are included here so
    /// the entire sequence runs on the same background thread without blocking
    /// the UI.
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

            // RevitActionBase exposes RevitModel for VerifyParametersInModel
            RevitModel = revitDataModel;
        }

        // ── IRevitAction ──────────────────────────────────────────────────────

        /// <summary>
        /// Runs the three-step CSV startup sequence.
        /// </summary>
        /// <param name="doc">The active Revit document.</param>
        /// <returns>
        /// A tuple containing a human-readable summary message and a
        /// <see cref="Utils.WPF.Stores.MessageTypes"/> value:
        /// <list type="bullet">
        ///   <item><c>Information</c> — all steps passed; rooms are loaded.</item>
        ///   <item><c>Error</c> — a step failed; rooms may not be loaded.</item>
        /// </list>
        /// </returns>
        public (string messageAction, Utils.WPF.Stores.MessageTypes messageActionType) Execute(
            Document doc)
        {
            try
            {
                // ── Step A: load header parameters ────────────────────────────
                _revitDataModel.ClearParameters();
                _revitDataModel.LoadParameterData();

                if (_revitDataModel.GetAllParameters().Count == 0)
                {
                    string noParamsMsg = "CSV startup: no parameters were read from the CSV file headers. " +
                                        "Check that the CSV file is present and correctly formatted.";
                    AddMessage(noParamsMsg, Utils.WPF.Stores.MessageTypes.Error);
                    _revitDataModel.AddStartupMessage(noParamsMsg, Utils.WPF.Stores.MessageTypes.Error);
                    return GetReturnValue("CSV startup: parameters loaded.");
                }

                // ── Step B: verify parameters against Revit document ──────────
                VerifyParametersInModel actionVerify = new(_revitDataModel);
                (string messageActionVerify, Utils.WPF.Stores.MessageTypes messageActionTypeVerify) =
                    actionVerify.Execute(doc);

                _revitDataModel.LogMessages(actionVerify.GetLogMessagesAndLogTypes());

                // Forward each verification message into the startup message store
                // so Main can relay them to the UI banner after the window opens.
                foreach (var entry in actionVerify.GetLogMessagesAndLogTypes())
                {
                    _revitDataModel.AddStartupMessage(entry.Item1, entry.Item2);
                }

                if (messageActionTypeVerify == Utils.WPF.Stores.MessageTypes.Error)
                {
                    // Parameter check failed — do not load rooms against an invalid
                    // parameter set. The error detail is already in the log and the
                    // startup message list.
                    AddMessage(messageActionVerify, Utils.WPF.Stores.MessageTypes.Error);
                    return (messageActionVerify, messageActionTypeVerify);
                }

                // ── Step C: load rooms ────────────────────────────────────────
                _revitDataModel.ClearAllRooms();
                _revitDataModel.LoadRoomsData();

                string successMsg = "CSV startup: parameters verified and rooms loaded successfully.";
                _revitDataModel.AddStartupMessage(successMsg, Utils.WPF.Stores.MessageTypes.Information);
                return GetReturnValue(successMsg);
            }
            catch (Exception ex)
            {
                string errorMsg = $"CSV startup: an unexpected error occurred: {ex.Message}";
                AddMessage(errorMsg, Utils.WPF.Stores.MessageTypes.Error);
                _revitDataModel.AddStartupMessage(errorMsg, Utils.WPF.Stores.MessageTypes.Error);
                return GetReturnValue("CSV startup: completed with errors.");
            }
        }
    }
}
