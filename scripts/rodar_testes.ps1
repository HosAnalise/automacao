# Define usuários e ambientes correspondentes
$usuarios = @(
	# @{usuario="GABRIEL"; ambiente="HOMOLOGACAO_FL3"},
	# @{usuario="GABRIEL"; ambiente="HOMOLOGACAO_GRUPO"},
	@{usuario="TESTE"; ambiente="NONE"}
)

$timeToRunScripts = 20  # Número de repetições

# Define as paths dos testes
$paths = @(
	"testes\Web\ContasReceber\",
	"testes\Web\ContasPagar\"

)

# Executa os testes pelo número de vezes definido
for ($i = 0; $i -lt $timeToRunScripts; $i++) {
	Write-Host "Execução número: $($i+1)"
	
	# Itera sobre cada usuário e ambiente correspondente
	foreach ($usuarioInfo in $usuarios) {
		$usuario = $usuarioInfo.usuario
		$ambiente = $usuarioInfo.ambiente	
		
		# Itera sobre cada path de teste
		foreach ($path in $paths) {
			Write-Host "Rodando teste para o usuário $usuario no ambiente $ambiente com a path $path"
			pytest "testes/$path" --user=$usuario --ambiente=$ambiente
		}
	}
}
