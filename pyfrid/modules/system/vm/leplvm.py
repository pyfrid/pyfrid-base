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

from types import ListType
from lepl import List, Token, Or, Real, Integer, Line, Repeat, And, Empty, Eos, to_right, s_delta

from pyfrid.modules.system.vm.core.vm import BaseVMModule, ParseError, ValidateError, ExecuteError
from pyfrid.core.object import BaseObject

BOOLEANS=['0','1','off','on','false','true','False','True']

class BaseNode(List):
    """Base Node class for all nodes.
    """
    stop_flag=False #used to stop execution
    parser=None
    
    def process(self):
        """Analyzes the parameters and returns the value
        """
        return self

class ValueNode(BaseNode):
    """Base node for the constants
       While processing returns the value transformed to the given type.
       Type can be any function of the form::
       def type_(string):
           #do_something
           return converted_value
    """
    
    type_=str
    
    def process(self):
        return self.type_(self[0])

    def __str__(self):
        return str(self[0])

class ListNode(BaseNode):
    
    def process(self):
        return [item.process() for item in self]

    def __str__(self):
        return (", ".join(str(item) for item in self))

class DictNode(BaseNode):
    
    def process(self):
        return tuple([(self[i],self[i+1].process()) for i in range(0, len(self), 2)])

    def __str__(self):
        return ", ".join(["{0}={1}".format(self[i],self[i+1].process()) for i in range(0, len(self), 2)])

class IntConstNode(ValueNode):type_=int

class FloatConstNode(ValueNode):
    type_=float
     
    def __str__(self):
        return str("{0:.4f}".format(self.type_(self[0])))

class BoolConstNode(ValueNode):
    
    def process(self):
        i=BOOLEANS.index(self[0].lower())
        self.val=bool(i%2)
        return self.val
    
    def __str__(self):
        return str(self.val)
    
class StrConstNode(ValueNode): 
    
    def process(self):
        return str(self[0][1:len(self[0])-1])
    
    def __str__(self):
        return str(self[0])

class CommandNode(BaseNode):

    def process(self):
        obj=self.parser.get_command(self[0])
        return obj
    
    def __str__(self):
        return self[0]

class DeviceNode(BaseNode):

    def process(self):
        obj=self.parser.get_device(self[0])
        return obj
    
    def __str__(self):
        return self[0]

class ModuleNode(BaseNode):

    def process(self):
        obj=self.parser.get_module(self[0])
        return obj
    
    def __str__(self):
        return self[0]
    
class SysModNode(BaseNode):

    def process(self):
        obj=self.parser.get_sysmod(self[0])
        return obj
    
    def __str__(self):
        return self[0]

class StmtNode(BaseNode):
    
    def validate(self):
        return True
    
    def execute(self):
        pass
    
    def runtime(self):
        return 0
    
    def stop(self):
        pass
        
class CommentNode(StmtNode):

    def execute(self):
        self.parser.info("Comment: {0}".format(self[0]))
        
class CmdStmtNode(StmtNode):
    """Class of macro command node"""
         
    def process(self):
        #creating argument list
        self[0]=self.parser.get_command(self[0], permission="execute")
        if len(self)>1:
            for i in range(1,len(self)):
                if isinstance(self[i],BaseNode):
                    self[i]=self[i].process()
            for obj in self[1:]:
                if isinstance(obj,BaseObject):
                    if not self.parser.auth_module.validate_access(obj,self[0].alias):
                        raise ParseError("Access denied. No permission to perform '{0}' on the object '{1}'".format(self[0].alias,obj.name))
        return self
    
    def validate(self):
        args=[] if len(self)==1 else self[1:]
        return self[0].call_validate(*args)
    
    def runtime(self):
        args=[] if len(self)==1 else self[1:]
        return self[0].call_runtime(*args)
        
    def execute(self):
        if not self.stop_flag:
            args=[] if len(self)==1 else self[1:]
            self[0].call_execute(*args)
    
    def stop(self):
        if self[0]!=None: self[0].call_stop()
                   
    def __str__(self):
        return " ".join([str(item) for item in self])

class BlankNode(StmtNode): pass

class LineNode(StmtNode):

    def __init__(self, result, **kwargs):
        super(LineNode,self).__init__(result[0], **kwargs)
        self.line_number=result[1]
        
    def process(self):
        for i in range(0,len(self)):
            self[i]=self[i].process()
        return self
    
    def validate(self):
        self.parser._current_line=self.line_number
        for item in self:
            if self.stop_flag: break
            if not item.validate(): return False
        return True
    
    def runtime(self):
        return sum([item.runtime() for item in self])
            
    def execute(self):
        self.parser._current_line=self.line_number
        for item in self:
            if self.stop_flag: break
            item.execute()
    
    def stop(self):
        return [item.stop() for item in self]
    
    def __str__(self):
        return ";".join([str(item) for item in self])


###########################################################################parser##################################################################################
ARGSEPARATOR   = None
SPLITTER       = ~Token(';')
COMMA          = ~Token(',')
COMMENT        = Token('#.*')

LSBR           = ~Token("\[")
RSBR           = ~Token("\]")
LBR            = ~Token("\(")
RBR            = ~Token("\)")
EQOP           = ~Token("=")
IDENT          =  Token("[A-Za-z]+[A-za-z0-9_]*")

