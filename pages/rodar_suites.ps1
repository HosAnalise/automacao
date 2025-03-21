# Define usuários e ambientes correspondentes
$usuarios = @(
	@{usuario="GABRIEL"; ambiente="HOMOLOGACAO_FL3"},
	@{usuario="GABRIEL"; ambiente="HOMOLOGACAO_GRUPO"},
	@{usuario="TESTE"; ambiente="NONE"}
)
# Define as paths dos testes
$suites = @(
	"suiteCreditoFornecedor"
)
# Itera sobre cada usuário e ambiente correspondente
foreach ($usuarioInfo in $usuarios) {
	$usuario = $usuarioInfo.usuario
	$ambiente = $usuarioInfo.ambiente	
	# Itera sobre cada path de teste
	foreach ($suite in $suites) {
		Write-Host "Rodando teste para o usuário $usuario no ambiente $ambiente com a suite $suite"
		pytest -m "$suite" --user=$usuario --ambiente=$ambiente
	}
}
