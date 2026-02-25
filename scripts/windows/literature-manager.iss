; Build installer with Inno Setup (ISCC)
; Example:
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" scripts\windows\literature-manager.iss

#define AppName "literature-manager"
#define AppVersion "0.1.0"
#define Publisher "ymeng"
#define ExeName "literature-manager.exe"

[Setup]
AppId={{A93D8A09-68D0-4CDE-92C2-029A2A14E910}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#Publisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=dist
OutputBaseFilename=literature-manager-setup-{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: unchecked

[Files]
Source: "dist\literature-manager\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#ExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#ExeName}"; Description: "启动 {#AppName}"; Flags: nowait postinstall skipifsilent
