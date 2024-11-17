from fastapi import APIRouter, HTTPException, Depends, Request
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, set_seed
import torch
from pydantic import BaseModel, Field
from typing import Optional
import pandas as pd
import os
import json

router = APIRouter(
    prefix="/llm",
)

class LLMResponseModel(BaseModel):
    answer: str
    confidence: int
    justification : str

@router.get("/question", response_model=LLMResponseModel)
def llama(question: str, data):
    device = torch.device("cpu")

    pipe = pipeline("text-generation",
                    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                    torch_dtype=torch.bfloat16,
                    device=device)
    message = [
        {"role": "user",
            "content": "You are a investiment advisor, and you have to answer the following question:"},
        {"role": "user",
            "content": question},
        {"role": "user",
            "content": f'''Answer the question above using the data below: {data}'''},
        {"role": "user",
            "content": 
            '''You must return the answer in json format, with the following structure: 
            {
                'answer': 'your answer here in str type',
                'confidence': 'your confidence here in int type',
                'justification': 'your short justification here in str type',
            }
            '''}
        ]

    prompt = pipe.tokenizer.apply_chat_template(
        message,
        tokenize=False,
        add_generation_prompt=False
    )

    prediction = pipe(prompt,
                    max_new_tokens=1000,
                    do_sample=True,
                    temperature=0.2, top_k=50, top_p=0.95)

    generated_text = prediction[0]['generated_text']

    #Cleaning the response part 1
    try:
        json_response = generated_text[len(prompt):].strip()
    except:
        raise HTTPException(status_code=500, detail=f"Error in response in {json_response}")
    
    #Cleaning the response part 2
    try:
        json_response = json_response.split("{")[1]
    except:
        raise HTTPException(status_code=500, detail=f"Error in cleaning response, split response in {json_response}")
    
    #Cleaning the response part 3
    try:
        json_response = json_response.split("}")[0]
    except:
        raise HTTPException(status_code=500, detail=f"Error in cleaning response, split response in {json_response}")

    #Convert to json
    try:
        json_response = json.loads('{' + json_response + '}')
    except:
        raise HTTPException(status_code=500, detail=f"Error in converting response to json in in {json_response}")
    
    return json_response

