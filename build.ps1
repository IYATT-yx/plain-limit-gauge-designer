$startTime = Get-Date

python -m venv venv
.\venv\Scripts\Activate.ps1
python.exe -m pip install --upgrade pip
pip install nuitka==4.1.2

Set-Content -Path ".\buildtime.py" -Value "buildTime = '$(Get-Date -Format 'yyyyMMdd_HHmmss')'" -Encoding UTF8

nuitka --standalone --onefile --remove-output --windows-console-mode=disable `
--enable-plugin=tk-inter `
--windows-icon-from-ico=.\icon.ico --include-data-file=.\icon.ico=.\ `
--output-dir=dist --output-filename=plain-limit-gauge-designer_win_amd64 `
.\plain-limit-gauge-designer.py

$endTime = Get-Date
$elapsedTime = New-TimeSpan -Start $startTime -End $endTime
Write-Output "程序构建用时：$($elapsedTime.TotalSeconds) 秒"