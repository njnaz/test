# Eduroam Group Policy — Desktop Support Guide

**Audience:** Desktop Support / Help Desk  
**Purpose:** Explain how university-managed Windows devices are prepared for Rutgers eduroam via Group Policy, how setup works on a device, and how to verify or troubleshoot it.

---

## 1. Overview

Students/staff on managed Windows laptops download and run the official Rutgers installer:

`eduroam_at_RU.exe` (SecureW2 JoinNow)

Group Policy does **not** put them on eduroam by itself. It prepares the device so that:

1. AppLocker **allows** the SecureW2 installer to run.  
2. Windows **trusts** the Rutgers Device Root CA used during setup.  
3. The user runs the installer once and signs in with their NetID.

```text
[GPO applies to computer]
        │
        ├─► AppLocker: allow SecureW2-signed eduroam installer
        └─► Trusted Root: Rutgers University Device Root CA
                    │
                    ▼
        User downloads eduroam_at_RU.exe → runs JoinNow → enters NetID
                    │
                    ▼
              Device connects to eduroam
```

---

## 2. What Group Policy configures

There are **two** related settings (often in one GPO, or split across GPOs). Both are **Computer Configuration** (apply to the laptop, not only the user).

### 2.1 AppLocker — allow the installer

**Path in GPMC:**  
`Computer Configuration → Policies → Windows Settings → Security Settings → Application Control Policies → AppLocker → Executable Rules`

**Purpose:** Managed devices block unknown EXEs. Without an allow rule, `eduroam_at_RU.exe` fails to launch (AppLocker event **8004**).

**Rule that works for this SecureW2 package:**

| Setting | Value |
|---------|--------|
| Action | Allow |
| Condition | Publisher |
| Publisher | `O=SECUREW2, L=AMSTERDAM, C=NL` |
| Product name | *(blank — not `*`)* |
| File name | *(blank — not `*`)* |
| File version | `*` and above (any version) |
| Applies to | Everyone (or the student/staff group) |
| Exe rules | **Enforce** |

**Why blank product/file and version `*`?**  
AppLocker reads this installer as:

`Publisher : O=SECUREW2, L=AMSTERDAM, C=NL\\,0.0.0.0`

The `\\` means product and file name are empty. Rules with `*` in those fields, or version `0.0.0.0 and above`, often **look** OK in tests but still block at runtime. The working pattern matches the blank fields and uses version `*`.

**Optional fallback:** a **File hash** allow for a specific EXE build. That works, but breaks when Rutgers posts a new installer. Prefer the publisher rule above; use hash only if a device still logs 8004.

The installer also unpacks helpers (for example `%TEMP%\SecureW2_JoinNow.exe`). The same SecureW2 publisher allow typically covers the signed helper.

### 2.2 Trusted Root — Rutgers Device Root CA

**Path in GPMC:**  
`Computer Configuration → Policies → Windows Settings → Security Settings → Public Key Policies → Trusted Root Certification Authorities`

**Certificate:** Rutgers University Device Root CA  

| Attribute | Value |
|-----------|--------|
| Subject | CN=Rutgers University Device Root CA, O=Rutgers University |
| SHA1 | `2762E6D29F343A670E8F1D9BE0B776A30269861B` |

**Purpose:** JoinNow trusts Rutgers’ private root for eduroam. If this cert is missing, users may see a Windows warning that it cannot validate “Rutgers University Device Root CA.”

**Do not** put the SecureW2 *code-signing* cert in Trusted Root. That belongs to AppLocker/publisher trust only.

| Cert | Store |
|------|--------|
| Rutgers University Device Root CA | **Trusted Root** |
| SecureW2 (code signing on the EXE) | AppLocker publisher rule |

---

## 3. How it gets onto a device

### 3.1 Scope

1. Computer account is in an OU (or security group) linked to the eduroam/AppLocker GPO(s).  
2. Example label/scope used operationally: devices such as **RSDM All Student Devices** (or whatever OU/filtering IT assigned).  
3. Policy is **Computer** policy → user login alone is not enough; the machine must refresh computer policy.

