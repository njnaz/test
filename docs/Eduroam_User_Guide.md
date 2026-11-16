# Connecting to eduroam on Your University Windows Laptop

**Audience:** Students and staff using university-managed Windows devices  
**Network:** eduroam (Rutgers)

---

## What is eduroam?

**eduroam** is the secure campus Wi‑Fi network. Once your laptop is set up, you can connect on campus—and at many other colleges and universities that also offer eduroam—using your Rutgers login.

On university-managed Windows laptops, IT has already prepared your device in the background so setup is simpler and safer. You still need to run the official Rutgers installer once and sign in with your own credentials.

---

## What’s already done for you (Group Policy)

Your laptop receives settings automatically from IT. You don’t need to change these yourself.

| What’s configured | Why it helps you |
|-------------------|------------------|
| Permission to run the official Rutgers / SecureW2 eduroam installer | So the setup program isn’t blocked by the laptop’s application controls |
| Rutgers security certificate (Device Root CA) | So Windows trusts the campus Wi‑Fi setup and you avoid confusing certificate warnings |

Think of it like this: IT unlocks the door and installs the campus “trust” paperwork. You still walk through and sign in with your NetID.

---

## What you need before you start

- Your university-managed Windows laptop (on campus network or with internet access for the download)
- Your **Rutgers NetID** and password  
- About 5–10 minutes

**Tip:** It’s easiest if you start while connected to another network (for example **RUWireless** or wired Ethernet) so you can download the installer before switching to eduroam.

---

## Step-by-step: Set up eduroam

### 1. Download the official installer

1. Open a web browser.
2. Go to the Rutgers eduroam / SecureW2 download page provided by the university (the same place students are directed for **eduroam_at_RU**).
3. Download **`eduroam_at_RU.exe`**.

Save it somewhere easy to find, such as **Downloads** or **Desktop**.

> Only use the official Rutgers download. Do not use random “Wi‑Fi helper” tools from other websites.

### 2. Run the installer

1. Open the file you downloaded (`eduroam_at_RU.exe`).
2. If Windows asks “Do you want to allow this app to make changes?” choose **Yes** (if prompted).
3. Follow the on-screen SecureW2 / JoinNow instructions.

### 3. Sign in

When asked for your credentials:

- **Username:** your NetID in the format your campus requires (often `NetID@rutgers.edu`)  
- **Password:** your Rutgers password  

Enter them carefully and continue.

### 4. Finish and connect

1. Wait until the tool reports that setup is complete.
2. Select the **eduroam** Wi‑Fi network if your laptop does not connect automatically.
3. You should now stay connected with eduroam on campus.

You usually only need to do this **once** per laptop. After that, eduroam should connect on its own when you’re in range.

---

## What you might see (and what’s normal)

| Message or prompt | What it means |
|-------------------|---------------|
| SecureW2 / JoinNow welcome screen for Rutgers | Expected — continue |
| Request for username and password | Expected — use your Rutgers account |
| Setup completed / connected to eduroam | You’re done |

If you previously saw a Windows message about a certificate from **“Rutgers University Device Root CA,”** university-managed laptops should already trust that certificate. If that warning still appears, contact IT (see below)—don’t guess or install certificates from email attachments.

---

## After you’re set up

- Your laptop should prefer **eduroam** on campus.
- You can forget older networks like temporary guest Wi‑Fi if IT asks you to.
- If you change your Rutgers password, you may be asked to sign in to Wi‑Fi again the next time you connect.

---

## Troubleshooting

**The installer won’t open**  
- Make sure you downloaded `eduroam_at_RU.exe` from the official Rutgers site.  
- Try saving it to your Desktop and running it from there.  
- Restart the laptop and try once more.  
- If it still won’t open, contact IT—your device may not have received the latest security settings yet.

**Installer opens, but Wi‑Fi still fails**  
- Confirm you used the correct NetID format and password.  
- Forget the eduroam network, run the installer again, then reconnect.  
- Check that Wi‑Fi is turned on and that you’re in an area with campus coverage.

**Certificate warning about Rutgers**  
- On managed laptops this should be uncommon. Stop and contact IT rather than clicking through unfamiliar certificate prompts.

**Works on one laptop but not another**  
- Each computer needs its own one-time setup.  
- Both need to be university-managed devices covered by the same IT policies.

---

## Privacy & security notes (plain language)

- You are installing the **official Rutgers eduroam setup tool**, not unrelated software.
- Your password is used to join the secure Wi‑Fi service; use the same care you would for any Rutgers login.
- University policy settings help keep the installer allowed and the campus certificate trusted—they do not replace your password or give others access to your account.

---

## Need help?

Contact your campus or school IT support (for example, the help desk for your school or **RSDM** support if that’s your area). When you write in, include:

1. Your laptop name (if you know it) or that it’s a student/staff managed device  
2. That you were setting up **eduroam** with **`eduroam_at_RU.exe`**  
3. What happened (installer blocked, login failed, certificate warning, etc.)  
4. A screenshot if possible  

---

## Quick summary

1. IT already prepares your managed Windows laptop for eduroam (installer allowed + Rutgers certificate trusted).  
2. You download **`eduroam_at_RU.exe`** from the official Rutgers site.  
3. You run it and sign in with your NetID.  
4. Connect to **eduroam** and you’re set.

Welcome to campus Wi‑Fi—once it’s configured, you shouldn’t have to think about it again.
