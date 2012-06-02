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


import os
import re

from optparse import make_option
from pyfrid.management.core.command import CommandError
from pyfrid.management.core.project import BaseProjectCommand

class BaseCreateObjectCommand(BaseProjectCommand):
    
    subdir=""
    
    code_tpl=None
    
    config_tpl=None
    
    default_base_module="pyfrid"
    
    default_base_class="BaseObject"
    
    class_name_suffix="Object"
    
    config_file_name=""
    
    option_list=[
        make_option("-a", "--alias", dest="alias", type="string", default="", help="Alias of the object"),
        make_option("-b", "--base-class", dest="base_class", type="string", default="", help="Base class path, like pyfrid.devices.MyBaseClass"),
    ]    
            
    def import_object(self,path):
        _path=path.split(".")
        if len(_path)<=1:
            raise CommandError("Full base class path required")
        module_name,class_name=".".join(_path[:-1]),_path[-1]
        try:
            module=__import__(module_name,globals(), locals(), [class_name], -1)
            if not hasattr(module,class_name):
                raise CommandError("Can not find class '{0}' in module {1}".format(class_name,module_name)) 
        except ImportError,err:
            raise CommandError(err)
        return module_name, class_name
                
    def handle(self, name, **options):
        #creating sources
        if not re.match(r"[A-Za-z_]+[0-9]*",name):
            raise CommandError("Object name is not regular. It can contain only letters, numbers and '_'")
        bcopt=options.get("base_class",'')
        alias=options.get("alias",'')
        basemodule, baseclass=self.default_base_module, self.default_base_class
        if bcopt:
            basemodule, baseclass=self.import_object(bcopt)
        codepath=os.path.join(self.projpath, self.subdir,"{0}.py".format(name))
        if os.path.exists(codepath):
            raise CommandError("Source file '{0}.py' already exists".format(name))
        objclass="{0}{1}".format(name.capitalize(),self.class_name_suffix)
        try:
            with open(codepath,'w') as fp:
                fp.write(self.code_tpl.substitute(name=name,
                                       alias=alias if alias else name,
                                       objclass=objclass,
                                       baseclass=baseclass,
                                       basemodule=basemodule)
                         )
        except IOError, e:
            raise CommandError(str(e))
        #creating config file
        cfgpath=os.path.join( self.projpath, "config", self.config_file_name )
        try:
            with open(cfgpath,'a') as fp:
                fp.write(self.config_tpl.substitute(alias=alias if alias else name, name=name))
        except IOError, err:
            raise CommandError(str(err))
