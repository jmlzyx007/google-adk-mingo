import asyncio
import os
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

from agent import root_agent

# Helper function to load an image from a local file path
def load_image_from_file(path: str) -> types.Part:
    """Load image from file and return a types.Part object."""
    with open(path, 'rb') as f:
        image_bytes = f.read()
    
    # Simple logic to determine mime type
    mime_type = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'

    return types.Part(
        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
    )

class VisualCatalogApp:
    def __init__(self):
        # 1. The Agent (The Intelligence) lives in agent.py so it is also
        # discoverable by `adk web`.
        self.agent = root_agent
        # 2. Build the App and Runner (The Infrastructure)
        self.app = App(name="visual_catalog", root_agent=self.agent)
        self.runner = InMemoryRunner(app=self.app)

    async def analyze_product(self, product_id: str, image_path: str):
        print(f"\n--- Analyzing Product: {product_id} ---")
        user_id = "catalog_admin"
        session_id = f"sess_{product_id}"

        # Step 1: Explicitly create the session
        # For run_async, the session resource must exist before sending messages.
        await self.runner.session_service.create_session(
            app_name=self.app.name,
            user_id=user_id,
            session_id=session_id
        )

        # Step 2: Load the image using the helper
        image_part = load_image_from_file(image_path)

        # Step 3: Construct the multimodal Content object
        msg = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Analyze product ID '{product_id}' and write a catalog description."),
                image_part
            ]
        )

        # Step 4: Run the agent using run_async
        print("Sending image to Gemini...")
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=msg
        ):
            # Step 5: Extract the final text response
            if event.is_final_response():
                description = event.content.parts[0].text
                print(f"Description Generated:\n{description}\n")

async def main():
    load_dotenv()
    catalog = VisualCatalogApp()

    # Assumes images are in the parent directory relative to your terminal
    products = [
        ('HEADPHONES-01', '../headphones.jpg'),
        ('LAPTOP-02', '../laptop.jpg'),
    ]

    for product_id, path in products:
        if os.path.exists(path):
            await catalog.analyze_product(product_id, path)
            await asyncio.sleep(1) # Rate limit protection
        else:
            print(f"Warning: Image not found at {path}")

if __name__ == '__main__':
    asyncio.run(main())