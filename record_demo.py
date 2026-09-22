import asyncio
import os
import shutil
import subprocess
import imageio_ffmpeg
from playwright.async_api import async_playwright

FRONTEND_URL = "https://smart-plant-assistant-frontend-549755004699.us-east1.run.app"
OUTPUT_DIR = "/config/.gemini/antigravity/brain/a132b4ed-7591-4433-8f19-3862654c9ce0"
TEMP_REC_DIR = "/tmp/playwright_recording"
LOFI_AUDIO = "/tmp/lofi_music.wav"

async def record_demo():
    os.makedirs(TEMP_REC_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=TEMP_REC_DIR,
            record_video_size={"width": 1280, "height": 800}
        )
        
        page = await context.new_page()
        print(f"Navigating to {FRONTEND_URL}...")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await asyncio.sleep(3)

        # 1. Prompt 1: Click prompt chip "Show plant inventory"
        print("Clicking prompt chip 1: '🌿 Show plant inventory'...")
        chip = page.locator(".chip-btn", has_text="Show plant inventory")
        if await chip.count() > 0:
            await chip.click()
        else:
            await page.fill("#input", "🌿 Show my plant inventory")
            await page.click("button[type='submit']")

        print("Waiting 10s for Agent inventory response...")
        await asyncio.sleep(10)

        # 2. Prompt 2: Richer prompt showing tool call & image generation
        rich_prompt = "Generate a vibrant image of a Monstera Deliciosa plant growing in a bright sunny greenhouse"
        print(f"Submitting Prompt 2: '{rich_prompt}'...")
        await page.fill("#input", rich_prompt)
        await asyncio.sleep(1)
        await page.click("button[type='submit']")

        print("Waiting for Agent image generation response...")
        # Wait up to 35s for the generated image component to render in the DOM
        try:
            await page.wait_for_selector("img.a2img", timeout=35000)
            print("Image element found in DOM! Waiting for complete image download...")
            # Ensure the image element is fully loaded (naturalWidth > 0)
            await page.wait_for_function(
                "() => { const img = document.querySelector('img.a2img'); return img && img.complete && img.naturalWidth > 0; }",
                timeout=15000
            )
            print("Image fully loaded and displayed on screen!")
        except Exception as e:
            print(f"Image load wait warning: {e}. Giving generous fallback pause...")
            await asyncio.sleep(15)

        # Additional generous pause so the completed image and conversation display clearly on video
        print("Pausing 8s to showcase completed generated image and UI dialogue...")
        await asyncio.sleep(8)

        # Close page and context to finalize raw video recording file
        video_path = await page.video.path()
        await page.close()
        await context.close()
        await browser.close()

        print(f"Raw video recording saved at: {video_path}")

        # Mix upbeat lo-fi audio track into the recorded video using full imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        target_mp4 = os.path.join(OUTPUT_DIR, "demo_recording.mp4")
        target_webm = os.path.join(OUTPUT_DIR, "demo_recording.webm")

        print("Mixing upbeat lo-fi audio into final video...")
        cmd_mp4 = [
            ffmpeg_bin,
            "-y",
            "-i", video_path,
            "-i", LOFI_AUDIO,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            target_mp4
        ]
        res_mp4 = subprocess.run(cmd_mp4, capture_output=True, text=True)

        cmd_webm = [
            ffmpeg_bin,
            "-y",
            "-i", video_path,
            "-i", LOFI_AUDIO,
            "-c:v", "copy",
            "-c:a", "libopus",
            "-b:a", "128k",
            "-shortest",
            target_webm
        ]
        res_webm = subprocess.run(cmd_webm, capture_output=True, text=True)

        if res_mp4.returncode == 0:
            print(f"Final MP4 video with upbeat lo-fi music saved at: {target_mp4}")
        if res_webm.returncode == 0:
            print(f"Final WebM video with upbeat lo-fi music saved at: {target_webm}")

if __name__ == "__main__":
    asyncio.run(record_demo())
