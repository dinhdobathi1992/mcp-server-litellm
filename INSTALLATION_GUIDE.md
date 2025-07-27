# **LiteLLM MCP Server Installation Guide**

This guide provides a step-by-step process to install and set up the LiteLLM MCP Server. It is designed to be beginner-friendly and includes platform-specific instructions for macOS, Linux, and Windows.

---

## **1. System Requirements**

Before installing the LiteLLM MCP Server, ensure your system meets the following requirements:

- **Python Version**: Python 3.8 or higher
- **Operating System Compatibility**:
  - macOS (Intel and Apple Silicon M1/M2)
  - Linux (Ubuntu/Debian, CentOS/RHEL)
  - Windows (via WSL or native installation)
- **Hardware**: At least 4GB of RAM and 2 CPU cores are recommended for smooth operation.

---

## **2. Prerequisites**

Before proceeding with the installation, ensure the following are installed on your system:

1. **Python 3.8+**:
   - Verify Python installation:
     ```bash
     python3 --version
     ```
   - If not installed, refer to platform-specific instructions below.

2. **pip** (Python package manager):
   - Verify pip installation:
     ```bash
     pip --version
     ```
   - If not installed, it is typically bundled with Python or can be installed separately.

3. **Git**:
   - Verify Git installation:
     ```bash
     git --version
     ```
   - Install Git if not already installed.

4. **Virtual Environment Tool**:
   - `venv` is included with Python 3.8+. No additional installation is required.

5. **Text Editor** (optional but recommended):
   - Use a text editor like VS Code, Sublime Text, or Nano to edit configuration files.

---

## **3. Step-by-step Installation**

### **Step 1: Clone the Repository**
1. Open a terminal or command prompt.
2. Clone the LiteLLM MCP Server repository:
   ```bash
   git clone https://github.com/your-organization/litellm-mcp-server.git
   ```
3. Navigate into the project directory:
   ```bash
   cd litellm-mcp-server
   ```

---

### **Step 2: Create a Virtual Environment**
1. Create a virtual environment in the project directory:
   ```bash
   python3 -m venv venv
   ```
2. Activate the virtual environment:
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

---

### **Step 3: Install Dependencies**
1. Upgrade `pip` to the latest version:
   ```bash
   pip install --upgrade pip
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### **Step 4: Set Up Configuration**
1. Copy the example `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open the `.env` file in a text editor and configure the following:
   - **LiteLLM Proxy URL**: Set the URL for the LiteLLM proxy.
   - **MCP Server Port**: Specify the port the server will run on (default: 8000).
   - **Other Environment Variables**: Update as needed for your setup.

3. Save and close the `.env` file.

---

## **4. Platform-specific Instructions**

### **macOS**
1. **Install Python**:
   - Use Homebrew to install Python:
     ```bash
     brew install python
     ```
   - For M1/M2 Macs, ensure you install the ARM-compatible version of Python.

2. **Install Git**:
   - Git is typically pre-installed on macOS. If not, install it via Homebrew:
     ```bash
     brew install git
     ```

3. Follow the general installation steps above.

---

### **Linux**

#### **Ubuntu/Debian**
1. **Install Python and pip**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git -y
   ```

2. Follow the general installation steps above.

#### **CentOS/RHEL**
1. **Install Python and pip**:
   ```bash
   sudo yum install python3 python3-pip python3-virtualenv git -y
   ```

2. Follow the general installation steps above.

---

### **Windows**

#### **Option 1: Using WSL (Recommended)**
1. Install WSL and set up Ubuntu:
   - Follow the official [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install).
2. Open the WSL terminal and follow the **Linux (Ubuntu/Debian)** instructions above.

#### **Option 2: Native Installation**
1. Install Python:
   - Download and install Python from [python.org](https://www.python.org/downloads/).
   - During installation, ensure you check the box to "Add Python to PATH."
2. Install Git:
   - Download and install Git from [git-scm.com](https://git-scm.com/).
3. Follow the general installation steps above.

---

## **5. Verification**

1. Start the LiteLLM MCP Server:
   ```bash
   python main.py
   ```
2. Open a web browser and navigate to:
   ```
   http://localhost:8000
   ```
3. You should see a confirmation page or API response indicating the server is running.

4. Run the test suite (if available):
   ```bash
   pytest
   ```

---

## **6. Troubleshooting**

### **Common Issues and Solutions**

#### **Issue 1: Python Command Not Found**
- Ensure Python is installed and added to your system's PATH.
- Use `python3` instead of `python` on Linux/macOS.

#### **Issue 2: Virtual Environment Activation Fails**
- On Windows, ensure you are using the correct command:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux, ensure you are in the correct directory and use:
  ```bash
  source venv/bin/activate
  ```

#### **Issue 3: Missing Dependencies**
- Ensure you ran the command:
  ```bash
  pip install -r requirements.txt
  ```

#### **Issue 4: Port Already in Use**
- Change the port in the `.env` file to an available port.

#### **Issue 5: Configuration Errors**
- Double-check the `.env` file for typos or missing values.

#### **Issue 6: Permission Denied**
- Use `sudo` for commands requiring elevated privileges (Linux/macOS).

---

By following this guide, you should have the LiteLLM MCP Server installed and running successfully. If you encounter further issues, consult the project's documentation or reach out to the support team. 