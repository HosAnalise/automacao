import inspect
import os
from functools import wraps
from classes.utils.VisualValidator import VisualValidator


# --- Instância compartilhada para o validador ---
# Esta variável viverá durante toda a sessão de teste e será
# compartilhada por todos os testes que usam o decorator.
_validator_instance: VisualValidator = None


def finalizar_testes_visuais():
    """
    Função de finalização que deve ser chamada UMA VEZ no final de toda a suíte de testes.
    Ela coleta e envia os resultados de todos os testes visuais executados.
    """
    global _validator_instance
    if _validator_instance:
        print("\nFinalizando e coletando resultados dos testes visuais do Applitools...")
        try:
            # O método get_all_results já imprime um resumo e lança exceção em caso de falha.
            results = _validator_instance.get_all_results(raise_ex=True)
            print(results)
        finally:
            # Zera a instância para execuções futuras
            _validator_instance = None


def com_visual(app_name: str = "Automação Web", batch_name: str = "Testes Visuais", viewport_size: tuple = (1280, 720)):
    """
    Decorator modernizado para testes visuais com Applitools.

    Gerencia o ciclo de vida de cada teste (`start_test`, `close_test`) e injeta
    a instância do validador na função de teste se ela aceitar o argumento 'validator'.

    Args:
        app_name (str): Nome da aplicação no painel do Applitools.
        batch_name (str): Nome do lote que agrupará os testes.
        viewport_size (tuple): Tamanho da janela do navegador (largura, altura).
    """
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            global _validator_instance

            # A flag para desativar os testes permanece uma ótima funcionalidade
            use_applitools = os.getenv("USE_APPLITOOLS", "True").lower() == "true"
            if not use_applitools:
                # Executa o teste normalmente sem validação visual
                return test_func(*args, **kwargs)

            # --- Lógica para encontrar o driver ---
            # Sua lógica original para encontrar o driver/browser é mantida
            init = kwargs.get('init', None)
            if init is None and len(args) > 0:
                init = args[0] # Assume que 'self' ou a instância da classe de teste é o primeiro argumento
            
            # Extrai o browser da propriedade 'browser' do objeto 'init'
            if not hasattr(init, 'browser'):
                 raise AttributeError("O objeto de teste passado para o decorator não possui um atributo 'browser'.")
            browser = init.browser

            test_name = test_func.__name__

            # --- Gerenciamento da Instância Compartilhada ---
            # Cria a instância do validador apenas na primeira vez que for necessário
            if _validator_instance is None:
                _validator_instance = VisualValidator(app_name=app_name, batch_name=batch_name)
            
            # Usa a instância global/compartilhada
            validator = _validator_instance
            
            # --- Execução do Teste com Ciclo de Vida do Applitools ---
            try:
                # Usa os novos métodos da classe VisualValidator
                validator.start_test(driver=browser, test_name=test_name, viewport_size=viewport_size)

                # Sua lógica de injeção de dependência é excelente e foi mantida
                sig = inspect.signature(test_func)
                if 'validator' in sig.parameters:
                    result = test_func(*args, validator=validator, **kwargs)
                else:
                    # Se o teste não pede o validator, ele ainda assim será executado
                    # dentro do contexto visual. Útil para um check_window automático no início.
                    # Para isso, você poderia adicionar um validator.check_window("Início do Teste") aqui.
                    result = test_func(*args, **kwargs)
                
                # Usa o novo método de fechamento assíncrono
                validator.close_test()
                return result

            except Exception:
                # Em caso de qualquer erro, aborta o teste visual
                if validator:
                    validator.abort_test_if_needed()
                # E propaga a exceção original
                raise

        return wrapper
    return decorator