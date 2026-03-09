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

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace duHastNet.Utils.Logging
{
    /// <summary>
    /// Utility class for cleaning up old log files from a directory.
    /// </summary>
    public class LogFileCleanup
    {
        private List<string> _errorMessages = [];

        /// <summary>
        /// Any errors encountered during the last cleanup operation.
        /// </summary>
        public IReadOnlyList<string> ErrorMessages => _errorMessages.AsReadOnly();

        /// <summary>
        /// Deletes log files in the specified directory that are older than the given number of days.
        /// </summary>
        /// <param name="directoryPath">Directory to scan for old log files.</param>
        /// <param name="olderThanDays">Files last written more than this many days ago will be deleted.</param>
        /// <param name="fileNamePrefix">
        /// Optional prefix that file names must start with (case-insensitive), e.g. "AppLog_".
        /// Pass null or empty to match all files with the given extension.
        /// </param>
        /// <param name="fileExtension">
        /// File extension filter, e.g. "*.csv" or "*.log". Defaults to "*.csv" to match
        /// the format used by <see cref="SimpleLogger"/>.
        /// </param>
        /// <param name="includeSubDirectories">Whether to recurse into sub-directories.</param>
        /// <returns>A list of the file paths that were successfully deleted.</returns>
        public List<string> DeleteOldLogFiles(
            string directoryPath,
            int olderThanDays,
            string fileNamePrefix = null,
            string fileExtension = "*.csv",
            bool includeSubDirectories = false)
        {
            _errorMessages = [];
            var deleted = new List<string>();

            if (!ValidateArguments(directoryPath, olderThanDays, fileExtension))
                return deleted;

            var cutoff = DateTime.Now.AddDays(-olderThanDays);
            var searchOption = includeSubDirectories
                ? SearchOption.AllDirectories
                : SearchOption.TopDirectoryOnly;

            IEnumerable<string> candidates;
            try
            {
                candidates = Directory.EnumerateFiles(directoryPath, fileExtension, searchOption);
            }
            catch (Exception ex)
            {
                _errorMessages.Add($"Error enumerating files in '{directoryPath}': {ex.Message}");
                return deleted;
            }

            // Apply prefix filter when a non-empty prefix is supplied
            bool applyPrefixFilter = !string.IsNullOrEmpty(fileNamePrefix);

            foreach (var filePath in candidates)
            {
                try
                {
                    if (applyPrefixFilter)
                    {
                        var fileName = Path.GetFileName(filePath);
                        if (!fileName.StartsWith(fileNamePrefix, StringComparison.OrdinalIgnoreCase))
                            continue;
                    }

                    if (File.GetLastWriteTime(filePath) < cutoff)
                    {
                        File.Delete(filePath);
                        deleted.Add(filePath);
                    }
                }
                catch (Exception ex)
                {
                    _errorMessages.Add($"Error deleting '{filePath}': {ex.Message}");
                }
            }

            return deleted;
        }

        /// <summary>
        /// Asynchronous version of <see cref="DeleteOldLogFiles"/>.
        /// Offloads the file-system work to a background thread so the UI thread is not blocked.
        /// </summary>
        /// <param name="directoryPath">Directory to scan for old log files.</param>
        /// <param name="olderThanDays">Files last written more than this many days ago will be deleted.</param>
        /// <param name="fileNamePrefix">Optional file name prefix filter. Pass null or empty to match all files.</param>
        /// <param name="fileExtension">File extension filter. Defaults to "*.csv".</param>
        /// <param name="includeSubDirectories">Whether to recurse into sub-directories.</param>
        /// <returns>A task whose result is the list of file paths that were successfully deleted.</returns>
        public Task<List<string>> DeleteOldLogFilesAsync(
            string directoryPath,
            int olderThanDays,
            string fileNamePrefix = null,
            string fileExtension = "*.csv",
            bool includeSubDirectories = false)
        {
            return Task.Run(() =>
                DeleteOldLogFiles(directoryPath, olderThanDays, fileNamePrefix, fileExtension, includeSubDirectories));
        }

        /// <summary>
        /// Fire-and-forget version of <see cref="DeleteOldLogFiles"/>.
        /// Errors are captured in <see cref="ErrorMessages"/> and any unhandled exceptions are
        /// appended there rather than propagated to the caller.
        /// </summary>
        /// <param name="directoryPath">Directory to scan for old log files.</param>
        /// <param name="olderThanDays">Files last written more than this many days ago will be deleted.</param>
        /// <param name="fileNamePrefix">Optional file name prefix filter. Pass null or empty to match all files.</param>
        /// <param name="fileExtension">File extension filter. Defaults to "*.csv".</param>
        /// <param name="includeSubDirectories">Whether to recurse into sub-directories.</param>
        public void DeleteOldLogFilesFireAndForget(
            string directoryPath,
            int olderThanDays,
            string fileNamePrefix = null,
            string fileExtension = "*.csv",
            bool includeSubDirectories = false)
        {
            Task.Run(async () =>
            {
                try
                {
                    await DeleteOldLogFilesAsync(directoryPath, olderThanDays, fileNamePrefix, fileExtension, includeSubDirectories);
                }
                catch (Exception ex)
                {
                    _errorMessages.Add($"Cleanup error: {ex.Message}");
                }
            });
        }

        // -------------------------------------------------------------------------
        // Private helpers
        // -------------------------------------------------------------------------

        private bool ValidateArguments(string directoryPath, int olderThanDays, string fileExtension)
        {
            if (string.IsNullOrWhiteSpace(directoryPath))
            {
                _errorMessages.Add("directoryPath must not be null or empty.");
                return false;
            }

            if (olderThanDays < 0)
            {
                _errorMessages.Add($"olderThanDays must be a non-negative integer (received {olderThanDays}).");
                return false;
            }

            if (string.IsNullOrWhiteSpace(fileExtension))
            {
                _errorMessages.Add("fileExtension must not be null or empty.");
                return false;
            }

            if (!Directory.Exists(directoryPath))
            {
                _errorMessages.Add($"Directory not found: '{directoryPath}'.");
                return false;
            }

            return true;
        }
    }
}
