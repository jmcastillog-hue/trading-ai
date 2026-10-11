[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("SelfCheck", "Preflight", "Context", "Binding", "Audit")]
    [string]$Mode,

    [string]$RepoPath = "C:\Users\jmcas\OpenClawProjects\trading-ai"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (Test-Path variable:PSNativeCommandUseErrorActionPreference) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$CohortId = "CONTEXT_LEVEL_A_DAILY_EVENING_30_V4_HYBRID"
$ExpectedCoreCommit = "ba66d0b07cf1ea365d6ddbb42006f6cb886da51c"
$ExpectedTimeZone = "Pacific SA Standard Time"

$PythonPath = "C:\TAE\venvs\context-daily-evening-v4\Scripts\python.exe"
$RunnerPath = Join-Path $RepoPath `
    "tools\context_evaluation_daily_evening_hybrid_runner_v4.py"
$PlanPath = Join-Path $RepoPath `
    "research\context_evaluation\context_evaluation_daily_evening_30_plan_v4.json"

$LogRoot = Join-Path `
    "C:\TAE\automation_logs" `
    $CohortId

$StateRoot = Join-Path `
    "C:\TAE\automation_state" `
    $CohortId

$AttemptRoot = Join-Path $StateRoot "binding_attempts"

$SourceAttestation = `
    "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"

$FrozenHashes = [ordered]@{
    "requirements/context_daily_evening_v4.txt" = "483e2fd4959cde135f8cc7d1918acbe2467c17d5cdcdddaa354f28dad0fd4d73"
    "research/context_evaluation/context_evaluation_daily_evening_30_plan_v4.json" = "9f8823b28444dda1aae4d4bfa362a88147287e3fc8a7e0100a3a365e3ee2124f"
    "research/context_evaluation/context_evaluation_daily_evening_30_protocol_v4.json" = "ba4165dc2d135e3ea58879a26ba09292cefee3e30c8d8ae97e19381044302460"
    "research/context_evaluation/reference_runners/outcome_binding_historical_automated_reference_s008_v4.py" = "4c24ce929a3befb8b135a2c13681650113ffb97d166dc702926b5e76286fe838"
    "src/exchange/binance_public_historical_closed_candle_capture_v2.py" = "3ee10379f823f5c28f92d84298f2421613dce596979b6b6a252f4206d64ec119"
    "tools/context_evaluation_daily_evening_hybrid_runner_v4.py" = "5ec4bfa21f37715d8b52ccafa572bb09711982cb8a677bcee745855e57a4b48c"
}

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Get-LowerHash {
    param([string]$Path)

    return (
        Get-FileHash $Path -Algorithm SHA256
    ).Hash.ToLowerInvariant()
}

function Assert-CoreArtifacts {
    Assert-True (Test-Path $RepoPath) "Repository not found."
    Assert-True (Test-Path $PythonPath) "V4 Python not found."
    Assert-True (Test-Path $RunnerPath) "V4 runner not found."
    Assert-True (Test-Path $PlanPath) "V4 plan not found."

    foreach ($RelativePath in $FrozenHashes.Keys) {
        $AbsolutePath = Join-Path $RepoPath $RelativePath

        Assert-True (
            Test-Path $AbsolutePath
        ) "Frozen artifact missing: $RelativePath"

        $ActualHash = Get-LowerHash $AbsolutePath

        Assert-True (
            $ActualHash -eq $FrozenHashes[$RelativePath]
        ) "Frozen artifact hash mismatch: $RelativePath"
    }
}

function Assert-OperationalRepository {
    Push-Location $RepoPath

    try {
        $Branch = (git branch --show-current).Trim()
        $Head = (git rev-parse HEAD).Trim()
        $Main = (git rev-parse main).Trim()
        $OriginMain = (git rev-parse origin/main).Trim()

        Assert-True (
            $LASTEXITCODE -eq 0
        ) "Unable to inspect repository references."

        Assert-True (
            $Branch -eq "main"
        ) "Operational execution requires main."

        Assert-True (
            $Head -eq $Main -and
            $Head -eq $OriginMain
        ) "HEAD, main and origin/main must match."

        git merge-base --is-ancestor $ExpectedCoreCommit $Head

        Assert-True (
            $LASTEXITCODE -eq 0
        ) "Published V4 core commit is not an ancestor of HEAD."

        $Status = @(
            git status --porcelain=v1 --untracked-files=all
        )

        Assert-True (
            $Status.Count -eq 0
        ) "Operational execution requires a clean worktree."
    }
    finally {
        Pop-Location
    }
}

function Invoke-Runner {
    param([string[]]$Arguments)

    $Output = @(
        & $PythonPath $RunnerPath @Arguments 2>&1
    )

    $ExitCode = $LASTEXITCODE

    foreach ($Line in $Output) {
        Write-Host $Line
    }

    if ($ExitCode -ne 0) {
        throw "Runner exited with code $ExitCode."
    }

    return $Output
}

function Get-RunnerState {
    param([object[]]$Output)

    $StateLine = @(
        $Output |
            ForEach-Object { "$_" } |
            Where-Object { $_ -match "^STATE=" }
    ) | Select-Object -Last 1

    if ($null -eq $StateLine) {
        return ""
    }

    return (
        "$StateLine" -replace "^STATE=", ""
    ).Trim()
}

function Get-SlotRecords {
    $Plan = Get-Content `
        -Raw `
        -Path $PlanPath |
        ConvertFrom-Json

    Assert-True (
        $Plan.cohort_id -eq $CohortId
    ) "Unexpected cohort ID."

    Assert-True (
        $Plan.slots.Count -eq 30
    ) "Unexpected slot count."

    $TimeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById(
        $ExpectedTimeZone
    )

    $Records = foreach ($Slot in $Plan.slots) {
        $Anchor = [DateTimeOffset]::Parse(
            $Slot.context_anchor_open_utc
        )

        $LocalAnchor = [System.TimeZoneInfo]::ConvertTime(
            $Anchor,
            $TimeZone
        )

        [pscustomobject]@{
            SlotId = "$($Slot.slot_id)"
            AnchorUtc = $Anchor
            LocalAnchor = $LocalAnchor
            LocalDate = $LocalAnchor.Date
            H16MaturityUtc = $Anchor.AddHours(4)
        }
    }

    return @($Records)
}

function Get-NowLocal {
    $TimeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById(
        $ExpectedTimeZone
    )

    return [System.TimeZoneInfo]::ConvertTime(
        [DateTimeOffset]::UtcNow,
        $TimeZone
    )
}

function Get-TodaysSlot {
    $NowLocal = Get-NowLocal
    $Matches = @(
        Get-SlotRecords |
            Where-Object {
                $_.LocalDate -eq $NowLocal.Date
            }
    )

    if ($Matches.Count -eq 0) {
        return $null
    }

    Assert-True (
        $Matches.Count -eq 1
    ) "More than one slot resolved for local date."

    return $Matches[0]
}

function Write-AtomicAttemptMarker {
    param(
        [string]$Path,
        [hashtable]$Document
    )

    $Payload = (
        $Document |
        ConvertTo-Json -Compress -Depth 10
    ) + "`n"

    $Bytes = [System.Text.UTF8Encoding]::new(
        $false
    ).GetBytes($Payload)

    $Stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )

    try {
        $Stream.Write($Bytes, 0, $Bytes.Length)
        $Stream.Flush($true)
    }
    finally {
        $Stream.Dispose()
    }
}

