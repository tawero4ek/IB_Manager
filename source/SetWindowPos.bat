@echo off
chcp 1251
start ArchiveViewer.exe -ISViewer
rem echo Archive Viewer
rem pause 3
rem @powershell -ExecutionPolicy UnRestricted -Command "(Add-Type -memberDefinition \"[DllImport(\"\"user32.dll\"\")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x,int y,int cx, int xy, uint flagsw);\" -name \"Win32SetWindowPos\" -passThru )::SetWindowPos((Add-Type -memberDefinition \"[DllImport(\"\"user32.dll\"\", SetLastError = true)] public static extern IntPtr FindWindowA(IntPtr sClassName, string lpWindowName);\" -name \"Win32FindWindowA\" -passThru )::FindWindowA([IntPtr]::Zero,'Archive viewer'),-1,800,50,1100,800,80)"
@powershell -ExecutionPolicy UnRestricted -Command "(Add-Type -memberDefinition \"[DllImport(\"\"user32.dll\"\")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x,int y,int cx, int xy, uint flagsw);\" -name \"Win32SetWindowPos\" -passThru )::SetWindowPos((Add-Type -memberDefinition \"[DllImport(\"\"user32.dll\"\", SetLastError = true)] public static extern IntPtr FindWindowA(IntPtr sClassName, string lpWindowName);\" -name \"Win32FindWindowA\" -passThru )::FindWindowA([IntPtr]::Zero,'Просмоторщик архивов'),-1,680,50,1200,740,80)"
exit