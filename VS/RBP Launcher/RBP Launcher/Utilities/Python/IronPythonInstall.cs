using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using Serilog;

namespace RBP_Launcher.Utilities
{
    public class IronPythonInstall
    {
        public static string GetLatestVersionInstallPath()
        {
            string latestInstallPath = null;
            // get all versions
            Dictionary<string, string> installPaths = GetIronPythonInstallPaths();
            if (installPaths == null)
            {
                return latestInstallPath;
            }

            //get the latest version based on the key
            var sortedPairs= installPaths.OrderBy(kv => ParseVersion(kv.Key));
            // Reconstruct an OrderedDictionary from the sorted key-value pairs
            OrderedDictionary orderedDict = new OrderedDictionary();
            foreach (var kvp in sortedPairs)
            {
                orderedDict.Add(kvp.Key, kvp.Value);
            }
            return (orderedDict[orderedDict.Count - 1]).ToString();
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
            Dictionary<string, string> installPaths = new Dictionary<string, string>();
            try
            {

                installPaths = RegistryTools.GetNestedSubKeyValues(
                    RegistryTools._keyInstallPath,
                    @"SOFTWARE\IronPython",
                    Registry.LocalMachine
                );

                //// Determine the base registry key to use based on the application's bitness
                //RegistryKey baseKey = Registry.LocalMachine;
                //if (Environment.Is64BitProcess)
                //{
                //    baseKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64);
                //}

                //// Open the registry key for IronPython installations
                //using (RegistryKey ironPythonKey = baseKey.OpenSubKey(@"SOFTWARE\IronPython"))
                //{
                //    if (ironPythonKey != null)
                //    {
                //        // Get the names of all subkeys (versions)
                //        string[] versions = ironPythonKey.GetSubKeyNames();
                //        // Iterate through each version to get the install path
                //        foreach (string version in versions)
                //        {
                //            using (RegistryKey versionKey = ironPythonKey.OpenSubKey(version))
                //            {
                //                if (versionKey != null)
                //                {
                //                    string installPath = RegistryTools.GetSubKeyValue(RegistryTools._keyInstallPath, versionKey);
                //                    if (!string.IsNullOrEmpty(installPath))
                //                    {
                //                        installPaths[version]=installPath;
                //                    }
                //                    else
                //                    {
                //                        Log.Debug($"InstallPath value is null or empty for IronPython version {version}");
                //                    }
                //                }
                //                else
                //                {
                //                    Log.Debug($"Unable to open registry key for IronPython version {version}");
                //                }
                //            }
                //        }
                //    }
                //    else
                //    {
                //        Log.Debug("Registry key for IronPython not found");
                //    }
                //}
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(IronPythonInstall), nameof(GetIronPythonInstallPaths));
            }
            return installPaths;
        }
    }
}
