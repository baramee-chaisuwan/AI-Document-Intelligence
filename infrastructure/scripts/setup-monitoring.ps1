[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z][a-z0-9-]{4,28}[a-z0-9]$')]
    [string]$ProjectId,

    [switch]$Apply,

    [string]$ConfirmProjectId,

    [ValidatePattern('^projects/[^/]+/notificationChannels/[^/]+$')]
    [string]$NotificationChannel
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$metrics = @(
    [ordered]@{
        Name = 'ats_worker_request_failures'
        Description = 'Authenticated Pub/Sub worker requests that failed and requested retry.'
        Filter = 'resource.type="cloud_run_revision" AND resource.labels.service_name="ats-worker" AND jsonPayload.event="pubsub_worker_request_failed"'
        DisplayName = 'ATS - Worker request failures'
        WindowSeconds = 600
        Threshold = 2
        ThresholdText = '3 or more failures in 10 minutes'
    },
    [ordered]@{
        Name = 'ats_pubsub_publication_failures'
        Description = 'Resume-processing Pub/Sub publication failures emitted by the API.'
        Filter = 'resource.type="cloud_run_revision" AND resource.labels.service_name="ats-api" AND jsonPayload.event="async_resume_submission_failed" AND jsonPayload.operation="pubsub_resume_publication"'
        DisplayName = 'ATS - Pub/Sub publication failures'
        WindowSeconds = 600
        Threshold = 1
        ThresholdText = '2 or more failures in 10 minutes'
    },
    [ordered]@{
        Name = 'ats_rag_gemini_failures'
        Description = 'Failures in verified RAG retrieval/generation and Gemini operations.'
        Filter = 'resource.type="cloud_run_revision" AND jsonPayload.event="operation_failed" AND jsonPayload.operation=~"^(rag_retrieval|rag_answer_generation|gemini_resume_analysis|gemini_resume_extraction|gemini_resume_summarization|gemini_job_requirement_extraction)$"'
        DisplayName = 'ATS - RAG or Gemini failures'
        WindowSeconds = 600
        Threshold = 2
        ThresholdText = '3 or more failures in 10 minutes'
    },
    [ordered]@{
        Name = 'ats_high_api_latency'
        Description = 'API requests whose structured duration is at least 2500 milliseconds.'
        Filter = 'resource.type="cloud_run_revision" AND resource.labels.service_name="ats-api" AND jsonPayload.event="http_request" AND jsonPayload.duration_ms>=2500'
        DisplayName = 'ATS - High API request latency'
        WindowSeconds = 300
        Threshold = 9
        ThresholdText = '10 or more requests at or above 2500 ms in 5 minutes'
    },
    [ordered]@{
        Name = 'ats_resume_processing_failures'
        Description = 'Resume jobs that failed during worker processing.'
        Filter = 'resource.type="cloud_run_revision" AND resource.labels.service_name="ats-worker" AND jsonPayload.event="resume_worker_failed"'
        DisplayName = 'ATS - Resume processing failures'
        WindowSeconds = 300
        Threshold = 0
        ThresholdText = '1 or more failures in 5 minutes'
    }
)

function New-AlertPolicy {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Metric
    )

    $policy = [ordered]@{
        displayName = $Metric.DisplayName
        combiner = 'OR'
        enabled = $true
        userLabels = [ordered]@{
            project = 'ats'
            managed_by = 'repository_script'
        }
        documentation = [ordered]@{
            content = "Signal: $($Metric.Description) Threshold: $($Metric.ThresholdText). Review Cloud Run structured logs before retrying or changing production resources."
            mimeType = 'text/markdown'
        }
        conditions = @(
            [ordered]@{
                displayName = $Metric.ThresholdText
                conditionThreshold = [ordered]@{
                    filter = "resource.type = `"cloud_run_revision`" AND metric.type = `"logging.googleapis.com/user/$($Metric.Name)`""
                    aggregations = @(
                        [ordered]@{
                            alignmentPeriod = "$($Metric.WindowSeconds)s"
                            perSeriesAligner = 'ALIGN_SUM'
                            crossSeriesReducer = 'REDUCE_SUM'
                        }
                    )
                    comparison = 'COMPARISON_GT'
                    thresholdValue = $Metric.Threshold
                    duration = '0s'
                    trigger = [ordered]@{
                        count = 1
                    }
                }
            }
        )
        alertStrategy = [ordered]@{
            autoClose = '1800s'
        }
    }

    if ($NotificationChannel) {
        $policy['notificationChannels'] = @(
            $NotificationChannel
        )
    }

    return $policy
}

Write-Output "ATS monitoring configuration for project: $ProjectId"
Write-Output "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY RUN' })"

foreach ($metric in $metrics) {
    Write-Output ''
    Write-Output "Metric: $($metric.Name)"
    Write-Output "Filter: $($metric.Filter)"
    Write-Output "Alert: $($metric.ThresholdText)"
}

if (-not $Apply) {
    Write-Output ''
    Write-Output 'No gcloud commands were executed.'
    Write-Output 'Review the definitions, then rerun with -Apply and -ConfirmProjectId matching -ProjectId.'
    return
}

if ($ConfirmProjectId -cne $ProjectId) {
    throw 'Apply blocked: -ConfirmProjectId must exactly match -ProjectId.'
}

$gcloud = if ($env:OS -eq 'Windows_NT') {
    'gcloud.cmd'
} else {
    'gcloud'
}
if (-not (Get-Command $gcloud -ErrorAction SilentlyContinue)) {
    throw "Apply blocked: $gcloud was not found."
}

$temporaryDirectory = Join-Path (
    [System.IO.Path]::GetTempPath()
) ("ats-monitoring-" + [guid]::NewGuid().ToString('N'))

New-Item -ItemType Directory -Path $temporaryDirectory | Out-Null

try {
    foreach ($metric in $metrics) {
        & $gcloud logging metrics create $metric.Name `
            "--project=$ProjectId" `
            "--description=$($metric.Description)" `
            "--log-filter=$($metric.Filter)" `
            --quiet

        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create log-based metric: $($metric.Name)"
        }
    }

    foreach ($metric in $metrics) {
        $policyPath = Join-Path (
            $temporaryDirectory
        ) "$($metric.Name).json"

        New-AlertPolicy -Metric $metric |
            ConvertTo-Json -Depth 12 |
            Set-Content -LiteralPath $policyPath -Encoding utf8

        & $gcloud monitoring policies create `
            "--project=$ProjectId" `
            "--policy-from-file=$policyPath" `
            --quiet

        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create alert policy: $($metric.DisplayName)"
        }
    }
}
finally {
    if (Test-Path -LiteralPath $temporaryDirectory) {
        Remove-Item -LiteralPath $temporaryDirectory -Recurse -Force
    }
}

Write-Output 'Monitoring metrics and alert policies were created successfully.'
