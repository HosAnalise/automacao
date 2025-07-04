from classes.utils.LogManager import LogManager

log = LogManager()



def test_delete(collection_name):
    """
    Testa a remoção de logs antigos de uma coleção específica.
    """
    log.clear_collection(collection_name=collection_name)    
