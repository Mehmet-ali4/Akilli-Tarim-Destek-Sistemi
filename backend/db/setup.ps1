param(
    [string]$DbName = "akilli_tarim",
    [string]$DbUser = "postgres",
    [string]$ServerHost = "localhost",
    [int]$Port = 5432
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$SchemaFile = Join-Path $PSScriptRoot "schema_postgresql.sql"

Write-Host "Veritabani olusturuluyor: $DbName"
psql -U $DbUser -h $Host -p $Port -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DbName'" | Out-Null
$dbExists = psql -U $DbUser -h $ServerHost -p $Port -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DbName'"

if ($dbExists -ne "1") {
    psql -U $DbUser -h $ServerHost -p $Port -d postgres -c "CREATE DATABASE $DbName"
    Write-Host "Veritabani olusturuldu."
} else {
    Write-Host "Veritabani zaten mevcut."
}

Write-Host "Semalar uygulaniyor..."
psql -U $DbUser -h $ServerHost -p $Port -d $DbName -f $SchemaFile

Write-Host "Tablolar:"
psql -U $DbUser -h $ServerHost -p $Port -d $DbName -c "\dt"

Write-Host "Tamamlandi."
