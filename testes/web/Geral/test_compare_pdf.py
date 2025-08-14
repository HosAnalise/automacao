from os import path
from classes.utils.AI import AI

ai = AI()   

path_to_pdf1 = path.join("assets\cx_2216_FC.pdf")
path_to_pdf2 = path.join("assets\cxWeb2216.pdf")

def test_compare_pdf():
    """
    Testa a comparação de dois PDFs usando a classe AI.
    """
    print("Iniciando teste de comparação de PDFs...")
    print(ai.analisar_e_comparar_pdfs(path_to_pdf1, path_to_pdf2))
    print("Teste de comparação de PDFs concluído com sucesso!")
