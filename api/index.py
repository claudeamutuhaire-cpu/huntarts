from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import requests
import asyncio
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="HuntClaw - Apex Predator Webhook")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
REPLICATE_TOKEN = os.getenv("REPLICATE_TOKEN")

HUNTER_PROMPT = """
You are HuntClaw — apex predator from Kampala, Uganda. HUNT ARTS savage twin.
No weak politeness. Hunter tone ONLY: "Trash detected 🔪", "Prey locked 🎯", "Kill shot delivered 💀", "Matooke-fresh glow-up 🔥", "Boda-fast", "Weak vibes terminated", Luganda flex ("Munno oyee", "Tulina okuhunt", "Savage delivered").
Services: cinematic photo glow-up/NSFW (quote high & discreet), WhatsApp bots (500k setup + 100k/mo), site/domain flips.
Push MoMo/Airtel upfront HARD. Privacy: "Pics hunted, data ghosted".
Direct, rude to wasters. All caps emphasis. Emojis heavy: 🔥 💀 🔪 📸 🎯 😈
When image: roast trash original, hype cinematic upgrade using EXACT base: "Transform this photo into a stunning cinematic masterpiece portrait, regardless of original quality: ultra-detailed and razor-sharp focus, perfectly smooth natural skin with preserved authentic texture and fine details, dramatic yet flattering cinematic lighting with soft glowing highlights, subtle rim light and gentle depth, rich professional color grading with dynamic contrast, cinematic teal-orange tones and elegant harmony, intense captivating movie-star charisma and magnetic presence, shallow depth of field with creamy cinematic bokeh, subtle authentic film grain for a high-end movie feel, shot on premium cinema camera, 8K resolution, breathtaking and fascinating mood, absolute masterpiece quality" + user text.
Sell pro edit hard. No mercy.
"""

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()
    except:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    sender = data.get("from", "unknown")
    message = data.get("message", {})
    text = message.get("text", "") or message.get("body", "")
    image_data = message.get("image")  # base64 expected from gateway

    if not text and not image_data:
        return JSONResponse({"status": "ok"})

    user_input = text
    if image_data:
        user_input += " [image attached - roast trash + cinematic kill]"

    reply = "Hunter offline — send MoMo 100k to wake the beast 😈"
    if client:
        try:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": HUNTER_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.95,
                max_tokens=450
            )
            reply = resp.choices[0].message.content
        except Exception as e:
            reply = f"Groq fucked: {str(e)}. Weak vibes."

    enhanced_url = None
    if image_data and REPLICATE_TOKEN:
        try:
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]

            full_prompt = HUNTER_PROMPT.split("EXACT base:")[1].strip().split("+ user text")[0] + text

            payload = {
                "version": "black-forest-labs/flux-kontext-pro",
                "input": {
                    "image": f"data:image/jpeg;base64,{image_data}",
                    "prompt": full_prompt,
                    "negative_prompt": "blurry, ugly, deformed, low quality, artifacts",
                    "strength": 0.65,
                    "num_inference_steps": 35,
                    "guidance_scale": 7.5
                }
            }

            headers = {"Authorization": f"Token {REPLICATE_TOKEN}", "Content-Type": "application/json"}
            resp = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
            pred = resp.json()

            if "error" in pred:
                reply += f"\nReplicate error: {pred['error']}"
            else:
                for _ in range(25):
                    await asyncio.sleep(5)
                    poll = requests.get(f"https://api.replicate.com/v1/predictions/{pred['id']}", headers=headers).json()
                    if poll.get("status") == "succeeded":
                        enhanced_url = poll["output"][0] if isinstance(poll["output"], list) else poll["output"]
                        reply += f"\nKILL SHOT DELIVERED 🔥 {enhanced_url}\nPay 150k UGX full res munno!"
                        break
                    if poll.get("status") == "failed":
                        reply += "\nHunt failed."
                        break
        except Exception as e:
            reply += f"\nCinematic kill crashed: {str(e)}"

    return JSONResponse({"reply": reply, "enhanced": enhanced_url})

@app.get("/")
def health():
    return {"status": "HuntClaw LIVE — prey locked 🔥💀🔪"}
