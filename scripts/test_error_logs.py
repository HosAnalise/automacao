from math import log
from classes.utils.LogManager import LogManager



log = LogManager()


def test_error_logs():
    """
    Test to ensure that error logs are being generated correctly.
    """

    logs = log.analisar_erros()


    print (f"Total de erros encontrados: {logs}")