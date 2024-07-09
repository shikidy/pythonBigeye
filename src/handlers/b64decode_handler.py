import ast

import base64

from src.consts import PAYLOAD_TRIGGERS


def b64_handler(target):
    if not isinstance(target, ast.Call): 
        print("Non qualed", target)
        return "need update"
    
    if not target.args: return 
    
    if not isinstance(target.args[0], ast.Constant): return

    to_unpack = target.args[0].value

    

    try: 
        result = base64.b64decode(to_unpack)
    except: return
    
    #FIXME 
    return f"[PAYLOAD FOUND AND DECODED]: {result}"