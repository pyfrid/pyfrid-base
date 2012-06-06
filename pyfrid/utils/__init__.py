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


import shutil
import os
from types import ListType,DictType,TupleType,IntType,BooleanType,FloatType, StringType

def splitall(path, prev=[]):
    """
    """
    part1, part2 = os.path.split(path)
    if part1 == '':
        return [part2] + prev
    if part1 == path:
        return prev
    return splitall(part1, [part2] + prev)

def copytree(src, dst):
    root_src_dir = os.path.abspath(src)
    root_dst_dir = os.path.abspath(dst)
    
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        for file_ in files:
            if not file_.endswith(".pyc") or file_.endswith(".pyd"):
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)

def format_value(value, string_qoutes=True):
    _type=type(value)
    if _type==IntType:
        return ("{0:d}".format(value))
    elif _type==BooleanType:
        return ("{0}".format(value))
    elif _type==StringType:
        if string_qoutes: return ("\"{0}\"".format(value))
        else: return ("{0}".format(value))
    elif _type==FloatType:
        return ("{0:.4f}".format(value))
    elif _type==ListType:
        return "[ {0} ]".format(", ".join([format_value(item) for item in value]))
    elif _type==DictType:
        return "[ {0} ]".format(", ".join(["{0}={1}".format(key,format_value(val)) for key,val in value.iteritems()]))
    else:
        return str(value)  

def format_status(value,format_spec=(0,0,0)):
    if not format_spec:
        format_spec=(0,0,0)
    _type=type(value) 
    (nw,vw,uw)=format_spec
    res=["{0:>{1}}: {2:<{3}} {4:<{5}}".format(item[0],nw,format_value(item[1], string_qoutes=False),vw,item[2],uw) for item in value]
    return "\n{0}".format("\n".join(res))

format_settings=format_status