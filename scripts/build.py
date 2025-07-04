import re
import yaml
import configparser
import argparse # Dica Pro: Usar argparse para scripts de linha de comando!

def get_markers(ini_file='pytest.ini'):
    """Retorna uma lista de marcadores definidos no arquivo pytest.ini."""
    config = configparser.ConfigParser()
    config.read(ini_file)
    
    # fallback='' previne erros se a seção ou chave não existir
    markers_string = config.get('pytest', 'markers', fallback='')
    
    # List comprehension para limpar e filtrar os marcadores
    marker_list = [marker.strip() for marker in markers_string.split('\n') if marker.strip()]
    return marker_list

def get_base_config(marker: str):
    """
    Retorna a configuração de um serviço do docker-compose como um dicionário Python,
    baseado em um marcador do pytest.
    
    """


    # Sanitiza o nome do marcador para ser um nome de serviço válido
    safe_service_name = re.sub(r'[^a-zA-Z0-9_-]', '', marker)
    
    # --- LÓGICA DINÂMICA ---
    # Deriva o nome do diretório de testes a partir do nome do marcador.
    # Ex: 'dockerContaPagar' -> 'ContaPagar'
    tests_dir = marker.replace('docker', '', 1)

    return {
        'version': '1.0',
        'services': {
            safe_service_name: {
                'build': {
                    'context': '.',
                    'dockerfile': 'docker/Dockerfile',
                    'args': {
                        # Valores agora são dinâmicos!
                        'TESTS_DIR': tests_dir,
                        'PYTESTMARK': marker
                    }
                },
                'image': f'hosanalise/{safe_service_name}:latest',
                # 'environment': [
                #     'APPLITOOLS_API_KEY=${APPLITOOLS_API_KEY}'
                # ]
            }
        }
    }

def write_docker_compose(config, filename='docker-compose.yml'):
    """Escreve a configuração final em um arquivo YAML."""
    print(f" Gerando o arquivo '{filename}'...")
    try:
        with open(filename, 'w') as file:
            # sort_keys=False mantém a ordem de inserção, o que é mais legível
            yaml.dump(config, file, sort_keys=False, indent=2)
        print(f" Arquivo '{filename}' gerado com sucesso!")
    except Exception as e:
        print(f" Erro ao escrever o arquivo YAML: {e}")

def main(marker_source='pytest.ini', output_file='docker-compose.yml'):
    """
    Cria o arquivo docker-compose.yml com base nos marcadores do pytest.
    """
    print(" Iniciando a criação do docker-compose dinâmico...")
    
    # 1. Pega a lista de marcadores
    marks_list = get_markers(ini_file=marker_source)
    if not marks_list:
        print(" Nenhum marcador encontrado. Saindo.")
        return

    # 2. Inicia a configuração final
    final_config = {'version': '1.0', 'services': {}}

    # 3. Itera sobre os marcadores, construindo o dicionário de serviços
    for mark in marks_list:
        # Pega a configuração para o marcador atual
        service_config = get_base_config(mark)
        # Atualiza o dicionário de serviços com o novo serviço
        final_config['services'].update(service_config['services'])

    # 4. Escreve o arquivo UMA VEZ, após o loop terminar
    write_docker_compose(final_config, filename=output_file)

# --- Ponto de Entrada do Script ---
# É uma boa prática usar um bloco `if __name__ == '__main__':`
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gera um docker-compose.yml dinamicamente a partir dos marcadores do pytest.")
    parser.add_argument(
        '--source',
        default='pytest.ini',
        help="Caminho para o arquivo de configuração do pytest. Padrão: pytest.ini"
    )
    parser.add_argument(
        '--output',
        default='docker-compose.yml',
        help="Nome do arquivo de saída. Padrão: docker-compose.yml"
    )
    args = parser.parse_args()
    
    main(marker_source=args.source, output_file=args.output)


main()    



