Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = ScriptDir
WshShell.Environment("PROCESS")("VIRALPULSE_NO_BROWSER") = "1"
WshShell.Environment("PROCESS")("PEAKCUT_NO_BROWSER") = "1"
WshShell.Run "cmd /c """ & ScriptDir & "\ViralPulse AI Studio.bat""", 0, False
