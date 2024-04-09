using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Serilog;
using Microsoft.Win32;

namespace RBP_Launcher.Utilities
{
    public class RegistryTools
    {
        public static string _keyInstallPath = "InstallPath";

        /// <summary>
        /// Returns the value of a sub key from a provided registry key
        /// </summary>
        /// <param name="subKeyName"></param>
        /// <param name="key"></param>
        /// <returns></returns>
        public static string? GetSubKeyValue(string subKeyName, RegistryKey key)
        {
            string? subKeyValue = null;

            try
            {
                // Check if the subkey exists
                if (key.GetSubKeyNames().Contains(subKeyName))
                {
                    using (RegistryKey? installPathKey = key.OpenSubKey(subKeyName))
                    {
                        if (installPathKey != null)
                        {
                            // Get the value of the subkey
                            subKeyValue = installPathKey.GetValue("") as string;
                        }
                    }
                }
                else
                {
                    Log.Debug($"{subKeyName} subkey not found  in key: {key.Name}");
                }
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(RegistryTools), nameof(GetSubKeyValue));
            }
            return subKeyValue;
        }


        public static Dictionary<string,string> GetNestedSubKeyValues(string subKeyNameMatch, string baseKeyName, RegistryKey rootKey)
        {
            Dictionary<string, string> values = new Dictionary<string, string>();

            try
            {
                // Registry base key for 32-bit Python installations
                RegistryKey? baseKey = rootKey.OpenSubKey(baseKeyName);

                if (baseKey != null)
                {
                    // Get the list of installed Python versions
                    string[] subKeyNames = baseKey.GetSubKeyNames();

                    // Iterate through each Python version
                    foreach (var subKeyName in subKeyNames)
                    {
                        using (RegistryKey? subKey = baseKey.OpenSubKey(subKeyName))
                        {
                            if (subKey != null)
                            {
                                string? value = GetSubKeyValue(subKeyNameMatch, subKey);
                                if (!string.IsNullOrEmpty(value))
                                {
                                    values[subKeyName] = value;
                                }
                                else
                                {
                                    Log.Debug($"{subKeyNameMatch} value is null or empty for base key {subKey.Name}");
                                }
                            }
                        }
                    }
                }
                else
                {
                    Log.Debug($"Unable to open registry key {baseKeyName} from root {rootKey.Name}");
                }
            }
            catch (Exception ex)
            {
                Log.Error(ex, "An error occurred in {ClassName}.{MethodName}", nameof(RegistryTools), nameof(GetNestedSubKeyValues));
            }
            
            return values;
        }
    }
}
