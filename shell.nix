{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.torch
    python3Packages.torchvision
    python3Packages.torchaudio
    python3Packages.opencv4
    python3Packages.transformers
    python3Packages.tqdm
    python3Packages.imageio
    python3Packages.numpy
    python3Packages.setuptools
    ffmpeg
    git
    openssh
  ];

  shellHook = ''
    export PATH="$HOME/.local/bin:$PATH"
    export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PWD:$PYTHONPATH"
    echo "Wan2.2 development environment loaded!"
    echo "Python version: $(python3 --version)"
    echo "PyTorch available: $(python3 -c 'import torch; print("Yes, version:", torch.__version__)' 2>/dev/null || echo "No")"
    echo "Diffusers available: $(python3 -c 'import diffusers; print("Yes")' 2>/dev/null || echo "No")"
    echo ""
    echo "To run the video generation:"
    echo "python3 generate.py --task ti2v-5B --size 1280*704 --ckpt_dir ./Wan2.2-TI2V-5B --prompt 'Your prompt here'"
  '';
}