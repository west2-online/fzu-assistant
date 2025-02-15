from accelerate.utils import calculate_maximum_sizes, convert_bytes
from accelerate.commands.estimate import check_has_model, create_empty_model
import torch
from config import conf
DTYPE_MODIFIER = {"float32": 1, "float16/bfloat16": 2, "int8": 4, "int4": 8}

def calculate_memory(model: torch.nn.Module, options: list):
    "Calculates the memory usage for a model init on `meta` device"
    total_size, largest_layer = calculate_maximum_sizes(model)

    data = []
    for dtype in options:
        dtype_total_size = total_size
        dtype_largest_layer = largest_layer[0]

        modifier = DTYPE_MODIFIER[dtype]
        dtype_total_size /= modifier
        dtype_largest_layer /= modifier

        dtype_training_size = convert_bytes(dtype_total_size * 4)
        dtype_total_size = convert_bytes(dtype_total_size)
        dtype_largest_layer = convert_bytes(dtype_largest_layer)
        data.append(
            {
                "dtype": dtype,
                "Largest Layer or Residual Group": dtype_largest_layer,
                "Total Size": dtype_total_size,
                "Training using Adam": dtype_training_size,
            }
        )
    return data

model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
model = create_empty_model(model_name, library_name=None, trust_remote_code=True, access_token=None)
results = calculate_memory(model, ["float32", "float16/bfloat16", "int8", "int4"])
for result in results:
    print(f"Total size of the Model with dtype {result['dtype']} is {result['Total Size']}")
    