# 🐛 VS Code Debugging Guide

This guide provides comprehensive instructions for debugging the Medical Secretary AI application using VS Code.

## 🚀 Quick Start

1. **Open the project in VS Code**
2. **Select the Python interpreter**: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose `.venv/bin/python`
3. **Set breakpoints** by clicking in the left margin of any Python file
4. **Press F5** or go to Run & Debug → Select a configuration → Click the play button

## 🔧 Debug Configurations

### 1. FastAPI Debug (UV) - **Recommended**
- **Purpose**: Debug the main FastAPI application using UV
- **Use Case**: Main development and debugging
- **Features**: Hot reload, integrated terminal, full debugging capabilities

### 2. FastAPI Debug (Direct)
- **Purpose**: Debug using direct Python module execution
- **Use Case**: Alternative to UV, direct Python debugging
- **Features**: Standard Python debugging, no UV dependency

### 3. FastAPI Debug (Attach)
- **Purpose**: Attach to a running FastAPI process
- **Use Case**: Debug production or remote processes
- **Features**: Remote debugging, process attachment

### 4. Test Agent Debug
- **Purpose**: Debug AI agent functionality in isolation
- **Use Case**: Testing agent logic without web server
- **Features**: Focused agent testing, quick iteration

### 5. Database Tools Debug
- **Purpose**: Debug database operations and models
- **Use Case**: Database-related issues, CRUD operations
- **Features**: Database testing, model validation

### 6. Clinic Info Debug
- **Purpose**: Debug clinic information system
- **Use Case**: Clinic data, search functionality
- **Features**: Data validation, search testing

### 7. Docker Debug
- **Purpose**: Debug with Docker environment variables
- **Use Case**: Containerized debugging, production-like environment
- **Features**: Docker environment, production settings

## 🎯 Debugging Workflow

### Setting Breakpoints
1. **Line Breakpoints**: Click in the left margin of any line
2. **Conditional Breakpoints**: Right-click breakpoint → "Edit Breakpoint" → Add condition
3. **Logpoints**: Right-click breakpoint → "Add Logpoint" → Add message

### Debug Console
- **Variables**: Inspect current variable values
- **Watch**: Add expressions to monitor
- **Call Stack**: Navigate through function calls
- **Breakpoints**: Manage all breakpoints

### Debug Controls
- **Continue (F5)**: Resume execution
- **Step Over (F10)**: Execute current line, don't step into functions
- **Step Into (F11)**: Step into function calls
- **Step Out (Shift+F11)**: Complete current function and pause
- **Restart (Ctrl+Shift+F5)**: Restart debugging session
- **Stop (Shift+F5)**: Stop debugging

## 🧪 Testing Individual Components

### Test AI Agent
```bash
# Run from terminal
python test_agent.py

# Or use VS Code task: Ctrl+Shift+P → "Tasks: Run Task" → "Run AI Agent Tests"
```

### Test Database
```bash
# Run from terminal
python test_database.py

# Or use VS Code task: Ctrl+Shift+P → "Tasks: Run Task" → "Run Database Tests"
```

### Test Clinic Info
```bash
# Run from terminal
python test_clinic_info.py

# Or use VS Code task: Ctrl+Shift+P → "Tasks: Run Task" → "Run Clinic Info Tests"
```

## 🛠️ Common Debugging Scenarios

### 1. FastAPI Server Issues
- **Problem**: Server won't start
- **Debug**: Use "FastAPI Debug (UV)" configuration
- **Check**: Import errors, missing dependencies, port conflicts

### 2. AI Agent Problems
- **Problem**: Agent not responding correctly
- **Debug**: Use "Test Agent Debug" configuration
- **Check**: Intent detection, agent routing, conversation state

### 3. Database Errors
- **Problem**: Database operations failing
- **Debug**: Use "Database Tools Debug" configuration
- **Check**: Connection strings, model definitions, SQL queries

### 4. Clinic Information Issues
- **Problem**: Clinic data not loading
- **Debug**: Use "Clinic Info Debug" configuration
- **Check**: JSON file format, file paths, data parsing

### 5. WhatsApp Integration
- **Problem**: Messages not sending
- **Debug**: Use "FastAPI Debug (UV)" + set breakpoints in WhatsApp tools
- **Check**: API credentials, webhook configuration, message format