FLOATCONST     = Token(Real())                                                        >FloatConstNode   
INTCONST       = Token(Integer())                                                     >IntConstNode
BOOLCONST      = Or(*[Token(item) for item in BOOLEANS])                              >BoolConstNode
STRCONST       = Or(Token('"[^"]*"'),Token("'[^']*'"))                                >StrConstNode
BOOLCONSTLIST  = LSBR & BOOLCONST[1:, COMMA]  & RSBR                                  >ListNode
STRCONSTLIST   = LSBR & STRCONST[1:, COMMA]   & RSBR                                  >ListNode
INTCONSTLIST   = LSBR & INTCONST[1:, COMMA]   & RSBR                                  >ListNode
FLOATCONSTLIST = LSBR & FLOATCONST[1:, COMMA] & RSBR                                  >ListNode

CONSTVALUE     = Or(INTCONST,FLOATCONST,BOOLCONST, STRCONST)
CONSTVALUELIST = LSBR & CONSTVALUE[1:, COMMA] & RSBR                                  >ListNode
CONSTVALUEDICT = LSBR & (IDENT & EQOP & CONSTVALUE)[1:, COMMA] & RSBR                 >DictNode

#VALUE=Or(CONSTVALUE,CONSTVALUELIST,CONSTVALUEDICT)

OBJECT=None
COMMAND=None
DEVICE=None
MODULE=None
SYSMOD=None

def with_line(node):
    def wrapper(results, stream_in, **kargs):
        try: 
            ln = s_delta(stream_in)[1] 
        except StopIteration: 
            ln = 'eof' 
        return node([results, ln])
    return wrapper


class BaseLeplVMModule(BaseVMModule):
    """This is virtual machine system module, based on LEPL parser."""
    
    def __init__(self,*args, **kwargs):
        super(BaseLeplVMModule,self).__init__(*args, **kwargs)
        self._parser=None

    def initialize(self):
        super(BaseLeplVMModule,self).initialize()
        
        global OBJECT, DEVICE, COMMAND, MODULE, SYSMOD
        
        BaseNode.parser=self
        
        dev_tokens=[Token(obj.name) for _, obj in self.app.device_manager.iterate_objects()]
        cmd_tokens=[Token(obj.name) for _, obj in self.app.command_manager.iterate_objects()]
        mod_tokens=[Token(obj.name) for _, obj in self.app.module_manager.iterate_objects()]
        sys_tokens=[Token(obj.name) for _, obj in self.app.system_manager.iterate_objects()]
        

        DEVICE  = Or(*(dev_tokens))                       >DeviceNode
        COMMAND = Or(*(cmd_tokens))                       >CommandNode
        MODULE  = Or(*(mod_tokens))                       >ModuleNode
        SYSMOD  = Or(*(sys_tokens))                       >SysModNode
        OBJECT  = Or(DEVICE, COMMAND, MODULE)
        
        grammar=[]
                
        for _,obj in self.app.command_manager.iterate_objects():
            (args, start, stop)=obj.call_grammar()
            if start==None: start=0
            args_rule=None
            if args==None:
                args_rule=None
            elif type(args)!=ListType:
                args_rule=Repeat(args,start=start, stop=stop, separator=ARGSEPARATOR)
            else:
                args_rule=Repeat(And(*args),start=start, stop=stop, separator=ARGSEPARATOR)
            node_type=getattr(obj,"node_type",CmdStmtNode)
            if args_rule!=None:
                rule=And(Token(obj.name),args_rule)         > node_type
            else:
                rule=Token(obj.name)                        > node_type
            grammar.append(rule)
            
        cmd_stmt= Or(*grammar)                                 
        blank     = Line(Empty(),indent=False)                  >BlankNode
        comment   = Line(COMMENT,   indent=False)               >CommentNode
        statement = Line(cmd_stmt[1:, SPLITTER],indent=False)   
        line = Or(statement,blank,comment)                      **with_line(LineNode)
        program = line[:]
        program.config.no_memoize().lines(block_policy=to_right)
        self._parser=program.get_parse()

    def parse_code(self,code):
        assert self._parser!=None, "parser is None"
        if not code or self.stopped: return None
        try: 
            ast=self._parser(code)
        except Exception, err:
            raise ParseError(err)
        else:
            if ast==None:
                raise ParseError("None syntax tree")
            for item in ast:
                if self.stopped: break
                item.process()
            return ast
        return None

    def validate_ast(self, ast):
        time_=0
        if ast==None or self.stopped: return False
        try:
            for item in ast:
                if self.stopped: break
                if not item.validate(): 
                    raise ValidateError("Validation failed...")
                time_+=float(item.runtime())
        except Exception, err:
            raise ValidateError(err)
        return time_
    
    def execute_ast(self, ast):
        if ast==None or self.stopped: return
        try:
            for _, item in enumerate(ast):
                if self.stopped: break
                self._current_node=item
                item.execute()
        except Exception, err:
            raise ExecuteError(err)
    
    def stop(self):
        BaseNode.stop_flag=True
        
    def release(self):
        BaseNode.stop_flag=False
        