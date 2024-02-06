using System;
using Microsoft.Win32;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Serilog;


namespace RBP_Launcher.Utilities
{
    public class CPythonInstall
    {
        public static KeyValuePair<string, string> GetLatestPythonVersion()
        {
            try
            {
                Dictionary<string, string> versions = GetAllStandardPythonInstalls();
                //check for empty dictioanry ( no python installed)
                if (versions.Count == 0)
                {
                    throw new Exception("No standard python installations found");
                }
                // Find the version with the highest major version, then highest minor version
                var latestVersion = versions.OrderByDescending(kv => kv.Key[0])
                                           .ThenByDescending(kv => kv.Key.Length > 1 ? int.Parse(kv.Key.Substring(1)) : 0)
                                           .First();

                return latestVersion;
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(CPythonInstall), nameof(GetLatestPythonVersion));
                return default (KeyValuePair<string, string>);
            }
            
        }

        public static Dictionary<string, string> GetAllStandardPythonInstalls()
        {
            List<string>allUsers = GetStandardPythonInstallPaths();
            List<string>currentUser = GetCurrentUserPythonInstallPaths();

            allUsers.AddRange(currentUser);

            Dictionary<string,string> result = new Dictionary<string,string>();
            foreach (string pythonInstallPath in allUsers)
            {
                string? pythonVersion = GetParentDirectoryName(pythonInstallPath);
                if (pythonVersion != null)
                {
                    string? pythonVersionNumber = GetPythonVersion(pythonVersion);
                    if (pythonVersionNumber != null)
                    {
                        result[pythonVersionNumber] = pythonInstallPath;
                    }
                }
                
            }
             
            return result;
        }
        public static string? GetParentDirectoryName(string directoryPath)
        {
            // Get the parent directory's full path
            string? parentDirectoryPath = Path.GetDirectoryName(directoryPath);

            if(parentDirectoryPath != null)
            {
                // Extract the last part of the path (parent directory's name)
                string? parentDirectoryName = Path.GetFileName(parentDirectoryPath);
                return parentDirectoryName;
            }
            else
            {
                return null;
            }

            
        }

        public static string? GetPythonVersion(string input)
        {
            // Define a regular expression pattern to match "Python" followed by digits
            string pattern = @"Python(\d+)";

            // Use Regex.Match to find the first match in the input string
            Match match = Regex.Match(input, pattern);

            // If a match is found, retrieve the captured version number
            if (match.Success)
            {
                // The version number is captured in the first capturing group
                return match.Groups[1].Value;
            }

            // If no match is found, return an indication that the version couldn't be extracted
            return null;
        }

        
        public static List<string> GetStandardPythonInstallPaths()
        {

            Dictionary<string, string> result32 = RegistryTools.GetNestedSubKeyValues(
                RegistryTools._keyInstallPath, 
                @"SOFTWARE\Python\PythonCore",
                Registry.LocalMachine
            );
            Dictionary<string, string> result64 = RegistryTools.GetNestedSubKeyValues(
                RegistryTools._keyInstallPath, 
                @"SOFTWARE\Wow6432Node\Python\PythonCore",
                Registry.LocalMachine
            );

            List<string> pythonPaths = result32.Values.Concat(result64.Values).ToList();
            return pythonPaths;


            //// Registry base key for 32-bit Python installations
            //RegistryKey baseKey32 = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\Python\PythonCore");

            //if (baseKey32 != null)
            //{
            //    // Get the list of installed Python versions
            //    string[] versionKeys32 = baseKey32.GetSubKeyNames();

            //    // Iterate through each Python version
            //    foreach (var versionKeyName in versionKeys32)
            //    {
            //        using (RegistryKey versionKey32 = baseKey32.OpenSubKey(versionKeyName))
            //        {
            //            string installPath32 = RegistryTools.GetSubKeyValue(RegistryTools._keyInstallPath, versionKey32);
            //            if (!string.IsNullOrEmpty(installPath32))
            //            {
            //                pythonPaths.Add(installPath32);
            //            }
            //        }
            //    }
            //}

            //// Registry base key for 64-bit Python installations
            //RegistryKey baseKey64 = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\Wow6432Node\Python\PythonCore");

            //if (baseKey64 != null)
            //{
            //    // Get the list of installed Python versions
            //    string[] versionKeys64 = baseKey64.GetSubKeyNames();

            //    // Iterate through each Python version
            //    foreach (var versionKeyName in versionKeys64)
            //    {
            //        using (RegistryKey versionKey64 = baseKey64.OpenSubKey(versionKeyName))
            //        {
            //            string installPath64 = RegistryTools.GetSubKeyValue(RegistryTools._keyInstallPath, versionKey64);
            //            if (!string.IsNullOrEmpty(installPath64))
            //            {
            //                pythonPaths.Add(installPath64);
            //            }
            //        }
            //    }
            //}

            //return pythonPaths;
        }

        public static List<string> GetCurrentUserPythonInstallPaths()
        {

            Dictionary<string, string> result32 = RegistryTools.GetNestedSubKeyValues(
                RegistryTools._keyInstallPath,
                @"SOFTWARE\Python\PythonCore",
                Registry.CurrentUser
            );
            Dictionary<string, string> result64 = RegistryTools.GetNestedSubKeyValues(
                RegistryTools._keyInstallPath,
                @"SOFTWARE\Wow6432Node\Python\PythonCore",
                Registry.CurrentUser
            );

            List<string> pythonPaths = result32.Values.Concat(result64.Values).ToList();
            return pythonPaths;


            //List<string> pythonPaths = new List<string>();

            //// Registry base key for 32-bit Python installations in the current user hive
            //RegistryKey baseKey32 = Registry.CurrentUser.OpenSubKey(@"SOFTWARE\Python\PythonCore");

            //if (baseKey32 != null)
            //{
            //    // Get the list of installed Python versions
            //    string[] versionKeys32 = baseKey32.GetSubKeyNames();

            //    // Iterate through each Python version
            //    foreach (var versionKey in versionKeys32)
            //    {
            //        // Get the install path for each Python version
            //        RegistryKey versionKey32 = baseKey32.OpenSubKey($@"{versionKey}\InstallPath");
            //        string installPath32 = versionKey32?.GetValue("").ToString();

            //        if (!string.IsNullOrEmpty(installPath32))
            //        {
            //            pythonPaths.Add(installPath32);
            //        }
            //    }
            //}

            //// Registry base key for 64-bit Python installations in the current user hive
            //RegistryKey baseKey64 = Registry.CurrentUser.OpenSubKey(@"SOFTWARE\Wow6432Node\Python\PythonCore");

            //if (baseKey64 != null)
            //{
            //    // Get the list of installed Python versions
            //    string[] versionKeys64 = baseKey64.GetSubKeyNames();

            //    // Iterate through each Python version
            //    foreach (var versionKey in versionKeys64)
            //    {
            //        // Get the install path for each Python version
            //        RegistryKey versionKey64 = baseKey64.OpenSubKey($@"{versionKey}\InstallPath");
            //        string installPath64 = versionKey64?.GetValue("").ToString();

            //        if (!string.IsNullOrEmpty(installPath64))
            //        {
            //            pythonPaths.Add(installPath64);
            //        }
            //    }
            //}

            //return pythonPaths;
        }
    }
}
