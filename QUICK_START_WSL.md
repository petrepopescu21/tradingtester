# Quick Start: WSL Installation

**Complete guide to get Trading Tester running in WSL Ubuntu**

---

## 📋 Complete Installation Steps

### 1️⃣ Install WSL Ubuntu (Windows PowerShell as Admin)
```powershell
wsl --install -d Ubuntu
```
- Create username/password when prompted
- Close and reopen terminal

### 2️⃣ Update Ubuntu (WSL Terminal)
```bash
sudo apt update && sudo apt upgrade -y
```

### 3️⃣ Install System Dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential git curl
```

### 4️⃣ Install Node.js and Claude Code
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Claude Code
sudo npm install -g @anthropic-ai/claude-code

# Authenticate
claude auth login
```

### 5️⃣ Navigate to Project
```bash
cd /mnt/s/code/tradingtester
ls -la  # Verify files are there
```

### 6️⃣ Start Claude Code
```bash
claude
```

### 7️⃣ Tell Claude to Resume
In Claude Code, type:
```
I'm in WSL, let's resume
```

---

## 🎯 What Happens Next

After you say "I'm in WSL, let's resume", Claude will:

1. ✅ Create `setup.sh` (Linux installation script)
2. ✅ Install Python dependencies
3. ✅ Set up virtual environment
4. ✅ Test the installation
5. ✅ Run a demo to verify everything works

---

## 📍 Key Locations

**Project in Windows:**
```
S:\code\tradingtester
```

**Project in WSL:**
```
/mnt/s/code/tradingtester
```

**Files to check:**
- `RESUME_STATE.md` - What's been built and what's next
- `PROJECT_SUMMARY.md` - Complete project overview
- `ARCHITECTURE.md` - Technical details

---

## 🔧 Troubleshooting

### WSL not installing
```powershell
# Enable WSL first
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all
# Restart Windows, then: wsl --install -d Ubuntu
```

### Can't find project files
```bash
# Make sure you're in the right directory
cd /mnt/s/code/tradingtester
pwd  # Should show: /mnt/s/code/tradingtester
```

### Claude Code not found
```bash
# Check if installed
which claude

# If not found, reinstall
sudo npm install -g @anthropic-ai/claude-code

# Check PATH
echo $PATH
```

### Python version too old
```bash
# Check version
python3 --version

# If < 3.10, install newer version
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

---

## ✅ Verification Checklist

Before resuming with Claude, verify:

- [ ] WSL Ubuntu is installed and running
- [ ] Can navigate to `/mnt/s/code/tradingtester`
- [ ] Files are visible with `ls -la`
- [ ] Python 3.10+ installed: `python3 --version`
- [ ] Claude Code installed: `claude --version`
- [ ] Claude Code authenticated: `claude auth login` (done)

---

## 🚀 After Setup is Complete

Once Claude helps you complete the setup, you can:

```bash
# Activate environment
source venv/bin/activate

# Test a strategy
tradingtester test strategies/rsi_mean_reversion.md --symbol AAPL

# Generate variations
tradingtester generate strategies/rsi_mean_reversion.md --variations 5

# Run batch test
tradingtester batch strategies/ --symbols AAPL,MSFT,GOOGL

# Run demo
python3 demo.py 1
```

---

## 📚 Additional Resources

- `WSL_SETUP.md` - Detailed WSL installation
- `INSTALL_CLAUDE_CODE.md` - Claude Code installation options
- `MIGRATION_CHECKLIST.md` - Step-by-step checklist
- `RESUME_STATE.md` - Complete project state
- `GETTING_STARTED.md` - How to use Trading Tester

---

**Ready?** Follow the steps above, then start Claude Code and say:
> "I'm in WSL, let's resume"

See you on the other side! 🐧✨
