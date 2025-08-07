

class Apex:
    @staticmethod
    def setValue(browser, element: str, value: str | int | list):
        """
        Define um valor em um item do Oracle APEX via JavaScript.

        :param browser: Instância do WebDriver.
        :param element: Nome do item APEX (como string, ex: 'P1_NOME').
        :param value: Valor a ser atribuído ao item (str, int ou list).
        """
        script = "apex.item(arguments[0]).setValue(arguments[1]);"

        if isinstance(value, int):
            # Se for um inteiro, convertemos para string
            value = str(value)

        if isinstance(value, list):
            value = [i if isinstance(i, (str, int)) else str(i) for i in value]

        
        # Agora passamos o valor (string, int ou list) diretamente.
        # O Selenium converterá a lista Python para um Array JavaScript.
        browser.execute_script(script, element, value)

    @staticmethod
    def getValue(browser, element: str) -> str:
        """
        Obtém o valor de um item do Oracle APEX via JavaScript.

        :param browser: Instância do WebDriver.
        :param element: Nome do item APEX (como string, ex: 'P1_NOME').
        :return: Valor atual do item (str).
        """
        return browser.execute_script(f"return apex.item('{element}').getValue()")
