#    This file is part of PyFRID.
#
#    PyFRID is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyFRID is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyFRID.  If not, see <http://www.gnu.org/licenses/>.
#

import time
from pyfrid.core.device import BaseDevice

class BaseDummyShutterDevice(BaseDevice):
    
    def __init__(self, *args, **kwargs):
        super(BaseDummyShutterDevice, self).__init__(*args, **kwargs)
        self._pos=False
        
    def position(self):
        return self._pos
    
    def status(self):
        return None 
        
    def do_switch(self, newpos):
        time.sleep(1)
        self._pos=bool(newpos)
        return self._pos