import os
import ast
from typing import Union

from . import consts
from .handlers.b64decode_handler import b64_handler


class Observer:


    def __init__(self, main_module_path: str, work_dir: str = None) -> None:
        self.__main_module = main_module_path
        self.__work_dir = work_dir
        with open(main_module_path, encoding='utf-8') as f:
            self._ast = ast.parse(f.read())

        self.warning_logs = ""
        self.critical_logs = ""
        self.function_handlers = {
            "b64decode": b64_handler
        }

        self.walker(self._ast)

        
    def warn(self, text):
        self.warning_logs += text + '\n'

    def crit(self, text):
        self.critical_logs += text + '\n'
        

    @property
    def logs(self):
        if not self.critical_logs: return

        result = f"[MODULE LOGS] {self.__main_module}\n"

        if self.critical_logs:
            result += "!!CRITICAL!!:\n" + self.critical_logs 

        return  result
    
    def import_worker(self, target: Union[ast.ImportFrom, ast.Import]):
        libs_name = []
        if isinstance(target, ast.Import):
            libs_name += [name.name for name in target.names]
        if isinstance(target, ast.ImportFrom):
            libs_name += [target.module]
        
        for name in libs_name:
            if not name in consts.WARNING_IMPORTS: continue
            self.warn(f"[IMPORT WARNING] `{name}` import detected! Line {target.lineno}")
    
    def expression_worker(self, target: Union[ast.Expr, ast.Call]): 
        func_name = ""
        func_args = []
        func_kwargs = []
        old_type = type(target)


        if isinstance(target, ast.Expr):
            if isinstance(target.value, (ast.Call, ast.Attribute)):
                target = target.value
                # print(target.func.__dict__)
            else: return
        
        func_name = target.func.__dict__.get("id")
        if not func_name:
            func_name = target.func.__dict__.get("attr")

        func_args = target.args
        func_kwargs = target.keywords

        for arg in func_args:
            if isinstance(arg, (ast.Expr, ast.Call)):
                self.expression_worker(arg)

        for kwarg in func_kwargs:
            if isinstance(kwarg.value, (ast.Expr, ast.Call)):
                self.expression_worker(kwarg.value)
        
        if func_name in consts.CRITICAL_FUNCS and not isinstance(target.func, ast.Attribute):
            print(target.__dict__)
            self.crit(f"[CRITICAL FUNCTION] `{func_name}`! Line {target.lineno}")
 
        if func_name in self.function_handlers.keys():
            critical = self.function_handlers[func_name](target)
            if critical: 
                self.crit(critical)
        
        if func_name in consts.CRITICAL_ATTRIBUTES:
            self.crit(f"[CRITICAL ATTRIBUTE] `{func_name}`! Line {target.lineno}")

    def handler(self, item):
        if isinstance(item, (ast.Import, ast.ImportFrom)):
            self.import_worker(item)

        if isinstance(item, (ast.Expr, ast.Call)):
            self.expression_worker(item)


    def walker(self, item):
        if not 'body' in item.__dir__(): return
        for body_item in item.body:
            self.handler(body_item)
            self.walker(body_item)