### 3.2 Refresh cycle

| Trigger | When settings appear |
|---------|----------------------|
| Background refresh | Often within ~90 minutes |
| `gpupdate /force` | Immediately (after success) |
| Reboot | Reliable after first enabling AppLocker |

Nothing is instant just because the GPO was edited in GPMC. The laptop must **apply** policy.

### 3.3 What the user still does

After GPO is applied:

1. Connect to another network if needed (e.g. RUWireless / Ethernet) to download.  
2. Download `eduroam_at_RU.exe` from the **official Rutgers** site.  
3. Run the EXE.  
4. Complete SecureW2 JoinNow and sign in with NetID (format as campus requires, often `NetID@rutgers.edu`).  
5. Connect to **eduroam**.

GPO prepares the device; **credentials and the installer run are per user/device**.

---

## 4. Verify on a device (support checklist)

Run these on the laptop (prefer a **standard user** account for AppLocker tests—local admins can be misleading because AppLocker has a default “Administrators can run all files” rule).

### 4.1 Did Computer policy apply?

```powershell
gpresult /r /scope computer
gpresult /h "$env:USERPROFILE\Desktop\gpresult.html"
```

Confirm the eduroam/AppLocker GPO is listed under **Applied Group Policy Objects** for the computer—not Denied (Security) or missing.

```powershell
gpupdate /force
```

### 4.2 Is the Rutgers root present?

```powershell
Get-ChildItem Cert:\LocalMachine\Root |
  Where-Object { $_.Subject -like '*Rutgers University Device Root CA*' -or $_.Thumbprint -eq '2762E6D29F343A670E8F1D9BE0B776A30269861B' } |
  Format-List Subject, Thumbprint, NotAfter
```

Or:

```powershell
certutil -store Root | findstr /i "Rutgers 2762E6D2"
```

- **Found** → Trusted Root side is OK.  
- **Empty** → GPO not applied to this PC, or wrong store. Fix link/filtering; do not tell users to ignore random cert prompts.

### 4.3 What does AppLocker see on the EXE?

```powershell
Get-AppLockerFileInformation -Path "$env:USERPROFILE\Downloads\eduroam_at_RU.exe" |
  Format-List Path, Publisher, Hash
```

Expect something like:

```text
Publisher : O=SECUREW2, L=AMSTERDAM, C=NL\\,0.0.0.0
```

Signature check:

```powershell
Get-AuthenticodeSignature "$env:USERPROFILE\Downloads\eduroam_at_RU.exe" |
  Format-List Status, StatusMessage, @{n='Subject';e={$_.SignerCertificate.Subject}}
```

Expect **Valid** and Subject containing **SecureW2**.

### 4.4 Policy test vs real block

```powershell
Test-AppLockerPolicy -PolicyObject (Get-AppLockerPolicy -Effective) `
  -Path "$env:USERPROFILE\Desktop\eduroam_at_RU.exe" `
  -User "$env:USERDOMAIN\$env:USERNAME" |
  Format-List PolicyDecision, MatchingRule
```

Then have the user launch the EXE and check events:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-AppLocker/EXE and DLL" -MaxEvents 10 |
  Select-Object TimeCreated, Id, Message
```

| Event ID | Meaning |
|----------|---------|
| **8002** | Allowed — good |
| **8004** | Blocked — AppLocker still denying that path/file |

**Important:** `Test-AppLockerPolicy` can say **Allowed** while the EXE still gets **8004**. Trust the event log after a real launch.

### 4.5 Effective SecureW2 rule shape

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
  ForEach-Object { $_ } |
  Where-Object { $_.PublisherConditions -and (($_ | Out-String) -match 'SECUREW2') } |
  Format-List Name, PublisherConditions
```

Working pattern resembles:

`{\O=SECUREW2, L=AMSTERDAM, C=NL\,*}`  
(blank product/file, version any)

Problematic pattern often used by mistake:

version `0.0.0.0-*` only, or product/file set to `*`.

---

