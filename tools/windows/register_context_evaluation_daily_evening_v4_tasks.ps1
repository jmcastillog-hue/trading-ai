[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("SelfCheck", "Install", "Verify")]
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

$PowerShellPath = `
    "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

$WrapperPath = Join-Path $RepoPath `
    "tools\windows\context_evaluation_daily_evening_v4_task.ps1"

$ExpectedWrapperHash = `
    "e4f223bb57f64588171e5f61f57d8421c095efc08a17c8853eec429178d4b1b8"

$TaskNames = [ordered]@{
    Preflight = "TradingAI-V4-Preflight"
    Context   = "TradingAI-V4-Context"
    Binding   = "TradingAI-V4-Binding"
    Audit     = "TradingAI-V4-Audit"
}

$TaskStartLocal = [ordered]@{
    Preflight = "2026-10-14 18:45:00"
    Context   = "2026-10-14 19:00:05"
    Binding   = "2026-10-14 23:32:00"
    Audit     = "2026-10-14 23:45:00"
}

$TaskEndLocal = "2026-11-13 00:00:00"

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

function Get-TimeZoneContract {
    $TimeZone = [System.TimeZoneInfo]::FindSystemTimeZoneById(
        $ExpectedTimeZone
    )

    Assert-True (
        (Get-TimeZone).Id -eq $ExpectedTimeZone
    ) "Active Windows time zone is unexpected."

    return $TimeZone
}

function Assert-BaseFiles {
    Assert-True (Test-Path $RepoPath) "Repository not found."
    Assert-True (Test-Path $PowerShellPath) "PowerShell not found."
    Assert-True (Test-Path $WrapperPath) "V4 wrapper not found."

    $WrapperHash = Get-LowerHash $WrapperPath

    Assert-True (
        $WrapperHash -eq $ExpectedWrapperHash
    ) "V4 wrapper hash mismatch."
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
        ) "Unable to inspect repository state."

        Assert-True (
            $Branch -eq "main"
        ) "Task installation and verification require main."

        Assert-True (
            $Head -eq $Main -and
            $Head -eq $OriginMain
        ) "HEAD, main and origin/main must match."

        git merge-base --is-ancestor $ExpectedCoreCommit $Head

        Assert-True (
            $LASTEXITCODE -eq 0
        ) "V4 core commit is not an ancestor of HEAD."

        $Status = @(
            git status --porcelain=v1 --untracked-files=all
        )

        Assert-True (
            $Status.Count -eq 0
        ) "Task installation requires a clean worktree."
    }
    finally {
        Pop-Location
    }
}

function Convert-LocalTextToUtc {
    param([string]$LocalText)

    $TimeZone = Get-TimeZoneContract

    $LocalDateTime = [datetime]::ParseExact(
        $LocalText,
        "yyyy-MM-dd HH:mm:ss",
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::None
    )

    return [System.TimeZoneInfo]::ConvertTimeToUtc(
        $LocalDateTime,
        $TimeZone
    )
}

function New-V4TaskTrigger {
    param([string]$TaskMode)

    Assert-True (
        $TaskStartLocal.Contains($TaskMode)
    ) "Unknown task mode: $TaskMode"

    $LocalStart = [datetime]::ParseExact(
        $TaskStartLocal[$TaskMode],
        "yyyy-MM-dd HH:mm:ss",
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::None
    )

    $Trigger = New-ScheduledTaskTrigger `
        -Daily `
        -At $LocalStart

    $EndUtc = Convert-LocalTextToUtc $TaskEndLocal

    $Trigger.EndBoundary = $EndUtc.ToString(
        "yyyy-MM-ddTHH:mm:ss'Z'",
        [System.Globalization.CultureInfo]::InvariantCulture
    )

    return $Trigger
}

function New-V4TaskAction {
    param([string]$TaskMode)

    $WindowStyle = if ($TaskMode -eq "Context") {
        "Normal"
    }
    else {
        "Hidden"
    }

    $Arguments = (
        '-NoLogo -NoProfile -ExecutionPolicy Bypass ' +
        '-WindowStyle {0} ' +
        '-File "{1}" ' +
        '-Mode {2} ' +
        '-RepoPath "{3}"'
    ) -f (
        $WindowStyle,
        $WrapperPath,
        $TaskMode,
        $RepoPath
    )

    return New-ScheduledTaskAction `
        -Execute $PowerShellPath `
        -Argument $Arguments `
        -WorkingDirectory $RepoPath
}