## 🔍 Advanced Debugging

### Environment Variables
- **Local**: Use `.env` file in project root
- **Docker**: Set in `docker-compose.yml` or `Dockerfile`
- **Debug**: Override in launch configuration

### Remote Debugging
1. **Start remote process** with debugpy:
   ```python
   import debugpy
   debugpy.listen(("0.0.0.0", 5678))
   debugpy.wait_for_client()
   ```

2. **Use "FastAPI Debug (Attach)"** configuration
3. **Set breakpoints** and start debugging

### Debugging with Docker
1. **Build image**: `docker build -t medical-secretary-ai .`
2. **Run with debug port**: 
   ```bash
   docker run -p 8000:8000 -p 5678:5678 medical-secretary-ai
   ```
3. **Use "FastAPI Debug (Attach)"** configuration

## 📋 VS Code Tasks

### Available Tasks
- **Start FastAPI Server (UV)**: Start development server
- **Run AI Agent Tests**: Test agent functionality
- **Run Database Tests**: Test database operations
- **Run Clinic Info Tests**: Test clinic information
- **Install Dependencies (UV)**: Install Python packages
- **Build Docker Image**: Build Docker container
- **Start/Stop Docker Compose**: Manage Docker services
- **Clean Python Cache**: Remove cache files
- **Format Code (Black)**: Format Python code
- **Sort Imports**: Organize import statements

### Running Tasks
1. **Command Palette**: `Ctrl+Shift+P` → "Tasks: Run Task"
2. **Terminal**: `Ctrl+Shift+`` → Select task
3. **Shortcuts**: Configure keyboard shortcuts for common tasks

## 🎨 VS Code Settings

### Python Configuration
- **Interpreter**: Automatically uses `.venv/bin/python`
- **Linting**: Enabled with flake8 and mypy
- **Formatting**: Black code formatter
- **Testing**: pytest integration
- **Analysis**: Type checking and import completion

### File Exclusions
- **Cache files**: `__pycache__`, `.pyc`, `.pytest_cache`
- **Virtual environments**: `.venv`, `venv`
- **Build artifacts**: `dist`, `build`, `*.egg-info`

### Search Configuration
- **Include**: `src/**/*.py` (all Python files in src)
- **Exclude**: Cache files, virtual environments, build artifacts

## 🚨 Troubleshooting

### Common Issues

#### 1. Python Interpreter Not Found
```bash
# Solution: Recreate virtual environment
rm -rf .venv
uv venv
source .venv/bin/activate
uv sync
```

#### 2. Import Errors
```bash
# Solution: Check Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"
# Or add to .env file
PYTHONPATH=${PWD}
```

#### 3. Debugger Not Starting
- **Check**: Python extension installed and enabled
- **Verify**: Correct interpreter selected
- **Restart**: VS Code and Python extension

#### 4. Breakpoints Not Working
- **Verify**: File is saved
- **Check**: Python extension status
- **Restart**: Debug session

#### 5. Hot Reload Issues
- **Check**: File watching enabled
- **Verify**: No syntax errors
- **Restart**: Development server

### Performance Tips

1. **Limit file watching**: Exclude unnecessary directories
2. **Use appropriate debug level**: Set `justMyCode: false` for library debugging
3. **Optimize imports**: Use `isort` to organize imports
4. **Clean cache**: Regularly clean Python cache files
5. **Monitor resources**: Watch CPU and memory usage during debugging

## 📚 Additional Resources

- **VS Code Python Extension**: [Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- **Python Debugging**: [Official Documentation](https://code.visualstudio.com/docs/python/debugging)
- **FastAPI Debugging**: [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/debugging/)
- **UV Package Manager**: [UV Documentation](https://docs.astral.sh/uv/)

## 🎯 Best Practices

1. **Set meaningful breakpoints**: Don't over-debug
2. **Use conditional breakpoints**: For specific conditions
3. **Monitor variables**: Use watch expressions for key values
4. **Test incrementally**: Debug one component at a time
5. **Document issues**: Keep notes of common problems and solutions
6. **Use logging**: Combine debugging with strategic logging
7. **Version control**: Commit working code before major debugging sessions

---

**Happy Debugging! 🐛✨**
