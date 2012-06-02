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


import traceback
from types import FunctionType 
from weakref import WeakValueDictionary
import threading
import inspect

class SignalError(Exception): pass

class Signal(object):
    
    def __init__(self,sender,max_connections=0, exc_catch=True):
        self._maxconn=max_connections
        self._sender=sender
        self._exc_catch=exc_catch
        self._slots = WeakValueDictionary()
        self._lock = threading.Lock()

    @property
    def connected(self):
        return len(self._slots)

    def connect(self, slot):
        if self._maxconn>0 and len(self._slots)>=self._maxconn:
            raise SignalError("Maximum number of connections was exceeded")
        assert callable(slot), "Signal slots must be callable."
        # Check for **kwargs
        try:
            argspec = inspect.getargspec(slot)
        except TypeError:
            try:
                argspec = inspect.getargspec(slot.__call__)
            except (TypeError, AttributeError):
                argspec = None
        if argspec:
            assert argspec[2] is not None,  \
                "Signal receivers must accept keyword arguments (**kwargs)."
        self._lock.acquire()
        try:
            key = (slot.im_func, id(slot.im_self))
            self._slots[key] = slot.im_self
        finally:
            self._lock.release()

    def disconnect(self, slot):
        self._lock.acquire()
        try:
            key = (slot.im_func, id(slot.im_self))
            if key in self._slots: self._slots.pop(key)
        finally:
            self._lock.release()

    def __call__(self,*args,**kwargs):
        assert not kwargs.has_key("sender"),  \
                "'sender' keyword argument is occupied"
        responses = []
        kwargs["sender"]=self._sender
        for key in self._slots:
            func, _ = key
            try:
                response=func(self._slots[key], *args, **kwargs)
                responses.append((func,response))
            except Exception, err:
                if self._exc_catch: self.exception("Slot {0} exception: {1}".format(str(func), err))
                else: raise Exception(traceback.format_exc())
        return responses    
    
    def exception(self, msg):
        func=getattr(self._sender, "exception", None)
        if func==None or type(func)!=FunctionType:
            traceback.print_exc()
        else:
            func(msg)

