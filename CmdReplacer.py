import re


class ReplaceReg:
    def __init__(self, type, str_reg, sub_str):
        self.type = type
        self.str_reg = re.compile(str_reg)
        self.sub_str = sub_str

    def sub(self, str):
        ret = re.sub(self.str_reg, self.sub_str, str)
        return ret


class CmdReplacer:
    def __init__(self) -> None:
        self.__regs = None
        self.__reg_list = []

    def loadRegFile(self, path):
        self.__regs = open(path).readlines()
        self.__parseRegs()

    def loadRegString(self, string):
        self.__regs = string.split('\n')
        self.__parseRegs()

    def __parseRegs(self):
        for each_reg in self.__regs:
            params = re.match(re.compile(r'^(\w+)\s+(".*")\s+(".*")\s*'),each_reg).groups()
            type = params[0]
            str_reg = eval(params[1])
            sub_str = eval(params[2])
            self.__reg_list.append(ReplaceReg(type, str_reg, sub_str))

    def applyTo(self, string):
        ret_str = string
        for reg in self.__reg_list:
            ret_str = reg.sub(ret_str)
        return ret_str
