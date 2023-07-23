def get_revit_version_number(doc):
    """
    Returns the revit version as an integer.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Revit version
    :rtype: int
    """

    app = doc.Application
    return int(app.VersionNumber)
