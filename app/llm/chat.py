from openai import AsyncOpenAI
import json

class FitnessChat:
    def __init__(self, config):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = config.OPENAI_MODEL
        
    def build_system_prompt(self) -> str:
        return """You are FitBot, an advanced, highly knowledgeable AI fitness assistant. 
Your goal is to provide accurate, helpful, and motivational fitness, nutrition, and wellness advice.
Always be polite, encouraging, and supportive.

IMPORTANT RULES:
1. Use the provided context to answer questions accurately. If the answer is in the context, prioritize that information.
2. Cite your sources when providing information from the context.
3. Give evidence-based advice.
4. Format your responses clearly using Markdown (bullet points, bold text, etc.).
5. SAFETY FIRST: Always recommend consulting a medical professional, doctor, or physical therapist for injury-related or medical concerns. You are an AI, not a doctor.
6. Do NOT provide medical advice or diagnoses.

Be the ultimate personal trainer and health companion for the user!"""

    def build_messages(self, user_query: str, context: str, chat_history: list[dict] = None) -> list[dict]:
        messages = [{"role": "system", "content": self.build_system_prompt()}]
        
        if chat_history:
            messages.extend(chat_history)
            
        augmented_query = user_query
        if context:
            augmented_query = f"Context information is below:\n\n{context}\n\nGiven the context information and not prior knowledge, answer the following question: {user_query}"
            
        messages.append({"role": "user", "content": augmented_query})
        return messages

    async def chat(self, user_query: str, context: str, chat_history: list[dict] = None) -> str:
        messages = self.build_messages(user_query, context, chat_history)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

    async def chat_stream(self, user_query: str, context: str, chat_history: list[dict] = None):
        messages = self.build_messages(user_query, context, chat_history)
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
