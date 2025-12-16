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


using duHastNet.DocManager.Core.Models.CurrentFolder;

namespace duHastNet.DocManager.UI.Shared.ViewModels.Settings.CurrentFolder
{
    /// <summary>
    /// ViewModel wrapper for SupportedFileType for display in ListView
    /// Provides formatted display strings for the UI
    /// </summary>
    public class SupportedFileTypeViewModel
    {
        /// <summary>
        /// Reference to the underlying domain model
        /// </summary>
        public SupportedFileType UnderlyingFileType { get; }

        /// <summary>
        /// File extension for display (e.g., ".pdf", ".dwg")
        /// </summary>
        public string FileExtension => UnderlyingFileType.FileExtension;

        /// <summary>
        /// Description of the file type (e.g., "PDF Document", "AutoCAD Drawing")
        /// </summary>
        public string Description => UnderlyingFileType.Description;

        /// <summary>
        /// Display string for the document number modifier
        /// Shows user-friendly description of what the modifier does
        /// Delegates to the modifier's GetDisplayText() method
        /// </summary>
        public string ModifierDisplay => UnderlyingFileType.DocumentNumberModifier?.GetDisplayText() ?? "None";

        /// <summary>
        /// Indicates if this file type is PDF (required and protected)
        /// </summary>
        public bool IsPdf => FileExtension.Equals(".pdf", StringComparison.OrdinalIgnoreCase);

        /// <summary>
        /// Constructor
        /// </summary>
        /// <param name="fileType">The underlying SupportedFileType model</param>
        public SupportedFileTypeViewModel(SupportedFileType fileType)
        {
            UnderlyingFileType = fileType ?? throw new ArgumentNullException(nameof(fileType));
        }
    }
}
