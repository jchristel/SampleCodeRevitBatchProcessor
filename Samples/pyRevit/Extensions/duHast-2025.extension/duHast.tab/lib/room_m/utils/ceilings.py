# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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

"""The ceiling facts the duHast export does not carry USABLY.

One function, and the reason it exists is worth stating carefully, because on a
quick read it looks like the thing `CLAUDE.md` forbids.

**The rule is "the extractor reads from Revit what the export does not contain,
and does not re-measure what it does".** A ceiling's height above its level IS
in the export -- duHast puts it on the level block as `offset_from_level`. It
arrives as the string `"2700"`.

That is not a number in the contract's units. It is Revit's DISPLAY value: a
millimetre figure, formatted, rounded to the document's display precision, and
typed as text. The contract declares `height_offset` as decimal feet, matching
`loops`, and the API answers 8.858267716535433 for that same ceiling. So this is
not a second implementation competing with duHast's -- there is no measurement
here to disagree about. It is reading the parameter in its own units instead of
a rendering of it.

**The spaces probe learned exactly this and paid for it.** Its v1 read compared
properties with `AsValueString`, which returned `"71 m2"` for a space duHast
exports as `71.27892877719862`, and any threshold calibrated on that would have
been calibrated on the rounding. Same shape of mistake, same fix.
"""


def ceiling_offsets(doc):
    """`{ceiling id: height above its level}` in Revit's internal feet.

    A ceiling missing the parameter is simply absent from the map, and
    `translate_ceiling` then sends `None`. Absent is a legal value on the
    contract -- it means the export could not say, not that the offset is zero,
    and zero would be a plausible-looking lie.
    """
    from Autodesk.Revit.DB import (
        BuiltInCategory,
        BuiltInParameter,
        FilteredElementCollector,
    )

    from room_m.utils.generic import element_id_str

    out = {}
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Ceilings)
        .WhereElementIsNotElementType()
    )
    for element in collector:
        try:
            parameter = element.get_Parameter(
                BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM
            )
            if parameter is None:
                continue
            out[element_id_str(element.Id)] = float(parameter.AsDouble())
        except Exception:
            # One unreadable ceiling costs its own offset and not the run's.
            continue
    return out
