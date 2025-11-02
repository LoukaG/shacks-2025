from huggingface_hub import InferenceClient
import os 
HF_TOKEN=os.getenv( "HF_TOKEN")
print(HF_TOKEN)