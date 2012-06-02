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