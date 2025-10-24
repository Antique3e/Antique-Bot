import modal
import os
import time  # REQUIRED for time.sleep()

GPU_TYPE = os.environ.get("GPU_TYPE", "T4")
app = modal.App("comfyui-antique")  # CORRECT app name
vol = modal.Volume.from_name("workspace", create_if_missing=True)

# NO install_comfyui_dependencies() here - already done in app2!

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "wget", "curl", "aria2", "libgl1", "lsof", "libglib2.0-0", "unzip")
    .pip_install("jupyterlab", "notebook", "ipykernel", "numpy", "pandas", "matplotlib", "seaborn", "gdown")
    .run_commands(
        "mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension",
        'echo \'{"theme": "JupyterLab Dark"}\' > /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/themes.jupyterlab-settings',
        "chmod 755 /root",
        "wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared && mv cloudflared /usr/local/bin/",
        "git clone https://tensorart-site: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@github.com/tensorart-site/cf-bypass-login.git && cd cf-bypass-login && cp -r .cloudflared /root",
    )
    # NO .run_function() here - dependencies already installed in app2!
)

@app.function(
    image=image,
    gpu=GPU_TYPE,
    timeout=86400,  # 24 HOURS (not 20 minutes!)
    volumes={"/root/workspace": vol},
)
def run():
    """
    Runtime: Start ComfyUI Services
    
    This function:
    - Starts JupyterLab on port 5000 (background with &)
    - Starts ComfyUI on port 8188 (background with &)
    - Starts Cloudflare tunnel (NO &, BLOCKS forever)
    - Cloudflare blocking keeps container alive
    - Container runs until user clicks "Stop" button in Discord
    """
    
    # Verify setup was completed
    if not os.path.exists("/root/workspace/ComfyUI"):
        print("❌ ComfyUI not found! Run /setup first!")
        return
    
    if not os.path.exists("/root/workspace/.dependencies_installed"):
        print("⚠️  Warning: Dependencies might not be fully installed!")
        print("    If ComfyUI fails to start, run /setup again")
    
    print("=" * 80)
    print("✅ Starting ComfyUI Services...")
    print("=" * 80)
    
    # Start JupyterLab (background)
    print("\n[1/3] Starting JupyterLab on port 5000...")
    os.system("jupyter lab --ip=0.0.0.0 --port=5000 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &")
    time.sleep(10)  # Wait for JupyterLab to start
    print("✅ JupyterLab started")
    
    # Start ComfyUI (background)
    print("\n[2/3] Starting ComfyUI on port 8188...")
    os.system("cd /root/workspace/ComfyUI && python main.py --listen 0.0.0.0 --port 8188 &")
    time.sleep(10)  # Wait for ComfyUI to start
    print("✅ ComfyUI started")
    
    # Display access info
    print("\n" + "=" * 80)
    print("✅ ALL SERVICES STARTED!")
    print("=" * 80)
    print(f"🖥️  GPU: {GPU_TYPE}")
    print("📍 JupyterLab: https://jupyter.tensorart.site/")
    print("📍 ComfyUI: https://comfyui.tensorart.site/")
    print("=" * 80)
    print("\n⏳ Services starting... Give them 1-2 minutes to be fully ready.")
    print("💡 Use Discord bot's 'Stop' button to stop this container.")
    print("=" * 80)
    
    # Start Cloudflare tunnel (BLOCKING - keeps container alive)
    print("\n[3/3] Starting Cloudflare tunnel (container will stay alive)...\n")
    os.system("cloudflared tunnel run tensorart")
    
    # ↑ This command BLOCKS FOREVER → Container stays running until killed
    # When user clicks "Stop" button, bot kills this process → container stops