function Invoke-SelfCheck {
    Assert-CoreArtifacts

    $TimeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById(
        $ExpectedTimeZone
    )

    Assert-True (
        $TimeZone.Id -eq $ExpectedTimeZone
    ) "Unexpected Windows time zone."

    $Slots = @(Get-SlotRecords)

    for ($Index = 1; $Index -lt $Slots.Count; $Index++) {
        $Spacing = (
            $Slots[$Index].AnchorUtc -
            $Slots[$Index - 1].AnchorUtc
        )

        Assert-True (
            $Spacing.TotalHours -eq 24
        ) "Slot spacing is not 24 hours."
    }

    Write-Host "MODE=SELFCHECK"
    Write-Host "REAL_NETWORK_REQUEST_ALLOWED=False"
    Write-Host "REAL_COHORT_MODIFICATION_ALLOWED=False"
    Write-Host "CONTEXT_HUMAN_ATTESTATION_REQUIRED=True"
    Write-Host "BINDING_HUMAN_ATTESTATION_REQUIRED=False"
    Write-Host "BINDING_MAXIMUM_REAL_ATTEMPTS_PER_INVOCATION=1"
    Write-Host "BINDING_AUTOMATIC_RETRY_AFTER_NETWORK_PHASE=False"
    Write-Host "BINDING_ATTEMPT_MARKER_CREATE_ONLY=True"
    Write-Host "PLAN_SLOT_COUNT=30"
    Write-Host "ALL_29_INTERVALS_EQUAL_24_HOURS=True"
    Write-Host "WINDOWS_TIME_ZONE_VERIFIED=True"
    Write-Host "FROZEN_CORE_HASHES_VERIFIED=True"
    Write-Host "SELF_CHECK_PASSED=True"
}

