"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A timer class to measure code performance.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

from System.Diagnostics import Stopwatch
from duHast.Utilities.Objects import base

#: time output formatting 2 digit padding
PAD_SINGLE_DIGIT_TO_TWO = "%02d"
#: time output formatting default 3 digit padding
PAD_SINGLE_DIGIT_TO_THREE = "%03d"


class TimerError(Exception):
    """
    A custom exception used to report errors in use of Timer class
    """


class Timer(base.Base):
    def __init__(self):
        self._stop_watch = None

        super(Timer, self).__init__()

    def start(self):
        """
        Start a new timer

        :raises TimerError: When timer is running already.
        """

        if self._stop_watch is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")

        self._stop_watch = Stopwatch()
        self._stop_watch.Start()

    def stop(self):
        """
        Stop the timer, and report the elapsed time.

        :raises TimerError: When timer is not running yet.
        :return: The elapsed time since the timer has started.

        :rtype: str
        """

        if self._stop_watch is None:
            raise TimerError("Timer is not running. Use .start() to start it")
        self._stop_watch.Stop()
        time_span = self._stop_watch.Elapsed
        self._stop_watch = None
        return (
            "Elapsed time: "
            + str(PAD_SINGLE_DIGIT_TO_TWO % time_span.Hours)
            + "h."
            + str(PAD_SINGLE_DIGIT_TO_TWO % time_span.Minutes)
            + "m."
            + str(PAD_SINGLE_DIGIT_TO_TWO % time_span.Seconds)
            + "s."
            + str(PAD_SINGLE_DIGIT_TO_THREE % time_span.Milliseconds)
            + "ms"
        )

    def is_running(self):
        """
        Check whether the stop watch running.
        """

        if (self._stop_watch is None):
            return False
        else:
            return True