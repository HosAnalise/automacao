class Apex:
    @staticmethod
    def setValue(browser, element: str, value: str | int):
        """
        Define um valor em um item do Oracle APEX via JavaScript.

        :param browser: Instância do WebDriver.
        :param element: Nome do item APEX (como string, ex: 'P1_NOME').
        :param value: Valor a ser atribuído ao item (str ou int).
        """
        browser.execute_script(f"apex.item('{element}').setValue('{value}')")

    @staticmethod
    def getValue(browser, element: str) -> str:
        """
        Obtém o valor de um item do Oracle APEX via JavaScript.

        :param browser: Instância do WebDriver.
        :param element: Nome do item APEX (como string, ex: 'P1_NOME').
        :return: Valor atual do item (str).
        """
        return browser.execute_script(f"return apex.item('{element}').getValue()")
