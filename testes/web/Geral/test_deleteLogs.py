from classes.utils.LogManager import LogManager

log_manager = LogManager()

def test_delete():
    log_manager.delete_logs_older_than(0)