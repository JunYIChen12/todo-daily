param(
  [Parameter(Mandatory = $true)]
  [string]$ShortcutPath,
  [Parameter(Mandatory = $true)]
  [string]$TargetPath,
  [Parameter(Mandatory = $true)]
  [string]$AppId,
  [string]$Description = "Daily Todo",
  [string]$WorkingDirectory = "",
  [string]$Arguments = "",
  [string]$IconPath = "",
  [int]$IconIndex = 0
)

$ErrorActionPreference = "Stop"

$shortcutDir = Split-Path -Parent $ShortcutPath
if (-not (Test-Path -LiteralPath $shortcutDir)) {
  New-Item -ItemType Directory -Force -Path $shortcutDir | Out-Null
}

$shortcutInterop = @"
using System;
using System.Runtime.InteropServices;

[ComImport]
[Guid("00021401-0000-0000-C000-000000000046")]
internal class CShellLink {}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("000214F9-0000-0000-C000-000000000046")]
internal interface IShellLinkW
{
    void GetPath(IntPtr pszFile, int cchMaxPath, IntPtr pfd, int fFlags);
    void GetIDList(out IntPtr ppidl);
    void SetIDList(IntPtr pidl);
    void GetDescription(IntPtr pszName, int cchMaxName);
    void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string pszName);
    void GetWorkingDirectory(IntPtr pszDir, int cchMaxPath);
    void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string pszDir);
    void GetArguments(IntPtr pszArgs, int cchMaxPath);
    void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string pszArgs);
    void GetHotkey(out short pwHotkey);
    void SetHotkey(short wHotkey);
    void GetShowCmd(out int piShowCmd);
    void SetShowCmd(int iShowCmd);
    void GetIconLocation(IntPtr pszIconPath, int cchIconPath, out int piIcon);
    void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string pszIconPath, int iIcon);
    void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string pszPathRel, int dwReserved);
    void Resolve(IntPtr hwnd, int fFlags);
    void SetPath([MarshalAs(UnmanagedType.LPWStr)] string pszFile);
}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
internal interface IPropertyStore
{
    uint GetCount(out uint cProps);
    uint GetAt(uint iProp, out PROPERTYKEY pkey);
    uint GetValue(ref PROPERTYKEY key, out PROPVARIANT pv);
    uint SetValue(ref PROPERTYKEY key, ref PROPVARIANT pv);
    uint Commit();
}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("0000010b-0000-0000-C000-000000000046")]
internal interface IPersistFile
{
    void GetClassID(out Guid pClassID);
    [PreserveSig] int IsDirty();
    void Load([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, uint dwMode);
    void Save([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, bool fRemember);
    void SaveCompleted([MarshalAs(UnmanagedType.LPWStr)] string pszFileName);
    void GetCurFile([MarshalAs(UnmanagedType.LPWStr)] out string ppszFileName);
}

[StructLayout(LayoutKind.Sequential, Pack = 4)]
internal struct PROPERTYKEY
{
    public Guid fmtid;
    public uint pid;
}

[StructLayout(LayoutKind.Explicit)]
internal struct PROPVARIANT
{
    [FieldOffset(0)] public ushort vt;
    [FieldOffset(8)] public IntPtr pointerValue;

    public static PROPVARIANT FromString(string value)
    {
        var pv = new PROPVARIANT();
        pv.vt = 31;
        pv.pointerValue = Marshal.StringToCoTaskMemUni(value);
        return pv;
    }

    public void Clear()
    {
        PropVariantClear(ref this);
    }

    [DllImport("ole32.dll")]
    private static extern int PropVariantClear(ref PROPVARIANT pvar);
}

public static class ShortcutInstaller
{
    private static PROPERTYKEY AppIdKey = new PROPERTYKEY
    {
        fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"),
        pid = 5
    };

    public static void Install(
        string shortcutPath,
        string targetPath,
        string arguments,
        string workingDirectory,
        string description,
        string iconPath,
        int iconIndex,
        string appId)
    {
        var link = (IShellLinkW)new CShellLink();
        link.SetPath(targetPath);
        link.SetArguments(arguments ?? string.Empty);
        if (!string.IsNullOrWhiteSpace(workingDirectory))
        {
            link.SetWorkingDirectory(workingDirectory);
        }
        if (!string.IsNullOrWhiteSpace(description))
        {
            link.SetDescription(description);
        }
        if (!string.IsNullOrWhiteSpace(iconPath))
        {
            link.SetIconLocation(iconPath, iconIndex);
        }
        link.SetShowCmd(1);

        var propertyStore = (IPropertyStore)link;
        var appIdVariant = PROPVARIANT.FromString(appId);
        try
        {
            uint hr = propertyStore.SetValue(ref AppIdKey, ref appIdVariant);
            if (hr != 0)
            {
                Marshal.ThrowExceptionForHR((int)hr);
            }

            hr = propertyStore.Commit();
            if (hr != 0)
            {
                Marshal.ThrowExceptionForHR((int)hr);
            }
        }
        finally
        {
            appIdVariant.Clear();
        }

        var persistFile = (IPersistFile)link;
        persistFile.Save(shortcutPath, true);
    }
}
"@

Add-Type -TypeDefinition $shortcutInterop -Language CSharp
[ShortcutInstaller]::Install(
  $ShortcutPath,
  $TargetPath,
  $Arguments,
  $WorkingDirectory,
  $Description,
  $IconPath,
  $IconIndex,
  $AppId
)
