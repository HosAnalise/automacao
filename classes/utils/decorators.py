from functools import wraps
from classes.utils.VisualValidator import VisualValidator

def com_visual(viewport_size=(1280, 720)):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):

            init = kwargs.get('init', None)

            # se não tiver em kwargs, tenta pegar do primeiro argumento positional
            if init is None and len(args) > 0:
                init = args[0]

            # se ainda não tiver init, só chama o teste direto (evita crash)
            if init is None:
                return test_func(*args, **kwargs)       # pega a tupla
            
            browser = init[0]     # extrai o driver da posição 0

            test_name = test_func.__name__

            validator = VisualValidator()
            validator.open(browser, test_name, viewport_size)

            try:
                # Passa o validator para o teste (via kwargs)
                result = test_func(*args, validator=validator, **kwargs)
                
                validator.close()
                return result
            except Exception:
                validator.abort()
                raise

        return wrapper
    return decorator
