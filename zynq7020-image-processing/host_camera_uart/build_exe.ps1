param(
    [string]$PythonExe = "d:/deskbox/test01/05_fpga_1/zynq7020-image-processing/.venv/Scripts/python.exe",
    [string]$Name = "camera_uart_gui",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install --upgrade pyinstaller

if ($Clean) {
    Remove-Item -Recurse -Force .\build, .\dist -ErrorAction SilentlyContinue
}

$pyinstallerArgs = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", $Name,
    "--distpath", "dist",
    "--workpath", "build",
    "--specpath", "build",
    "--collect-all", "cv2",
    "--collect-submodules", "serial",
    "--collect-submodules", "numpy",
    "--hidden-import", "serial.tools.list_ports",
    "camera_uart_gui.py"
)

& $PythonExe -m PyInstaller @pyinstallerArgs

Write-Host "Build finished. Output: $scriptDir\dist\$Name.exe"