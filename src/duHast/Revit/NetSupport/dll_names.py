"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.net dll names currently in use.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is required since the dll's used have a version number in their file name.

"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
# 

DLL_VERSION = ".23.0.0.5"

# family reloader ui
FAMILY_RELOADER_UI = "FamilyReloaderUI{}.dll".format(DLL_VERSION)

# pdf and dwg exporter selection ui
PDF_AND_DWG_EXPORTER_SELECTION_UI = "PDFDWGExporterSelectionUI{}.dll".format(DLL_VERSION)

# pdf and dwg exporter settings ui
PDF_AND_DWG_EXPORTER_SETTINGS_UI = "PDFDWGExporterUI{}.dll".format(DLL_VERSION)

# .net revit utility classes
REVIT_UTILS= 'RevitUtils{}.dll'.format(DLL_VERSION)

# .net custom controls
WPF_CUSTOM_CONTROLS = "duHastUICustomControls{}.dll".format(DLL_VERSION)

# .net wrapper class  of csv helper
FILE_WRAPPER = "FileIOWrapper{}.dll".format(DLL_VERSION)

# .net utility classes
UTILITY = "Utils{}.dll".format(DLL_VERSION)