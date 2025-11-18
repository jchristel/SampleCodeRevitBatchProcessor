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
using Autodesk.Revit.UI;
using duHastNet.DocManager.UI.Shared.Services;
using System;
using System.Windows;

namespace duHastNet.DocManager.Revit.RevitAddIn
{
    /// <summary>
    /// External Command that launches the DocManager application.
    /// Revit is used solely as a launcher to bypass executable restrictions.
    /// The DocManager runs as an independent WPF window with no Revit API interaction.
    /// </summary>
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class LaunchDocManagerCommand : IExternalCommand
    {
        /// <summary>
        /// Static reference to track if a window is already open.
        /// Prevents multiple instances from being launched simultaneously.
        /// </summary>
        private static Window? _window;

        /// <summary>
        /// Static reference to the bootstrapper instance.
        /// Maintains lifecycle across multiple command invocations.
        /// </summary>
        private static DocManagerBootstrapper? _bootstrapper;

        /// <summary>
        /// Executes the command to launch DocManager.
        /// Uses a dedicated STA thread with synchronous initialization to support WPF UI.
        /// </summary>
        /// <param name="commandData">Command data from Revit (not used)</param>
        /// <param name="message">Error message to return to Revit if command fails</param>
        /// <param name="elements">Element set for error reporting (not used)</param>
        /// <returns>Result indicating success or failure</returns>
        public Result Execute(
            ExternalCommandData commandData,
            ref string message,
            ElementSet elements)
        {
            try
            {
                // Check if window already exists and is loaded
                if (_window != null && _window.IsLoaded)
                {
                    // Window already open - bring to front on its own thread
                    _window.Dispatcher.Invoke(() =>
                    {
                        _window.Activate();
                        _window.WindowState = WindowState.Normal;
                    });
                    return Result.Succeeded;
                }

                // Launch initialization on a new STA thread
                // Must use synchronous delegate (not async) for Thread constructor
                var thread = new System.Threading.Thread(() =>
                {
                    try
                    {
                        // Set up WPF synchronization context for this STA thread
                        // Required before creating any WPF UI elements
                        System.Threading.SynchronizationContext.SetSynchronizationContext(
                            new System.Windows.Threading.DispatcherSynchronizationContext());

                        // Create new bootstrapper instance if needed
                        if (_bootstrapper == null)
                        {
                            _bootstrapper = new DocManagerBootstrapper();
                        }

                        // Initialize the application synchronously on STA thread
                        _window = _bootstrapper.Initialize();

                        // Subscribe to window closed event to clean up reference
                        _window.Closed += Window_Closed;

                        // Show the window
                        _window.Show();

                        // Start WPF message pump to keep window responsive
                        System.Windows.Threading.Dispatcher.Run();
                    }
                    catch (Exception ex)
                    {
                        // Log error (in production, use proper logging)
                        System.Diagnostics.Debug.WriteLine($"Failed to initialize DocManager: {ex.Message}");

                        // Show error to user via MessageBox
                        System.Windows.MessageBox.Show(
                            $"Failed to launch DocManager: {ex.Message}",
                            "DocManager Error",
                            System.Windows.MessageBoxButton.OK,
                            System.Windows.MessageBoxImage.Error);
                    }
                });

                // Set thread to STA (Single-Threaded Apartment) for WPF compatibility
                thread.SetApartmentState(System.Threading.ApartmentState.STA);
                thread.IsBackground = true; // Thread terminates when main app exits
                thread.Start();

                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                // Return error message to Revit for catastrophic failures
                message = $"Failed to launch DocManager: {ex.Message}";
                return Result.Failed;
            }
        }

        /// <summary>
        /// Handles the window closed event to clean up static references.
        /// </summary>
        private static void Window_Closed(object? sender, EventArgs e)
        {
            // Clean up window reference
            if (_window != null)
            {
                _window.Closed -= Window_Closed;
                _window = null;
            }

            // Dispose and clean up bootstrapper
            if (_bootstrapper != null)
            {
                _bootstrapper.Dispose();
                _bootstrapper = null;
            }
        }
    }
}