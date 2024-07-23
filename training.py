from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
import torch
import re
import time
import bio
device = torch.device("cuda")
model_name = 'google/flan-t5-base'

print("LOADING THE MODEL...")
original_model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

print("LOADING THE TOKENIZER...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

def questions_to_dict(questions):
    pattern = r"Question: (.*?)\nAnswer: (.*?)(?=\nQuestion: |\Z)"
    matches = re.findall(pattern, questions, re.DOTALL)

    qa_dict = {
        "Question": [],
        "Answer": []
    }

    for qa in matches:
        qa_dict["Question"].append(qa[0])
        qa_dict["Answer"].append(qa[1])

    return qa_dict

def tokenize_function(example):
    start_prompt = f"""Your Bio:

                    {bio.bio}

                    Based on your bio answer the question:\n"""
    end_prompt = '\nAnswer: '
    prompt = [start_prompt + question + end_prompt for question in example["Question"]]
    print(len(question))
    inputs = tokenizer(prompt, padding="max_length", truncation=True, return_tensors="pt").input_ids
    targets = tokenizer(example["Answer"], padding="max_length", truncation=True, return_tensors="pt").input_ids

    # Flatten the tensors
    inputs = inputs.view(-1, inputs.shape[-1])
    targets = targets.view(-1, targets.shape[-1])

    return {"input_ids": inputs, "labels": targets}

class QADataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: val[idx] for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings['input_ids'])

def train_val_split(questions):
    qa_dict = questions_to_dict(questions)

    # Split the data into train and validation sets
    train_questions, val_questions, train_answers, val_answers = train_test_split(
        qa_dict["Question"], qa_dict["Answer"], test_size=0.2, random_state=42
    )

    train_dict = {"Question": train_questions, "Answer": train_answers}
    val_dict = {"Question": val_questions, "Answer": val_answers}

    tokenized_train_dataset = tokenize_function(train_dict)
    tokenized_val_dataset = tokenize_function(val_dict)

    train_dataset = QADataset(tokenized_train_dataset)
    val_dataset = QADataset(tokenized_val_dataset)

    print(f"Training questions: {len(train_dict['Question'])}")
    print(f"Validation questions: {len(val_dict['Question'])}")

    return train_dataset, val_dataset

train_dataset, val_dataset = train_val_split(bio.training_questions)

# output_dir = f'./QA-training-{str(int(time.time()))}'

# training_args = TrainingArguments(
#     output_dir=output_dir,
#     per_device_train_batch_size=1,  # Reduce batch size
#     per_device_eval_batch_size=1, 
#     learning_rate=1e-5,
#     num_train_epochs=5,
#     evaluation_strategy="steps",
#     eval_steps=5,
#     weight_decay=0.01,
#     logging_steps=1,
#     # max_steps=1
# )

# trainer = Trainer(
#     model=original_model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=val_dataset
# )

# trainer.train()