function Invoke-Preflight {
    $Slot = Get-TodaysSlot

    if ($null -eq $Slot) {
        Write-Host "NO_SLOT_PLANNED_FOR_LOCAL_DATE=True"
        return
    }

    Write-Host "PREFLIGHT_SLOT_ID=$($Slot.SlotId)"

    $StatusOutput = Invoke-Runner @(
        "--status",
        "--slot", $Slot.SlotId,
        "--repo", $RepoPath
    )

    $State = Get-RunnerState $StatusOutput
    Write-Host "PREFLIGHT_INITIAL_STATE=$State"

    if ($State -ne "PLANNED") {
        Write-Host "PREFLIGHT_NO_ACTION_REQUIRED=True"
        return
    }

    $null = Invoke-Runner @(
        "--offline-validate-context",
        "--slot", $Slot.SlotId,
        "--repo", $RepoPath
    )

    Write-Host "PREFLIGHT_OFFLINE_CONTEXT_VALIDATION_PASSED=True"
    Write-Host "REAL_NETWORK_REQUEST_EXECUTED=False"
}

function Invoke-Context {
    $Slot = Get-TodaysSlot

    if ($null -eq $Slot) {
        Write-Host "NO_SLOT_PLANNED_FOR_LOCAL_DATE=True"
        return
    }

    Write-Host "CONTEXT_SLOT_ID=$($Slot.SlotId)"

    $StatusOutput = Invoke-Runner @(
        "--status",
        "--slot", $Slot.SlotId,
        "--repo", $RepoPath
    )

    $State = Get-RunnerState $StatusOutput
    Write-Host "CONTEXT_INITIAL_STATE=$State"

    if ($State -ne "PLANNED") {
        Write-Host "CONTEXT_CAPTURE_NOT_STARTED=True"
        Write-Host "CONTEXT_REASON=SLOT_NOT_PLANNED"
        return
    }

    $null = Invoke-Runner @(
        "--offline-validate-context",
        "--slot", $Slot.SlotId,
        "--repo", $RepoPath
    )

    Add-Type -AssemblyName System.Windows.Forms

    $Message = @"
Slot $($Slot.SlotId)

Confirme que esta captura utilizará datos reales de mercado desde una fuente pública de solo lectura y que los datos no son sintéticos.

La captura será única y no tendrá reintento automático.

¿Autoriza continuar?
"@

    $Decision = [System.Windows.Forms.MessageBox]::Show(
        $Message,
        "Trading AI V4 - Confirmación humana",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Warning,
        [System.Windows.Forms.MessageBoxDefaultButton]::Button2
    )

    if (
        $Decision -ne
        [System.Windows.Forms.DialogResult]::Yes
    ) {
        Write-Host "HUMAN_ATTESTATION_CONFIRMED=False"
        Write-Host "REAL_CONTEXT_CAPTURE_EXECUTED=False"
        return
    }

    Write-Host "HUMAN_ATTESTATION_CONFIRMED=True"

    $null = Invoke-Runner @(
        "--execute-context",
        "--slot", $Slot.SlotId,
        "--source-attestation", $SourceAttestation,
        "--repo", $RepoPath
    )

    Write-Host "REAL_CONTEXT_CAPTURE_EXECUTED=True"
    Write-Host "CONTEXT_AUTOMATIC_RETRY_EXECUTED=False"
}

function Invoke-Binding {
    New-Item `
        -ItemType Directory `
        -Path $AttemptRoot `
        -Force |
        Out-Null

    $NowUtc = [DateTimeOffset]::UtcNow

    $Candidates = @(
        Get-SlotRecords |
            Where-Object {
                $_.H16MaturityUtc -le $NowUtc
            } |
            Sort-Object AnchorUtc
    )

    foreach ($Slot in $Candidates) {
        $StatusOutput = Invoke-Runner @(
            "--status",
            "--slot", $Slot.SlotId,
            "--repo", $RepoPath
        )

        $State = Get-RunnerState $StatusOutput

        if ($State -ne "ADMITTED_OUTCOME_NOT_BOUND") {
            continue
        }

        $AttemptPath = Join-Path `
            $AttemptRoot `
            "$($Slot.SlotId).attempted.json"

        if (Test-Path $AttemptPath) {
            Write-Host "BINDING_RETRY_SUPPRESSED[$($Slot.SlotId)]=True"
            continue
        }

        Write-Host "BINDING_SELECTED_SLOT=$($Slot.SlotId)"

        $null = Invoke-Runner @(
            "--offline-validate-binding",
            "--slot", $Slot.SlotId,
            "--repo", $RepoPath
        )

        Write-AtomicAttemptMarker `
            -Path $AttemptPath `
            -Document @{
                schema_version = "TRADING_AI_V4_BINDING_ATTEMPT_V1"
                cohort_id = $CohortId
                slot_id = $Slot.SlotId
                attempt_started_utc = [DateTimeOffset]::UtcNow.ToString("o")
                automatic_retry_permitted = $false
                maximum_real_attempts_this_invocation = 1
            }

        Write-Host "BINDING_ATTEMPT_MARKER_CREATED=True"

        $BindingSucceeded = $false

        try {
            $null = Invoke-Runner @(
                "--bind-outcomes",
                "--slot", $Slot.SlotId,
                "--repo", $RepoPath
            )

            $BindingSucceeded = $true
        }
        finally {
            $ResultPath = Join-Path `
                $AttemptRoot `
                "$($Slot.SlotId).result.json"

            $Result = @{
                schema_version = "TRADING_AI_V4_BINDING_RESULT_V1"
                cohort_id = $CohortId
                slot_id = $Slot.SlotId
                result_recorded_utc = [DateTimeOffset]::UtcNow.ToString("o")
                binding_succeeded = $BindingSucceeded
                automatic_retry_executed = $false
            }

            [System.IO.File]::WriteAllText(
                $ResultPath,
                (
                    $Result |
                    ConvertTo-Json -Compress -Depth 10
                ) + "`n",
                [System.Text.UTF8Encoding]::new($false)
            )
        }

        Write-Host "BINDING_SUCCEEDED=$BindingSucceeded"
        Write-Host "BINDING_AUTOMATIC_RETRY_EXECUTED=False"
        Write-Host "BINDING_REAL_ATTEMPT_COUNT=1"
        return
    }

    Write-Host "NO_ELIGIBLE_UNATTEMPTED_BINDING_SLOT=True"
    Write-Host "REAL_NETWORK_REQUEST_EXECUTED=False"
}

