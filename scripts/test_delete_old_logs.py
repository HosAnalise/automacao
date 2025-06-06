from classes.utils.LogManager import LogManager

log = LogManager()

# log.delete_logs_older_than(0)

data = log.delete_logs_older_than(0)
print(data)
