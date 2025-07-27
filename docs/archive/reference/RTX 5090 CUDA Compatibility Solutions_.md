

# **Resolving CUDA Kernel Compatibility for RTX 5090 with NeMo and PyTorch on Windows: An Exhaustive Technical Guide**

### **Executive Summary**

This report provides an exhaustive analysis and a set of tiered solutions for the CUDA error: no kernel image is available for execution on the device encountered when initializing the NVIDIA Parakeet-TDT-1.1B model with the NeMo toolkit on a Windows system equipped with an NVIDIA GeForce RTX 5090 GPU. The issue stems from a software incompatibility between the newly released GPU architecture and the standard, stable versions of the machine learning frameworks being used.

The root cause of the error is a mismatch between the CUDA Compute Capability of the hardware and the compiled code within the PyTorch library. The NVIDIA RTX 5090 is based on the new Blackwell architecture, which possesses a CUDA Compute Capability of 12.0.1 Standard, stable PyTorch binaries, such as those automatically installed as a dependency of the

nemo-toolkit, are typically compiled for older, more established GPU architectures and do not include the necessary pre-compiled binary (cubin) or forward-compatible intermediate code (PTX) required to run kernels on this new hardware.2

The primary and most immediate solution involves a strategic re-ordering of the installation process. By manually installing a **PyTorch nightly build** compiled with support for CUDA 12.8 or newer *before* installing the NeMo toolkit, the environment is properly prepared with the necessary Blackwell-compatible libraries. This preempts the standard dependency resolver from installing an incompatible, stable version of PyTorch.

For long-term project stability, scalability, and reproducibility, this report strongly recommends a more robust alternative: a **containerized development workflow using Docker Desktop with the Windows Subsystem for Linux (WSL2) backend**. This approach leverages NVIDIA's official, pre-configured, and highly optimized PyTorch containers (nvcr.io), which entirely isolates the development environment from the host system, thereby eliminating conflicts and ensuring consistency from development to deployment.

This situation is characteristic of working with bleeding-edge hardware, where the software ecosystem often lags behind the hardware release cycle. Resolving this requires moving from stable software channels to preview or nightly builds and adopting more sophisticated environment management practices, such as containerization, which are considered best practices in modern machine learning operations (MLOps). This report offers detailed, step-by-step instructions for all viable solution paths, from immediate fixes to professional-grade workflows.

## **Section 1: Root Cause Analysis: The Blackwell Architecture and CUDA Kernel Compatibility**

A thorough understanding of the error requires dissecting the interplay between the GPU hardware architecture, the CUDA compilation model, and the software libraries involved. The error is not a hardware or driver fault but a predictable software compilation mismatch that arises with the introduction of a new GPU generation.

### **1.1 Dissecting the Error: "no kernel image is available for execution on the device"**

The error message CUDA error: no kernel image is available for execution on the device is an explicit statement from the CUDA runtime. It signifies that when the PyTorch framework attempted to dispatch a specific function, known as a CUDA kernel, for execution on the RTX 5090, it searched its binary for a version of that kernel compiled for the target GPU's architecture and found none.3

This is fundamentally a software packaging and compilation issue. The application (in this case, the Python script using PyTorch and NeMo) possesses the logic, but the underlying PyTorch library lacks the correctly compiled, GPU-specific machine code that the RTX 5090 can execute. The system's ability to detect the GPU via nvidia-smi and run other GPU-accelerated applications confirms that the driver and hardware are functioning correctly; the failure point is confined to the specific version of the PyTorch library being used.

### **1.2 The CUDA Compilation Model: Compute Capability, PTX, and JIT**

To grasp the core of the problem, it is essential to understand how CUDA applications are compiled and executed. A common point of confusion is the distinction between the different "CUDA versions" present on a system. The version reported by nvidia-smi (e.g., 12.9) is the version of the **CUDA Driver API**. This driver is backward-compatible, meaning it can run applications built with older CUDA versions.6 However, deep learning frameworks like PyTorch ship with their own, specific set of

**CUDA runtime libraries** (e.g., cuBLAS, cuDNN).7 The error arises from an incompatibility with these bundled libraries, not the system-wide driver. A third component, the full

**CUDA Toolkit**, which includes the nvcc compiler, is only necessary when compiling CUDA code from source.9

The compatibility of these libraries is dictated by the GPU's **Compute Capability (CC)**.

* **Compute Capability (CC):** This is a version number (e.g., 8.6, 9.0, 12.0) that defines the hardware features, supported instruction set, and general capabilities of an NVIDIA GPU. Each major version number corresponds to a new GPU architecture.1  
* **Cubin and PTX:** When CUDA code is compiled by nvcc, it can produce two types of output for the application binary 10:  
  * **Cubin:** A fully compiled, architecture-specific binary object. A cubin compiled for sm\_90 (Hopper architecture) will run on any GPU with CC 9.x, but it is not forward-compatible and will not run on a GPU with CC 10.x or 12.x. This is the fastest execution path as no further compilation is needed.  
  * **PTX (Parallel Thread Execution):** A stable, intermediate assembly-like language. PTX code is forward-compatible. When an application is run on a GPU for which no native cubin exists, the CUDA driver can **Just-in-Time (JIT)** compile the PTX code into a native cubin for that new architecture. This ensures that applications can run on future, unreleased hardware, albeit with a one-time JIT compilation delay at startup.

The "no kernel image" error occurs when an application binary contains neither a native cubin for the target GPU's CC nor a suitable PTX version that the driver can JIT-compile.10

### **1.3 The RTX 5090: A Blackwell GPU with Compute Capability 12.0**

The NVIDIA GeForce RTX 5090 is built on the **Blackwell** microarchitecture, a successor to the Ada Lovelace (40-series) and Hopper (data center) architectures.11 This new architecture introduces significant changes and a new set of hardware features.

According to NVIDIA's official documentation, consumer GPUs in the Blackwell family, including the GeForce RTX 5090, have a **Compute Capability of 12.0**.1 This is a new major version, distinct from the CC 8.9 of the RTX 4090 and the CC 9.0 of the H100.

Critically, native support for the Blackwell architecture (CC 10.x for data center, CC 12.x for consumer) was first introduced in the **CUDA Toolkit version 12.8**.2 This establishes a minimum software toolkit version required to build applications that can natively target the RTX 5090\. Any PyTorch binary compiled with a toolkit older than 12.8 will not contain a native

cubin for sm\_120. While it could theoretically work via PTX JIT compilation, this depends on the PTX version included during the original build.

### **1.4 Identifying the Software Mismatch: Why Stable PyTorch and NeMo Fail**

The direct cause of the failure lies in the automated dependency resolution process of pip. The command pip install nemo-toolkit\[asr\] instructs the package manager to install the NeMo toolkit and its dependencies. The nemo-toolkit package specifies a dependency on a minimum version of PyTorch, such as pytorch\>=2.5.15

