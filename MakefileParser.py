'''Makefile paerser
TODO:
    - Add support for multiple line commands
    - Add support for pseudo-targets ok
    - Add support for comments ok
    - Add support for special blocks
    - Add support for abitrary sequence of variables
'''

import os
import re
from CmdReplacer import *
from typing import Pattern

class Variable:
    REG_PATTERN = re.compile(r'\$[\({](\s*\w+\s*)[\)}]')
    
    @staticmethod
    def varRegPattern(var):
        return re.compile(r'\$[\({](\s*' + var + r'\s*)[\)}]')
    def __init__(self,name,value):
        self.name = name
        self.value = value
    def getFullString(self):
        return self.name + ' = ' + self.value + "\n"

class Target:
    def __init__(self,name,prerequisites,cmd_strs,gl_vars):
        self.name = GrammerBlock(name,gl_vars)
        self.prerequisites = GrammerBlock(prerequisites,gl_vars)
        self.cmd_strs = cmd_strs
        self.cmds = []
        for cmd_str in cmd_strs:
            self.cmds.append(GrammerBlock(cmd_str,gl_vars))
    def getFullString(self):
        cmd_full_strs = ""
        for cmd in self.cmds:
            cmd_full_strs += cmd.getFullString()
        return self.name.getFullString() + ':' + self.prerequisites.getFullString() + "\n" + cmd_full_strs
    def getReplacedStr(self,replacer:CmdReplacer):
        cmd_re_strs = ""
        for cmd in self.cmds:
            cmd_re_strs += cmd.getReplacedStr(replacer)
        return self.name.getFullString() + ':' + self.prerequisites.getFullString() + "\n" + cmd_re_strs

class GrammerBlock:
    def __init__(self,str,gl_vars):
        self.raw_str = str
        self.fmt_str,self.full_str,self.var_names,self.var_values = self.__parse_str(gl_vars)

    def __parse_str(self,gl_vars):
        full_var_names = re.findall(Variable.REG_PATTERN,self.raw_str)
        var_names = []
        var_values = []
        fmt_str = self.raw_str
        
        for var in full_var_names:
            tem = gl_vars.get(var)
            value = ""
            if tem is None:
                value = "$(" + var + ")"
            else:
                value = tem.value
            var_names.append(var)
            var_values.append(value)
        
        for var in var_names:
            # fmt_str = fmt_str.replace("$("+var+")","{}")
            fmt_str = re.sub(Variable.varRegPattern(var),"{}",fmt_str)
        full_str = fmt_str.format(*var_values)
        return fmt_str,full_str,full_var_names,var_values

    def getFullString(self):
        return self.full_str

    def getFormatString(self):
        return self.fmt_str
    
    def getReplacedStr(self,replacer:CmdReplacer):
        text = self.getFullString()
        return '\t' + replacer.applyTo(text).strip('\t ')

class Makefile:
    def __init__(self,path) -> None:
        self.__makefile = open(path,"r")
        self.__makefile_lines = self.__linkLines(self.__makefile.readlines())
        self.__line_index = 0
        self.variables = {}
        self.targets = {}
        self.pseudo_target = None
        self.element_list = []
        self.__parseFile()
        # self.__linkVariables()
        self.__makefile.close()
        
    def genLinkedText(self):
        text = ""
        for line in self.__makefile_lines:
            text += line
        return text

    def genFullText(self):
        full_text = ""
        for ele in self.element_list:
            full_text += ele.getFullString()
        return full_text
    def genFullTextTo(self,path):
        full_text = self.genFullText()
        file = open(path,'w')
        file.write(full_text)
        file.close()
    def genReplacedFullTextTo(self,replacer:CmdReplacer,path:str):
        full_text = ""
        for ele in self.element_list:
            if isinstance(ele,Variable):
                continue
            # if isinstance(ele,Target):
            #     print("ds")
            full_text += ele.getReplacedStr(replacer)
        file = open(path,'w')
        file.write(full_text)
        file.close()

    def __parseFile(self):
        line = self.__popNextLine()
        while line:
            element = None
            if line[0] == '#':
                line = self.__popNextLine()
                continue
            elif line.find(":") != -1:
                element = self.__parseTarget(line)
            elif line.find("=") != -1:
                element = self.__parseVariable(line)
            else:
                element = self.__parseSpecialBlock(line)
            self.element_list.append(element)
            line = self.__popNextLine()

    def __parsePseudoTarget(self,line):
        target_name = line.split(":")[0].strip()
        target_pre = line.split(":")[1].strip()
        cmd_strs = []
        self.pseudo_target = Target(target_name,target_pre,cmd_strs,self.variables)
        return self.pseudo_target
        
    def __parseVariable(self,line):
        var_name = line[:line.find("=")].strip()
        var_value = line[line.find("=")+1:].strip()

        recur_vars = re.findall(Variable.REG_PATTERN,var_value)
        while len(recur_vars) > 0:
            counter = len(recur_vars)
            for var in recur_vars:
                if self.variables.get(var) != None and self.variables.get(var).value != var:
                    var_value = re.sub(Variable.varRegPattern(var),self.variables[var].value,var_value)
                    counter -= 1
            if counter == len(recur_vars):
                break
            recur_vars = re.findall(Variable.REG_PATTERN,var_value)
        var = Variable(var_name,var_value)
        self.variables[var_name] = var
        return var
    
    def __parseTarget(self,line):
        target_name = line.split(":")[0].strip()
        target_pre = line.split(":")[1].strip()
        cmd_strs = []
        cur_line = self.__popNextLine()
        while cur_line and  cur_line[0] == '\t':
            cmd_strs.append(cur_line)
            cur_line = self.__popNextLine()
        if cur_line:
            self.__back2PreLine()
        target = Target(target_name,target_pre,cmd_strs,self.variables)
        self.targets[target.name] = target
        return target
    def __parseSpecialBlock(self,line):
        return GrammerBlock(line,self.variables)

    def __linkVariables(self):
        for var in self.variables:
            var_value = self.variables[var].value
            recur_vars = re.findall(Variable.REG_PATTERN,var_value)
            while len(recur_vars) > 0:
                counter = len(recur_vars)
                for var in recur_vars:
                    if self.variables.get(var) != None and self.variables.get(var).value != var:
                        var_value = re.sub(Variable.varRegPattern(var),self.variables[var].value,var_value)
                        counter -= 1
                if counter == len(recur_vars):
                    break
                recur_vars = re.findall(Variable.REG_PATTERN,var_value)
            self.variables[var].value = var_value

    def __linkLines(self,lines):
        index = 0
        linked_lines = []
        cur_line = ""
        while index < len(lines):
            cur_line += lines[index]
            if len(cur_line.strip()) <= 0 or cur_line.strip()[-1] != '\\':
                linked_lines.append(cur_line)
                cur_line = ""
            index += 1
        return linked_lines
        
    def __popNextLine(self):
        if self.__line_index < len(self.__makefile_lines):
            line = self.__makefile_lines[self.__line_index]
            self.__line_index += 1
            return line
        else:
            return None
    def __back2PreLine(self):
        if self.__line_index > 0:
            self.__line_index -= 1


if __name__ == '__main__':
    # makefile = Makefile("./Makefile")
    # makefile.genFullTextTo("./Makefile.full")
    # str = "ggcc ${ dff } -c file.c"
    # ret = re.sub(re.compile(r"(\s+|^)(gcc)(\s+|$)"),"clang",str)
    # print(ret)
    print(os.getcwd())
    
   
    