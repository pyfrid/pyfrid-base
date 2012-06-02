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


from pyfrid.management.core.project.templates import MODULETEMPLATE, MODULECONFIGTEMPLATE
from pyfrid.management.core.project.objcmd import BaseCreateObjectCommand


class CreateModule(BaseCreateObjectCommand):
    
    name="newmod"
    
    descr = "Creates a new module by adding configuration files and python source files to the current project"
    args = "[module_name]"
    
    subdir="modules"
    
    code_tpl= MODULETEMPLATE
    
    config_tpl=MODULECONFIGTEMPLATE
    
    default_base_module="pyfrid.core"
    
    default_base_class="BaseModule"
    
    class_name_suffix="Module"
    
    config_file_name="modules.yml"

