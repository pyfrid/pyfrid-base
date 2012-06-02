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
        
        