$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$HOME\Desktop\ANAY AI.lnk")
$Shortcut.TargetPath = "c:\Users\Sahil khurana\Desktop\ANAY-DESKTOP\launch_anay.vbs"
$Shortcut.WorkingDirectory = "c:\Users\Sahil khurana\Desktop\ANAY-DESKTOP"
$Shortcut.IconLocation = "c:\Users\Sahil khurana\Desktop\ANAY-DESKTOP\anay_icon.ico"
$Shortcut.Save()
Write-Host "Desktop shortcut 'ANAY AI' created successfully!"
