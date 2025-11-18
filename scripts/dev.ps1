param([string]$cmd='help')

switch ($cmd) {
  'install' { python -m pip install -r requirements.txt }
  'run' { python -m uvicorn sentinel.dashboard.app:app --host 0.0.0.0 --port 8000 }
  'test' { python -m pytest -q }
  'up' { docker compose up --build }
  'down' { docker compose down }
  default { Write-Output 'install|run|test|up|down' }
}
