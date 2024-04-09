using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using Serilog;

namespace RBP_Launcher.Utilities
{
    public class IronPythonInstall
    {
        public static string? GetLatestVersionInstallPath()
        {
            string? latestInstallPath = null;
            // get all versions
            Dictionary<string, string> installPaths = GetIronPythonInstallPaths();
            if (installPaths == null || installPaths.Count == 0)
            {
                return latestInstallPath;
            }

            //get the latest version based on the key
            var sortedPairs = installPaths.OrderBy(kv => ParseVersion(kv.Key));
            // Reconstruct an OrderedDictionary from the sorted key-value pairs
            OrderedDictionary orderedDict = new();
            foreach (var kvp in sortedPairs)
            {
                orderedDict.Add(kvp.Key, kvp.Value);
            }

            // Check if the dictionary is not empty
            if (orderedDict.Count > 0)
            {
                var latestItem = orderedDict[orderedDict.Count - 1];
                if (latestItem != null)
                {
                    return latestItem.ToString();
                }
            }

            return latestInstallPath;
        }

        private static (int, int) ParseVersion(string version)
        {
            var parts = version.Split('.');
            int major = int.Parse(parts[0]);
            int minor = int.Parse(parts[1]);
            return (major, minor);
        }

        public static Dictionary<string, string> GetIronPythonInstallPaths()
        {
            Dictionary<string, string> installPaths = new();
            try
            {

                installPaths = RegistryTools.GetNestedSubKeyValues(
                    RegistryTools._keyInstallPath,
                    @"SOFTWARE\IronPython",
                    Registry.LocalMachine
                );
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(IronPythonInstall), nameof(GetIronPythonInstallPaths));
            }
            return installPaths;
        }
    }
}
