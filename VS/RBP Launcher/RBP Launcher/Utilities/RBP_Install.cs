using System;
using Microsoft.Win32;

namespace RBP_Launcher.Utilities
{
    public class RBP_Install
    {
        
        public static string? GetInstallPathFromRegistry(string applicationName)
        {
            string uninstallKeyPath = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall";

            using (RegistryKey? uninstallKey = Registry.LocalMachine.OpenSubKey(uninstallKeyPath))
            {
                if (uninstallKey != null)
                {
                    foreach (string subKeyName in uninstallKey.GetSubKeyNames())
                    {
                        using RegistryKey? appKey = uninstallKey.OpenSubKey(subKeyName);
                        if (appKey != null)
                        {
                            object? displayName = appKey.GetValue("DisplayName");
                            if (displayName != null && displayName.ToString() == applicationName)
                            {
                                object? installLocation = appKey.GetValue("InstallLocation");
                                if (installLocation != null)
                                {
                                    return installLocation.ToString();
                                }
                            }
                        }
                    }
                }
            }

            return null;
        }

        public static string? GetInstallPathForCurrentUser(string applicationName)
        {
            // Base registry key for the current user
            RegistryKey baseKey = Registry.CurrentUser;

            // Subkey path for uninstall information
            string uninstallKeyPath = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{B5CA57EA-7BB2-4620-916C-AE98376C1EF1}_is1";

            using (RegistryKey? appKey = baseKey.OpenSubKey(uninstallKeyPath))
            {
                if (appKey != null)
                {
                    // Check if the application name matches
                    object? displayName = appKey.GetValue("DisplayName");
                    if (displayName != null && displayName.ToString() == applicationName)
                    {
                        // Get the install path
                        object? installLocation = appKey.GetValue("InstallLocation");
                        if (installLocation != null)
                        {
                            return installLocation.ToString();
                        }
                    }
                }
            }

            return null;
        }
    }
}
