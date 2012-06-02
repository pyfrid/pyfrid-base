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
            