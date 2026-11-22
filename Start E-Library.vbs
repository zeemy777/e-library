' E-Library one-click starter.
' Starts the Flask server (which also serves the built frontend)
' and opens the site in the default browser. No terminal needed.

Option Explicit

Dim fso, shell, root, backend, python, url, started, i, dbStatus
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

root = fso.GetParentFolderName(WScript.ScriptFullName)
backend = root & "\backend"
python = root & "\.venv\Scripts\pythonw.exe"
url = "http://127.0.0.1:5000/"

' Fetch a URL and return its body (empty string on any error).
Function HttpGet(target)
  On Error Resume Next
  Dim xhr
  Set xhr = CreateObject("MSXML2.XMLHTTP.6.0")
  xhr.Open "GET", target, False
  xhr.Send
  If Err.Number <> 0 Then
    HttpGet = ""
  Else
    HttpGet = xhr.responseText
  End If
  On Error GoTo 0
End Function

' Start the server only if it is not already running.
started = False
If InStr(HttpGet(url & "api/health"), """status"": ""success""") > 0 Then
  started = True
Else
  shell.CurrentDirectory = backend
  shell.Run """" & python & """ run.py", 0, False

  For i = 1 To 60
    WScript.Sleep 500
    If InStr(HttpGet(url & "api/health"), "success") > 0 Then
      started = True
      Exit For
    End If
  Next
End If

If Not started Then
  MsgBox "The E-Library server did not start." & vbCrLf & _
         "Make sure MySQL is running, then try again.", _
         vbExclamation, "E-Library"
  WScript.Quit 1
End If

' Warn if MySQL itself is down.
dbStatus = HttpGet(url & "api/db-health")
If InStr(dbStatus, "successful") = 0 Then
  MsgBox "The website is running, but the MySQL database is not." & vbCrLf & _
         "Start MySQL (XAMPP/WAMP) and refresh the page.", _
         vbExclamation, "E-Library"
End If

' Open the website.
shell.Run url, 1, False
