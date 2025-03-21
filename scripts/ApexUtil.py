

class Apex:
    @staticmethod
    def setValue(browser,element,value):
        browser.execute_script(f"apex.item({element}).setValue('{value}')")  

    @staticmethod
    def getValue(browser,element):
        value = browser.execute_script(f"return apex.item({element}).getValue()")
        return value
