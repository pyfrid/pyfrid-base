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

import os

import pyfrid
from pyfrid.management.core.admin import BaseAdminCommand
from pyfrid.management.core.command import CommandError

class NewProjectCommand(BaseAdminCommand):
    
    name='newproj'
    
    descr = "Creates a project directory structure for the given project name in the current directory"
    args = "project_name"
    option_list=[]
        
    def handle(self, *args, **options):
        proj_name=''
        if not args:
            try:
                while not proj_name:
                    proj_name=raw_input("Type name of the project: ")
            except EOFError, err:
                raise CommandError(str(err))
        else:
            proj_name=args[0]
        import re
        import shutil
        if not re.search(r'^[_a-zA-Z]\w*$', proj_name):
            raise CommandError("{0} is not a valid project name. Please use only numbers, letters and underscores".format(proj_name))
        directory = os.getcwd()
        top_dir = os.path.join(directory, proj_name)
        if os.path.exists(top_dir):
            raise CommandError("Directory '{0}' already exists".format(top_dir))
        template_dir = os.path.join(pyfrid.__path__[0], "management",'templates', 'project_template')
        try:
            shutil.copytree(template_dir,top_dir,ignore=shutil.ignore_patterns('*.pyc', '*.pyd'))
        except OSError,e:
            raise CommandError(e)
        return "Project '{0}' was successfully created".format(proj_name)
    
