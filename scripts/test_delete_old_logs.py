from matplotlib.pylab import f
from classes.utils.LogManager import LogManager

log = LogManager()



def test_delete():
    """
    Testa a remoção de logs antigos de uma coleção específica.
    """
    # log.clear_collection(collection_name='web_logs')    
    logs_list  = log.get_logs_not_async(collection='emails')
    for log_entry in logs_list:
      print(log_entry['email'])