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


from pyfrid.management.core.project.templates import DEVICETEMPLATE, DEVICECONFIGTEMPLATE
from pyfrid.management.core.project.objcmd import BaseCreateObjectCommand


class CreateDevice(BaseCreateObjectCommand):
    
    name="newdev"
    
    descr = "Creates a new device by adding configuration files and python source files to the current project"
    args = "[device_name]"
    
    subdir="devices"
    
    code_tpl= DEVICETEMPLATE
    
    config_tpl=DEVICECONFIGTEMPLATE
    
    default_base_module="pyfrid.core"
    
    default_base_class="BaseDevice"
    
    class_name_suffix="Device"
    
    config_file_name="devices.yml"
        
        