#  Copyright 2012 Denis Korolkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import time
from pyfrid.core import FloatSetting
from pyfrid.core.device import BaseDevice

class BaseDummyMotorDevice(BaseDevice):
    
    lim1=FloatSetting(-100, fixed=False)
    lim2=FloatSetting( 100, fixed=False)
    precision= FloatSetting(0.0001, fixed=True)
    
    step=0.01
    time_step=0.01
    
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
             
             
             