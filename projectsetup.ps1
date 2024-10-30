# Set base directory
$BaseDir = "C:\Projects\AI_Debugger_Assistant"

# Step 1: Create and activate virtual environment
Write-Host "Creating virtual environment..."
python -m venv "$BaseDir\venv"
& "$BaseDir\venv\Scripts\Activate.ps1"

# Step 2: Update pip if necessary
Write-Host "Checking pip version..."
$PipUpgradeCommand = "$BaseDir\venv\Scripts\python.exe -m pip install --upgrade pip"
Invoke-Expression $PipUpgradeCommand

# Step 3: Install dependencies
Write-Host "Installing dependencies..."

$dependencies = @(
    "dearpygui", "docker", "pylint", "flake8", "black", "pre-commit", "python-dotenv"
)

# Try installing each dependency individually with error handling
foreach ($dep in $dependencies) {
    try {
        Write-Host "Installing $dep..."
        & "$BaseDir\venv\Scripts\python.exe" -m pip install $dep
    } catch {
        Write-Host "Error installing $dep. Retrying with '--no-cache-dir'..."
        & "$BaseDir\venv\Scripts\python.exe" -m pip install $dep --no-cache-dir
    }
}

# Step 4: Generate requirements.txt
Write-Host "Saving dependencies to requirements.txt..."
& "$BaseDir\venv\Scripts\python.exe" -m pip freeze > "$BaseDir\requirements.txt"

# Step 5: Set up pre-commit hooks if 'pre-commit' is available
$PreCommitPath = "$BaseDir\venv\Scripts\pre-commit.exe"
if (Test-Path -Path $PreCommitPath) {
    Write-Host "Setting up pre-commit hooks..."
    & "$PreCommitPath" install
} else {
    Write-Host "'pre-commit' is not available. Skipping hook setup."
}

Write-Host "Project AI_Debugger_Assistant has been scaffolded successfully!"
Write-Host "Activate the virtual environment and start development with:"
Write-Host "  . C:\Projects\AI_Debugger_Assistant\venv\Scripts\Activate.ps1"
Write-Host "Navigate to C:\Projects\AI_Debugger_Assistant to begin development."
