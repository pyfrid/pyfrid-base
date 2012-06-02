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


from lepl import And, Or
from pyfrid.utils import format_settings, format_value
from pyfrid.core import BaseCommand, get_completions

class BaseSetCommand(BaseCommand):
    
    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import OBJECT, IDENT, CONSTVALUE, CONSTVALUELIST
        return ([OBJECT, IDENT, Or(CONSTVALUE,CONSTVALUELIST)],1,1)
            
    def complete(self, text, line):
        objlist=self.app.objects_names()
        attr=line.split()
        l=len(attr)
        try:
            if not text:
                l=l+1
            if l==2:
                return get_completions(text,objlist)
            elif l==3:
                obj=self.app.get_object(attr[1],byname=True)
                sl=[name for name,_ in obj.iterate_settings(permission=["set","get"], fixed=False)]
                return get_completions(text,sl)
            else:
                return []
        except:
                return []

    def validate(self,obj,setting, value, *args, **kwargs):
        if not setting: return True
        return obj.validate_setting(setting, permission="set", value=value, check_value=True)

    def execute(self, obj, setting, value, *args, **kwargs):
        try:
            setattr(obj,setting,value)
        finally:
            self.info("Setting {0}.{1}: {2}".format(obj.name,setting,format_value(getattr(obj, setting))))
    
    def runtime(self,*args, **kwargs):
        return 0.0
            