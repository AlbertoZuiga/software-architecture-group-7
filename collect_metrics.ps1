param(
    [int]$Duration = 300, 
    [int]$Interval = 5      
)

$Output = "metrics.csv"
"timestamp,container,cpu,mem" | Out-File -FilePath $Output -Encoding utf8

$End = (Get-Date).AddSeconds($Duration)

while ((Get-Date) -lt $End) {
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" |
        ForEach-Object { "$timestamp,$_"} | Out-File -FilePath $Output -Append -Encoding utf8
    Start-Sleep -Seconds $Interval
}

Write-Output "Métricas guardadas en $Output"
