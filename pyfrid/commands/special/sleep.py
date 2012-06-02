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
    