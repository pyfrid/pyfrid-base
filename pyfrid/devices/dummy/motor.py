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
from pyfrid.core import FloatSetting
from pyfrid.core.device import BaseDevice

class BaseDummyMotorDevice(BaseDevice):
    
    lim1=FloatSetting(-100, fixed=False)
    lim2=FloatSetting( 100, fixed=False)
    precision= FloatSetting(0.0001, fixed=True)
    
    step=0.0001
    time_step=0.0001
    
    def __init__(self, *args, **kwargs):
        super(BaseDummyMotorDevice, self).__init__(*args, **kwargs)
        self._pos=0.0
        self._mov=False
        
    def position(self):
        return self._pos
    
    def status(self):
        return (
                ("Moving", self._mov, ""),
               ) 
        
    def do_move(self, newpos):
        self._mov=True
        while abs(self._pos-newpos)>self.precision and not self.stopped:
            time.sleep(self.time_step)
            self._pos+=self.step
        self._mov=False
        return self._pos
    
    def validate_move(self, pos):
        if pos>max(self.lim1, self.lim2) or pos<min(self.lim1, self.lim2):
            self.error("Position {0:4f} is out of limits".format(pos))
            return False
        return True
    
    def runtime_move(self, newpos):
        delta=abs(self._pos-newpos)
        return delta/self.step*self.time_step
        
    def do_reference(self, newpos):
        self.do_move(0.0)
             
             
             