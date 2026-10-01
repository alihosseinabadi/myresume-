# Launch a clean Chrome window on localhost:3000, force it to the foreground,
# then grab the live desktop so the open landing page can be verified visually.

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
}
"@

Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$profile = Join-Path $env:TEMP 'myresume-shot-profile'
$chrome  = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$outDir  = 'C:\Users\ali hosseinabadi\myresume\screenshots\live'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Start-Process -FilePath $chrome -ArgumentList @(
  "--user-data-dir=$profile", '--no-first-run', '--no-default-browser-check',
  '--new-window', '--window-size=1536,820', '--window-position=0,0',
  'http://localhost:3000/'
) | Out-Null

Start-Sleep -Seconds 14

$win = Get-Process chrome -ErrorAction SilentlyContinue |
       Where-Object { $_.MainWindowTitle -like '*MyResume*' } |
       Select-Object -First 1

if ($win) {
  Write-Output "window : $($win.MainWindowTitle)"
  [void][Win]::ShowWindow($win.MainWindowHandle, 3)   # SW_MAXIMIZE
  Start-Sleep -Milliseconds 700
  [void][Win]::BringWindowToTop($win.MainWindowHandle)
  [void][Win]::SetForegroundWindow($win.MainWindowHandle)
} else {
  Write-Output 'window : not found by title'
}

Start-Sleep -Seconds 3

$b    = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp  = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g    = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)

$out = Join-Path $outDir 'browser-open.png'
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "wrote  : $out ($([math]::Round((Get-Item $out).Length/1KB)) KB)"
