$ErrorActionPreference = "Continue"

$ProjectPath = "C:\Users\jmcas\OpenClawProjects\trading-ai"
$PythonPath = Join-Path $ProjectPath ".venv\Scripts\python.exe"
$ScriptPath = Join-Path $ProjectPath "src\workflows\run_fib_v5_full_cycle.py"

$RunCount = 20
$SleepSeconds = 1800

$LogDir = Join-Path $ProjectPath "logs"

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$LogFile = Join-Path $LogDir (
    "full_cycle_20x_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log"
)

Set-Location $ProjectPath

Write-Host ""
Write-Host "=== FIB V5 AUTO RUNNER 20X ==="
Write-Host ""
Write-Host "Proyecto: $ProjectPath"
Write-Host "Python: $PythonPath"
Write-Host "Script: $ScriptPath"
Write-Host "Ejecuciones: $RunCount"
Write-Host "Intervalo: 30 minutos"
Write-Host "Log: $LogFile"
Write-Host ""

for ($i = 1; $i -le $RunCount; $i++) {

    $StartTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Host ""
    Write-Host "=================================================="
    Write-Host "EJECUCION $i / $RunCount"
    Write-Host "Inicio: $StartTime"
    Write-Host "=================================================="
    Write-Host ""

    "==================================================" | Tee-Object -FilePath $LogFile -Append
    "EJECUCION $i / $RunCount" | Tee-Object -FilePath $LogFile -Append
    "Inicio: $StartTime" | Tee-Object -FilePath $LogFile -Append
    "==================================================" | Tee-Object -FilePath $LogFile -Append

    & $PythonPath $ScriptPath 2>&1 | Tee-Object -FilePath $LogFile -Append

    $EndTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    ""
    "Fin: $EndTime" | Tee-Object -FilePath $LogFile -Append
    "Ejecucion $i finalizada." | Tee-Object -FilePath $LogFile -Append

    Write-Host ""
    Write-Host "Ejecucion $i finalizada: $EndTime"

    if ($i -lt $RunCount) {

        Write-Host ""
        Write-Host "Esperando 30 minutos para la siguiente ejecucion..."
        Write-Host ""

        Start-Sleep -Seconds $SleepSeconds
    }
}

Write-Host ""
Write-Host "=== PROCESO COMPLETADO ==="
Write-Host "Total ejecuciones: $RunCount"
Write-Host "Log guardado en: $LogFile"
Write-Host ""

"=== PROCESO COMPLETADO ===" | Tee-Object -FilePath $LogFile -Append
"Total ejecuciones: $RunCount" | Tee-Object -FilePath $LogFile -Append
"Log guardado en: $LogFile" | Tee-Object -FilePath $LogFile -Append