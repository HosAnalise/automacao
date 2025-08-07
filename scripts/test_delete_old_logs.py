from matplotlib.pylab import f
from classes.utils.LogManager import LogManager

log = LogManager()



def test_delete():
    """
    Testa a remoção de logs antigos de uma coleção específica.
    """
    log.clear_collection(collection_name='error_logs')  # Limpa a coleção de logs de erro antes do teste
    log.clear_collection(collection_name='web_logs')  # Limpa a coleção de logs da web antes do teste