When resolving this, pip defaults to installing the latest **stable** version of PyTorch that satisfies this requirement. As of the time of the error, stable PyTorch releases were compiled with older CUDA toolkits (e.g., 12.1) and did not include support for the sm\_120 compute capability of the RTX 5090\. This is explicitly confirmed by the user warning that often precedes the fatal error: UserWarning: NVIDIA GeForce RTX 5090 with CUDA capability sm\_120 is not compatible with the current PyTorch installation.2

This creates a "dependency inversion" problem. The correct workflow requires inverting the installation order: a compatible, non-stable version of PyTorch must be installed *manually* first. This pre-satisfies the dependency, preventing pip from subsequently installing an incompatible version when nemo-toolkit is installed. The PyTorch version 2.3.2 reported by the user, having been pulled in as a dependency, is therefore the root of the incompatibility.

## **Section 2: Priority Solution: Correcting the PyTorch and NeMo Environment on Windows**

This section provides the most direct and immediate solution to resolve the CUDA kernel compatibility error. The strategy is to manually construct a compatible environment by installing the correct PyTorch version before installing the NeMo toolkit. This approach directly addresses the root cause identified in the previous section.

### **2.1 Step 1: Establish a Clean Python Virtual Environment**

To prevent conflicts with any previously installed packages or system-level Python installations, it is imperative to begin with a clean, isolated virtual environment. This ensures that the subsequent steps operate on a known, controlled software stack.

Using a terminal (Command Prompt or PowerShell), execute the following commands to create and activate a new virtual environment. It is recommended to create this in the project's root directory.

Bash

\# Navigate to your project directory  
\# cd C:\\path\\to\\your\\project

\# Create a new virtual environment named 'nemo\_rtx5090\_env'  
python \-m venv nemo\_rtx5090\_env

\# Activate the virtual environment. The command prompt will now be prefixed with the environment name.  
.\\nemo\_rtx5090\_env\\Scripts\\activate

All subsequent pip commands in this section should be run from within this activated environment.

### **2.2 Step 2: Installing the Requisite PyTorch Nightly Build (The Critical Fix)**

The core of the solution is to install a version of PyTorch that has been compiled with support for the Blackwell architecture's Compute Capability 12.0. This support is not available in the stable releases but is present in the **PyTorch nightly builds**. These builds are compiled against the latest CUDA toolkits (12.8 or newer) and include the necessary sm\_120 kernel images.2

Execute the following command to install the latest pre-release (nightly) versions of torch, torchvision, and torchaudio from the dedicated nightly channel for CUDA 12.8+. This is the single most important command to fix the issue.

Bash

\# This command fetches and installs the PyTorch nightly build, along with its companion libraries,  
\# compiled for a CUDA 12.8+ environment. The '--pre' flag allows installation of pre-releases.  
pip3 install \--pre torch torchvision torchaudio \--index-url https://download.pytorch.org/whl/nightly/cu128

This command was identified as the official solution for Windows users with RTX 50-series GPUs in PyTorch's GitHub issue tracker and has been confirmed to work by community members in developer forums.4

### **2.3 Step 3: Installing the NeMo Toolkit into the Corrected Environment**

With a compatible PyTorch version now installed and active in the virtual environment, the NeMo toolkit can be installed. When pip processes the dependencies for nemo-toolkit, it will detect that the pytorch requirement is already satisfied by the nightly build and will not attempt to download or replace it.

Bash

\# Install the core NeMo toolkit along with its ASR-specific dependencies.  
pip install nemo\_toolkit\[asr\]

This sequence correctly resolves the "dependency inversion" issue, ensuring that NeMo is layered on top of a functional, hardware-aware PyTorch installation.

### **2.4 Step 4: Verification and Validation**

After the installation is complete, it is crucial to verify that the environment is correctly configured. Run the following Python script from within the activated virtual environment to confirm that PyTorch recognizes the RTX 5090 and is using the correct CUDA backend.

Python

import torch

print("--- PyTorch and CUDA Verification \---")  
try:  
    print(f"PyTorch Version: {torch.\_\_version\_\_}")  
      
    cuda\_available \= torch.cuda.is\_available()  
    print(f"CUDA Available: {cuda\_available}")

    if cuda\_available:  
        print(f"CUDA Version (used by PyTorch): {torch.version.cuda}")  
          
        device\_count \= torch.cuda.device\_count()  
        print(f"Number of GPUs: {device\_count}")  
          
        for i in range(device\_count):  
            print(f"\\n--- GPU {i} \---")  
            device\_name \= torch.cuda.get\_device\_name(i)  
            print(f"  Device Name: {device\_name}")  
              
            \# Check for RTX 5090  
            if "5090" not in device\_name:  
                print("  WARNING: Expected RTX 5090, but a different GPU was found.")

            capability \= torch.cuda.get\_device\_capability(i)  
            print(f"  Device Compute Capability: {capability}")

            \# Verify Compute Capability for Blackwell  
            if capability\!= (12, 0):  
                print(f"  WARNING: Expected Compute Capability (12, 0\) for RTX 5090, but got {capability}.")  
              
            \# Perform a simple tensor operation on the GPU  
            tensor \= torch.randn(3, 3).to(f"cuda:{i}")  
            print(f"  Successfully created a tensor on cuda:{i}")  
            print(f"  Tensor: \\n{tensor}")

    else:  
        print("\\nERROR: PyTorch cannot find a CUDA-enabled GPU. The installation may be incorrect.")

except Exception as e:  
    print(f"\\nAn error occurred during verification: {e}")

print("\\n--- Verification Complete \---")

The expected output from this script should confirm:

* CUDA Available: True  
* CUDA Version (used by PyTorch) is 12.8 or a higher version number.  
* Device Name is NVIDIA GeForce RTX 5090\.  
* Device Compute Capability is (12, 0).  
* The script completes without errors.

If this output is achieved, the environment is correctly configured, and the original NeMo model loading script should now execute successfully.

