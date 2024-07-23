from transformers import AutoModelForSeq2SeqLM, AutoTokenizer #, GenerationConfig, TrainingArguments, Trainer
import torch
import bio

device = "cuda"
model_name='google/flan-t5-base'

print("LOADING THE MODEL...")
original_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

print("LOADING THE TOKENIZER...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("SETTING MODEL TO CUDA...")
original_model.to(device)
# Example text
question = "Have you passed an internship?"
prompt = f"""

        Your Bio:
        
        {bio.bio}
        
        Based on your bio answer the question:
        
        {question}
        
        Answer:
        """

# Encode the input text
# input_ids = tokenizer(text, return_tensors="pt").input_ids

# Generate output
inputs = tokenizer(prompt, return_tensors='pt').to(device)
print("GENERATING...")
output = tokenizer.decode(
    original_model.generate(
        inputs["input_ids"], 
        max_new_tokens=200,
        do_sample=True,
        temperature=0.5
    )[0], 
    skip_special_tokens=True
)


print(output)
