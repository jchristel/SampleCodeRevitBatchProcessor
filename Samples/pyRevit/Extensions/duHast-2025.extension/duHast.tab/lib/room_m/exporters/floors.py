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

"""One model's contribution to a run's FLOORS bucket, and the push for the
whole bucket: `room_m.exporters.surfaces` bound to floors.

The seventh entity, and the second slab. Every push rule is the ceilings one
and lives in `exporters.surfaces`. What is floor-specific:

**The collector is duHast's BY CATEGORY, so it includes in-place floors and
excludes foundation slabs.** `get_all_floor_instances_in_model_by_category`
answers `OST_Floors`, which holds system floors and in-place floor families
alike; a foundation slab is class `Floor` but category
`OST_StructuralFoundation`, and is not here. The by-class collector would miss
the in-place ones, and `get_2d_points_from_solid` now measures those.

**Structural slabs and finish floors are both pushed.** They share the
category; the `Structural` instance parameter tells them apart, and it rides
the property map. Which one a question wants is the reader's call, not this
producer's.

**The offset is to the TOP of the floor** (`FLOOR_HEIGHTABOVELEVEL_PARAM`),
where a ceiling's is to its underside. An in-place floor has no such
parameter and pushes `None`.
"""

from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter

from duHast.Revit.Floors.Export.to_data_floor import get_all_floor_data
from duHast.Revit.Floors.floors import (
    get_all_floor_instances_in_model_by_category,
)
from duHast.Data.Objects.Collectors import data_floor as df

from room_m.exporters import surfaces
from room_m.post_floors import (
    post_payload_stream,
)


SPEC = surfaces.SurfaceExport(
    plural="floors",
    singular="floor",
    category=BuiltInCategory.OST_Floors,
    collect=get_all_floor_instances_in_model_by_category,
    export=get_all_floor_data,
    data_type=df.DataFloor.data_type,
    offset_parameter=BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM,
    post_stream=post_payload_stream,
)


# Nothing per model to stamp beyond the shared identity envelope, as for
# ceilings.
stamp_envelope = None


def export_model(selected_doc, phase_name, return_value):
    """See `exporters.surfaces.export_model`."""
    return surfaces.export_model(SPEC, selected_doc, phase_name, return_value)


def post_bucket(run_envelope, entries, return_value):
    """See `exporters.surfaces.post_bucket`."""
    return surfaces.post_bucket(SPEC, run_envelope, entries, return_value)
