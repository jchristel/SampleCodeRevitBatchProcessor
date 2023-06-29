import glob
from os import path


def get_link_path(fileName, possibleLinkLocations, fileExtension):
    """
    Gets a fully qualified file path to a file name match (revit project file extension .rvt) in given directory locations.
    Returns the first file name match it finds! If no match found returns None.
    :param fileName: Filter to identify match. Filter is string.startswith(fileName)
    :type fileName: str
    :param possibleLinkLocations: List of folders which may contain the link file.
    :type possibleLinkLocations: list str
    :param fileExtension: A file extension in format: '.xyz'. Use '.rvt' for revit project files.
    :type fileExtension: str
    :return: Fully qualified file path if match is found otherwise None.
    :rtype: str
    """

    linkPath = None
    counter = 0
    try:
        foundMatch = False
        # attempt to find filename match in given locations
        for linkLocation in possibleLinkLocations:
            fileList = glob.glob(linkLocation + "\\*" + fileExtension)
            if fileList != None:
                for file in fileList:
                    fileNameInFolder = path.basename(file)
                    if fileNameInFolder.startswith(fileName):
                        linkPath = file
                        counter = +1
                        foundMatch = True
                        break
        # return none if multiple matches where found
        if foundMatch == True and counter > 1:
            linkPath = None
    except Exception:
        linkPath = None
    return linkPath
