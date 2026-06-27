# Replace GSC with GSE in all markdown files
Get-ChildItem -Path "." -Filter "*.md" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    $content = $content -replace 'GSC', 'GSE'
    $content = $content -replace 'Global Scoping Questionnaire', 'GreenStar Estimation Engine Input'
    Set-Content -Path $_.FullName -Value $content -NoNewline -Encoding UTF8
    Write-Host "Updated: $($_.FullName)"
}
Write-Host "Replacement complete!"

# Made with Bob
