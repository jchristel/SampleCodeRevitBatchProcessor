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



def clean_up_family_name (fam_name):
    """
    Cleans up the family name by removing  any dashes and spaces, replacing them with underscores.

    :param fam_name: The family name to clean up.
    :type fam_name: str
    :return: The cleaned up family name.
    :rtype: str
    """
    
    if fam_name is None:
        return None
    
    # replace any "-" with "_"
    fam_name = fam_name.replace('-', '_')

    # replace any spaces with "_"
    fam_name = fam_name.replace(' ', '_')

    # remove illegal filename characters
    illegal_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_chars:
        fam_name = fam_name.replace(char, '')
    
    # remove ampersand (&) and replace it with "and"
    fam_name = fam_name.replace('&', 'And')

    return fam_name

def build_family_name_from_descriptor(description, code_to_use, output):
    """
    Builds a family name from the given description by cleaning it up.

    Description is in format

    MAJOR CATEGORY: description part, description part, description part

    :param description: The description to build the family name from.
    :type description: str
    :return: The cleaned up family name.
    :rtype: str
    """
    
    # isolate the major category and change to sentence case


    if description is None:
        return None
    
    # split the description into parts

    #output ("...Building family name from description: {}".format(description))

    parts = description[1].split(':')

    #output("...Parts after splitting by colon: {}".format(parts))

    if len(parts) < 2:
        # just a major category in the descriptor
        fam_name = ("{}_".format(description[1].title().strip().replace(' ', '')))
        return "{}{}".format(fam_name, code_to_use)
        #raise ValueError("Description must contain a major category followed by a colon. {}".format(description))
    
    # get the major category and clean it up
    major_category = parts[0].title().strip().replace(' ', '')
    description_parts = []
    try:
        
        # get the description parts and clean it up: break up in parts at each comma, Capitalize case each part, remove all spaces in each part, join parts by underscore
        for part in parts[1].split(','):
            
            # strip leading/trailing spaces from the part
            part = part.strip()

            # break up into words at each space
            words = []
            # check each word in the part
            for word in part.split(" "):
                # check if part is all upper case idf not capitalize it
                if not word.isupper():
                    #print("word '{}' is not all upper case, capitalizing it.".format(word))
                    word = word.title()  # Capitalize the first letter of each word and strip leading/trailing spaces
                else:
                    #print("Word '{}' is all upper case, keeping it as is.".format(word))
                    pass
                words.append(word)


            description_parts.append("".join(words))
    except Exception as e:
        output("...Error processing description parts: {}".format(e))
        return None
           
    # join the major category and description parts with an underscore
    family_name = major_category + '_' + '_'.join(description_parts)

    # remove any duplicate underscores
    family_name = family_name.replace('__', '_')
    # remove illegal characters from the family name
    family_name = clean_up_family_name (family_name)
   

    #output("...Family name after processing description: {}".format(family_name))
    # add the code to the family name
    # check if family end on underscore
    if family_name.endswith('_'):
        # just append the code
        family_name = "{}{}".format(family_name, code_to_use)
    else:
        # add an underscore before the code
        family_name = "{}_{}".format(family_name, code_to_use)
    
    output("...Family name after processing description and code {} added: {}".format(code_to_use, family_name))
    return family_name