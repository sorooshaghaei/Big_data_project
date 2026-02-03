# Get the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = Join-Path $ScriptDir "datasets"
$KaggleSlug = "gatandubuc/public-transport-traffic-data-in-france"

# Create directory
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Write-Host "--- Step 1: Downloading IDFM dataset ---"

# Stable API export link (v2.1)
$IdfmApiUrl = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/exports/csv?use_labels=true&csv_separator=%3B"
$IdfmOutput = Join-Path $TargetDir "idfm_validations_surface.csv"

Invoke-WebRequest -Uri $IdfmApiUrl -OutFile $IdfmOutput

Write-Host "--- Step 2: Downloading Kaggle dataset ---"

# Download via Kaggle CLI (must already be installed and configured)
kaggle datasets download -d $KaggleSlug -p $TargetDir

Write-Host "--- Step 3: Unpacking and Filtering Kaggle Files ---"

$KaggleZip = Join-Path $TargetDir "public-transport-traffic-data-in-france.zip"
$TempKaggleDir = Join-Path $TargetDir "temp_kaggle"

if (Test-Path $KaggleZip) {

    # Create temp folder
    New-Item -ItemType Directory -Force -Path $TempKaggleDir | Out-Null

    # Extract zip
    Expand-Archive -Path $KaggleZip -DestinationPath $TempKaggleDir -Force

    # Move only requested files
    Move-Item -Path (Join-Path $TempKaggleDir "Travel_titles_validations_in_Paris_and_suburbs.csv") -Destination $TargetDir -Force
    Move-Item -Path (Join-Path $TempKaggleDir "Regularities_by_liaisons_Trains_France.csv") -Destination $TargetDir -Force

    # Cleanup
    Remove-Item $KaggleZip -Force
    Remove-Item $TempKaggleDir -Recurse -Force

    Write-Host "Successfully extracted and filtered Kaggle files."
}
else {
    Write-Host "❌ Error: Kaggle zip file not found."
}

Write-Host "--- Step 4: Generating citations.txt ---"

$CitationsPath = Join-Path $TargetDir "citations.txt"

@"
Dataset 1: Validations sur le réseau de surface (1er trimestre)
Link: https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/

Dataset 2: Public transport traffic data in France
Link: https://www.kaggle.com/datasets/gatandubuc/public-transport-traffic-data-in-france
"@ | Out-File -FilePath $CitationsPath -Encoding UTF8

Write-Host "✅ Done! Your files are ready in: $TargetDir"

Get-ChildItem $TargetDir | Format-Table Name, Length, LastWriteTime
