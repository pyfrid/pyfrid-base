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


from types import IntType, FloatType, BooleanType, StringType, UnicodeType, ListType, NoneType
from pyfrid.core.descriptor import BaseDescriptor

class SettingError(Exception): pass

class BaseSetting(BaseDescriptor):
    """
    Main class for all settings
    """
    setting_types=None
    typename=""
    
    def __init__(self, value, getter=None, setter=None, units="", docs="", expected=[], limits=[None, None], fixed=False, allownone=False):
        super(BaseSetting, self).__init__()
        assert self.setting_types!=None, "setting_type is None"
        assert getter==None or callable(getter), "getter must be callable or None"
        assert setter==None or callable(setter), "setter must be callable or None"
        assert type(expected)==ListType, "Expected values list can have only a list type"
        assert type(limits)==ListType, "limits can have only a list type"
        assert len(limits)==2, "limits must be array with two value"
        
        self._limits=limits
        
        if type(self.setting_types)!=ListType:
            self.setting_types=[self.setting_types]
        
        if allownone and NoneType not in self.setting_types:
            self.setting_types.append(NoneType)
        
        self.validate_limits(limits)
        self.validate_expected(expected)
               
        self._initmode=False
        self._getter=getter
        self._setter=setter
        self._units=str(units)
        self._docs=str(docs)
        self._defvalue=value
        self._fixed=bool(fixed) 
        self._expected=expected
        self._registry=dict()
        
    def validate_expected(self, expected):
        for item in expected:
            if type(item)not in self.setting_types:
                raise SettingError("expected list type mismatch for value '{0}'".format(item)) 
            if self._limits[0]!=None and item<self._limits[0]:
                raise SettingError("value '{0}' is out of limits [{1}, {2}]".format(item, *self._limits))
            if self._limits[1]!=None and item>self._limits[1]:
                raise SettingError("value '{0}' is out of limits [{1}, {2}]".format(item, *self._limits))  
                 
    def validate_limits(self, limits):
        if type(limits[0])!=NoneType and type(limits[0]) not in self.setting_types:
            raise SettingError("lower limit type mismatch for value '{0}'".format(limits[0]))
        if type(limits[1])!=NoneType and type(limits[1]) not in self.setting_types:
            raise SettingError("upper limit type mismatch for value '{0}'".format(limits[1]))
        if limits[0]!=None and limits[1]!=None and limits[0]>limits[1]:
            raise SettingError("lower limit is larger then upper limit")
                          
    @property
    def units(self):
        return self._units
    
    @property
    def docs(self):
        return self._docs
    
    @property
    def fixed(self):
        return self._fixed
    
    @property
    def expected(self):
        return self._expected[:]
    
    def configure(self, instance, default_value=None, permissions=None):
        if not instance.alias: 
            raise SettingError("Instance with empty alias")
        if permissions   ==None: permissions={}
        if default_value ==None:
            if callable(self._defvalue):
                default_value=self._defvalue(instance)
            else:
                default_value=self._defvalue
        self.validate(default_value)    
        self._registry[instance.alias]={
                                        "default_value":default_value,
                                        "permissions":permissions,
                                        "value":None
                                        }
        
    def initialize(self, instance):
        self._initmode=True
        try:
            if not instance.alias: 
                raise SettingError("Instance with empty alias")
            if instance.alias not in self._registry:
                raise SettingError("The setting has not been configured yet")
            self.__set__(instance, self._registry[instance.alias]["default_value"])
        finally:
            self._initmode=False
                
    def get_permission_groups(self,instance,perm):
        if not instance.alias: 
            raise SettingError("Instance with empty alias")
        return self._registry[instance.alias]["permissions"].get(perm,[])
        
    def __get__(self, instance, owner):
        if instance==None: return self
        assert instance.alias, "Instance with empty alias"
        if self._getter!=None:
            value=self._getter(instance)
            self.validate(value)
            return value
        return self._registry[instance.alias]["value"]
    
    def __set__(self, instance, value):
        if instance==None:
            raise AttributeError("can not set setting value without instance")
        if not instance.alias: 
            raise SettingError("Instance with empty alias")
        self.validate(value)
        if self._setter!=None and self._getter!=None:
            self._setter(instance, value)
            self._registry[instance.alias]["value"]=self.__get__(instance)
        elif self._setter!=None and self._getter==None:
            value=self._setter(instance, value)
            self.validate(value)
            self._registry[instance.alias]["value"]=value
        else:
            self._registry[instance.alias]["value"]=value
                                                    
    def validate_value(self,value):
        if self._limits[0]!=None and value<self._limits[0]:
            raise SettingError("value '{0}' is out of limits [{1}, {2}]".format(value, *self._limits))
        if self._limits[1]!=None and value>self._limits[1]:
            raise SettingError("value '{0}' is out of limits [{1}, {2}]".format(value, *self._limits))    
        if self._expected and value not in self._expected:
            raise SettingError("value '{0}' is  not in expected values".format(value))
        
    def validate_type(self, value):
        if type(value) not in self.setting_types:
            raise SettingError("type mismatch for value '{0}'".format(value))
        
    def validate(self, value):
        self.validate_type(value)
        self.validate_value(value)  
                      
