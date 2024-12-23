import os
import settings


from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.WPF.ViewModels.MainViewModel import MainViewModel
from duHast.UI.Objects.WPF.Stores.NavigationStore import NavigationStore
from duHast.UI.Objects.WPF.Services.NavigationService import NavigationService
from duHast.pyRevit.console_output import print_header
from duHast.Revit.Family.family_utils import load_family
from duHast.Revit.Family.family_reload_single import reload_family

from families.reload.get_families import get_families_in_model
from ViewModels.FamiliesSelectionViewModel import FamiliesSelectionViewModel
from Models.RevitFamiliesModel import RevitFamiliesModel
from Objects.MainWindow import Reloader

from Autodesk.Revit.DB import ElementId

# view model types and their XAML file path
XAML_BY_VIEW = {
    FamiliesSelectionViewModel: os.path.join(
        settings.SCRIPT_DIRECTORY, r"Views\FamiliesSelectionView.xaml"
    ),
}

# set up a navigation store
NAVIGATION_STORE = NavigationStore()

# set up the revit model container
REVIT_MODEL = RevitFamiliesModel()


def Create_Families_Selection_View_Model():

    # used to create a family selection view model
    fam_view_model = FamiliesSelectionViewModel(
        revit_model=REVIT_MODEL,
        navigation_service=NavigationService(
            navigation_store=NAVIGATION_STORE,
            create_view_model=Create_Families_Selection_View_Model,
        ),
    )

    return fam_view_model


def reload_families(doc, families, forms):

    return_value = Result()

    fam_counter = 0
    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Reloading families: {value} of {max_value}", cancellable=True
    ) as pb:
        try:
            for fam in families:
                # reload_family(doc, family, family_file_path):
                revit_family = doc.GetElement(ElementId(fam.id))
                reload_result = reload_family(
                    doc=doc, family=revit_family, family_file_path=fam.family_file_path
                )
                return_value.update(reload_result)

                # check for cancel
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    # get out of loop
                    break

                fam_counter = fam_counter + 1
                pb.update_progress(fam_counter, len(families))

        except Exception as e:
            print(e)
    return return_value


def reloaded_families_entry(doc, output, forms):
    """
    Reports on loaded families in a project file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module
    
    :return: Result class instance.
        - `result` (bool): True if warnings where reported without an exception, otherwise False.
        - `message` (str): details how many warnings where retrieved.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get alll families in file
    families = get_families_in_model(doc=doc, library_path=None)

    print_header("Starting UI...")
    print("\nFound {} families in file.".format(len(families)))

    # sort by family names
    sorted_family_list = sorted(families, key=lambda obj: obj.family_name)

    # add family to the model
    for fam in sorted_family_list:
        REVIT_MODEL.add_family(family_model=fam)

    # get the settings path from file and assign the revit model
    settings_data = settings.get_settings()
    # check if any settings where found otherwise go with default
    if settings_data:
        REVIT_MODEL.settings = settings_data
        print("found settings: {}\n{}".format(settings_data, REVIT_MODEL.settings))

    # set up UI
    # set up the initial view to be displayed
    NAVIGATION_STORE.CurrentViewModel = Create_Families_Selection_View_Model()

    # the main view model ( container for all other view models)
    main_view_model = MainViewModel(navigation_store=NAVIGATION_STORE)

    # set up a window instance
    my_window = Reloader(
        xaml_path=os.path.join(
            settings.DU_HAST_DIRECTORY, r"UI\Objects\WPF\Views\MainWindow_py.xaml"
        ),
        main_view_model=main_view_model,
        xaml_by_view_model=XAML_BY_VIEW,
        resources_xaml_path=None,
    )

    # show the window to the user
    my_window.ShowDialog()
    print("settings to save\n{}".format(REVIT_MODEL.settings.to_json()))
    # store settings
    result_settings_save = settings.write_settings(REVIT_MODEL.settings)
    if not (result_settings_save.status):
        print(result_settings_save.message)

    # reload the families
    print("Will {} reload families").format(len(REVIT_MODEL.families_to_reload))
    if len(REVIT_MODEL.families_to_reload) > 0:
        reloader_result = reload_families(
            doc=doc, families=REVIT_MODEL.families_to_reload, forms=forms
        )
        print(reloader_result.message)
    else:
        print("No families to reload selected.")
        return_value.append_message("No families to reload selected.")

    print("Finished.")
    return return_value
