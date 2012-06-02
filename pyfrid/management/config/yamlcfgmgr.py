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


import yaml
from pyfrid.management.core.config import BaseConfigManager, ConfigError

class YamlConfigManager(BaseConfigManager):
    
    name="yaml"
    
    extension="yml"
    
    def _load_cfg(self,path, holder):
        for item in yaml.safe_load_all(file(path,  'r')):
            alias =item.pop("alias")
            active=item.pop("active",True)
            perm_ =item.pop("permissions",{})
            set_  =item.copy()
            if active:
                holder[alias]={
                                        "permissions":perm_,
                                        "settings":set_
                }
        
    def load_devices_config  (self, path, holder):
        self._load_cfg(path, holder)
    
    def load_commands_config (self, path, holder):
        self._load_cfg(path, holder)
    
    def load_modules_config  (self, path, holder):
        self._load_cfg(path, holder)
    
    def load_system_config   (self, path, holder):
        self._load_cfg(path, holder)
    
    def create_device_config(self, alias, name, active=True, settings={}, permissions={}):
        pass
    
    def create_command_config(self, alias, name, active=True, settings={}, permissions={}):
        pass
    
    def create_module_config(self, alias, name, active=True, settings={}, permissions={}):
        pass    
    