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
    
    