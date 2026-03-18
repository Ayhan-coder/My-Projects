# Quick GCC and Make Installation Guide for Windows

## You have Git installed ✓
## You need: GCC compiler and Make utility

## Option 1: Install MSYS2 (RECOMMENDED - Easiest)

### Step 1: Download and Install MSYS2
1. Go to: https://www.msys2.org/
2. Download the installer (msys2-x86_64-XXXXXXXX.exe)
3. Run the installer and follow the wizard (use default installation path: C:\msys64)
4. When installation completes, it will open an MSYS2 terminal

### Step 2: Install GCC and Make
In the MSYS2 terminal that opens, run these commands:
```bash
pacman -Syu
# Press Y to proceed, close the window when asked
# Re-open MSYS2 MSYS from Start Menu and run:
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-make
# Press Y to install
```

### Step 3: Add to PATH
Add this to your Windows PATH (System Environment Variables):
```
C:\msys64\mingw64\bin
```

**To add to PATH:**
1. Press Win + X, select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", select "Path" and click "Edit"
5. Click "New" and add: `C:\msys64\mingw64\bin`
6. Click OK on all windows
7. **Restart VS Code**

---

## Option 2: Use Chocolatey Package Manager

If you have Chocolatey installed, run in PowerShell (as Administrator):
```powershell
choco install mingw make
```

---

## Option 3: Install MinGW-w64 Standalone

1. Download from: https://sourceforge.net/projects/mingw-w64/
2. Run the installer
3. Choose:
   - Version: Latest
   - Architecture: x86_64
   - Threads: posix
   - Exception: seh
4. Note the installation path
5. Add `<install-path>\mingw64\bin` to your PATH

---

## Option 4: Use WSL2 (Most Linux-like experience)

Since you already have WSL (docker-desktop), you can use a proper Linux distribution:

### Install Ubuntu on WSL2:
```powershell
wsl --install -d Ubuntu
# Or if already installed:
wsl --list --online
wsl --install -d Ubuntu-22.04
```

### Once Ubuntu is running:
```bash
sudo apt update
sudo apt install build-essential
gcc --version
make --version
```

### Then run CoreMark in WSL:
```bash
cd /mnt/c/Users/gunde/Desktop/344Labs/344LAB3/coremark
make
```

---

## Quick Test After Installation

After installing, **restart VS Code** or open a new terminal, then test:

```powershell
gcc --version
mingw32-make --version
# or
make --version
```

---

## For This Lab - Use WSL2 (Quick Start)

If you want to start immediately without installing more Windows software:

```powershell
# Install Ubuntu on WSL2
wsl --install -d Ubuntu

# After Ubuntu is installed and you've set a username/password:
wsl

# Inside WSL (Linux terminal):
sudo apt update && sudo apt install -y build-essential
cd /mnt/c/Users/gunde/Desktop/344Labs/344LAB3/coremark
make
```

This approach is actually closest to the lab instructions (Unix-like environment).
