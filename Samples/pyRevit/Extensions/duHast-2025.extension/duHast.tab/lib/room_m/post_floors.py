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

"""The floors push: `room_m.post_surfaces` bound to the v1 floors contract.

duHast's `to_data_floor` is `to_data_ceiling` with the category and the offset
parameter swapped, so a floor reaches the server exactly as a ceiling does --
see `post_surfaces` for every rule that implies. The one difference a reader of
the pushed data needs is on the server's side of the contract: a floor's
`height_offset` is to its TOP, where a ceiling's is to its underside.
"""

from room_m import post_surfaces

FLOORS_PUSH = post_surfaces.SurfacePush(
    entity="floors",
    list_key="floor",
    schema_version=1,
    url="http://127.0.0.1:5151/floors",
    url_stream="http://127.0.0.1:5151/floors/stream",
)


def post_payload(run_envelope, entries):
    """Buffered push of the run's floors bucket. Returns `(ok, status, text)`."""
    return post_surfaces.post_payload(FLOORS_PUSH, run_envelope, entries)


def post_payload_stream(run_envelope, entries):
    """Streamed push of the run's floors bucket. Returns `(ok, status, text)`."""
    return post_surfaces.post_payload_stream(FLOORS_PUSH, run_envelope, entries)
