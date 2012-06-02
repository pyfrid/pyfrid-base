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

import hashlib
import os
from string import Template
import yaml

from pyfrid.modules.system.auth.core.auth import BaseAuthModule, User
from pyfrid.core.settings import StringSetting


USERTPL=Template(
"""
---
login:        $login
password:     $password
groups:       $groups
name:         $name
organization: $organization
email:        $email

"""
)

class BaseYamlAuthModule(BaseAuthModule):
    """
    This is a simple authentication module which uses YAML file to keep information about users and their login and passwords.
    Passwords a encoded with sha224 algorithm.
    """
    
    def __init__(self, *args, **kwargs):
        super(BaseYamlAuthModule, self).__init__(*args, **kwargs)
        assert self.dbpath!="", "database path is empty"
    
    def initialize(self):
        super(BaseYamlAuthModule, self).initialize()
        if not self.user_exists('root'):
            self.info("Root user was not found. Preparing for the first start...")
            import getpass
            login, passwd, passwd2="root", "", ""
            while True:
                while not passwd: passwd=getpass.getpass("Root password: ")
                while not passwd2: passwd2=getpass.getpass("Retype password: ")
                if passwd!=passwd2:
                    self.error("Password mismatch. try again...")
                else: break
            self.add_user(login, passwd, ['ROOT'])
    
    def set_dbpath(self, path):
        if not path:
            path=os.path.join(self.app.projpath,"users.yml")
        if not os.path.exists(path):
            head, _=os.path.split(path)
            if head and not os.path.exists(head): os.makedirs(head)
            open(path,'w').close()
        return path
    
    
    #: path to YAML file with users information 
    dbpath=StringSetting("", fixed=True, setter=set_dbpath)
    
    def validate_user(self,login,password):
        password=hashlib.sha224(password if password!=None else "").hexdigest()
        for user in yaml.load_all(file(self.dbpath)):
            try:
                login_=user.pop("login")
                password_=user.pop("password")
                if login_==login and password_==password:
                    groups=user.pop("groups",[])
                    name=user.pop("groups","")
                    email=user.pop("email","")
                    org=user.pop("organization","")
                    extra=user.copy()
                    return User(login, password, groups, name, org, email, extra)
            except KeyError, err:
                self.exception("Bad user info: {0}".format(err))
        return None
    
    def add_user(self, login, password, groups=[], name="", organization="", email="", extra={}):
        if self.user_exists(login): raise Exception("User '{0}' exists".format(login))
        password=hashlib.sha224(password if password!=None else "").hexdigest()
        info={"login":login,
              "password":password,
              "groups":groups,
              "name":name,
              "email":email,
              "organization":organization}
        info.update(extra)
        with open(self.dbpath,'a') as f:
            f.write(USERTPL.substitute(**info))
        self.info("User '{0}' was successfully created".format(login))
        
    def del_user(self, login):
        db=yaml.load(file(self.dbpath))
        open(self.dbpath, 'w').close()
        for user in db:
            if user["login"]==login: continue
            with open(self.dbpath,'a') as f:
                f.write(USERTPL.substitute(user))
        return None
    
    def user_exists(self, login):
        for user in yaml.load_all(file(self.dbpath)):
            if user["login"]==login: return True
        return False
    
    @property
    def noauth(self):
        return False