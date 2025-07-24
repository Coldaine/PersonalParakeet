import subprocess
import os

print("Installing Workshop Box UI dependencies...")
os.chdir("workshop-box-ui")
subprocess.run(["C:\\Program Files\\nodejs\\npm.cmd", "install"], check=True)
print("Dependencies installed successfully!")