function Invoke-Audit {
    $null = Invoke-Runner @(
        "--status",
        "--repo", $RepoPath
    )

    $AttemptCount = 0
    $ResultCount = 0

    if (Test-Path $AttemptRoot) {
        $AttemptCount = @(
            Get-ChildItem `
                -Path $AttemptRoot `
                -Filter "*.attempted.json" `
                -File
        ).Count

        $ResultCount = @(
            Get-ChildItem `
                -Path $AttemptRoot `
                -Filter "*.result.json" `
                -File
        ).Count
    }

    Write-Host "BINDING_ATTEMPT_MARKER_COUNT=$AttemptCount"
    Write-Host "BINDING_RESULT_MARKER_COUNT=$ResultCount"
    Write-Host "AUDIT_REAL_NETWORK_REQUEST_EXECUTED=False"
}

New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

$Timestamp = [DateTimeOffset]::UtcNow.ToString(
    "yyyyMMddTHHmmssfffZ"
)

$LogFile = Join-Path `
    $LogRoot `
    "$($Mode.ToLowerInvariant())_$Timestamp.log"

$MutexName = "Global\TradingAI_V4_DailyEvening30"
$Mutex = [System.Threading.Mutex]::new(
    $false,
    $MutexName
)

$MutexAcquired = $false
$TranscriptStarted = $false

try {
    $MutexAcquired = $Mutex.WaitOne(0)

    if (-not $MutexAcquired) {
        Write-Host "TASK_OVERLAP_SUPPRESSED=True"
        exit 75
    }

    Start-Transcript `
        -Path $LogFile `
        -NoClobber |
        Out-Null

    $TranscriptStarted = $true

    Write-Host "=== TRADING AI V4 WINDOWS TASK WRAPPER ==="
    Write-Host "MODE=$Mode"
    Write-Host "COHORT_ID=$CohortId"
    Write-Host "STARTED_UTC=$([DateTimeOffset]::UtcNow.ToString('o'))"
    Write-Host "LOG_FILE=$LogFile"

    Assert-CoreArtifacts

    if ($Mode -ne "SelfCheck") {
        Assert-OperationalRepository
    }

    switch ($Mode) {
        "SelfCheck" {
            Invoke-SelfCheck
        }

        "Preflight" {
            Invoke-Preflight
        }

        "Context" {
            Invoke-Context
        }

        "Binding" {
            Invoke-Binding
        }

        "Audit" {
            Invoke-Audit
        }
    }

    Write-Host "TASK_WRAPPER_STATUS=PASSED"
    Write-Host "FINISHED_UTC=$([DateTimeOffset]::UtcNow.ToString('o'))"
}
catch {
    Write-Host "TASK_WRAPPER_STATUS=FAILED"
    Write-Host "ERROR_TYPE=$($_.Exception.GetType().FullName)"
    Write-Host "ERROR_MESSAGE=$($_.Exception.Message)"
    Write-Host "AUTOMATIC_RETRY_EXECUTED=False"
    Write-Host "NO_RESET_NO_FORCE_NO_AMEND=True"
    throw
}
finally {
    if ($TranscriptStarted) {
        Stop-Transcript | Out-Null
    }

    if ($MutexAcquired) {
        $Mutex.ReleaseMutex()
    }

    $Mutex.Dispose()
}
