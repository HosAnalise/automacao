from classes.utils.LogManager import LogManager

log_manager = LogManager()

def test_delete_old_logs(days = 7):
    log_manager.delete_logs_older_than(days)