| Component | Recommended Version / Specification | Installation Command / Source | Key Notes |
| :---- | :---- | :---- | :---- |
| **Operating System** | Windows 11 | \- | WSL2 is highly recommended for advanced use and long-term stability. |
| **NVIDIA Driver** | \>= 576.57 (User has 576.80) | ([https://www.nvidia.com/Download/index.aspx](https://www.nvidia.com/Download/index.aspx)) | The user's current driver is recent and fully sufficient.19 No change is needed. |
| **Python** | 3.11.x (User has 3.11.13) | python.org | NeMo requires Python \>=3.10. The user's version is compatible.15 |
| **PyTorch** | Nightly Build (e.g., 2.7.1+) | pip3 install \--pre torch \--index-url https://download.pytorch.org/whl/nightly/cu128 | **This is the critical fix.** Must be installed *before* NeMo into a clean virtual environment.4 |
| **NeMo Toolkit** | 2.3.2 (or latest) | pip install nemo\_toolkit\[asr\] | Install *after* the correct PyTorch version is already present in the environment. |
| **CUDA Toolkit (Optional)** | 12.8 or 12.9 | ([https://developer.nvidia.com/cuda-toolkit-archive](https://developer.nvidia.com/cuda-toolkit-archive)) | Only required for compiling custom C++/CUDA extensions from source, not for running the above stack.8 |
| **cuDNN (Optional)** | \>= 9.x for CUDA 12.x | ([https://developer.nvidia.com/rdp/cudnn-archive](https://developer.nvidia.com/rdp/cudnn-archive)) | Bundled with the PyTorch binaries. A manual install is only needed if building PyTorch or other libraries from source.21 |

## **Section 3: Comprehensive Environment and Installation Guide for Windows**

While the priority solution resolves the immediate problem, a deeper understanding of the full development stack is beneficial, particularly if the project requires compiling custom CUDA extensions or other third-party libraries from source. This section provides a detailed guide to setting up a complete CUDA development environment on Windows from the ground up.

### **3.1 NVIDIA Driver Installation and Verification**

The NVIDIA driver is the foundational software layer that allows the operating system to communicate with the GPU. The user's currently installed driver, version 576.80, is a recent release and is fully compatible with the RTX 5090 and CUDA 12.9.19 No action is required.

For future reference or clean installations, driver integrity can be verified by:

1. **NVIDIA Control Panel:** Right-click the desktop, select "NVIDIA Control Panel," and navigate to "System Information" in the bottom-left corner to view the driver version.  
2. **Command Line (nvidia-smi):** Open a Command Prompt or PowerShell and run nvidia-smi. The output will display the driver version in the top-left corner and the highest supported CUDA API version (e.g., "CUDA Version: 12.9") in the top-right.

### **3.2 Installing the Full CUDA Toolkit (When and Why You Need It)**

As established, the PyTorch binaries installed via pip are self-contained and include the necessary CUDA runtime libraries. Therefore, for running pre-compiled models with PyTorch and NeMo, a system-wide installation of the CUDA Toolkit is **not required**.

However, the full CUDA Toolkit becomes essential under the following circumstances:

* Compiling PyTorch from source.  
* Building custom C++ or CUDA extensions for PyTorch.  
* Compiling third-party libraries that have CUDA-accelerated components and do not provide pre-built wheels (e.g., older versions of flash-attn).8

To install the full toolkit for these development scenarios:

1. **Download:** Navigate to the official([https://developer.nvidia.com/cuda-toolkit-archive](https://developer.nvidia.com/cuda-toolkit-archive)).  
2. **Select Version:** Choose a version that supports the Blackwell architecture, such as **CUDA Toolkit 12.9** or 12.8.19  
3. **Select Platform:** Choose the options for Windows, x86\_64, Windows 11, and the exe (local) installer type.  
4. **Run Installer:** Execute the downloaded installer. During installation, it is recommended to use the "Custom (Advanced)" option and select only the components needed. If the driver is already up-to-date, it can be deselected to avoid a downgrade. The core components are the "CUDA Development" tools, including the nvcc compiler.  
5. **Verify Installation:** After installation, open a new Command Prompt and run nvcc \-V. This should return the version of the installed CUDA Toolkit, confirming that the nvcc compiler is accessible.24

### **3.3 Configuring Windows Environment Variables: CUDA\_HOME and PATH**

Many development tools and build scripts rely on environment variables to locate the CUDA Toolkit installation. On Linux, this is typically handled with export commands, but on Windows, a graphical interface is used.25 The CUDA Toolkit installer usually sets these variables automatically, but it is crucial to know how to verify and set them manually.

To access the Environment Variables panel on Windows 11:

1. Press the Windows key and type "Edit the system environment variables," then select the matching Control Panel result.  
2. In the "System Properties" window that appears, click the "Environment Variables..." button.24

Within the "Environment Variables" dialog, check the "System variables" section for the following:

* **CUDA\_HOME**: This variable should point to the root of the CUDA Toolkit installation. If it is not present, create it.  
  * **Variable name:** CUDA\_HOME  
  * **Variable value:** C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.9 (adjust version number as needed) 9  
* **Path**: The system's Path variable must contain the paths to the CUDA compiler and other essential binaries. Select the Path variable, click "Edit...", and ensure the following two entries exist. If not, add them using the "New" button.  
  * %CUDA\_HOME%\\bin  
  * %CUDA\_HOME%\\libnvvp

These settings ensure that tools invoked from any command line can find nvcc.exe and other required libraries.29

### **3.4 Manual Installation and Verification of cuDNN**

The NVIDIA CUDA Deep Neural Network library (cuDNN) is a GPU-accelerated library of primitives for deep neural networks. Similar to the CUDA runtime, the required cuDNN libraries are bundled with the PyTorch binaries.6 A manual installation is only necessary when building frameworks or custom kernels from source.

To install cuDNN manually on Windows:

1. **Download:** Go to the([https://developer.nvidia.com/rdp/cudnn-archive](https://developer.nvidia.com/rdp/cudnn-archive)). An NVIDIA Developer account is required.  
2. **Select Version:** Download a version of cuDNN that is compatible with the installed CUDA Toolkit. For CUDA 12.x, any recent cuDNN 9.x version is appropriate.21 Select the "Local Installer for Windows (Zip)" option.  
3. **Extract Files:** Unzip the downloaded archive to a temporary location. It will contain bin, include, and lib folders.  
4. **Copy to CUDA Toolkit Directory:** Manually copy the contents of the extracted folders into their corresponding locations within the CUDA\_HOME directory established in the previous step.27  
   * Copy the contents of the bin folder (e.g., cudnn\*.dll) to C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.9\\bin.  
   * Copy the contents of the include folder (e.g., cudnn\*.h) to C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.9\\include.  
   * Copy the contents of the lib folder (e.g., cudnn\*.lib) to C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.9\\lib.

This process effectively merges the cuDNN library into the main CUDA Toolkit installation, making it available to any tool (like nvcc) that needs it during compilation.

## **Section 4: Robust Alternative: A Docker-Based Solution via WSL2**

While the direct environment fix in Section 2 is effective, it can be brittle. Host system updates, changes in Python versions, or conflicting package dependencies can easily break the environment in the future. For professional development, deployment, and long-term project maintainability, a containerized approach is the superior solution. This method provides a completely isolated, reproducible, and optimized environment, mitigating the vast majority of "works on my machine" issues.

### **4.1 The Case for Containerization: Reproducibility and Stability**

Using Docker with the Windows Subsystem for Linux (WSL2) backend offers several compelling advantages for machine learning development:

* **Dependency Isolation:** All project dependencies—from the OS libraries to the Python interpreter and specific package versions—are encapsulated within the Docker image. This prevents any conflict with software installed on the host Windows system.  
* **Environment Consistency:** The exact same Docker image can be used by all team members and, more importantly, in production deployment, guaranteeing that the environment is identical everywhere.  
* **Leveraging NVIDIA NGC:** NVIDIA provides official, pre-built Docker containers on their NGC (NVIDIA GPU Cloud) catalog. These containers are highly optimized for performance and come with tested, compatible versions of the NVIDIA driver, CUDA toolkit, cuDNN, and frameworks like PyTorch, saving significant setup and debugging time.15

### **4.2 Step-by-Step Guide: Installing and Configuring WSL2 on Windows 11**

WSL2 allows running a genuine Linux kernel directly on Windows, providing the performance and compatibility needed for Docker.

1. **Enable Required Windows Features:** Ensure "Virtual Machine Platform" and "Windows Subsystem for Linux" are enabled in "Turn Windows features on or off."  
2. **Install WSL and Ubuntu:** Open PowerShell as an Administrator and execute the following commands. This will install WSL, download the latest Linux kernel, and set up an Ubuntu distribution.36  
   PowerShell  
   \# Installs WSL and the default Ubuntu distribution  
   wsl \-\-install \-d Ubuntu

   \# Ensures the WSL kernel is up to date  
   wsl \-\-update

   \# Sets WSL 2 as the default for all future installations  
   wsl \-\-set-default-version 2

3. **Initialize Ubuntu:** Launch "Ubuntu" from the Start Menu for the first time to complete the installation and create a user account and password for the Linux environment.

### **4.3 Step-by-Step Guide: Installing Docker Desktop and NVIDIA Container Toolkit**

Docker Desktop for Windows can integrate seamlessly with WSL2 to run Linux containers.

1. **Install Docker Desktop:** Download and install the latest version of Docker Desktop for Windows. During setup, ensure the option "Use WSL 2 instead of Hyper-V (recommended)" is selected.39  
2. **Configure WSL Integration:** After installation, open Docker Desktop. Navigate to Settings \> Resources \> WSL Integration. Ensure that integration is enabled for the Ubuntu distribution installed in the previous step. This allows Docker commands run from Windows to operate within the WSL environment.39  
3. **Install NVIDIA Container Toolkit:** This step is performed *inside the WSL/Ubuntu terminal*. It allows containers to securely access the host machine's GPU. Open the Ubuntu terminal and execute the following commands to add the NVIDIA container toolkit repository and install the package.37  
   Bash  
   \# Set up the repository configuration  
   curl \-fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg \--dearmor \-o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \\  
     && curl \-s \-L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \\  
       sed 's\#deb https://\#deb \[signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg\] https://\#g' | \\  
       sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

   \# Update package lists and install the toolkit  
   sudo apt-get update  
   sudo apt-get install \-y nvidia-container-toolkit

   \# Configure the Docker daemon to recognize the NVIDIA runtime  
   sudo nvidia-ctk runtime configure \--runtime=docker

   \# Restart the Docker daemon to apply the changes. This can be done by restarting Docker Desktop.

### **4.4 Deploying the Application in an NVIDIA PyTorch Container**

With the infrastructure in place, the application can now be run inside an official NVIDIA PyTorch container. These containers are versioned monthly (e.g., 25.04 for April 2025\) and include the latest compatible software stack. The 25.04 release, for instance, includes PyTorch built against CUDA 12.9, making it ideal for the RTX 5090\.40

1. **Pull the Container:** From a Windows PowerShell or Command Prompt, pull the desired container from the NGC registry.  
   Bash  
   docker pull nvcr.io/nvidia/pytorch:25.04-py3

2. **Run the Container:** Start an interactive session inside the container. Use the \--gpus all flag to grant access to the host's GPU(s) and mount the local project directory into the container's /workspace directory.  
   Bash  
   \# Replace C:\\path\\to\\your\\project with the actual path to your project files  
   docker run \--gpus all \-it \--rm \-v C:\\path\\to\\your\\project:/workspace nvcr.io/nvidia/pytorch:25.04-py3 /bin/bash

3. **Install NeMo and Run:** The terminal prompt will now be a bash shell *inside the container*. From here, install NeMo and run the application as usual.  
   Bash  
   \# Now inside the container's bash shell  
   cd /workspace

   \# The container already has a compatible PyTorch, so just install NeMo  
   pip install nemo\_toolkit\[asr\]

   \# Run the application script  
   python your\_application\_script.py

### **4.5 Verification: Running nvidia-smi Inside the Container**

To confirm that the GPU has been successfully passed through from the Windows host to the Linux container, run nvidia-smi from within the container's bash shell.

Bash

\# Inside the running container  
nvidia-smi

The output should be identical to running the same command on the host Windows PowerShell, showing the RTX 5090, driver version, and CUDA version. This confirms the entire stack—from the Windows driver through WSL2 and Docker to the container—is functioning correctly.38

## **Section 5: Advanced Debugging and Diagnostics**

For complex issues that persist beyond environment correction, or for performance tuning, a deeper level of debugging is necessary. The following tools and techniques provide granular insight into the execution of CUDA kernels.

### **5.1 Synchronous Error Reporting with CUDA\_LAUNCH\_BLOCKING=1**

By default, CUDA kernel launches are asynchronous. The CPU issues a command to the GPU and immediately continues executing the next line of code without waiting for the GPU to finish. While this is efficient, it can make debugging difficult. An error occurring within a GPU kernel might not be reported back to the CPU until a later, unrelated synchronization point (e.g., copying data back from the GPU). This results in a misleading stack trace that points to the wrong line of code.2

Setting the environment variable CUDA\_LAUNCH\_BLOCKING=1 forces every kernel launch to be synchronous. The CPU will wait for the kernel to complete before moving on. This ensures that if a kernel fails, the error is reported immediately, and the stack trace will point directly to the API call that launched the faulty kernel.

**Usage (in PowerShell before running the script):**

PowerShell

$env:CUDA\_LAUNCH\_BLOCKING\=1  
python your\_application\_script.py

This should be used for debugging only, as it severely degrades performance.

### **5.2 Enabling Device-Side Assertions with TORCH\_USE\_CUDA\_DSA**

This PyTorch-specific environment variable enables Device-Side Assertions. When compiled with this flag, CUDA kernels can include assert() statements that are executed directly on the GPU. This is useful for catching logical errors within the kernel code itself, such as out-of-bounds memory accesses or invalid intermediate values. The user's original error message recommended this as a debugging step.

**Usage (in PowerShell before running the script):**

PowerShell

$env:TORCH\_USE\_CUDA\_DSA\=1  
python your\_application\_script.py

Combining this with CUDA\_LAUNCH\_BLOCKING=1 provides the most precise error reporting for kernel-level failures.

### **5.3 A Primer on Kernel Debugging with NVIDIA Nsight Visual Studio Edition**

For the most powerful and interactive debugging experience on Windows, NVIDIA Nsight Visual Studio Edition (VSE) is the primary tool. It integrates directly into Visual Studio and allows for graphical debugging of CUDA C++ code, much like debugging standard CPU code.42

A high-level debugging workflow involves the following steps:

1. **Installation:** Nsight VSE can be installed as part of the CUDA Toolkit installation or downloaded separately. It requires a supported version of Microsoft Visual Studio (e.g., 2019, 2022).44  
2. **Project Configuration:** The application must be compiled with debug information. In the Visual Studio project properties, this typically involves setting a flag like \-G0 for the nvcc compiler to generate GPU debug symbols.46  
3. **Start Nsight Monitor:** The Nsight Monitor must be running in the system tray. This service handles the communication between the debugger and the GPU driver.47  
4. **Launch Debugger:** Instead of the standard "Start Debugging (F5)," the session is initiated from the Visual Studio menu via Nsight \> Start CUDA Debugging (Next-Gen).48  
5. **Set Breakpoints and Inspect:** Developers can set breakpoints directly within .cu files containing kernel code. When a GPU thread hits a breakpoint, execution halts, and the developer can use the Nsight debugger windows to:  
   * Inspect the values of variables in GPU memory (Locals, Watch windows).47  
   * View the state of all threads within a warp (CUDA Warp Watch).43  
   * Examine raw GPU memory contents (Memory window).48  
   * Step through kernel code line by line (F11 for Step Into, F10 for Step Over).

While this level of debugging is not required to fix the user's current problem, it is an invaluable skill for any developer writing or customizing CUDA kernels.

### **5.4 NeMo-Specific Debugging Flags**

The NeMo framework and its underlying components (like NVIDIA NIM) offer several environment variables for controlling logging verbosity, which can be useful during model initialization. While many are specific to the NIM deployment service, the NIM\_LOG\_LEVEL variable is a common pattern.49 Setting this to

DEBUG can provide more detailed output during the from\_pretrained call.

**Usage (in PowerShell):**

PowerShell

$env:NIM\_LOG\_LEVEL\="DEBUG"  
python your\_application\_script.py

Additionally, NeMo configuration files (formerly YAML, now Python-based in NeMo 2.0) offer extensive options for controlling behavior, and reviewing the launcher configurations can reveal other debugging or environment settings.15

## **Section 6: Fallbacks and Model Alternatives**

Given that the RTX 5090 is new hardware and its support in some frameworks is still in a "Beta" state 52, it is prudent to have contingency plans. If instability persists even with the correct environment, or if performance is not as expected, the following fallbacks and alternatives should be considered.

### **6.1 Code Modification for CPU Fallback and Performance Considerations**

For purely functional testing (i.e., to verify that the application logic works, independent of the GPU), the NeMo model can be loaded onto the CPU. This is achieved with a minor modification to the model loading call.

Python

\# Original code:  
\# self.model \= nemo\_asr.models.ASRModel.from\_pretrained(  
\#     "nvidia/parakeet-tdt-1.1b",  
\#     map\_location="cuda"  
\# ).to(dtype=torch.float16)

\# Modified code for CPU fallback:  
\# Change map\_location to "cpu" and remove the subsequent.to() call.  
\# The dtype conversion to float16 is a GPU optimization and should be removed for CPU.  
self.model \= nemo\_asr.models.ASRModel.from\_pretrained(  
    "nvidia/parakeet-tdt-1.1b",  
    map\_location="cpu"  
)

It must be emphasized that this is **not a viable solution for a real-time dictation system**. ASR model inference is computationally intensive, and performance on a CPU will be orders of magnitude slower than on the RTX 5090, making real-time transcription impossible. This method should only be used for temporary debugging and validation purposes.

### **6.2 Exploring Alternative NeMo ASR Models**

The NVIDIA NeMo framework offers a family of high-performance ASR models. If the Parakeet-TDT-1.1B model proves to be unstable on the new hardware, switching to a different but related model is a sound strategy. These models can be loaded using the same ASRModel.from\_pretrained() method, requiring minimal code changes.

Key alternatives include:

* **Parakeet-RNNT-1.1B:** This model uses the same FastConformer encoder but employs a Recurrent Neural Network Transducer (RNN-T) decoder instead of the Token-and-Duration Transducer (TDT) decoder. RNN-T is a more mature and widely deployed architecture for streaming ASR. While its measured Real-Time Factor (RTF) may be slightly lower than the TDT variant, its stability is well-established.55  
* **Parakeet-TDT-0.6B-v2:** A smaller, 600-million-parameter version of the TDT model. It offers exceptionally fast inference speeds, often outperforming much larger models like Whisper Large, while maintaining very competitive accuracy. For a real-time system where latency is critical, this model could be an excellent choice, trading a small amount of accuracy for a significant speed-up.58  
* **Canary-1B:** This is NVIDIA's state-of-the-art multilingual and multi-task model. It uses a FastConformer encoder with a Transformer decoder. While its primary strength is handling multiple languages (English, German, French, Spanish) and performing speech-to-text translation, it is also a top-performing model for English-only ASR. Its different decoder architecture might offer different stability characteristics on the new hardware.60

| Model Name | Base Architecture | Parameters | Key Strengths | Noted Limitations / Considerations |
| :---- | :---- | :---- | :---- | :---- |
| **Parakeet-TDT-1.1B** | FastConformer \+ TDT | 1.1B | Excellent accuracy (low Word Error Rate), very fast inference due to TDT decoder skipping blank predictions.64 | "Beta" support status on RTX 50-series hardware suggests potential for undiscovered issues.52 |
| **Parakeet-RNNT-1.1B** | FastConformer \+ RNN-T | 1.1B | State-of-the-art accuracy, robust and mature architecture, well-suited for streaming ASR.55 | Slightly slower Real-Time Factor (RTF) compared to the TDT version. Vocabulary size is fixed at 1024\.56 |
| **Parakeet-TDT-0.6B-v2** | FastConformer \+ TDT | 600M | Extremely fast inference, highly resource-efficient, and holds a top position on ASR leaderboards for its size.58 | Word Error Rate (WER) is slightly higher than its 1.1B counterparts, but still excellent. |
| **Canary-1B** | FastConformer \+ Transformer | 1B | State-of-the-art multilingual (En, De, Fr, Es) and speech-to-text translation capabilities; top-tier English ASR performance.60 | Encoder-decoder architecture may have different latency characteristics than transducer models for pure ASR tasks. |

## **Section 7: Final Recommendations and Best Practices**

Resolving the CUDA compatibility issue for the RTX 5090 requires a targeted approach that acknowledges the nature of working with next-generation hardware. The following recommendations synthesize the findings of this report into actionable pathways and long-term best practices.

### **7.1 The Recommended Solution Pathway**

A tiered approach is recommended based on project needs for speed of resolution versus long-term robustness:

1. **Immediate Resolution (Primary Path):** For the fastest path to a functional system, follow the steps outlined in **Section 2**. Create a clean Python virtual environment, manually install the **PyTorch nightly build for CUDA 12.8+**, and then install the NeMo toolkit. This directly resolves the kernel incompatibility with minimal overhead.  
2. **Robust Development and Deployment (Recommended Path):** For any serious development effort intended for production, the **Docker \+ WSL2 workflow described in Section 4** is the superior choice. By leveraging official NVIDIA PyTorch containers, this method provides a stable, reproducible, and highly optimized environment that is insulated from host system vagaries. This approach aligns with modern MLOps best practices and will significantly reduce environment-related issues throughout the project lifecycle.

### **7.2 Best Practices for Developing on Bleeding-Edge GPU Hardware**

Working with brand-new hardware like the RTX 5090 places a developer at the forefront of the technology curve, which necessitates certain practices:

* **Embrace Non-Stable Builds:** Expect that stable releases of major frameworks will not have immediate support for new hardware. Default to using nightly, preview, or release candidate builds of critical libraries like PyTorch and TensorFlow for initial development.  
* **Monitor Community Channels:** Actively monitor the official support channels for the tools in use. This includes the NVIDIA Developer Forums, the PyTorch GitHub Issues page, and the NVIDIA NeMo GitHub repository. These are often the first places where compatibility issues are reported and solutions are posted.  
* **Prioritize Containerization:** Make containerization a default part of the development workflow. The time invested in setting up Docker and WSL2 is paid back manifold by eliminating environment-specific bugs and ensuring smooth transitions between development, testing, and production.  
* **Maintain a Fallback Plan:** As demonstrated in Section 6, identify and test alternative models or libraries that can serve as a fallback if the primary choice proves unstable on the new hardware. This is a critical risk mitigation strategy for time-sensitive projects.

### **7.3 Key Resources and Community Links**

For ongoing support and access to the necessary software components, the following resources are invaluable:

* **PyTorch Nightly Builds:** [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/) (Select "Preview (Nightly)") 65  
* **NVIDIA CUDA Toolkit Archive:** [https://developer.nvidia.com/cuda-toolkit-archive](https://developer.nvidia.com/cuda-toolkit-archive) 24  
* **NVIDIA cuDNN Archive:** [https://developer.nvidia.com/rdp/cudnn-archive](https://developer.nvidia.com/rdp/cudnn-archive) 30  
* **NVIDIA NeMo GitHub Repository:**(https://github.com/NVIDIA/NeMo) 15  
* **NVIDIA Developer Forums (CUDA Setup):** [https://forums.developer.nvidia.com/c/accelerated-computing/cuda/cuda-setup-and-installation/](https://forums.developer.nvidia.com/c/accelerated-computing/cuda/cuda-setup-and-installation/) 2  
* **NVIDIA NGC Container Catalog:** [https://catalog.ngc.nvidia.com/containers](https://catalog.ngc.nvidia.com/containers) 34

#### **Works cited**

1. CUDA GPU Compute Capability | NVIDIA Developer, accessed July 15, 2025, [https://developer.nvidia.com/cuda-gpus](https://developer.nvidia.com/cuda-gpus)  
2. Rtx 5090 \- GPU \- Hardware \- NVIDIA Developer Forums, accessed July 15, 2025, [https://forums.developer.nvidia.com/t/rtx-5090/331369](https://forums.developer.nvidia.com/t/rtx-5090/331369)  
3. How to enable PyTorch RTX 5090 with sm\_120 support? \- Super User, accessed July 15, 2025, [https://superuser.com/questions/1905004/how-to-enable-pytorch-rtx-5090-with-sm-120-support](https://superuser.com/questions/1905004/how-to-enable-pytorch-rtx-5090-with-sm-120-support)  
4. NVIDIA GeForce RTX 5090 \- PyTorch Forums, accessed July 15, 2025, [https://discuss.pytorch.org/t/nvidia-geforce-rtx-5090/218954](https://discuss.pytorch.org/t/nvidia-geforce-rtx-5090/218954)  
5. PyTorch for Cuda 12, accessed July 15, 2025, [https://discuss.pytorch.org/t/pytorch-for-cuda-12/169447](https://discuss.pytorch.org/t/pytorch-for-cuda-12/169447)  
6. Compatibility between CUDA 12.6 and PyTorch, accessed July 15, 2025, [https://discuss.pytorch.org/t/compatibility-between-cuda-12-6-and-pytorch/209649](https://discuss.pytorch.org/t/compatibility-between-cuda-12-6-and-pytorch/209649)  
7. How to use torch with CUDA 12.9 \- windows \- PyTorch Forums, accessed July 15, 2025, [https://discuss.pytorch.org/t/how-to-use-torch-with-cuda-12-9/220827](https://discuss.pytorch.org/t/how-to-use-torch-with-cuda-12-9/220827)  
8. Is cuda installed automatically when following pytorch instlalation directions?, accessed July 15, 2025, [https://discuss.pytorch.org/t/is-cuda-installed-automatically-when-following-pytorch-instlalation-directions/215493](https://discuss.pytorch.org/t/is-cuda-installed-automatically-when-following-pytorch-instlalation-directions/215493)  
9. python \- Get CUDA\_HOME environment path PYTORCH \- Stack Overflow, accessed July 15, 2025, [https://stackoverflow.com/questions/52731782/get-cuda-home-environment-path-pytorch](https://stackoverflow.com/questions/52731782/get-cuda-home-environment-path-pytorch)  
10. 1\. Blackwell Architecture Compatibility \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/cuda/blackwell-compatibility-guide/](https://docs.nvidia.com/cuda/blackwell-compatibility-guide/)  
11. PNY GeForce RTX 5090 Models GPUs, accessed July 15, 2025, [https://www.pny.com/geforce-rtx-5090-models](https://www.pny.com/geforce-rtx-5090-models)  
12. Blackwell (microarchitecture) \- Wikipedia, accessed July 15, 2025, [https://en.wikipedia.org/wiki/Blackwell\_(microarchitecture)](https://en.wikipedia.org/wiki/Blackwell_\(microarchitecture\))  
13. The Engine Behind AI Factories | NVIDIA Blackwell Architecture, accessed July 15, 2025, [https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/)  
14. Can I use my NVIDIA Blackwell architecture GPU with MATLAB for GPU Computing?, accessed July 15, 2025, [https://ch.mathworks.com/matlabcentral/answers/2173867-can-i-use-my-nvidia-blackwell-architecture-gpu-with-matlab-for-gpu-computing](https://ch.mathworks.com/matlabcentral/answers/2173867-can-i-use-my-nvidia-blackwell-architecture-gpu-with-matlab-for-gpu-computing)  
15. NVIDIA/NeMo: A scalable generative AI framework built for ... \- GitHub, accessed July 15, 2025, [https://github.com/NVIDIA/NeMo](https://github.com/NVIDIA/NeMo)  
16. nemo-toolkit \- PyPI, accessed July 15, 2025, [https://pypi.org/project/nemo-toolkit/](https://pypi.org/project/nemo-toolkit/)  
17. RTX 5090 not working with PyTorch and Stable Diffusion (sm\_120 ..., accessed July 15, 2025, [https://forums.developer.nvidia.com/t/rtx-5090-not-working-with-pytorch-and-stable-diffusion-sm-120-unsupported/338015](https://forums.developer.nvidia.com/t/rtx-5090-not-working-with-pytorch-and-stable-diffusion-sm-120-unsupported/338015)  
18. How to install Torch version that supports RTX 5090 on Windows? \- CUDA kernel errors might be asynchronously reported at some other API call \#146977 \- GitHub, accessed July 15, 2025, [https://github.com/pytorch/pytorch/issues/146977](https://github.com/pytorch/pytorch/issues/146977)  
19. CUDA Toolkit 12.9 Update 1 \- Release Notes \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)  
20. NVIDIA Studio Driver 576.80 | Windows 11, accessed July 15, 2025, [https://www.nvidia.com/en-us/drivers/details/247854/](https://www.nvidia.com/en-us/drivers/details/247854/)  
21. Support Matrix — NVIDIA cuDNN Backend, accessed July 15, 2025, [https://docs.nvidia.com/deeplearning/cudnn/backend/latest/reference/support-matrix.html](https://docs.nvidia.com/deeplearning/cudnn/backend/latest/reference/support-matrix.html)  
22. NVIDIA's v580 Driver Branch Ends Support for Maxwell, Pascal, and Volta GPUs, accessed July 15, 2025, [https://www.techpowerup.com/338497/nvidias-v580-driver-branch-ends-support-for-maxwell-pascal-and-volta-gpus](https://www.techpowerup.com/338497/nvidias-v580-driver-branch-ends-support-for-maxwell-pascal-and-volta-gpus)  
23. How to find CUDA path inside venv \- PyTorch Forums, accessed July 15, 2025, [https://discuss.pytorch.org/t/how-to-find-cuda-path-inside-venv/191075](https://discuss.pytorch.org/t/how-to-find-cuda-path-inside-venv/191075)  
24. CUDA Installation Guide for Microsoft Windows \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)  
25. PATH & LD\_LIBRARY\_PATH \- CUDA Setup and Installation \- NVIDIA Developer Forums, accessed July 15, 2025, [https://forums.developer.nvidia.com/t/path-ld-library-path/48080](https://forums.developer.nvidia.com/t/path-ld-library-path/48080)  
26. CUDA\_HOME environment variable is not set & No CUDA runtime is found, accessed July 15, 2025, [https://forums.developer.nvidia.com/t/cuda-home-environment-variable-is-not-set-no-cuda-runtime-is-found/179224](https://forums.developer.nvidia.com/t/cuda-home-environment-variable-is-not-set-no-cuda-runtime-is-found/179224)  
27. How to Install cuDNN on Windows \- GPU Mart, accessed July 15, 2025, [https://www.gpu-mart.com/blog/install-cudnn-on-windows](https://www.gpu-mart.com/blog/install-cudnn-on-windows)  
28. Installing Error: CUDA\_HOME environment variable is not set · Issue \#19 · facebookresearch/sam2 \- GitHub, accessed July 15, 2025, [https://github.com/facebookresearch/sam2/issues/19](https://github.com/facebookresearch/sam2/issues/19)  
29. A Guide to Enabling CUDA and cuDNN for TensorFlow on Windows 11 | by Gokulprasath, accessed July 15, 2025, [https://medium.com/@gokulprasath100702/a-guide-to-enabling-cuda-and-cudnn-for-tensorflow-on-windows-11-a89ce11863f1](https://medium.com/@gokulprasath100702/a-guide-to-enabling-cuda-and-cudnn-for-tensorflow-on-windows-11-a89ce11863f1)  
30. cuDNN Archive \- NVIDIA Developer, accessed July 15, 2025, [https://developer.nvidia.com/rdp/cudnn-archive](https://developer.nvidia.com/rdp/cudnn-archive)  
31. Step-by-Step Guide to Installing CUDA and cuDNN for GPU Acceleration | DigitalOcean, accessed July 15, 2025, [https://www.digitalocean.com/community/tutorials/install-cuda-cudnn-for-gpu](https://www.digitalocean.com/community/tutorials/install-cuda-cudnn-for-gpu)  
32. Installing cuDNN Backend on Windows \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/deeplearning/cudnn/installation/latest/windows.html](https://docs.nvidia.com/deeplearning/cudnn/installation/latest/windows.html)  
33. How to make Nvidia GPU RTX 50 Series work with Nvidia PyTorch Container \- Medium, accessed July 15, 2025, [https://medium.com/@kirillchufarov/how-to-make-nvidia-gpu-50-series-work-with-pytorch-14838d811b7b](https://medium.com/@kirillchufarov/how-to-make-nvidia-gpu-50-series-work-with-pytorch-14838d811b7b)  
34. PyTorch with CUDA 12.9 – Official Support or Workarounds? \- Reddit, accessed July 15, 2025, [https://www.reddit.com/r/CUDA/comments/1l4yvhl/pytorch\_with\_cuda\_129\_official\_support\_or/](https://www.reddit.com/r/CUDA/comments/1l4yvhl/pytorch_with_cuda_129_official_support_or/)  
35. Install NeMo Framework \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nemo-framework/user-guide/latest/installation.html](https://docs.nvidia.com/nemo-framework/user-guide/latest/installation.html)  
36. Enable NVIDIA CUDA on WSL 2 \- Learn Microsoft, accessed July 15, 2025, [https://learn.microsoft.com/en-us/windows/ai/directml/gpu-cuda-in-wsl](https://learn.microsoft.com/en-us/windows/ai/directml/gpu-cuda-in-wsl)  
37. Setting up Docker with GPU support for Windows 11 \- Test and deploy your container, accessed July 15, 2025, [https://grand-challenge.org/documentation/setting-up-wsl-with-gpu-support-for-windows-11/](https://grand-challenge.org/documentation/setting-up-wsl-with-gpu-support-for-windows-11/)  
38. Setup Windows 10/11 machines for Deep Learning with Docker and GPU using WSL, accessed July 15, 2025, [https://gdevakumar.medium.com/setup-windows-10-11-machines-for-deep-learning-with-docker-and-gpu-using-wsl-9349f0224971](https://gdevakumar.medium.com/setup-windows-10-11-machines-for-deep-learning-with-docker-and-gpu-using-wsl-9349f0224971)  
39. Docker Desktop WSL 2 backend on Windows, accessed July 15, 2025, [https://docs.docker.com/desktop/features/wsl/](https://docs.docker.com/desktop/features/wsl/)  
40. PyTorch Release 25.04 \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-25-04.html](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-25-04.html)  
41. GPU support \- Docker Docs, accessed July 15, 2025, [https://docs.docker.com/desktop/features/gpu/](https://docs.docker.com/desktop/features/gpu/)  
42. Introduction — nsight-visual-studio-edition 12.9 documentation \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nsight-visual-studio-edition/introduction/index.html](https://docs.nvidia.com/nsight-visual-studio-edition/introduction/index.html)  
43. NVIDIA Nsight Visual Studio Edition, accessed July 15, 2025, [https://docs.nvidia.com/nsight-visual-studio-edition/index.html](https://docs.nvidia.com/nsight-visual-studio-edition/index.html)  
44. NVIDIA Nsight Visual Studio Edition 2025.1.0.25002 Setup stuck on "Configuring Visual Studio 2022 settings for Nsight Visual Studio Edition", accessed July 15, 2025, [https://forums.developer.nvidia.com/t/nvidia-nsight-visual-studio-edition-2025-1-0-25002-setup-stuck-on-configuring-visual-studio-2022-settings-for-nsight-visual-studio-edition/323713](https://forums.developer.nvidia.com/t/nvidia-nsight-visual-studio-edition-2025-1-0-25002-setup-stuck-on-configuring-visual-studio-2022-settings-for-nsight-visual-studio-edition/323713)  
45. Installation and Setup — nsight-visual-studio-edition 12.9 documentation \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nsight-visual-studio-edition/install-setup/index.html](https://docs.nvidia.com/nsight-visual-studio-edition/install-setup/index.html)  
46. Walkthrough: Debugging a CUDA Application \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nsight-visual-studio-edition/3.2/Content/Debugging\_CUDA\_Application.htm](https://docs.nvidia.com/nsight-visual-studio-edition/3.2/Content/Debugging_CUDA_Application.htm)  
47. Tutorial: Using the CUDA Debugger \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nsight-visual-studio-edition/3.2/Content/Using\_CUDA\_Debugger.htm](https://docs.nvidia.com/nsight-visual-studio-edition/3.2/Content/Using_CUDA_Debugger.htm)  
48. Getting Started with the CUDA Debugger — nsight-visual-studio-edition 12.9 documentation, accessed July 15, 2025, [https://docs.nvidia.com/nsight-visual-studio-edition/cuda-debugger/](https://docs.nvidia.com/nsight-visual-studio-edition/cuda-debugger/)  
49. Configure NeMo Retriever Text Embedding NIM \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nim/nemo-retriever/text-embedding/latest/configuration.html](https://docs.nvidia.com/nim/nemo-retriever/text-embedding/latest/configuration.html)  
50. Environment Variables \- NeMo Retriever Documentation \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nemo/retriever/extraction/environment-config/](https://docs.nvidia.com/nemo/retriever/extraction/environment-config/)  
51. Understand the Configurations — NVIDIA NeMo Framework User Guide 24.07 documentation, accessed July 15, 2025, [https://docs.nvidia.com/nemo-framework/user-guide/24.07/launcherguide/launchertutorial/understandconf.html](https://docs.nvidia.com/nemo-framework/user-guide/24.07/launcherguide/launchertutorial/understandconf.html)  
52. Support Matrix for NVIDIA NIM for Object Detection, accessed July 15, 2025, [https://docs.nvidia.com/nim/ingestion/object-detection/1.1.0/support-matrix.html](https://docs.nvidia.com/nim/ingestion/object-detection/1.1.0/support-matrix.html)  
53. Support Matrix for NeMo Retriever Text Embedding NIM \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nim/nemo-retriever/text-embedding/1.4.0/support-matrix.html](https://docs.nvidia.com/nim/nemo-retriever/text-embedding/1.4.0/support-matrix.html)  
54. Support Matrix for NeMo Retriever Text Embedding NIM \- NVIDIA Docs, accessed July 15, 2025, [https://docs.nvidia.com/nim/nemo-retriever/text-embedding/1.5.1/support-matrix.html](https://docs.nvidia.com/nim/nemo-retriever/text-embedding/1.5.1/support-matrix.html)  
55. parakeet-tdt-1.1b | AI Model Details \- AIModels.fyi, accessed July 15, 2025, [https://www.aimodels.fyi/models/huggingFace/parakeet-tdt-11b-nvidia](https://www.aimodels.fyi/models/huggingFace/parakeet-tdt-11b-nvidia)  
56. Parakeet Rnnt 1.1b · Models \- Dataloop, accessed July 15, 2025, [https://dataloop.ai/library/model/nvidia\_parakeet-rnnt-11b/](https://dataloop.ai/library/model/nvidia_parakeet-rnnt-11b/)  
57. nvidia/parakeet-rnnt-1.1b \- Hugging Face, accessed July 15, 2025, [https://huggingface.co/nvidia/parakeet-rnnt-1.1b](https://huggingface.co/nvidia/parakeet-rnnt-1.1b)  
58. GLaDOS has been updated for Parakeet 0.6B : r/LocalLLaMA \- Reddit, accessed July 15, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1kosbyy/glados\_has\_been\_updated\_for\_parakeet\_06b/](https://www.reddit.com/r/LocalLLaMA/comments/1kosbyy/glados_has_been_updated_for_parakeet_06b/)  
59. NVIDIA Parakeet-TDT-0.6B-V2: a deep dive into state-of-the-art speech recognition architecture \- QED42, accessed July 15, 2025, [https://www.qed42.com/insights/nvidia-parakeet-tdt-0-6b-v2-a-deep-dive-into-state-of-the-art-speech-recognition-architecture](https://www.qed42.com/insights/nvidia-parakeet-tdt-0-6b-v2-a-deep-dive-into-state-of-the-art-speech-recognition-architecture)  
60. NVIDIA Speech and Translation AI Models Set Records for Speed and Accuracy, accessed July 15, 2025, [https://developer.nvidia.com/blog/nvidia-speech-and-translation-ai-models-set-records-for-speed-and-accuracy/](https://developer.nvidia.com/blog/nvidia-speech-and-translation-ai-models-set-records-for-speed-and-accuracy/)  
61. Models — NVIDIA NeMo Framework User Guide, accessed July 15, 2025, [https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html)  
62. README.md · nvidia/canary-1b at main \- Hugging Face, accessed July 15, 2025, [https://huggingface.co/nvidia/canary-1b/blob/main/README.md](https://huggingface.co/nvidia/canary-1b/blob/main/README.md)  
63. nvidia/canary-1b \- Hugging Face, accessed July 15, 2025, [https://huggingface.co/nvidia/canary-1b](https://huggingface.co/nvidia/canary-1b)  
64. Turbocharge ASR Accuracy and Speed with NVIDIA NeMo Parakeet-TDT, accessed July 15, 2025, [https://developer.nvidia.com/blog/turbocharge-asr-accuracy-and-speed-with-nvidia-nemo-parakeet-tdt/](https://developer.nvidia.com/blog/turbocharge-asr-accuracy-and-speed-with-nvidia-nemo-parakeet-tdt/)  
65. Get Started \- PyTorch, accessed July 15, 2025, [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)