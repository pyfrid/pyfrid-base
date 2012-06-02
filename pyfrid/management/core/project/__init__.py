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
from pyfrid.management.core.registry import CommandRegistry, RegistryError
from pyfrid.management.core.command import BaseCommand

project_registry=CommandRegistry()

class ProjectCommandMeta(type):
    
    def __init__(cls, name, bases, d):
        try:
            project_registry.register(cls)
        except RegistryError, err:
            raise RegistryError("Exception while registering class '{0}': {1}".format(cls.__class__.__name__,err))
        return type.__init__(cls, name, bases, d)
    
class BaseProjectCommand(BaseCommand):
    __metaclass__=ProjectCommandMeta