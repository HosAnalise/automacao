from functools import wraps
from mimetypes import guess_file_type
from classes.utils.VisualValidator import VisualValidator

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

            validator = VisualValidator(batch_name=batch_name)


            # Abre sessão visual
            validator.open(driver=browser, test_name=test_name, viewport_size=viewport_size)

            try:
                # Passa o validator via kwargs para o teste
                result = test_func(*args, validator=validator, **kwargs)
                validator.close()
                return result
            except Exception:
                validator.abort()
                raise

        return wrapper
    return decorator



