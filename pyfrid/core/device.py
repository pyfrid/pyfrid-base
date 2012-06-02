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
import abc
import copy
from threading import Thread

from pyfrid.core.descriptor import UsedDeviceDescriptor
from pyfrid.core.object import BaseProjectObject, ObjectMetaClass, set_descriptors
from pyfrid.core.registry import ObjectRegistry, RegistryError
from pyfrid.core.settings import FloatSetting, StringSetting
from pyfrid.core.signal import Signal

device_registry=ObjectRegistry()

class DeviceMetaClass(ObjectMetaClass):
    
    def __new__(meta, name, bases, d):
        d["used_devices"]=set_descriptors("used_devices", UsedDeviceDescriptor, bases, d)
        return ObjectMetaClass.__new__(meta, name, bases, d)
    
    def __init__(cls, name, bases, d):
        ObjectMetaClass.__init__(cls, name, bases, d)
        try: device_registry.register(cls)
        except RegistryError, err:
            raise RegistryError("Exception while registering class '{0}': {1}".format(cls.__class__.__name__,err))

class BaseDevice(BaseProjectObject):

    __metaclass__=DeviceMetaClass
    
    used_devices={}
    
    units=StringSetting("",fixed=True)
    
    def __init__(self, app, *args, **kwargs):
        for _, descr in self.used_devices.iteritems():
            dev=app.get_device(descr.alias,exc=True)
            descr.object=dev
        super(BaseDevice,self).__init__(app, *args,**kwargs)
        
        self.before_position_signal=Signal(self)
        self.after_position_signal=Signal(self)
        
    @abc.abstractmethod   
    def position(self):
        return None
    
    def call_position(self):
        return self.position()
    
    def do_position(self):
        return self.position()
                                                              
class BaseCachedDevice(BaseDevice):
    
    poll_pause=FloatSetting(2.0)
    
    def __init__(self,*args,**kwargs):
        super(BaseCachedDevice,self).__init__(*args,**kwargs)
        self._poller=Thread(target=self._poll)
        self._poller.setDaemon(True)
        self._stop_poll=False
        self._cachedpos=None
        self._cachedstat=None
                
    def call_position(self):
        return copy.deepcopy(self._cachedpos)
    
    def call_status(self):
        return copy.deepcopy(self._cachedstat)
    
    def _poll(self):
        while not self._stop_poll:
            if not self.has_exception:
                self.force_update()
            time.sleep(self.poll_pause)    
            
    def call_shutdown(self):
        self._stop_poll=True
        self._poller.join()
        super(BaseDevice,self).call_shutdown()
       
    def call_initialize(self):
        super(BaseDevice,self).call_initialize()
        if not self._poller.is_alive():
            self._poller.start()
            
    def force_update(self):
        self._cachedpos=super(BaseCachedDevice,self).call_position()
        self._cachedstat=super(BaseCachedDevice,self).call_status()
    