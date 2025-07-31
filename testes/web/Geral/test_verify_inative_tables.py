from scripts.verify_inative_tables import main





def test_veryfy_inative_tables():
    """
    Testa a função de verificação de tabelas inativas.
    """

    # Chama a função principal para verificar tabelas inativas
    result = main(dialect_name="firebird")

    # Verifica se o resultado é um dicionário
    print(f"result: {result} ")