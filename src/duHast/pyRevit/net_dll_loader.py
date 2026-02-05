# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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


import clr
import System
import os
import sys

from duHast.Utilities.Objects.result import Result

from System.Collections.Generic import List


def get_bin_path(bin_directory = None):
    """
    Get the path to the bin directory of the extension. If a bin directory is provided, it will be used. Otherwise, the function will look for bin directories in the sys.path and return the shortest one.
    
    :param bin_directory: Optional path to the bin directory. If not provided, the function will search for bin directories in sys.path.
    :type bin_directory: str or None
    :return: Result object with status, message, and list of bin paths found.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    if bin_directory:
        # if a bin directory is provided, use that
        if os.path.exists(bin_directory) and os.path.isdir(bin_directory):
            return_value.append_message("Using provided bin directory: {}".format(bin_directory))
            return_value.result.append(bin_directory)
        else:
            return_value.update_sep(
                False, "Provided bin directory does not exist or is not a directory: {}".format(bin_directory)
            )
            return return_value
    else: 
        # get all the bin paths from the sys.path
        bin_paths = [path for path in sys.path if path.endswith("bin")]


        # Get the shortest path
        if bin_paths:
            shortest_path = min(bin_paths, key=len)
        else:
            shortest_path = None

        if shortest_path is None:
            return_value.update_sep(
                False, "No bin paths found in sys.path."
            )

            for p in sys.path:
                return_value.append_message("sys.path entry: {}".format(p))

            return return_value
        
        return_value.append_message("Using bin path: {}".format(shortest_path))
        return_value.result.append(shortest_path)
    
    return return_value
       

def find_dll_path(dll_name, bin_path, exact_match=True):
    """
    Find DLL path based on exact or startswith matching.

    :param dll_name: Name of the DLL to find (e.g., "MyLibrary.dll")
    :param bin_path: Directory to search for the DLL
    :param exact_match: If True, looks for an exact match of dll_name. If False, looks for files that start with dll_name.
    :return: Full path to the DLL if found, otherwise None
    """

    if exact_match:
        dll_path = os.path.join(bin_path, dll_name)
        return dll_path if os.path.exists(dll_path) else None
    else:
        if not os.path.exists(bin_path):
            return None
        matching_files = [
            f for f in os.listdir(bin_path) 
            if f.startswith(dll_name) and f.endswith('.dll')
        ]
        return os.path.join(bin_path, matching_files[0]) if matching_files else None


def is_assembly_loaded(assembly_name):
    """
    Check if an assembly with the given name is already loaded
    
    :param assembly_name: Name of the assembly to check (e.g., "MyLibrary")
    :return: True if assembly is loaded, False otherwise
    """

    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        if assembly_name in asm.FullName:
            return True
    return False


def load_net_dll_path(dlls_to_load, bin_directory = None,  exact_match=True):
    """
    Loads dlls from the libs folder of the duHast extension.
    Useful if a dll is not loaded through the startup script of a pyRevit extension.

    expects the bin folder to be in the sys.path
    which means it needs to be located in the root folder of the extension:
    YourExtension.extension\\bin

    :param dlls_to_load: List of dlls to load.
    :type dlls_to_load: list
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # type checking
        if not isinstance(dlls_to_load, list):
            return_value.update_sep(
                False, "dlls_to_load must be a list, got {} instead.".format(type(dlls_to_load))
            )
            return return_value


        # placeholder for bin paths to check for the dlls
        bin_path_result = get_bin_path(bin_directory=bin_directory)

        if not bin_path_result.status:
            return_value.update_sep(
                False, "Failed to get bin path. Error: {}".format(bin_path_result.message)
            )
            return return_value
        
        # get the path to be used for loading the dlls
        bin_paths = bin_path_result.result
        return_value.append_message("Found bin paths: {}".format(bin_paths))
        
        # Main loading loop
        for dll in dlls_to_load:
            found_match = False
            
            for p in bin_paths:

                # get the dll path
                dll_path = find_dll_path(dll, p, exact_match = exact_match)
                
                if dll_path:
                    # set the flag to indicate we found a match
                    found_match = True

                    # get the dll name without the file extension for checking if the assembly is already loaded
                    dll_name =os.path.splitext(dll)[0]

                    # check if the dll is already loaded
                    if  is_assembly_loaded(dll_name):
                        return_value.append_message("DLL {} is already loaded.".format(dll))
                        
                        # just add a reference to the already loaded assembly
                        # Find the already-loaded assembly
                        assembly = None
                        for asm in System.AppDomain.CurrentDomain.GetAssemblies():
                            if dll_name in asm.FullName:
                                assembly = asm
                                break
                        if assembly:
                            # Register it with IronPython using the assembly object
                            # the loader will have already loaded the assembly, so we can just reference it here without loading it again
                            clr.AddReference(assembly)
                            return_value.append_message("Added reference to already loaded dll: {}.".format(dll))
                        continue

                    # not loaded .. try to load
                    try:
                        clr.AddReferenceToFileAndPath(dll_path)
                        return_value.append_message("Loaded dll: {}".format(dll_path))
                        break
                    except Exception as e:
                        return_value.update_sep(
                            False, "Failed to load dll: {}. Error: {}".format(dll_path, e)
                        )
                        
            if not found_match:
                return_value.update_sep(
                    False, "DLL {} not found in any lib path.".format(dll)
                )
    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while processing attempting to load dlls: {}".format(e)
        return_value.update_sep(
            False, message
        )



    return return_value


