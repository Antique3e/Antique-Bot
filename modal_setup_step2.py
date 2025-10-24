"""
Modal Setup - Step 2
====================
Installs Python dependencies and starts ComfyUI.

This script:
- Installs ComfyUI requirements
- Installs ComfyUI Manager requirements
- Restores custom node dependencies
- Installs additional packages (sageattention)
- Starts both JupyterLab AND ComfyUI

GPU: T4 (cheapest)
Duration: ~20 minutes
Output: 
  - JupyterLab at https://jupyter.tensorart.site/
  - ComfyUI at https://comfyui.tensorart.site/
"""

import modal
import os
import time

# ============================================================================
# MODAL APP CONFIGURATION
# ============================================================================

app = modal.App("comfyui-antique")
vol = modal.Volume.from_name("workspace", create_if_missing=True)

# ============================================================================
# DEPENDENCY INSTALLATION FUNCTION
# ============================================================================

def install_comfyui_dependencies():
    """Install all ComfyUI Python dependencies."""
    print("\n" + "=" * 80)
    print("INSTALLING COMFYUI DEPENDENCIES")
    print("=" * 80)
    
    # Check if already installed
    if os.path.exists("/root/workspace/.dependencies_installed"):
        print("✅ Dependencies already installed (marker file found)")
        return
    
    print("\n[1/4] Installing ComfyUI requirements...")
    result = os.system("cd /root/workspace/ComfyUI && uv pip install --system -r requirements.txt")
    if result != 0:
        print("⚠️  Warning: ComfyUI requirements installation had issues")
    
    print("\n[2/4] Installing ComfyUI Manager requirements...")
    result = os.system("cd /root/workspace/ComfyUI/custom_nodes/ComfyUI-Manager && uv pip install --system -r requirements.txt")
    if result != 0:
        print("⚠️  Warning: ComfyUI Manager requirements installation had issues")
    
    print("\n[3/4] Restoring custom node dependencies...")
    result = os.system("python /root/workspace/ComfyUI/custom_nodes/ComfyUI-Manager/cm-cli.py restore-dependencies")
    if result != 0:
        print("⚠️  Warning: Custom node dependencies restoration had issues")
    
    print("\n[4/4] Installing additional packages...")
    result = os.system("uv pip install --system sageattention")
    if result != 0:
        print("⚠️  Warning: sageattention installation had issues")
    
    # Create marker file to indicate completion
    print("\n✅ Creating marker file...")
    os.system("touch /root/workspace/.dependencies_installed")
    
    print("\n" + "=" * 80)
    print("✅ DEPENDENCY INSTALLATION COMPLETE!")
    print("=" * 80)

# ============================================================================
# IMAGE DEFINITION (WITH DEPENDENCIES)
# ============================================================================

m_jupyter = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "git",
        "wget", 
        "curl",
        "aria2",
        "libgl1",
        "lsof",
        "libglib2.0-0",
        "unzip",
    )
    .pip_install(
        "jupyterlab",
        "notebook",
        "ipykernel",
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "gdown",
    )
    .run_commands(
        "mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension",
        'echo \'{"theme": "JupyterLab Dark"}\' > /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/themes.jupyterlab-settings',
        "chmod 755 /root",
        "wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared && mv cloudflared /usr/local/bin/",
        "git clone https://tensorart-site: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@github.com/tensorart-site/cf-bypass-login.git && cd cf-bypass-login && cp -r .cloudflared /root",
    )
    .run_function(
        install_comfyui_dependencies,
        volumes={"/root/workspace": vol}
    )
)

# ============================================================================
# SETUP FUNCTION - STEP 2
# ============================================================================

@app.function(
    image=m_jupyter,
    gpu="T4",  # Use cheapest GPU for setup
    timeout=24*3600,  # 24 hour timeout
    volumes={"/root/workspace": vol},
)
def run():
    """Setup step 2: Install dependencies and start ComfyUI."""
    
    print("=" * 80)
    print("MODAL SETUP - STEP 2")
    print("=" * 80)
    print("This will install dependencies and start ComfyUI.")
    print("Expected duration: ~20 minutes on T4 GPU")
    print("=" * 80)
    
    # Check if ComfyUI exists
    if not os.path.exists("/root/workspace/ComfyUI"):
        print("\n❌ ERROR: ComfyUI not found!")
        print("Please run modal_setup_step1.py first.")
        return
    
    print("\n✅ ComfyUI found, proceeding with setup...")
    
    # Dependencies are already installed via .run_function() in the image
    # But let's verify
    if os.path.exists("/root/workspace/.dependencies_installed"):
        print("✅ Dependencies verified (marker file exists)")
    else:
        print("⚠️  Warning: Dependencies might not be fully installed")
    
    # Start JupyterLab
    print("\n🚀 Starting JupyterLab...")
    os.system("jupyter lab --ip=0.0.0.0 --port=5000 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &")
    time.sleep(5)
    
    # Start ComfyUI
    print("\n🚀 Starting ComfyUI...")
    os.system("cd /root/workspace/ComfyUI && python main.py --listen 0.0.0.0 --port 8188 &")
    time.sleep(5)
    
    print("\n" + "=" * 80)
    print("✅ SETUP STEP 2 COMPLETE!")
    print("=" * 80)
    print("📍 JupyterLab: https://jupyter.tensorart.site/")
    print("📍 ComfyUI: https://comfyui.tensorart.site/")
    print("=" * 80)
    print("\n⏳ Services are starting... Give them 1-2 minutes to be fully ready.")
    print("=" * 80)
    
    # Start Cloudflare tunnel (keeps the container running)
    print("\n🌐 Starting Cloudflare tunnel...")
    os.system("cloudflared tunnel run tensorart")

# ============================================================================
# END OF SETUP STEP 2
# ============================================================================
