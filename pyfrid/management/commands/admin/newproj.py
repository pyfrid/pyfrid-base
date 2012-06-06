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


import os
import shutil

import pyfrid
from pyfrid.management.core.admin import BaseAdminCommand
from pyfrid.management.core.command import CommandError
from pyfrid.utils import copytree


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
        dst_dir = os.path.join(directory, proj_name)
        if os.path.exists(dst_dir):
            raise CommandError("Directory '{0}' already exists".format(dst_dir))
        for pyfrid_path in pyfrid.__path__:
            src_dir = os.path.join(pyfrid_path, "management",'templates', 'project_template')
            if os.path.exists(src_dir):
                copytree(src_dir,dst_dir)
        return "Project '{0}' was successfully created".format(proj_name)
    
