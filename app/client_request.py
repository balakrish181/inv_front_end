from pydantic import BaseModel
import instructor
from openai import OpenAI

def parse_lead_from_message(pydantic_model: BaseModel, user_message: str, model_name: str = "openai"):
    
    if model_name == "openai":
        client = instructor.from_openai(OpenAI())
        return client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            response_model=pydantic_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an intelligent assistant that extracts structured information from "
                    "credit card statements/ invoices based only on the information provided. Your ability "
                    "to extract and summarize this information accurately is essential. Do not use "
                    "outside knowledge. Only rely on the context passed by the user",
                },
                {
                    "role": "user",
                    "content": f"Extract the user's CreditCardStatement information from this statement: {user_message}",
                },
            ],
        )
    
    elif model_name == "ollama":
        client = instructor.from_openai(
                        OpenAI(
                            base_url="http://localhost:11434/v1",
                            api_key="ollama",  # required, but unused
                        ),
                        mode=instructor.Mode.JSON,
                    )
        
        return client.chat.completions.create(
                    model="llama3",
                    messages=[

                        {
                    "role": "system",
                    "content": "You are an intelligent assistant that extracts structured information from "
                    "credit card statements/ invoices based only on the information provided. Your ability "
                    "to extract and summarize this information accurately is essential. Do not use "
                    "outside knowledge. Only rely on the context passed by the user",
                        },
                        
                        {
                            "role": "user",
                            "content": f"Extract the user's CreditCardStatement information from this statement: {user_message}",
                        }
                    ],
                    response_model=pydantic_model,
                )
    

    else:
        raise ValueError(f"Model {model_name} not supported")
    