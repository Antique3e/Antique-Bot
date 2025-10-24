import modal
import os, time

GPU_TYPE = os.environ.get("GPU_TYPE", "T4")  #NEW
app = modal.App("setup-step1")
vol = modal.Volume.from_name("workspace", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "wget", "curl", "aria2", "libgl1", "lsof", "libglib2.0-0", "unzip")
)

@app.function(
    image=image,
    gpu=GPU_TYPE,
    timeout=3*3600 ,  # 3 hour
    volumes={"/root/workspace": vol},
)
def run():
    
    if not os.path.exists("/root/workspace/ComfyUI"):
        print("Cloning ComfyUI...")
        os.system("cd /root/workspace && git clone https://github.com/comfyanonymous/ComfyUI")

        print("Installing ComfyUI Manager...")
        os.system("cd /root/workspace/ComfyUI/custom_nodes && git clone https://github.com/Comfy-Org/ComfyUI-Manager")

        print("Installing custom nodes...")
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
        
        dl = "aria2c -x16 -s16 --max-tries=10 --retry-wait=5 --continue=true --allow-overwrite=false"
        print("Downloading diffusion models...")
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

        print("Downloading VAE models...")
        os.system(
            "cd /root/workspace/ComfyUI/models/vae && "
            f"{dl} --out=qwen_image_vae.safetensors https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors && "
            f"{dl} --out=wan_2.1_vae.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors && "
            f"{dl} --out=Wan2_1_VAE_bf16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_VAE_bf16.safetensors"
            )

        print("Downloading text encoder models...")
        os.system(
            "cd /root/workspace/ComfyUI/models/text_encoders && "
            f"{dl} --out=qwen_2.5_vl_7b.safetensors https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b.safetensors && "
            f"{dl} --out=umt5_xxl_fp16.safetensors https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp16.safetensors"
            )
        
        print("Downloading LoRA models...")
        os.system(
            "cd /root/workspace/ComfyUI/models/loras && "
            f"{dl} --out=lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors && "
            f"{dl} --out=lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank256_bf16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank256_bf16.safetensors && "
            f"{dl} --out=WanAnimate_relight_lora_fp16.safetensors https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_relight/WanAnimate_relight_lora_fp16.safetensors && "
            f"{dl} --out=Qwen-Image-Lightning-8steps-V2.0-bf16.safetensors https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-8steps-V2.0-bf16.safetensors && "
            f"{dl} --out=Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors"
            )
    else:
        print("ComfyUI Installed...✅")

