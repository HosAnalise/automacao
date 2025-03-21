from datetime import datetime,timedelta
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis



def test_contasPagar_insereConta_aba_intrucao_pagamento(init,query):  
      

    randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    random_value = round(random.uniform(1, 999999), 2)
    randomValue = FuncoesUteis.formatBrCurrency(random_value)
    randomText = GeradorDados.gerar_texto(20)

    bigText700 = GeradorDados.gerar_texto(700)



#_________________________________________________________________
# inicio da aba intrução de pagamento  

    try:

        abaInstrucaoPagamento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#R108405262283655634_tab")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba instrução de pagamento encontrada", routine="ContaPagar", error_details ="" )

        browser.execute_script("arguments[0].scrollIntoView(true);", abaInstrucaoPagamento)
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Sroll até Aba instrução de pagamento", routine="ContaPagar", error_details ="" )


        # Clica na aba de instrução de pagamento
        abaInstrucaoPagamento.click()
        Log_manager.add_log(application_type=env_application_type, level="INFO", message="Aba instrução de pagamento clicada", routine="ContaPagar", error_details="")

        # Gera um número aleatório para forma de pagamento
        formaPagamento = GeradorDados.randomNumberDinamic(0, 2)

        # Gera um número aleatório para DDA
        randomDda = GeradorDados.randomNumberDinamic(0, 2)
        if randomDda == 0:
            Apex.setValue(browser, "P47_DDA", "1")
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="DDA definido (DDA)", routine="ContaPagar", error_details="")

        if formaPagamento == 0:
            Apex.setValue(browser, "P47_FORMA_INSTRUCAO_PAGAMENTO_ID", 2)
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="Forma de pagamento definida como 2 (Boleto)", routine="ContaPagar", error_details="")

        elif formaPagamento == 1:
            Apex.setValue(browser, "P47_FORMA_INSTRUCAO_PAGAMENTO_ID", 3)
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="Forma de pagamento definida como 3 (PIX)", routine="ContaPagar", error_details="")
            
            # Aguarda o campo de tipo de chave PIX estar clicável
            WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#P47_PIX_TIPO_CHAVE_ID")))
            Apex.setValue(browser, "P47_PIX_TIPO_CHAVE_ID", randomChavePixId)
            Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Tipo de chave PIX definido como {randomChavePixId}", routine="ContaPagar", error_details="")
            
            if randomChavePixId == 1:
                cpfCnpj = GeradorDados.randomNumberDinamic(0, 1)
                if cpfCnpj == 0:
                    Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_cpf())
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como CPF", routine="ContaPagar", error_details="")
                else:
                    Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_cnpj())
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como CNPJ", routine="ContaPagar", error_details="")
            elif randomChavePixId == 2:
                Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_numero_celular())
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como número de celular", routine="ContaPagar", error_details="")
            elif randomChavePixId == 3:
                Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_email())
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como email", routine="ContaPagar", error_details="")
            elif randomChavePixId in (4, 5, 6):
                Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_chave_aleatoria())
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como chave aleatória", routine="ContaPagar", error_details="")

        elif formaPagamento == 2:
            Apex.setValue(browser, "P47_FORMA_INSTRUCAO_PAGAMENTO_ID", 4)
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="Forma de pagamento definida como 4 (TED)", routine="ContaPagar", error_details="")
            
            contaDestino = GeradorDados.randomNumberDinamic(0, 2)
            if contaDestino == 0:
                Apex.setValue(browser, "P47_TED_CONTA_DESTINO_ID", 1)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Conta destino definida como 1 (Corrente)", routine="ContaPagar", error_details="")
            elif contaDestino == 1:
                Apex.setValue(browser, "P47_TED_CONTA_DESTINO_ID", 2)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Conta destino definida como 2 (Poupança)", routine="ContaPagar", error_details="")
            elif contaDestino == 2:
                Apex.setValue(browser, "P47_TED_CONTA_DESTINO_ID", 3)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Conta destino definida como 3 (Pagamento)", routine="ContaPagar", error_details="")
            
            digitoConta = GeradorDados.randomNumberDinamic(0, 9)
            numeroAgencia = GeradorDados.randomNumberDinamic(0000, 9999)
            numeroConta = GeradorDados.randomNumberDinamic(0000000000, 999999999)
            nomeFavorcido = GeradorDados.gerar_nome()
            textOrNumber = GeradorDados.randomNumberDinamic(0, 1)

            if textOrNumber == 0:
                Apex.setValue(browser, "P47_TED_BANCO_ID", randomBancoId)
                Apex.setValue(browser, "P47_TED_AGENCIA", numeroAgencia)
                Apex.setValue(browser, "P47_TED_CONTA", numeroConta)
                Apex.setValue(browser, "P47_TED_CONTA_DIGITO", digitoConta)
                Apex.setValue(browser, "P47_TED_NOME_FAVORECIDO", nomeFavorcido)
                Apex.setValue(browser, "P47_INSTRUCAO_OBSERVACAO", randomText)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Informações da conta TED preenchidas corretamente", routine="ContaPagar", error_details="")
            else:
                Apex.setValue(browser, "P47_TED_BANCO_ID", randomBancoId)
                Apex.setValue(browser, "P47_TED_AGENCIA", randomText)
                Apex.setValue(browser, "P47_TED_CONTA", randomText)
                Apex.setValue(browser, "P47_TED_CONTA_DIGITO", randomText)
                Apex.setValue(browser, "P47_TED_NOME_FAVORECIDO", randomValue)
                Apex.setValue(browser, "P47_INSTRUCAO_OBSERVACAO", bigText700)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Informações de conta TED com texto aleatório preenchidas", routine="ContaPagar", error_details="")

            cpfCnpj2 = GeradorDados.randomNumberDinamic(0, 1)
            if cpfCnpj2 == 0:
                Apex.setValue(browser, "P47_TED_DOCUMENTO_FAVORECIDO", GeradorDados.gerar_cpf())
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Documento do favorecido definido como CPF", routine="ContaPagar", error_details="")
            else:
                Apex.setValue(browser, "P47_TED_DOCUMENTO_FAVORECIDO", GeradorDados.gerar_cnpj())
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Documento do favorecido definido como CNPJ", routine="ContaPagar", error_details="")
    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ContaPagar",
            error_details=str(e)
        )

    except NoSuchElementException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Elemento não encontrado na página",
            routine="ContaPagar",
            error_details=str(e)
        )

    except Exception as e:  # Captura qualquer outro erro inesperado
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro desconhecido ao acessar a página",
            routine="ContaPagar",
            error_details=str(e)
        )