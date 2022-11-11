#define MyAppName "Agent360"
#define MyAppVersion "1.2.38"
#define MyAppPublisher "360 Monitoring"
#define MyAppURL "https://360monitoring.io/"

[Setup]
AppId={{E536D193-F9A3-4711-9082-82264F210799}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=Setup{#MyAppName}-v{#MyAppVersion}
SetupIconFile=.\favicon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
OutputDir=dist
DisableWelcomePage=no
ArchitecturesInstallIn64BitMode=x64
UsedUserAreasWarning=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: ".\build\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\build\bin\*"; DestDir: "{app}\bin"; Excludes: "\python*\*,\nssm\*"; Flags: ignoreversion recursesubdirs
Source: ".\build\bin\python64\*"; DestDir: "{app}\bin\python"; Check: Is64BitInstallMode
Source: ".\build\bin\python32\*"; DestDir: "{app}\bin\python"; Check: not Is64BitInstallMode
Source: ".\build\bin\nssm\win64\nssm.exe"; DestDir: "{app}\bin"; Check: Is64BitInstallMode
Source: ".\build\bin\nssm\win32\nssm.exe"; DestDir: "{app}\bin"; Check: not Is64BitInstallMode
Source: ".\build\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs
Source: ".\build\src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs

[Dirs]
Name: "{userappdata}\{#MyAppName}\logs"

[Run]
Filename: "{app}\bin\python\python.exe"; Parameters: """{app}\bin\python\get-pip.py"""; Flags: runhidden
Filename: "{app}\bin\python\python.exe"; Parameters: "-m pip install psutil"; Flags: runhidden
Filename: "{app}\bin\python\python.exe"; Parameters: """{app}\src\agent360.py"" hello ""{code:GetUserToken}"" ""{app}\config\agent360-token.ini"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "install {#MyAppName} ""{app}\bin\start.bat"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "set {#MyAppName} AppStdout ""{userappdata}\{#MyAppName}\logs\output.log"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "set {#MyAppName} AppStderr ""{userappdata}\{#MyAppName}\logs\error.log"""; Flags: runhidden
Filename: "{app}\bin\nssm.exe"; Parameters: "start {#MyAppName}"; Flags: runhidden

[UninstallRun]
Filename: "{app}\bin\nssm.exe"; Parameters: "stop {#MyAppName}"; Flags: runhidden; RunOnceId: StopService
Filename: "{app}\bin\nssm.exe"; Parameters: "remove {#MyAppName} confirm"; Flags: runhidden; RunOnceId: RemoveService

[Code]
var
  CustomQueryPage: TInputQueryWizardPage;

function GetUserToken(Param: string): string;
begin
  Result := CustomQueryPage.Values[0];
end;

function CharIsAlpha(C: Char): Boolean;
begin
  Result := ((C >= '0') and (C <= '9')) or ((C >= 'A') and (C <= 'Z')) or ((C >= 'a') and (C <= 'z'));
end;

function StringIsAlpha(s: string): Boolean;
var
  i: Integer;
begin
  Result := True;
  i := 1;

  while (i <= Length(s)) and Result do
  begin
    if not CharIsAlpha(s[i]) then
    begin
      Result := False;

      Exit;
    end;

    Inc(i);
  end;
end;

function ValidateToken(Sender: TWizardPage): Boolean;
var
  Token: string;
begin
  Result := True;
  Token := CustomQueryPage.Values[0];

  if (Token = '') then
  begin
    MsgBox('Invalid token', mbError, MB_OK);

    Result := False;
  end
  else if Pos(' ', Token) > 0 then
  begin
    MsgBox('Invalid token', mbError, MB_OK);

    Result := False;
  end
  else if not StringIsAlpha(Token) then
  begin
    MsgBox('Invalid token', mbError, MB_OK);

    Result := False;
  end
  else if Length(Token) <> 24 then
  begin
    MsgBox('Invalid token', mbError, MB_OK);

    Result := False;
  end;
end;

procedure OpenBrowser(Url: string);
var
  ErrorCode: Integer;
begin
  ShellExec('open', Url, '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

procedure LinkClick(Sender: TObject);
begin
  OpenBrowser('https://www.example.com/');
end;

procedure AddCustomQueryPage();
var
  RichView: TRichEditViewer;
begin
  CustomQueryPage := CreateInputQueryPage(
    wpLicense,
    '360 Monitoring UserID Token',
    '',
    ''
  );

  CustomQueryPage.Add('Token:', False);
  CustomQueryPage.OnNextButtonClick := @ValidateToken;

  RichView := TRichEditViewer.Create(CustomQueryPage);
  RichView.Left := 0;
  RichView.Top := 1;
  RichView.Width := 500;
  RichView.Height := 20;
  RichView.WordWrap := True;
  RichView.BorderStyle := bsNone;
  RichView.TabStop := False;
  RichView.ReadOnly := True;
  RichView.Parent := CustomQueryPage.Surface;
  RichView.ParentColor := true;
  RichView.RTFText :=  '{\rtf1 ' +
    '{\colortbl ;\red0\green0\blue238;}' +
    'You can find your 24 character user token on the ' +
    '{{\field{\*\fldinst{HYPERLINK "https://monitoring.platform360.io/servers/overview" }}' +
    '{\fldrslt{\cf1 servers page\cf0 }}}}.}';
end;

procedure InitializeWizard();
begin
  AddCustomQueryPage();
end;