## 5. Common support scenarios

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| EXE won’t start; 8004 on `EDUROAM_AT_RU.EXE` | AppLocker allow missing/wrong, or GPO not applied | Confirm GPO applied; verify publisher rule (blank product/file, version `*`); `gpupdate` / reboot |
| EXE starts on one PC, blocked on another | Different effective policy, OU/filtering, or stale policy | Compare `gpresult` and effective AppLocker rules on both |
| Works for tech (admin), fails for student | Admin default AppLocker allow | Retest as standard user; fix Everyone/student allow rule |
| JoinNow cert warning for Rutgers Device Root CA | Root not in `LocalMachine\Root` | Confirm Trusted Root GPO; `certutil -store Root` |
| Installer OK, Wi‑Fi still fails | Bad credentials, wrong username format, radio/off SSID | Retry NetID format; forget eduroam; run installer again |
| New download of installer blocked after school update | Old **hash** rule only | Rely on SecureW2 publisher `*` version rule; update hash if hash was required |

---

## 6. What Desktop Support should / should not do

**Do**

- Confirm the device is managed and in scope for the GPO.  
- Run `gpupdate /force` and verify Rutgers root + AppLocker events.  
- Direct users to the **official** Rutgers `eduroam_at_RU.exe` download only.  
- Collect: device name, user (standard vs admin), 8002/8004 message, whether Rutgers root is present.

**Don’t**

- Broadly allow `%TEMP%\*` or all of Downloads in AppLocker.  
- Put SecureW2 code-signing cert into Trusted Root.  
- Tell users to install random root certificates from email or unofficial sites.  
- Unlink unrelated Wi‑Fi GPOs (e.g. a “secure” SSID policy) without planning—removing those GPOs can remove those Wi‑Fi profiles after refresh and knock users offline.

---

## 7. Relationship to other Wi‑Fi GPOs

A separate GPO may deploy another SSID (for example **secure**). That is independent of eduroam AppLocker/cert policy.

- Unlinking a Wi‑Fi profile GPO typically **removes** that SSID profile on the next policy refresh.  
- Do not unlink production Wi‑Fi GPOs while users are actively depending on that SSID unless a backup network exists.

---

## 8. Quick script for a support ticket

Ask the user (or run remotely) and attach output:

```powershell
Write-Host "User:" "$env:USERDOMAIN\$env:USERNAME"
Write-Host "Admin?" ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole('Administrator')

gpupdate /force

Write-Host "`n--- Rutgers Root ---"
certutil -store Root | findstr /i "Rutgers 2762E6D2"

$exe = @(
  "$env:USERPROFILE\Desktop\eduroam_at_RU.exe",
  "$env:USERPROFILE\Downloads\eduroam_at_RU.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($exe) {
  Write-Host "`n--- EXE ---" $exe
  Get-AppLockerFileInformation -Path $exe | Format-List Publisher, Hash
  Test-AppLockerPolicy -PolicyObject (Get-AppLockerPolicy -Effective) -Path $exe -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List PolicyDecision, MatchingRule
}

Write-Host "`n--- Recent AppLocker EXE events ---"
Get-WinEvent -LogName "Microsoft-Windows-AppLocker/EXE and DLL" -MaxEvents 15 |
  Select-Object TimeCreated, Id, Message | Format-List
```

---

## 9. One-page summary for Desktop Support

1. **GPO prepares** the PC: AppLocker allows SecureW2; Trusted Root has Rutgers Device Root CA.  
2. **User runs** official `eduroam_at_RU.exe` and signs in with NetID.  
3. **Verify** with `gpresult`, `certutil` / `Cert:\LocalMachine\Root`, and AppLocker **8002** (not only `Test-AppLockerPolicy`).  
4. **Publisher rule** must be SecureW2, blank product/file, version `*`.  
5. **Missing root** → certificate warnings; **8004** → installer blocked.  
6. Escalate with device name, events, and whether the Rutgers thumbprint `2762E6D2…861B` is present.

---

*Internal support document for eduroam on AppLocker-managed Windows endpoints. End-user steps are also summarized in `Eduroam_User_Guide.md`.*
