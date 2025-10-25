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


namespace duHastNet.DocManager.UI.Shared.Interfaces
{
    /// <summary>
    /// Interface for dialog services - provides abstraction for file and folder dialogs
    /// </summary>
    public interface IDialogService
    {
        /// <summary>
        /// Shows a folder browser dialog
        /// </summary>
        /// <param name="title">Dialog title</param>
        /// <param name="initialDirectory">Initial directory to display</param>
        /// <returns>Selected folder path, or null if cancelled</returns>
        string? ShowFolderBrowserDialog(string title, string? initialDirectory = null);

        /// <summary>
        /// Shows an open file dialog
        /// </summary>
        /// <param name="title">Dialog title</param>
        /// <param name="filter">File filter (e.g., "Database files (*.db)|*.db")</param>
        /// <param name="initialDirectory">Initial directory to display</param>
        /// <param name="multiselect">Allow multiple file selection</param>
        /// <returns>Selected file path(s), or null if cancelled</returns>
        string[]? ShowOpenFileDialog(string title, string filter, string? initialDirectory = null, bool multiselect = false);

        /// <summary>
        /// Shows a save file dialog
        /// </summary>
        /// <param name="title">Dialog title</param>
        /// <param name="filter">File filter</param>
        /// <param name="defaultExtension">Default file extension</param>
        /// <param name="initialDirectory">Initial directory to display</param>
        /// <returns>Selected file path, or null if cancelled</returns>
        string? ShowSaveFileDialog(string title, string filter, string defaultExtension, string? initialDirectory = null);
    }
}
