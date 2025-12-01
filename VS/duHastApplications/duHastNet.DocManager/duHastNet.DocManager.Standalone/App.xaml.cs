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

using duHastNet.DocManager.UI.Shared.Services;
using System.Windows;

namespace DocManager.Standalone;

/// <summary>
/// Interaction logic for App.xaml
/// Simplified to use DocManagerBootstrapper for initialization
/// </summary>
public partial class App : Application
{
    private DocManagerBootstrapper? _bootstrapper;

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        try
        {
            // Parse command-line arguments for custom settings path
            string? customSettingsPath = ParseSettingsPathFromArguments(e.Args);

            var bootstrapper = new DocManagerBootstrapper();
            Window window;

            if (!string.IsNullOrEmpty(customSettingsPath))
            {
                // Custom settings path provided
                window = await bootstrapper.InitializeAsync(customSettingsPath);
            }
            else
            {
                // Use default settings location
                window = await bootstrapper.InitializeAsync();
            }

            window.Show();
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                $"Failed to start application: {ex.Message}",
                "Startup Error",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
            Shutdown(1);
        }
    }

    // Add this helper method to your App class
    private string? ParseSettingsPathFromArguments(string[] args)
    {
        if (args == null || args.Length == 0)
            return null;

        // Look for --settings=path argument
        foreach (var arg in args)
        {
            if (arg.StartsWith("--settings=", StringComparison.OrdinalIgnoreCase))
            {
                string path = arg.Substring("--settings=".Length).Trim('"');
                return string.IsNullOrWhiteSpace(path) ? null : path;
            }
        }

        return null;
    }

    protected override void OnExit(ExitEventArgs e)
    {
        // Bootstrapper handles its own cleanup via Window.Closed event
        // But we can also explicitly dispose here for completeness
        _bootstrapper?.Dispose();

        base.OnExit(e);
    }
}