function New-V4TaskSettings {
    param([string]$TaskMode)

    switch ($TaskMode) {
        "Preflight" {
            return New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -MultipleInstances IgnoreNew `
                -ExecutionTimeLimit (
                    [timespan]::FromMinutes(20)
                )
        }

        "Context" {
            return New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -WakeToRun `
                -MultipleInstances IgnoreNew `
                -ExecutionTimeLimit (
                    [timespan]::FromMinutes(30)
                )
        }

        "Binding" {
            return New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -WakeToRun `
                -StartWhenAvailable `
                -RunOnlyIfNetworkAvailable `
                -MultipleInstances IgnoreNew `
                -ExecutionTimeLimit (
                    [timespan]::FromMinutes(20)
                )
        }

        "Audit" {
            return New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -MultipleInstances IgnoreNew `
                -ExecutionTimeLimit (
                    [timespan]::FromMinutes(15)
                )
        }

        default {
            throw "Unknown task mode: $TaskMode"
        }
    }
}

function New-V4TaskPrincipal {
    param(
        [string]$TaskMode,
        [string]$UserId
    )

    if (
        $TaskMode -eq "Preflight" -or
        $TaskMode -eq "Context"
    ) {
        return New-ScheduledTaskPrincipal `
            -UserId $UserId `
            -LogonType Interactive `
            -RunLevel Limited
    }

    return New-ScheduledTaskPrincipal `
        -UserId $UserId `
        -LogonType Password `
        -RunLevel Limited
}

function New-V4TaskDefinition {
    param(
        [string]$TaskMode,
        [string]$UserId
    )

    $Action = New-V4TaskAction $TaskMode
    $Trigger = New-V4TaskTrigger $TaskMode
    $Settings = New-V4TaskSettings $TaskMode
    $Principal = New-V4TaskPrincipal $TaskMode $UserId

    $Description = (
        "Trading AI V4 daily evening cohort - " +
        "$TaskMode - $CohortId"
    )

    return New-ScheduledTask `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description $Description
}

function Get-ExistingV4Tasks {
    return @(
        Get-ScheduledTask -ErrorAction Stop |
            Where-Object {
                $_.TaskName -like "TradingAI-V4-*"
            } |
            Sort-Object TaskName
    )
}

function Assert-Definition {
    param(
        [string]$TaskMode,
        [object]$Definition,
        [string]$UserId
    )

    $Action = @($Definition.Actions)[0]
    $Trigger = @($Definition.Triggers)[0]
    $Settings = $Definition.Settings
    $Principal = $Definition.Principal

    Assert-True (
        $Action.Execute -eq $PowerShellPath
    ) "Unexpected executable for $TaskMode."

    Assert-True (
        $Action.Arguments.Contains("-Mode $TaskMode")
    ) "Action mode mismatch for $TaskMode."

    Assert-True (
        $Action.Arguments.Contains($WrapperPath)
    ) "Wrapper path missing for $TaskMode."

    Assert-True (
        $Action.WorkingDirectory -eq $RepoPath
    ) "Working directory mismatch for $TaskMode."

    $ExpectedStartUtc = Convert-LocalTextToUtc(
        $TaskStartLocal[$TaskMode]
    )

    $ActualStart = [DateTimeOffset]::Parse(
        $Trigger.StartBoundary,
        [System.Globalization.CultureInfo]::InvariantCulture
    ).ToUniversalTime()

    Assert-True (
        $ActualStart.UtcDateTime -eq $ExpectedStartUtc
    ) "StartBoundary mismatch for $TaskMode."

    $ExpectedEndUtc = Convert-LocalTextToUtc $TaskEndLocal

    $ActualEnd = [DateTimeOffset]::Parse(
        $Trigger.EndBoundary,
        [System.Globalization.CultureInfo]::InvariantCulture
    ).ToUniversalTime()

    Assert-True (
        $ActualEnd.UtcDateTime -eq $ExpectedEndUtc
    ) "EndBoundary mismatch for $TaskMode."

    Assert-True (
        "$($Settings.MultipleInstances)" -eq "IgnoreNew"
    ) "MultipleInstances mismatch for $TaskMode."

    Assert-True (
        $Settings.RestartCount -eq 0
    ) "Automatic restart is enabled for $TaskMode."

    Assert-True (
        $Principal.UserId -eq $UserId
    ) "Principal user mismatch for $TaskMode."

    if ($TaskMode -eq "Context") {
        Assert-True $Settings.WakeToRun `
            "Context must wake the computer."

        Assert-True (-not $Settings.StartWhenAvailable) `
            "Context must not run late."

        Assert-True (
            "$($Principal.LogonType)" -match "Interactive"
        ) "Context must require an interactive user."

        Assert-True (
            $Action.Arguments.Contains("-WindowStyle Normal")
        ) "Context must use a normal window."
    }

    if ($TaskMode -eq "Preflight") {
        Assert-True (-not $Settings.StartWhenAvailable) `
            "Preflight must not run late."

        Assert-True (
            "$($Principal.LogonType)" -match "Interactive"
        ) "Preflight must use an interactive token."
    }

    if ($TaskMode -eq "Binding") {
        Assert-True $Settings.WakeToRun `
            "Binding must wake the computer."

        Assert-True $Settings.StartWhenAvailable `
            "Binding must support scheduled catch-up."

        Assert-True $Settings.RunOnlyIfNetworkAvailable `
            "Binding must require network availability."

        Assert-True (
            "$($Principal.LogonType)" -match "Password"
        ) "Binding must support logged-off execution."
    }

    if ($TaskMode -eq "Audit") {
        Assert-True (-not $Settings.StartWhenAvailable) `
            "Audit must not run late."

        Assert-True (
            "$($Principal.LogonType)" -match "Password"
        ) "Audit must support logged-off execution."
    }
}

