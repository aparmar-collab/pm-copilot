from groq import Groq
from config.settings import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def generate_summary(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You generate accurate project summaries."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
