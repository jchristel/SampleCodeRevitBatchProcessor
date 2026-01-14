//
//License: BSD License
// Copyright 2025, Jan Christel
//

using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using duHastNet.DocManager.Revit.Views;
using System;

namespace duHastNet.DocManager.Revit.Commands
{
    /// <summary>
    /// External command to show documents from database in a WebView window
    /// This is a proof of concept to test CEFSharp integration with Revit
    /// </summary>
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class ShowDocumentsCommand : IExternalCommand
    {
        // Hard-coded database path for POC
        private const string DATABASE_PATH = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager.Standalone.Tests\DataBaseTests\20260111_01.db";

        /// <summary>
        /// Execute the command
        /// </summary>
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            try
            {
                // Validate database path exists
                if (!System.IO.File.Exists(DATABASE_PATH))
                {
                    TaskDialog.Show("Error", 
                        $"Database file not found:\n{DATABASE_PATH}\n\nPlease check the path in ShowDocumentsCommand.cs");
                    return Result.Failed;
                }

                // Create and show the window modally
                var window = new DocumentViewerWindow(DATABASE_PATH);
                window.ShowDialog();

                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                // Show error dialog
                TaskDialog.Show("Error", 
                    $"Failed to open document viewer:\n\n{ex.Message}\n\nSee details:\n{ex.StackTrace}");
                
                message = ex.Message;
                return Result.Failed;
            }
        }
    }
}
