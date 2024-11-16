import os

from openai import OpenAI
client = OpenAI(api_key=os.environ.get('key'))
m = "Write a haiku about recursion in programming."
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": m
        }
    ]
)

print(completion.choices[0].message.content)