def get_specific_path(full_path, target_folder, endswith=False):
    """
    Extract path up to and including target folder.
    
    Args:
        full_path: Full file or directory path
        target_folder: Folder name to search for (e.g., 'lib')
        endswith: If True, match folders ending with target_folder. 
                  If False (default), exact match only.
    
    Returns:
        Path ending with target_folder + '\\' or None if target_folder not found
    """

    # Normalize the path (handles different separator styles)
    normalized_path = os.path.normpath(full_path)
    
    # Split the path into parts
    parts = normalized_path.split(os.sep)
    
    # Find the index of target_folder
    try:
        if endswith:
            # Find first folder that ends with target_folder
            target_folder_index = next(
                i for i, part in enumerate(parts) 
                if part.endswith(target_folder)
            )
        else:
            # Exact match
            target_folder_index = parts.index(target_folder)
        
        # Reconstruct path up to and including target_folder
        target_folder_path = os.sep.join(parts[:target_folder_index + 1])
        # Add trailing separator
        return target_folder_path + os.sep
    
    except (ValueError, StopIteration):
        # target_folder not found in path
        return None


def get_extension_path(full_path):
    """
    Extract path up to and including 'lib' directory.
    
    Args:
        full_path: Full file or directory path
        
    Returns:
        Path ending with 'lib\' or None if 'lib' not found
    """

    return get_specific_path(full_path=full_path,  target_folder='extension', endswith=True)


def get_lib_path(full_path):
    """
    Extract path up to and including 'lib' directory.
    
    Args:
        full_path: Full file or directory path
        
    Returns:
        Path ending with 'lib\' or None if 'lib' not found
    """
    
    return  get_specific_path(full_path, 'lib')
    

def is_bin_after_extension(path):
    """
    Check if \\bin folder comes directly after a folder ending with .extension
    
    Args:
        path: Full directory path
        
    Returns:
        True if \\bin is directly after .extension folder
    """
    # Normalize and split path
    parts = os.path.normpath(path).split(os.sep)
    
    # Find index of 'bin'
    try:
        bin_index = parts.index('bin')
        # Check if the part before 'bin' ends with '.extension'
        if bin_index > 0:
            return parts[bin_index - 1].endswith('.extension')
    except ValueError:
        pass
    
    return False


def get_bin_path_from_script_path_within_extension(script_path):
    """
    Get the path to the bin directory based on the location of the script folder.
    Assumes that the bin folder is located in the root of the extension and that the script folder is located somewhere within the extension.
    
    Args:
        script_folder: Full path to the folder where the script is located
        
    Returns:
        Path to the bin directory if found, otherwise None
    """
    
    # get the folder of the script
    script_folder = os.path.normpath(script_path)

    # try to get the extension path from the script folder
    extension_path = get_extension_path(script_folder)
    
    if extension_path:
        # If we found an extension path, assume bin is in there
        bin_path = os.path.join(extension_path, 'bin')
        if os.path.exists(bin_path) and os.path.isdir(bin_path):
            return bin_path
    
   
    return None