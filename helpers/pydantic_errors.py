from pydantic import ValidationError
from typing import List

def get_custom_error_message(e:ValidationError)->List[str]:
    err_msg = []
    e = e.errors()

    for error in e:
        field = error.get("loc")[0]
        msg = error.get("msg")

        err_msg.append(f"{field} : {msg}")
    
    return err_msg