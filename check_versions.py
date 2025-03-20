import sys
import torch

def get_python_version():
    return sys.version

def get_cuda_version():
    return torch.version.cuda

def get_pytorch_version():
    return torch.__version__

if __name__ == "__main__":
    print(f"Python version: {get_python_version()}")
    print(f"CUDA version: {get_cuda_version()}")
    print(f"PyTorch version: {get_pytorch_version()}")