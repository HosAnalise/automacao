from classes.utils.AI import AI
import os




def test_compare_pdf():
    """
    Testa a comparação de PDFs usando a classe AI.
    """

    ai = AI()

    pdf1 = "assets/RptRelatorioCaixaDetalhado853.pdf"
    pdf2 = "assets/report853.pdf"

    # Verifica se os PDFs existem
    assert os.path.exists(pdf1), f"Arquivo {pdf1} não encontrado."
    assert os.path.exists(pdf2), f"Arquivo {pdf2} não encontrado."

    # Compara os PDFs
    resultado = ai.analisar_e_comparar_pdfs(pdf1, pdf2)
    print(f"Resultado da comparação: {resultado}")
    # Verifica se o resultado é uma string e não está vazio
    assert isinstance(resultado, str), "O resultado da comparação deve ser uma string."
    assert resultado != "", "O resultado da comparação não deve ser vazio."