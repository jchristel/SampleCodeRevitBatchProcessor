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

using Newtonsoft.Json;
using System;
using System.IO;

namespace duHastNet.PushIt.Utilities
{
    public static class SettingsUtils
    {
        public static string settingsDirectory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "duHast");

        private static string settingsFilePath = Path.Combine(settingsDirectory, "pushIt_settings.json");

        /// <summary>
        /// Loads settings from the settings file.
        /// If the file does not exist a safe default is returned.
        /// <para>
        /// If the file was written before the DataSource refactor (i.e. it
        /// contains a plain <c>DataPath</c> string but no <c>DataSource</c>
        /// object), the legacy value is automatically migrated into
        /// <see cref="Models.DataSourceSettings.CsvConfig"/> so the rest of
        /// the application never needs to read <c>DataPath</c> again.
        /// The migration is transparent — no manual file editing is required.
        /// </para>
        /// </summary>
        public static Models.Settings LoadSettings()
        {
            try
            {
                // No settings file yet — return a safe default
                if (!File.Exists(settingsFilePath))
                {
                    return new Models.Settings
                    {
                        DataSource = new Models.DataSourceSettings(),
                        EnabledCategoryNames = ["Walls"]
                    };
                }

                string jsonString = File.ReadAllText(settingsFilePath);
                Models.Settings settings = JsonConvert.DeserializeObject<Models.Settings>(jsonString);

                // Safety fallback: at least one category must always be present
                if (settings.EnabledCategoryNames == null || settings.EnabledCategoryNames.Count == 0)
                {
                    settings.EnabledCategoryNames = ["Walls"];
                }

                // ── Migration: legacy DataPath → DataSource.CsvConfig ─────────────
                // Old settings files contain a non-empty DataPath string and no
                // DataSource object. Promote the path into the nested CSV config
                // so all downstream code works exclusively through DataSource.
                if (settings.DataSource == null ||
                    settings.DataSource.SourceType == Models.DataSourceType.None)
                {
                    if (!string.IsNullOrEmpty(settings.DataPath))
                    {
                        // Carry the legacy file path forward as a CSV config
                        settings.DataSource = new Models.DataSourceSettings(
                            Models.DataSourceType.Csv,
                            settings.DataPath);
                    }
                    else
                    {
                        // No legacy path either — leave as None so the user is
                        // prompted to configure a source via the new UI
                        settings.DataSource = new Models.DataSourceSettings();
                    }
                }
                // ── End migration ─────────────────────────────────────────────────

                return settings;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading settings: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Serialises <paramref name="settings"/> to the settings file.
        /// The legacy <c>DataPath</c> field is cleared before saving so it is
        /// silently dropped from the JSON on the first save after migration,
        /// without requiring any manual file editing.
        /// </summary>
        public static void SaveSettings(Models.Settings settings)
        {
            try
            {
                if (!Directory.Exists(settingsDirectory))
                {
                    try
                    {
                        Directory.CreateDirectory(settingsDirectory);
                    }
                    catch (Exception ex)
                    {
                        System.Windows.Forms.MessageBox.Show(
                            $"Failed to save settings with exception {ex.Message}",
                            "Exception at save",
                            System.Windows.Forms.MessageBoxButtons.OK,
                            System.Windows.Forms.MessageBoxIcon.Error);
                        return;
                    }
                }

                // Clear the legacy field before serialising so it is not written
                // back once the migration has run. NullValueHandling.Ignore on
                // the property means null is omitted from the JSON entirely.
                settings.DataPath = null;

                string jsonString = JsonConvert.SerializeObject(settings, Formatting.None);
                File.WriteAllText(settingsFilePath, jsonString);
            }
            catch (Exception ex)
            {
                System.Windows.Forms.MessageBox.Show(
                    $"Failed to save settings with exception {ex.Message}",
                    "Exception at save",
                    System.Windows.Forms.MessageBoxButtons.OK,
                    System.Windows.Forms.MessageBoxIcon.Error);
            }
        }
    }
}
