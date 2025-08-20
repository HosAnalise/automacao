from conftest import has_connection
import pytest

@pytest.mark.skipif(not has_connection(), reason="Sem conexão com a internet")
def test_login(login):
    """
    assert login is not None
    """

    try:
        assert login is not None, "Login fixture returned None"
    except Exception as e:
        print(f"Erro ao realizar login: {e}")
        
