import torch

# Check if CUDA is available
print(torch.cuda.is_available())  # This should return True if CUDA is available

# Get the current device (GPU)
print(torch.cuda.current_device())

# Get the name of the GPU
print(torch.cuda.get_device_name(0))
