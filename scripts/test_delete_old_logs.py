from pickle import TRUE
from unittest import result
from classes.utils.LogManager import LogManager

log = LogManager()

# log.delete_logs_older_than(0)

data = log.get_logs()
print(data)
