# PowerShell script to initialize Python Web Service Boilerplate project
param(
    [string]$ProjectName
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "=== Python Web Service Boilerplate Project Initialization ===" $Blue
Write-Host

# Get the script directory and set as working directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if we're in the right directory
if (-not (Test-Path "src\python_web_service_boilerplate")) {
    Write-ColorOutput "Error: This script must be run from the project root directory." $Red
    Write-ColorOutput "Expected to find 'src\python_web_service_boilerplate' directory." $Red
    exit 1
}

# Get project name if not provided as parameter
if ([string]::IsNullOrEmpty($ProjectName)) {
    Write-ColorOutput "Please enter your desired project name (use snake_case, e.g., 'my_awesome_project'):" $Yellow
    $ProjectName = Read-Host "Project name"
}

# Validate project name
if ([string]::IsNullOrEmpty($ProjectName)) {
    Write-ColorOutput "Error: Project name cannot be empty." $Red
    exit 1
}

# Check if name contains only valid characters (letters, numbers, underscores)
if ($ProjectName -notmatch "^[a-zA-Z][a-zA-Z0-9_]*$") {
    Write-ColorOutput "Error: Project name must start with a letter and contain only letters, numbers, and underscores." $Red
    exit 1
}

Write-Host
Write-ColorOutput "Initializing project with name: $ProjectName" $Blue
Write-Host

# Function to replace text in files
function Replace-InFiles {
    param(
        [string]$OldText,
        [string]$NewText,
        [string]$FilePattern
    )

    Write-ColorOutput "Updating $FilePattern files..." $Yellow

    # Get all files matching the pattern
    $files = Get-ChildItem -Recurse -Include $FilePattern -File |
             Where-Object {
                 $_.FullName -notlike "*\.git\*" -and
                 $_.FullName -notlike "*\build\*" -and
                 $_.FullName -notlike "*\__pycache__\*" -and
                 $_.FullName -notlike "*\data\*"
             }

    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw
            if ($content -match [regex]::Escape($OldText)) {
                $newContent = $content -replace [regex]::Escape($OldText), $NewText
                Set-Content -Path $file.FullName -Value $newContent -NoNewline
                Write-ColorOutput "  Updated: $($file.FullName)" "Gray"
            }
        }
        catch {
            Write-ColorOutput "  Warning: Could not update $($file.FullName): $($_.Exception.Message)" $Yellow
        }
    }
}

# Step 1: Update Python files
Write-ColorOutput "Step 1: Updating Python import statements..." $Blue
Replace-InFiles "python_web_service_boilerplate" $ProjectName "*.py"

# Step 2: Update configuration files
Write-ColorOutput "Step 2: Updating configuration files..." $Blue

# Update pyproject.toml
if (Test-Path "pyproject.toml") {
    Write-ColorOutput "Updating pyproject.toml..." $Yellow
    $content = Get-Content "pyproject.toml" -Raw
    $content = $content -replace "python-web-service-boilerplate", $ProjectName
    $content = $content -replace "python_web_service_boilerplate", $ProjectName
    Set-Content -Path "pyproject.toml" -Value $content -NoNewline
}

# Update docker-compose.yml
if (Test-Path "docker-compose.yml") {
    Write-ColorOutput "Updating docker-compose.yml..." $Yellow
    $content = Get-Content "docker-compose.yml" -Raw
    $content = $content -replace "python_web_service_boilerplate", $ProjectName
    Set-Content -Path "docker-compose.yml" -Value $content -NoNewline
}

# Update alembic.ini
if (Test-Path "alembic.ini") {
    Write-ColorOutput "Updating alembic.ini..." $Yellow
    $content = Get-Content "alembic.ini" -Raw
    $content = $content -replace "python_web_service_boilerplate", $ProjectName
    Set-Content -Path "alembic.ini" -Value $content -NoNewline
}

# Step 3: Rename directories
Write-ColorOutput "Step 3: Renaming directories..." $Blue

# Rename source directory
if (Test-Path "src\python_web_service_boilerplate") {
    Write-ColorOutput "Renaming src\python_web_service_boilerplate to src\$ProjectName..." $Yellow
    Move-Item "src\python_web_service_boilerplate" "src\$ProjectName"
}

# Rename test directory
if (Test-Path "tests\test_python_web_service_boilerplate") {
    Write-ColorOutput "Renaming tests\test_python_web_service_boilerplate to tests\test_$ProjectName..." $Yellow
    Move-Item "tests\test_python_web_service_boilerplate" "tests\test_$ProjectName"
}

# Step 4: Clean up cache directories
Write-ColorOutput "Step 4: Cleaning up cache directories..." $Blue
try {
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
catch {
    Write-ColorOutput "Could not remove some __pycache__ directories. Exception: $($_.Exception.Message)" $Yellow
}
try {
    Get-ChildItem -Recurse -File -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
}
catch {
    Write-ColorOutput "Could not remove some .pyc files. Exception: $($_.Exception.Message)" $Yellow
}
# Step 5: Update any remaining references
Write-ColorOutput "Step 5: Final cleanup..." $Blue

# Check for any remaining references and report them
try {
    $remainingRefs = Select-String -Path "." -Pattern "python_web_service_boilerplate" -Recurse -Exclude @("*.log", "init_project.*") |
                    Where-Object {
                        $_.Path -notlike "*\.git\*" -and
                        $_.Path -notlike "*\build\*" -and
                        $_.Path -notlike "*\__pycache__\*"
                    }

    if ($remainingRefs) {
        Write-ColorOutput "Warning: Found remaining references to 'python_web_service_boilerplate':" $Yellow
        $remainingRefs | ForEach-Object { Write-ColorOutput "  $($_.Path):$($_.LineNumber): $($_.Line.Trim())" "Gray" }
        Write-ColorOutput "You may need to update these manually." $Yellow
    }
}
catch {
    Write-ColorOutput "Could not check for remaining references: $($_.Exception.Message)" $Yellow
}

Write-Host
Write-ColorOutput "✅ Project initialization completed successfully!" $Green
Write-ColorOutput "Your project is now named: $ProjectName" $Green
Write-Host
Write-ColorOutput "Next steps:" $Blue
Write-ColorOutput "1. Review and commit your changes"
Write-ColorOutput "2. Update the README.md file with your project details"
Write-ColorOutput "3. Run: poetry install  (to install dependencies)" $Yellow
Write-ColorOutput "4. Run: poetry run python -m $ProjectName  (to start the application)" $Yellow
Write-Host
