
import System
from System.IO import File
from System.IO import MemoryStream
from System.Reflection import Assembly
import traceback


# do not load these, since they are the external command and dont need to be laoded
ignore_dlls = [
    "PushIt.dll",
]

# Load the DLLs required for the extension
# build the bin path
bin_directory_within_extension=r"Albury.tab\PushIt.panel\bin"
# file path of this file
startup_file_path = __file__
# get the directory of the startup file
startup_directory = System.IO.Path.GetDirectoryName(startup_file_path)

# build the full path to the bin directory\
bin_directory = System.IO.Path.Combine(startup_directory, bin_directory_within_extension)

# get all dlls in the bin directory
dlls_to_load  = System.IO.Directory.GetFiles(bin_directory, "*.dll")


for dll in dlls_to_load:

    try:
        #full_path = System.IO.Path.Combine(bin_directory, dll)
        # get the file name from the path
        dll_name_only = System.IO.Path.GetFileName(dll)
        
        # check if the dll should be ignored
        if dll_name_only in ignore_dlls:
            print("Ignoring: {dll}".format(dll=dll_name_only))
            continue

        print("Attempting to load: {dll}".format(dll=dll_name_only))
        
        # Check if the file exists
        if not File.Exists(dll):
            print("File not found: {dll}".format(dll=dll))
            continue

        dll_bytes = File.ReadAllBytes(dll)
        # Should print <class 'bytes'>
        #print("bytes array is of type: {}".format(type(dll_bytes)))
    
        # Load assembly into the default AppDomain
        stream = MemoryStream(dll_bytes)
        assembly = Assembly.Load(stream.ToArray())

        # Ensure it's registered for other add-ins
        System.AppDomain.CurrentDomain.Load(assembly.GetName())
        print("loaded successfully: {dll}".format(dll=dll_name_only))
    except Exception as e:
        print("Failed to load {dll} with exception: {e}".format(dll=dll, e=e))
        print(traceback.format_exc())
        continue