function Invoke-SelfCheck {
    Assert-BaseFiles

    $CurrentUser = (
        [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    )

    $Definitions = @{}

    foreach ($TaskMode in $TaskNames.Keys) {
        $Definition = New-V4TaskDefinition `
            -TaskMode $TaskMode `
            -UserId $CurrentUser

        Assert-Definition `
            -TaskMode $TaskMode `
            -Definition $Definition `
            -UserId $CurrentUser

        $Definitions[$TaskMode] = $Definition

        $Trigger = @($Definition.Triggers)[0]

        Write-Host "TASK[$TaskMode]_NAME=$($TaskNames[$TaskMode])"
        Write-Host "TASK[$TaskMode]_START_BOUNDARY=$($Trigger.StartBoundary)"
        Write-Host "TASK[$TaskMode]_END_BOUNDARY=$($Trigger.EndBoundary)"
        Write-Host "TASK[$TaskMode]_LOGON_TYPE=$($Definition.Principal.LogonType)"
        Write-Host "TASK[$TaskMode]_WAKE_TO_RUN=$($Definition.Settings.WakeToRun)"
        Write-Host "TASK[$TaskMode]_START_WHEN_AVAILABLE=$($Definition.Settings.StartWhenAvailable)"
        Write-Host "TASK[$TaskMode]_RESTART_COUNT=$($Definition.Settings.RestartCount)"
    }

    $ExistingTasks = @(Get-ExistingV4Tasks)

    Assert-True (
        $ExistingTasks.Count -eq 0
    ) "V4 scheduled tasks already exist."

    Write-Host "MODE=SELFCHECK"
    Write-Host "TASK_DEFINITION_COUNT=$($Definitions.Count)"
    Write-Host "EXISTING_V4_TASK_COUNT=0"
    Write-Host "CREDENTIAL_REQUESTED=False"
    Write-Host "PASSWORD_READ=False"
    Write-Host "PASSWORD_STORED_IN_REPOSITORY=False"
    Write-Host "SCHEDULED_TASKS_CREATED=False"
    Write-Host "REAL_NETWORK_CAPTURE_EXECUTED=False"
    Write-Host "REAL_MARKET_DATA_FETCHED=False"
    Write-Host "ALL_TASK_DEFINITIONS_VALID=True"
    Write-Host "SELF_CHECK_PASSED=True"
}

function Invoke-Verify {
    Assert-BaseFiles
    Assert-OperationalRepository

    $CurrentUser = (
        [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    )

    $ExistingTasks = @(Get-ExistingV4Tasks)

    Assert-True (
        $ExistingTasks.Count -eq 4
    ) "Expected exactly four V4 scheduled tasks."

    $ActualNames = @(
        $ExistingTasks |
            ForEach-Object { $_.TaskName } |
            Sort-Object
    )

    $ExpectedNames = @(
        $TaskNames.Values |
            Sort-Object
    )

    $Difference = @(
        Compare-Object $ExpectedNames $ActualNames
    )

    Assert-True (
        $Difference.Count -eq 0
    ) "Unexpected V4 task inventory."

    foreach ($TaskMode in $TaskNames.Keys) {
        $TaskName = $TaskNames[$TaskMode]

        $Task = Get-ScheduledTask `
            -TaskName $TaskName `
            -ErrorAction Stop

        $ExpectedDefinition = New-V4TaskDefinition `
            -TaskMode $TaskMode `
            -UserId $CurrentUser

        Assert-Definition `
            -TaskMode $TaskMode `
            -Definition $Task `
            -UserId $CurrentUser

        $Info = Get-ScheduledTaskInfo `
            -TaskName $TaskName `
            -ErrorAction Stop

        Write-Host "TASK[$TaskMode]_NAME=$TaskName"
        Write-Host "TASK[$TaskMode]_STATE=$($Task.State)"
        Write-Host "TASK[$TaskMode]_ENABLED=$($Task.Settings.Enabled)"
        Write-Host "TASK[$TaskMode]_NEXT_RUN_TIME=$($Info.NextRunTime)"
        Write-Host "TASK[$TaskMode]_LAST_RUN_TIME=$($Info.LastRunTime)"
        Write-Host "TASK[$TaskMode]_LAST_TASK_RESULT=$($Info.LastTaskResult)"

        Assert-True (
            $Task.Settings.Enabled
        ) "Task is disabled: $TaskName"

        Assert-True (
            $Task.State -ne "Running"
        ) "Task unexpectedly running: $TaskName"
    }

    Write-Host "TASK_INVENTORY_VERIFIED=True"
    Write-Host "TASK_ACTIONS_VERIFIED=True"
    Write-Host "TASK_TRIGGERS_VERIFIED=True"
    Write-Host "TASK_SETTINGS_VERIFIED=True"
    Write-Host "TASK_PRINCIPALS_VERIFIED=True"
    Write-Host "SCHEDULED_TASKS_CREATED=True"
    Write-Host "REAL_NETWORK_CAPTURE_EXECUTED=False"
    Write-Host "REAL_MARKET_DATA_FETCHED=False"
    Write-Host "VERIFY_PASSED=True"
}

function Invoke-Install {
    Assert-BaseFiles
    Assert-OperationalRepository

    $ExistingTasks = @(Get-ExistingV4Tasks)

    Assert-True (
        $ExistingTasks.Count -eq 0
    ) "Installation requires zero existing V4 tasks."

    $CurrentUser = (
        [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    )

    $Definitions = @{}

    foreach ($TaskMode in $TaskNames.Keys) {
        $Definition = New-V4TaskDefinition `
            -TaskMode $TaskMode `
            -UserId $CurrentUser

        Assert-Definition `
            -TaskMode $TaskMode `
            -Definition $Definition `
            -UserId $CurrentUser

        $Definitions[$TaskMode] = $Definition
    }

    Write-Host "CREDENTIAL_PROMPT_REQUIRED=True"
    Write-Host "CREDENTIAL_PURPOSE=BINDING_AND_AUDIT_LOGGED_OFF_EXECUTION"
    Write-Host "CREDENTIAL_WILL_NOT_BE_PRINTED_OR_SAVED_IN_REPOSITORY=True"

    $Credential = Get-Credential `
        -UserName $CurrentUser `
        -Message (
            "Ingrese la contraseña de Windows para registrar " +
            "Binding y Audit cuando la sesión esté cerrada."
        )

    Assert-True (
        $null -ne $Credential
    ) "Credential entry was cancelled."

    Assert-True (
        $Credential.UserName.Equals(
            $CurrentUser,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    ) "Credential user does not match the current Windows user."

    $Bstr = [IntPtr]::Zero
    $PlainPassword = $null
    $CreatedTasks = [System.Collections.Generic.List[string]]::new()

    try {
        $Bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR(
            $Credential.Password
        )

        $PlainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR(
            $Bstr
        )

        Assert-True (
            -not [string]::IsNullOrEmpty($PlainPassword)
        ) "An empty password cannot register background tasks."

        foreach ($TaskMode in $TaskNames.Keys) {
            $TaskName = $TaskNames[$TaskMode]
            $Definition = $Definitions[$TaskMode]

            if (
                $TaskMode -eq "Binding" -or
                $TaskMode -eq "Audit"
            ) {
                Register-ScheduledTask `
                    -TaskName $TaskName `
                    -InputObject $Definition `
                    -User $CurrentUser `
                    -Password $PlainPassword `
                    -ErrorAction Stop |
                    Out-Null
            }
            else {
                Register-ScheduledTask `
                    -TaskName $TaskName `
                    -InputObject $Definition `
                    -ErrorAction Stop |
                    Out-Null
            }

            $CreatedTasks.Add($TaskName)
            Write-Host "TASK_REGISTERED=$TaskName"
        }
    }
    catch {
        Write-Host "TASK_INSTALLATION_FAILED=True"
        Write-Host "ROLLBACK_CREATED_TASK_COUNT=$($CreatedTasks.Count)"

        foreach ($TaskName in $CreatedTasks) {
            $CreatedTask = Get-ScheduledTask `
                -TaskName $TaskName `
                -ErrorAction SilentlyContinue

            if ($null -ne $CreatedTask) {
                Unregister-ScheduledTask `
                    -TaskName $TaskName `
                    -Confirm:$false `
                    -ErrorAction SilentlyContinue

                Write-Host "ROLLED_BACK_TASK=$TaskName"
            }
        }

        throw
    }
    finally {
        if ($Bstr -ne [IntPtr]::Zero) {
            [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR(
                $Bstr
            )
        }

        $PlainPassword = $null
        $Credential = $null
    }

    Write-Host "TASK_INSTALLATION_TRANSACTION_COMPLETED=True"

    Invoke-Verify
}

Write-Host "=== TRADING AI V4 TASK REGISTRATION ==="
Write-Host "MODE=$Mode"
Write-Host "COHORT_ID=$CohortId"
Write-Host "STARTED_UTC=$([DateTimeOffset]::UtcNow.ToString('o'))"

try {
    switch ($Mode) {
        "SelfCheck" {
            Invoke-SelfCheck
        }

        "Install" {
            Invoke-Install
        }

        "Verify" {
            Invoke-Verify
        }
    }

    Write-Host "REGISTRATION_SCRIPT_STATUS=PASSED"
}
catch {
    Write-Host "REGISTRATION_SCRIPT_STATUS=FAILED"
    Write-Host "ERROR_TYPE=$($_.Exception.GetType().FullName)"
    Write-Host "ERROR_MESSAGE=$($_.Exception.Message)"
    Write-Host "NO_RESET_NO_FORCE_NO_AMEND=True"
    throw
}
finally {
    Write-Host "FINISHED_UTC=$([DateTimeOffset]::UtcNow.ToString('o'))"
}
