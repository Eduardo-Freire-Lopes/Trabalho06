# run_profiles.ps1 — Executa 3 perfis de carga para cada tecnologia
# Pre-requisito: todos os 4 servidores devem estar rodando:
#   REST    -> porta 8000  (cd rest/python    ; uvicorn main:app --port 8000)
#   GraphQL -> porta 8002  (cd graphql/python ; uvicorn main:app --port 8002)
#   SOAP    -> porta 8006  (cd soap/python    ; python server.py)
#   gRPC    -> porta 8004  (cd grpc/python    ; python server.py)
# E o seed deve ter sido executado:
#   .venv\Scripts\python.exe db/seed.py

param(
    [string]$ResultsDir = "load-tests\results"
)

$venv = ".venv\Scripts\python.exe"
$locust = ".venv\Scripts\locust"
$dir = $ResultsDir

# Cria pasta de resultados
New-Item -ItemType Directory -Force -Path $dir | Out-Null

# Perfis: nome, usuarios, taxa, duracao
$profiles = @(
    @{ name="leve";   users=10;  rate=2;  time="60s" },
    @{ name="medio";  users=50;  rate=10; time="60s" },
    @{ name="pesado"; users=150; rate=25; time="60s" }
)

# Tecnologias: locustfile, tag
$techs = @(
    @{ file="load-tests\locust_rest.py";     tag="rest"     },
    @{ file="load-tests\locust_graphql.py";  tag="graphql"  },
    @{ file="load-tests\locust_soap.py";     tag="soap"     },
    @{ file="load-tests\locust_grpc.py";     tag="grpc"     }
)

foreach ($tech in $techs) {
    foreach ($prof in $profiles) {
        $csv = "$dir\$($tech.tag)_$($prof.name)"
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "  $($tech.tag.ToUpper()) | perfil: $($prof.name) | usuarios: $($prof.users)" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan

        & $locust -f $tech.file --headless `
            -u $prof.users -r $prof.rate `
            --run-time $prof.time `
            --csv=$csv `
            --csv-full-history 2>&1

        Write-Host "Resultados salvos em: $csv*.csv"
    }
}

Write-Host "`nTodos os perfis concluidos!" -ForegroundColor Green
Write-Host "Arquivos CSV em: $dir\" -ForegroundColor Green
