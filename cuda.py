import torch

print(torch.cuda.is_available())  # This should return True if CUDA is available


print(torch.cuda.current_device())


print(torch.cuda.get_device_name(0))
