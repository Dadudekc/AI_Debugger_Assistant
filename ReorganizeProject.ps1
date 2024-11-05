# Add .gitignore entries
$GitIgnorePath = "$ProjectRoot\.gitignore"
$GitIgnoreEntries = @(
    "venv/",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.log",
    "ai_agent_memory.db"
)

Add-Content -Path $GitIgnorePath -Value "`n# Auto-generated entries for project structure`n"
foreach ($entry in $GitIgnoreEntries) {
    # Corrected Select-String syntax for checking if entry already exists in .gitignore
    if (-not (Select-String -Path $GitIgnorePath -Pattern ([regex]::Escape($entry)) -Quiet)) {
        Add-Content -Path $GitIgnorePath -Value $entry
        Add-Content -Path $LogFile -Value "Added to .gitignore: $entry"
    }
}
