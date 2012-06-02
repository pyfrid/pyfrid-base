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
    