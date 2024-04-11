from llm_commons.proxy.openai import ChatCompletion


# Use the OpenAI API to execute the prompt
def get_completion(prompt, model="gpt-35-turbo", temperature=0, role="user"):
    messages = [{"role": role, "content": prompt}]
    response = ChatCompletion.create(  # <---
        deployment_id=model,  # <---
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]
