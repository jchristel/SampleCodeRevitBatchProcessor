'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A timer class to measure code performance.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from System.Diagnostics import Stopwatch

#: time output formatting 2 digit padding
PAD_SINGLE_DIGIT_TO_TWO = '%02d'
#: time output formatting default 3 digit padding
PAD_SINGLE_DIGIT_TO_THREE = '%03d'

class TimerError(Exception):
    '''
    A custom exception used to report errors in use of Timer class
    '''

class Timer:
    def __init__(self):
        self._stopWatch = None

    def start(self):
        '''
        Start a new timer

        :raises TimerError: When timer is running already.
        '''

        if self._stopWatch is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")

        self._stopWatch = Stopwatch()
        self._stopWatch.Start()

    def stop(self):
        '''
        Stop the timer, and report the elapsed time.

        :raises TimerError: When timer is not running yet.
        :return: The elapsed time since the timer has started.
        
        :rtype: str
        '''

        if self._stopWatch is None:
            raise TimerError("Timer is not running. Use .start() to start it")
        self._stopWatch.Stop()
        timeSpan = self._stopWatch.Elapsed
        self._stopWatch = None
        return ('Elapsed time: ' + str(PAD_SINGLE_DIGIT_TO_TWO%timeSpan.Hours) + 'h.'+ str(PAD_SINGLE_DIGIT_TO_TWO%timeSpan.Minutes) + 'm.' + str(PAD_SINGLE_DIGIT_TO_TWO%timeSpan.Seconds) + 's.' + str(PAD_SINGLE_DIGIT_TO_THREE%timeSpan.Milliseconds) + 'ms')