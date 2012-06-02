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

from pyfrid.modules.system.auth.core.auth import BaseAuthModule, User

class BaseNoAuthModule(BaseAuthModule):
    """
    This is authentication module which doesn't perform any login and logout and all access validations will return True.
    Use it if you don't need any authentication control in your application.
    """
    
    def validate_user(self,login,password):
        """Returns empty user."""
        return User("","")
    
    def validate_access(self,*args, **kwargs):
        """Always returns True"""
        return True
    
    def add_user(self, login, password, groups, name, email, organization):
        """Raises NotImplementedError."""
        raise NotImplementedError("No valid authentication module in the system")
    
    def del_user(self, login):
        """Raises NotImplementedError."""
        raise NotImplementedError("No valid authentication module in the system")
    
    def user_exists(self, login):
        """Raises NotImplementedError."""
        raise NotImplementedError("No valid authentication module in the system")
    
    def status(self):
        return None
    
    @property
    def noauth(self):
        """Returns True"""
        return True