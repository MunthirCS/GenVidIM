# RunPod Network Volume Setup

To optimize the build process and to avoid downloading the models every time you build your project, you should store the models on a RunPod network volume. This will make your builds much faster, and it will also save you money on storage costs.

## 1. Create a Network Volume

1.  Go to the [RunPod Network Volumes page](https://www.runpod.io/console/user/storage).
2.  Click the "New Volume" button.
3.  Give your volume a name (e.g., "GenVidIM-models").
4.  Select the same location as your serverless endpoint.
5.  Set the size of the volume. The models are quite large, so you'll need at least 100 GB of space.
6.  Click the "Create" button.

## 2. Attach the Network Volume to a Pod

To download the models to the network volume, you'll need to attach it to a pod.

1.  Go to the [RunPod Pods page](https://www.runpod.io/console/pods).
2.  Create a new pod. You can use any template, but I recommend using a template that has the `huggingface-cli` pre-installed.
3.  When you're creating the pod, make sure to attach the network volume that you created in the previous step. The network volume will be mounted at the `/workspace/models` directory.
4.  Once the pod is running, you can connect to it using SSH.

## 3. Create Virtual Environment and Install Dependencies

This is a **one-time setup**. Once the virtual environment is created and the packages are installed on the volume, you won't need to do this again.

**IMPORTANT:** Use a terminal multiplexer like `screen` for this process, as it can take a long time and you don't want your SSH connection to drop.

First, install `screen` if you haven't already:
```bash
apt-get update && apt-get install -y screen
```

Start a `screen` session:
```bash
screen -S- cache /workspace/models/* /workspace/venv/*
```

Inside the `screen` session, run these commands:

```bash
# 1. Create a Python virtual environment on the network volume
python3 -m venv /workspace/venv

# 2. Activate the new virtual environment
source /workspace/venv/bin/activate

# 3. Install all dependencies into this virtual environment
# This will take a long time. It is safe to detach from the screen session while it runs.
pip install --no-cache-dir -r /workspace/GenVidIM/requirements.txt
pip install --no-cache-dir -r /workspace/GenVidIM/requirements_animate.txt
pip install --no-cache-dir -r /workspace/GenVidIM/requirements_s2v.txt
pip install --no-cache-dir torch>=2.4.0 torchvision>=0.19.0 torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install --no-cache-dir flash-attn --no-build-isolation || echo "Flash Attention 2 failed, continuing..."
```

After running the `pip install` commands, you can safely detach from the session by pressing **`Ctrl+A`** then **`D`**. You can re-attach later with `screen -r deps`.

## 4. Download the Models to the Network Volume

Once you're connected to the pod, you can download the models to the network volume using the following commands. The `hf-transfer` package is installed to accelerate the download speed.

```bash
pip install "huggingface_hub[cli]" hf-transfer
huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir /workspace/models/Wan2.2-TI2V-5B --quiet
huggingface-cli download Wan-AI/Wan2.2-Animate-14B --local-dir /workspace/models/Wan2.2-Animate-14B --quiet
huggingface-cli download Wan-AI/Wan2.2-S2V-14B --local-dir /workspace/models/Wan2.2-S2V-14B --quiet
huggingface-cli download Wan-AI/Wan2.2-T2V-A14B --local-dir /workspace/models/Wan2.2-T2V-A14B --quiet
```

## 4. Attach the Network Volume to Your Serverless Endpoint

Once the models have been downloaded to the network volume, you can attach the network volume to your serverless endpoint.

1.  Go to the [RunPod Serverless Endpoints page](https://www.runpod.io/console/serverless).
2.  Select your endpoint.
3.  Go to the "Settings" tab.
4.  Under "Network Volumes", select the network volume that you created in the first step. The network volume will be mounted at the `/workspace/models` directory.
5.  Click the "Save" button.

Once you've completed these steps, your serverless endpoint will be able to access the models from the network volume. This will make your builds much faster, and it will also save you money on storage costs.
