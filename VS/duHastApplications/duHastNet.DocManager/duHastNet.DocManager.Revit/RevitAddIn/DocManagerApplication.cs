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

using Autodesk.Revit.UI;
using System;
using System.IO;
using System.Reflection;

namespace duHastNet.DocManager.Revit.RevitAddIn
{
    /// <summary>
    /// External Application that manages the DocManager add-in lifecycle.
    /// Handles Revit startup and shutdown events.
    /// Creates ribbon panel and button for launching DocManager.
    /// </summary>
    public class DocManagerApplication : IExternalApplication
    {
        /// <summary>
        /// Called when Revit starts up.
        /// Creates the ribbon panel and button for launching DocManager.
        /// </summary>
        /// <param name="application">Revit UI application</param>
        /// <returns>Result indicating success or failure</returns>
        public Result OnStartup(UIControlledApplication application)
        {
            try
            {
                // Create ribbon panel on the Add-Ins tab
                RibbonPanel ribbonPanel = application.CreateRibbonPanel("DocManager");

                // Get the assembly location for the command
                string assemblyPath = Assembly.GetExecutingAssembly().Location;

                // Create push button data
                PushButtonData buttonData = new PushButtonData(
                    "DocManagerLaunchButton",
                    "Launch\r\nDocManager",
                    assemblyPath,
                    "duHastNet.DocManager.Revit.RevitAddIn.LaunchDocManagerCommand");

                // Set tooltip
                buttonData.ToolTip = "Launch the DocManager application";
                buttonData.LongDescription = "Opens the Document Manager application as an independent window. " +
                                            "DocManager can be used while Revit continues running.";

                // Try to set icon if available
                try
                {
                    string iconPath = Path.Combine(Path.GetDirectoryName(assemblyPath) ?? "", "Resources", "DocManager32.png");
                    if (File.Exists(iconPath))
                    {
                        buttonData.LargeImage = new System.Windows.Media.Imaging.BitmapImage(new Uri(iconPath));
                    }
                }
                catch
                {
                    // Icon loading is optional - continue without icon if it fails
                }

                // Add the button to the ribbon panel
                ribbonPanel.AddItem(buttonData);

                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                TaskDialog.Show("DocManager Startup Error",
                    $"Failed to initialize DocManager add-in: {ex.Message}");
                return Result.Failed;
            }
        }

        /// <summary>
        /// Called when Revit shuts down.
        /// Performs any necessary cleanup.
        /// </summary>
        /// <param name="application">Revit UI application</param>
        /// <returns>Result indicating success or failure</returns>
        public Result OnShutdown(UIControlledApplication application)
        {
            // No cleanup needed - bootstrapper handles its own disposal
            return Result.Succeeded;
        }
    }
}
