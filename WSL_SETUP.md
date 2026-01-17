# WSL Ubuntu Installation Guide

## Step 1: Install WSL with Ubuntu

Open PowerShell as Administrator and run:

```powershell
# Install WSL with Ubuntu (latest LTS)
wsl --install -d Ubuntu

# Or if WSL is already installed, just install Ubuntu
wsl --install Ubuntu
```

If you need to enable WSL first:
```powershell
# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart your computer
# Then set WSL 2 as default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu
```

## Step 2: Initial Ubuntu Setup

After installation, Ubuntu will launch and ask you to:
1. Create a UNIX username
2. Create a password

Choose whatever you like - this will be your sudo user.

## Step 3: Access Your Windows Files

In WSL Ubuntu, your Windows drives are mounted at `/mnt/`:
```bash
# Navigate to the project
cd /mnt/s/code/tradingtester

# Verify you're in the right place
ls -la
```

## Step 4: Install Python 3.14 (or Latest Python)

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Check version
python3 --version

# If you need Python 3.14 specifically, you may need to:
# Add deadsnakes PPA
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.14 python3.14-venv python3.14-dev -y
```

## Step 5: Resume the Project

Once you're in WSL Ubuntu:

```bash
# Navigate to project
cd /mnt/s/code/tradingtester

# Read the resume file
cat RESUME_STATE.md

# Run the setup script
./setup.sh
```

## Useful WSL Commands

```bash
# From Windows PowerShell:
wsl                          # Enter WSL default distro
wsl -l -v                   # List installed distros
wsl -d Ubuntu               # Enter Ubuntu specifically
wsl --shutdown              # Shutdown all WSL instances
wsl --terminate Ubuntu      # Terminate Ubuntu instance

# From within WSL:
exit                        # Exit WSL back to Windows
explorer.exe .              # Open current directory in Windows Explorer
code .                      # Open current directory in VS Code (if installed)
```

## VS Code Integration (Optional but Recommended)

1. Install VS Code on Windows
2. Install "WSL" extension in VS Code
3. From WSL terminal: `code .` to open project in VS Code with WSL integration

## Troubleshooting

### WSL not found
Make sure you're on Windows 10 version 2004+ or Windows 11

### Ubuntu won't install
Try: `wsl --update` then retry installation

### Can't access Windows files
Check `/mnt/c/` for C drive, `/mnt/s/` for S drive, etc.

### Permission issues
Use `sudo` for system operations, but don't use it for the venv or pip installs in your project

---

**Next Step:** After WSL Ubuntu is installed and running, restart Claude Code from WSL and tell me "I'm in WSL, let's resume". I'll pick up from the RESUME_STATE.md file.
