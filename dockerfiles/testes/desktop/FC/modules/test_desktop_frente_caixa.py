import json
from test_desktop_frente_caixa_login import test_desktop_realizar_login
from test_desktop_frente_caixa_insere_produto import test_desktop_inserir_produto
from test_desktop_frente_caixa_insere_cliente  import test_desktop_inserir_cliente
from test_desktop_frente_caixa_insere_tele import test_desktop_inserir_tele_entrega
from test_desktop_frente_caixa_finaliza_venda import test_desktop_finalizar_venda
from test_desktop_frente_caixa_config_tele  import test_desktop_config_tele
from test_desktop_frente_caixa_config_controlados import test_desktop_config_controlados


def test_init(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection):
    if has_connection:
        getEnv = env_vars
        env_application_type = getEnv.get("DESKTOP")
        payment_method_str = getEnv.get("PAYMENT_METHODS")
        payment_method = json.loads(payment_method_str)   
        app = None  
        has_client = False
        has_delivery = False
        amount = 1
        controlled =  False

        

        try:
            # Iterar sobre todas as formas de pagamento
            for payment_method_key, payment_method_value in payment_method.items():     
            
                    # Executando o login
                    app = test_desktop_realizar_login(log_manager, env_vars,has_connection)
                    
                    # Inserindo os produtos
                    test_desktop_inserir_produto(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection,amount=amount,controlled=controlled)
                
                    # Inserindo o cliente com base no tipo de pagamento
                    has_client = test_desktop_inserir_cliente(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection, client_credit=payment_method_key)
                    
                    # Inserindo dados de tele entrega
                    has_delivery = test_desktop_inserir_tele_entrega(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection)

                    #Configurando tele entrega
                    test_desktop_config_tele(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection, has_client=has_client, has_delivery=has_delivery,payment_method=payment_method_key)
                    
                    # Configurando produtos controlados
                    test_desktop_config_controlados(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection, controlled=controlled,has_client=has_client)

                    # Finalizando a venda com a forma de pagamento atual
                    test_desktop_finalizar_venda(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection, payment_methods=payment_method_key,has_client=has_client)

                    log_manager.insert_logs_for_execution()
                    if app is not None:
                        app.kill()
                    
        except Exception as e:
            log_manager.add_log(
                application_type=env_application_type, 
                level="ERROR",
                message=f"Erro ao executar o script venda não finalizada {payment_method_key}",
                routine="Inserção de venda", 
                error_details=str(e)
            )
            raise

       
