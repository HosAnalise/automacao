from classes.utils.LogManager import LogManager

log = LogManager()


def test_delete():

    log.delete_logs_older_than(0)

