import os
from openai import OpenAI


def ask_ai(question, data_context):
    """
    Answer questions using only the provided utility data.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "OpenAI API key is not configured."

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an AI assistant for a Utility Intelligence dashboard.

Your job is to answer questions using ONLY the utility data
provided below.

If the answer cannot be found in the provided data, clearly say:
"I could not find this information in the available data."

Do not invent numbers, dates, locations, or conclusions.

UTILITY DATA:
{data_context}

USER QUESTION:
{question}

Give a clear and concise answer.
If useful, include the relevant numbers and explain what they mean.
"""

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        return response.output_text

    except Exception as e:
        return f"AI error: {e}"