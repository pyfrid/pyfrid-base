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
from pyfrid.core import BaseCommand
from pyfrid.core import FloatSetting

class BaseSleepCommand(BaseCommand):
    
    limit_min=FloatSetting(0.0,fixed=False)
    limit_max=FloatSetting(7200.0,fixed=False)
    
    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import FLOATCONST
        return (FLOATCONST, 1, 1)
        
    def validate(self,val):
        if val>=self.limit_min and val<=self.limit_max:
            return True
        self.error("Time exceeds limits [{0},{1}] sec".format(self.limit_min, self.limit_max))
        return False
                
    def execute(self,val):
        self.info("Going to sleep for {0} sec...".format(val))
        start=time.time()
        while time.time()-start<val and not self.stopped: time.sleep(0.02)
        self.info("Waking up...")
        
    def runtime(self, tm, **kwargs):
        return tm
    