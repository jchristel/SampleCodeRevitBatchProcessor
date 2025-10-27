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

using duHastNet.DocManager.UI.Shared.Interfaces;
using System.IO;
using System.Windows;

namespace duHastNet.DocManager.UI.Shared.Services;

/// <summary>
/// WPF implementation of dialog services
/// </summary>
public class DialogService : IDialogService
{
    /// <summary>
    /// Shows a folder browser dialog
    /// </summary>
    public string? ShowFolderBrowserDialog(string title, string? initialDirectory = null)
    {
        using var dialog = new FolderBrowserDialog
        {
            Description = title,
            UseDescriptionForTitle = true,
            ShowNewFolderButton = true
        };

        if (!string.IsNullOrEmpty(initialDirectory) && Directory.Exists(initialDirectory))
        {
            dialog.SelectedPath = initialDirectory;
        }

        var result = dialog.ShowDialog();
        return result == DialogResult.OK ? dialog.SelectedPath : null;
    }

    /// <summary>
    /// Shows an open file dialog
    /// </summary>
    public string[]? ShowOpenFileDialog(string title, string filter, string? initialDirectory = null, bool multiselect = false)
    {
        var dialog = new Microsoft.Win32.OpenFileDialog
        {
            Title = title,
            Filter = filter,
            CheckFileExists = true,
            Multiselect = multiselect,
            InitialDirectory = initialDirectory ?? Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
        };

        var result = dialog.ShowDialog();
        return result == true ? (multiselect ? dialog.FileNames : new[] { dialog.FileName }) : null;
    }

    /// <summary>
    /// Shows a save file dialog
    /// </summary>
    public string? ShowSaveFileDialog(string title, string filter, string defaultExtension, string? initialDirectory = null)
    {
        var dialog = new Microsoft.Win32.SaveFileDialog
        {
            Title = title,
            Filter = filter,
            DefaultExt = defaultExtension,
            AddExtension = true,
            OverwritePrompt = true,
            InitialDirectory = initialDirectory ?? Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
        };

        var result = dialog.ShowDialog();
        return result == true ? dialog.FileName : null;
    }

    /// <summary>
    /// Shows a message box dialog
    /// </summary>
    public MessageBoxResult ShowMessageBox(
        string message,
        string title,
        MessageBoxButton button = MessageBoxButton.OK,
        MessageBoxImage icon = MessageBoxImage.None)
    {
        return System.Windows.MessageBox.Show(message, title, button, icon);
    }
}