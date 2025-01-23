

import csv

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Reporting.report_fam_types_from_XML import get_family_type_data_from_library_xml
from duHast.Revit.Family.Reporting.families_report_header import LIBRARY_FAMILIES_HEADER
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Utilities.files_csv import write_report_data_as_csv


from families.util.print_table import print_result_table

# directories to process (add more directories as needed)
# these directories will be searched for xml files
PROCESS_DIRECTORIES = [
    r"\\path\location\one",
    r"\\path\location\two",
    r"\\path\location\three",
]


def report_families_in_library_entry(doc, output, forms):

    # set up a status tracker
    return_value = Result()

    try:

        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Reading: {value} of {max_value}",
            cancellable=True,
        ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            print("Reporting families in library:")
            report_result = get_family_type_data_from_library_xml( 
                process_directories=PROCESS_DIRECTORIES,
                progress_callback=progress_callback
            )

            # update return value with comparison result
            return_value.update(report_result)
       
        # print comparison result to pyRevit output
        print_result_table (
            output=output,
            data=report_result.result, 
            header=LIBRARY_FAMILIES_HEADER,
            table_title="fams"
        )

        file_path = forms.save_file(file_ext='csv', title="Save report to csv file")

        if (file_path and len(file_path) > 0):
            write_result = write_report_data_as_csv(file_name=file_path, header= LIBRARY_FAMILIES_HEADER,  data=report_result.result, quoting=csv.QUOTE_MINIMAL)
            if(write_result.status):
                return_value.append_message("Succefully wrote families report to: {} ".format(file_path))
            else:
                return_value.update_sep(False, "Failed to write families report to: {} ".format(write_result.status))
                
        else:
            return_value.append_message("No file path selected")
    
    except Exception as e:
        return_value.update_sep(
            False, "Failed to compare families with exception: {}".format(e)
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value
