import inspect
from functools import wraps
from classes.utils.VisualValidator import VisualValidator
import os 

def com_visual(viewport_size=(1280, 720),batch_name="Testes Visuais"):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            # Tenta pegar 'init' dos kwargs ou dos args
            init = kwargs.get('init', None)
            if init is None and len(args) > 0:
                init = args[0]

            # Se ainda não tiver init ou se não for uma tupla/lista com browser
            if not isinstance(init, (tuple, list)) or len(init) == 0:
                return test_func(*args, **kwargs)

            browser = init[0]
            test_name = test_func.__name__

            validator = None

            use_applitools = os.getenv("USE_APPLITOOLS","True")

            try:
                # Passa o validator via kwargs para o teste, se aceito
                sig = inspect.signature(test_func)
                if use_applitools == "True":
                    validator = VisualValidator(batch_name=batch_name)
                    # Abre sessão visual
                    validator.open(driver=browser, test_name=test_name, viewport_size=viewport_size)
                if 'validator' in sig.parameters:
                    result = test_func(*args, validator=validator, **kwargs)
                else:
                    result = test_func(*args, **kwargs)
                if use_applitools == "True" and validator:
                    validator.close()
                return result
            except Exception:
                if validator:
                    validator.abort()
                raise

        return wrapper
    return decorator



