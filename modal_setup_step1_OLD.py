"""
Modal Setup - Step 1
====================
Downloads ComfyUI and all required models.

This script:
- Clones ComfyUI repository
- Clones custom nodes
- Downloads diffusion models (~14GB each)
- Downloads VAE models
- Downloads text encoder models
- Downloads LoRA models

GPU: T4 (cheapest)
Duration: ~2 hours
Output: JupyterLab running at https://jupyter.tensorart.site/
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
# IMAGE DEFINITION (WITHOUT DEPENDENCIES)
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
    # NOTE: We do NOT install dependencies in this step!
    # Dependencies will be installed in step 2
)

# ============================================================================
# SETUP FUNCTION - STEP 1
# ============================================================================

@app.function(
    image=m_jupyter,
    gpu="T4",  # Use cheapest GPU for setup
    timeout=24*3600,  # 24 hour timeout
    volumes={"/root/workspace": vol},
)
def run():
    """Setup step 1: Download ComfyUI and models."""
    
    print("=" * 80)
    print("MODAL SETUP - STEP 1")
    print("=" * 80)
    print("This will download ComfyUI and all required models.")
    print("Expected duration: ~2 hours on T4 GPU")
    print("=" * 80)
    
    # Install Cloudflare tunnel
    print("\n[0/8] Installing Cloudflare tunnel...")
    os.system("wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared && mv cloudflared /usr/local/bin/")
    os.system("git clone https://tensorart-site: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@github.com/tensorart-site/cf-bypass-login.git && cd cf-bypass-login && cp -r .cloudflared /root")
    
    # Check if ComfyUI already exists
    if not os.path.exists("/root/workspace/ComfyUI"):
        print("\n[1/7] Cloning ComfyUI...")
        os.system("cd /root/workspace && git clone https://github.com/comfyanonymous/ComfyUI")
        
        print("\n[2/7] Installing ComfyUI Manager...")
        os.system("cd /root/workspace/ComfyUI/custom_nodes && git clone https://github.com/Comfy-Org/ComfyUI-Manager")
        
        print("\n[3/7] Installing custom nodes...")
        os.system(
            "cd /root/workspace/ComfyUI/custom_nodes && "
            "git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git && "
            "git clone https://github.com/sipherxyz/comfyui-art-venture.git && "
            "git clone https://github.com/kijai/ComfyUI-KJNodes.git && "
            "git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && "
            "git clone https://github.com/chflame163/ComfyUI_LayerStyle.git && "
            "git clone https://github.com/chflame163/ComfyUI_LayerStyle_Advance.git && "
            "git clone https://github.com/yolain/ComfyUI-Easy-Use.git && "
            "git clone https://github.com/cubiq/ComfyUI_essentials.git && "
            "git clone https://github.com/SeargeDP/ComfyUI_Searge_LLM.git && "
            "git clone https://github.com/TinyTerra/ComfyUI_tinyterraNodes.git && "
            "git clone https://github.com/kijai/ComfyUI-Florence2.git && "
            "git clone https://github.com/city96/ComfyUI-GGUF.git && "
            "git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && "
            "git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git && "
            "git clone https://github.com/rgthree/rgthree-comfy.git && "
            "git clone https://github.com/welltop-cn/ComfyUI-TeaCache.git && "
            "git clone https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git && "
            "git clone https://github.com/giriss/comfy-image-saver.git && "
            "git clone https://github.com/chflame163/ComfyUI_IPAdapter_plus_V2.git && "
            "git clone https://github.com/ClownsharkBatwing/RES4LYF.git && "
            "git clone https://github.com/eddyhhlure1Eddy/auto_wan2.2animate_freamtowindow_server.git && " 
            "git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git && " 
            "git clone https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait.git && " 
            "git clone https://github.com/gokayfem/ComfyUI-fal-API.git && " 
            "git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git && " 
            "git clone https://github.com/Antique3e/ComfyUI-ModalCredits.git && " 
            "git clone https://github.com/9nate-drake/Comfyui-SecNodes.git && " 
            "git clone https://github.com/kijai/ComfyUI-WanAnimatePreprocess.git && " 
            "git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git && "
            "git clone https://github.com/crystian/ComfyUI-Crystools.git && "
            "git clone https://github.com/1dZb1/MagicNodes.git"
        )
        
        # Setup aria2c for faster downloads
        dl = "aria2c -x16 -s16 --max-tries=10 --retry-wait=5 --continue=true --allow-overwrite=false"
        
        print("\n[4/7] Downloading diffusion models... (This will take a while!)")
        os.system(
            "cd /root/workspace/ComfyUI/models/diffusion_models && "
            f"{dl} --out=wan2.2_t2v_high_noise_14B_fp16.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_high_noise_14B_fp16.safetensors && "
            f"{dl} --out=wan2.2_t2v_low_noise_14B_fp16.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_low_noise_14B_fp16.safetensors && "
            f"{dl} --out=qwen_image_edit_2509_bf16.safetensors https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_bf16.safetensors && "
            f"{dl} --out=Wan2_2-I2V-A14B-HIGH_fp8_e5m2_scaled_KJ.safetensors https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/I2V/Wan2_2-I2V-A14B-HIGH_fp8_e5m2_scaled_KJ.safetensors && "
            f"{dl} --out=Wan2_2-I2V-A14B-LOW_fp8_e5m2_scaled_KJ.safetensors https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/I2V/Wan2_2-I2V-A14B-LOW_fp8_e5m2_scaled_KJ.safetensors && "
            f"{dl} --out=Wan2_2-Animate-14B_fp8_scaled_e5m2_KJ_v2.safetensors https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/Wan22Animate/Wan2_2-Animate-14B_fp8_scaled_e5m2_KJ_v2.safetensors && "
            f"{dl} --out=wan2.2_animate_14B_bf16.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_animate_14B_bf16.safetensors"
        )
        
        print("\n[5/7] Downloading VAE models...")
        os.system(
            "cd /root/workspace/ComfyUI/models/vae && "
            f"{dl} --out=qwen_image_vae.safetensors https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors && "
            f"{dl} --out=wan_2.1_vae.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors && "
            f"{dl} --out=Wan2_1_VAE_bf16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_VAE_bf16.safetensors"
        )
        
        print("\n[6/7] Downloading text encoder models...")
        os.system(
            "cd /root/workspace/ComfyUI/models/text_encoders && "
            f"{dl} --out=qwen_2.5_vl_7b.safetensors https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b.safetensors && "
            f"{dl} --out=umt5_xxl_fp16.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp16.safetensors"
        )
        
        print("\n[7/7] Downloading LoRA models...")
        os.system(
            "cd /root/workspace/ComfyUI/models/loras && "
            f"{dl} --out=lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors && "
            f"{dl} --out=lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank256_bf16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank256_bf16.safetensors && "
            f"{dl} --out=WanAnimate_relight_lora_fp16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_relight/WanAnimate_relight_lora_fp16.safetensors && "
            f"{dl} --out=Qwen-Image-Lightning-8steps-V2.0-bf16.safetensors https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-8steps-V2.0-bf16.safetensors && "
            f"{dl} --out=Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors"
        )
        
        print("\n" + "=" * 80)
        print("✅ SETUP STEP 1 COMPLETE!")
        print("=" * 80)
        print("All models downloaded successfully.")
        print("Total download size: ~100GB")
        print("\nNext step: The bot will automatically run Step 2 to install dependencies.")
        print("=" * 80)
    else:
        print("\n⚠️  ComfyUI already exists, skipping download.")
        print("If you want to re-download, delete /root/workspace/ComfyUI first.")
        print("\n✅ SETUP STEP 1 COMPLETE (SKIPPED)")

# ============================================================================
# END OF SETUP STEP 1
# ============================================================================
