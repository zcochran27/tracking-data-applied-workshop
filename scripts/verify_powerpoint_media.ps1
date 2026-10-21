param(
    [string]$DeckPath = (Join-Path $PSScriptRoot '../slides/tracking-data-applied.pptx'),
    [string]$ReportPath = (Join-Path $PSScriptRoot '../.build/native-powerpoint-media.json')
)
# Read-only native check. Requires installed Windows Microsoft PowerPoint.
$ErrorActionPreference = 'Stop'
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$resolvedDeck = (Resolve-Path -LiteralPath $DeckPath).Path
$resolvedReport = [IO.Path]::GetFullPath($ReportPath)
if (-not $resolvedReport.StartsWith($workspaceRoot + [IO.Path]::DirectorySeparatorChar)) {
    throw 'The validation report must stay inside the workshop workspace.'
}
$content = Get-Content -LiteralPath (Join-Path $workspaceRoot 'slides/content.json') -Raw | ConvertFrom-Json
$nativeApp = New-Object -ComObject PowerPoint.Application
$records = @()
try {
    $nativeDeck = $nativeApp.Presentations.Open($resolvedDeck, -1, 0, 0)
    try {
        for ($index = 0; $index -lt $content.Count; $index++) {
            if (-not $content[$index].video) { continue }
            $slide = $nativeDeck.Slides.Item($index + 1)
            $movies = @($slide.Shapes | Where-Object { $_.Name -like 'Video:*' })
            if ($movies.Count -ne 1) { throw "Slide $($index+1): expected one native movie." }
            $movie = $movies[0]
            $duration = [int64]$movie.MediaFormat.Length
            $clickAction = [int]$movie.ActionSettings.Item(1).Action
            if ([int]$movie.Type -ne 16 -or [int]$movie.MediaType -ne 3 -or $duration -le 0) {
                throw "Slide $($index+1): PowerPoint cannot resolve playable video media."
            }
            if ($clickAction -ne 12) { throw "Slide $($index+1): native ppActionPlay click action is missing." }
            $records += [ordered]@{
                slide = $index + 1
                title = $content[$index].title
                asset = $content[$index].video
                native_shape_type = [int]$movie.Type
                native_media_type = [int]$movie.MediaType
                native_duration_ms = $duration
                click_action = $clickAction
            }
        }
        $report = [ordered]@{
            status = 'pass'
            powerpoint_version = $nativeApp.Version
            deck_sha256 = (Get-FileHash -LiteralPath $resolvedDeck -Algorithm SHA256).Hash.ToLowerInvariant()
            movie_count = $records.Count
            movies = $records
            scope = 'Native PowerPoint recognizes embedded videos with nonzero duration. This check alone does not run slideshow playback.'
        }
        $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resolvedReport -Encoding utf8
        Write-Output "PowerPoint native media check passed: $($records.Count) movies."
    } finally { $nativeDeck.Close() }
} finally {
    # Leave any unrelated user presentations alone if PowerPoint reused an instance.
    if ($nativeApp.Presentations.Count -eq 0) { $nativeApp.Quit() }
}
