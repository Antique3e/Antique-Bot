"""
Modal ComfyUI Runtime
=====================
Runs ComfyUI with your selected GPU.

This script is used AFTER setup is complete.
It loads the existing ComfyUI installation and models from the volume.

GPU: Configurable (set via environment variable)
Duration: Runs until you stop it
Output: 
  - JupyterLab at https://jupyter.tensorart.site/
  - ComfyUI at https://comfyui.tensorart.site/

USAGE:
  The Discord bot will set the GPU via environment variable before running.
  You can also run manually:
    GPU_TYPE=H100 modal run modal_comfyui_run.py
"""

import modal
import os
import time

# ============================================================================
# GPU SELECTION
# ============================================================================

# Get GPU from environment variable (set by Discord bot)
# Default to H100 if not specified
GPU_TYPE = os.environ.get("GPU_TYPE", "H100")

print(f"🖥️  Selected GPU: {GPU_TYPE}")

# ============================================================================
# MODAL APP CONFIGURATION
# ============================================================================

app = modal.App("comfyui-antique")
vol = modal.Volume.from_name("workspace", create_if_missing=True)

# ============================================================================
# DEPENDENCY INSTALLATION FUNCTION (Reused from step 2)
# ============================================================================

def install_comfyui_dependencies():
    """Install all ComfyUI Python dependencies."""
    print("\n" + "=" * 80)
    print("CHECKING DEPENDENCIES")
    print("=" * 80)
    
    # Check if already installed
    if os.path.exists("/root/workspace/.dependencies_installed"):
        print("✅ Dependencies already installed (marker file found)")
        return
    
    print("⚠️  Dependencies not found, installing now...")
    print("(This should only happen on first run)")
    
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
# IMAGE DEFINITION
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
    )
    .run_function(
        install_comfyui_dependencies,
        volumes={"/root/workspace": vol}
    )
)

# ============================================================================
# RUN FUNCTION
# ============================================================================

@app.function(
    image=m_jupyter,
    gpu=GPU_TYPE,  # ← Dynamic GPU based on environment variable!
    timeout=24*3600,  # 24 hour timeout
    volumes={"/root/workspace": vol},
)
def run():
    """Run ComfyUI with selected GPU."""
    
    print("=" * 80)
    print("COMFYUI RUNTIME")
    print("=" * 80)
    print(f"GPU: {GPU_TYPE}")
    print("=" * 80)
    
    # Install Cloudflare tunnel
    print("\n[0/1] Installing Cloudflare tunnel...")
    os.system("wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared && mv cloudflared /usr/local/bin/")
    os.system("git clone https://tensorart-site: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@github.com/tensorart-site/cf-bypass-login.git && cd cf-bypass-login && cp -r .cloudflared /root")
    
    # Check if ComfyUI exists
    if not os.path.exists("/root/workspace/ComfyUI"):
        print("\n❌ ERROR: ComfyUI not found!")
        print("Please run modal_setup_step1.py and modal_setup_step2.py first.")
        return
    
    print("\n✅ ComfyUI found, starting services...")
    
    # Verify dependencies
    if os.path.exists("/root/workspace/.dependencies_installed"):
        print("✅ Dependencies verified")
    else:
        print("⚠️  Warning: Dependencies might not be fully installed")
        print("    If ComfyUI fails to start, run modal_setup_step2.py again")
    
    # Start JupyterLab
    print("\n🚀 Starting JupyterLab...")
    os.system("jupyter lab --ip=0.0.0.0 --port=5000 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &")
    time.sleep(5)
    
    # Start ComfyUI
    print("\n🚀 Starting ComfyUI...")
    os.system("cd /root/workspace/ComfyUI && python main.py --listen 0.0.0.0 --port 8188 &")
    time.sleep(5)
    
    print("\n" + "=" * 80)
    print("✅ SERVICES STARTED!")
    print("=" * 80)
    print(f"🖥️  GPU: {GPU_TYPE}")
    print("📍 JupyterLab: https://jupyter.tensorart.site/")
    print("📍 ComfyUI: https://comfyui.tensorart.site/")
    print("=" * 80)
    print("\n⏳ Services are starting... Give them 1-2 minutes to be fully ready.")
    print("💡 Use Discord bot's /stop command to stop this container.")
    print("=" * 80)
    
    # Start Cloudflare tunnel (keeps the container running)
    print("\n🌐 Starting Cloudflare tunnel...")
    os.system("cloudflared tunnel run tensorart")

# ============================================================================
# END OF COMFYUI RUNTIME
# ============================================================================