class IntSetting(BaseSetting):       
    setting_types=IntType
    typename="int"
            
class FloatSetting(BaseSetting):        
    setting_types=[FloatType, IntType]
    typename="float"

class StringSetting(BaseSetting):        
    setting_types=[StringType, UnicodeType]
    typename="string"

class BoolSetting(BaseSetting):        
    setting_types=[BooleanType, IntType]
    typename="boolean"
    
class BaseListSetting(BaseSetting):
    setting_types=ListType
    item_types=None
    
    def __init__(self, value, getter=None, setter=None, units="", docs="", expected=[], limits=[None, None], fixed=False, allownone=False, maxitems=None):
        super(BaseListSetting, self).__init__(value, getter, setter, units, docs, expected, limits, fixed, allownone)
        assert self.item_types!=None, "item type is None"
        assert maxitems==None or maxitems!=0 and maxitems>0, "maxitems <= zero"
        if type(self.item_types)!=ListType:
            self.item_types=[self.item_types]
        if allownone and NoneType not in self.item_types:
            self.item_types.append(NoneType)
        self._maxitems=maxitems
    
    def validate_type(self, value):
        super(BaseListSetting, self).validate_type(value)
        for item in value:
            if type(item) not in self.item_types:
                raise SettingError("type mismatch for value '{0}'".format(item))
            
    def validate_value(self,value):
        if self._maxitems!=None and len(value) > self._maxitems:
            raise SettingError("length of the value is larger them maxitems")
        for item in value:
            super(BaseListSetting, self).validate_value(item)
    
    def validate_expected(self, expected):
        for item in expected:
            if type(item) not in self.item_types:
                raise SettingError("expected list type mismatch for value '{0}'".format(item)) 
            if self._limits[0]!=None and item<self._limits[0]:
                raise SettingError("value '{0}' is out of limits [{1}, {2}]".format(item, *self._limits))
            if self._limits[1]!=None and item>self._limits[1]:
                raise SettingError("value '{0}' is out of limits [{1}, {2}]".format(item, *self._limits))  
                 
    def validate_limits(self, limits):
        if type(limits[0])!=NoneType and type(limits[0]) not in self.item_types:
            raise SettingError("lower limit type mismatch for value '{0}'".format(limits[0]))
        if type(limits[1])!=NoneType and type(limits[1]) not in self.item_types:
            raise SettingError("upper limit type mismatch for value '{0}'".format(limits[1]))
        if limits[0]!=None and limits[1]!=None and limits[0]>limits[1]:
            raise SettingError("lower limit is larger then upper limit")

class BoolListSetting(BaseListSetting):        
    item_types=BooleanType
   
class IntListSetting(BaseListSetting):        
    item_types=IntType
         
class FloatListSetting(BaseListSetting):        
    item_types=[FloatType, IntType]

class StringListSetting(BaseListSetting):        
    item_types=StringType
            