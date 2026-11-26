# ⚡ ViralPulse AI Studio

> **AI-Powered Viral Video Shorts Generator, Live Stream Clipper & Engagement Engine**

ViralPulse AI Studio is an all-in-one, privacy-first desktop application that automatically transforms long-form videos (YouTube, podcasts, lectures) and live streams (Twitch, Kick, YouTube Live) into high-engagement **9:16 vertical viral shorts** ready for TikTok, YouTube Shorts, and Instagram Reels.

Equipped with audience retention heatmap analysis, live chat pressure tracking, SEO hook generation, dynamic animated captions, and offline speech-to-text, ViralPulse delivers studio-grade editing right from your computer.

---

## 🔥 Key Features

### 1. 📈 Audience Retention Heatmap AI
ViralPulse analyzes YouTube video retention graphs and "Most Replayed" peak points to pinpoint exactly where viewers were most engaged, automatically clipping the highest-impact moments.

### 2. 💬 Live Stream Chat Pressure Tracking
During Twitch, Kick, or YouTube live streams, ViralPulse tracks real-time chat velocity and message spikes (e.g., LMAO, W, POG, OMFG reactions) to clip viral highlights as they happen.

### 3. 🎯 High-CTR YouTube SEO Titles & Big Text Hooks
Every generated short includes a unique, search-optimized title, relevant viral hashtags (`#Shorts`, `#Viral`, `#Trending`), and bold on-screen header text hooks (e.g., `WAIT TILL THE END 💀`) designed to stop viewers from scrolling away in the first 3 seconds.

### 4. 🎨 Topic-Aware Smart Auto-Editing
ViralPulse automatically categorizes video content (Gaming, Podcast, Tech, Comedy, Reaction, Motivation) and selects the ideal aspect ratio crop, zoom tracking, face framing, and subtitle styling for that specific genre.

### 5. 🎬 Word-by-Word Animated Captions
Generate Hollywood-style synchronized captions with customizable animated styles (`Bounce`, `Hype`, `Clean`), vibrant highlight colors, custom fonts (Geist, Archivo Black, Anton, Poppins), and background badges.

### 6. 🎙️ 100% Free Offline Speech Recognition
Runs locally using high-accuracy Sherpa-ONNX Parakeet speech-to-text models. No cloud fees, subscriptions, or API costs are required for transcription.

### 7. 🛡️ Anti-Copyright Protection
Applies subtle micro-frequency audio shifts, frame curves, and metadata stripping to help safeguard your repurposed content against false copyright flags across social media platforms.

### 8. 🧹 1-Click Deep Factory Clean & Tour Reset
- **Reset & Tour**: Instantly resets the onboarding status and starts the interactive tour from scratch.
- **Fresh Clean (Factory Reset)**: Permanently purges all downloaded source media, cached intermediate renders, and temporary junk files, returning the studio to a clean, fresh install state.

### 9. 🔒 100% Safe Local AI Key Storage
Connect your preferred AI model (OpenAI, Anthropic Claude, Google Gemini, Groq, or local Ollama). API keys are stored strictly on your local PC and are fully excluded by `.gitignore` so they are never committed or exposed online.

### 10. 🖥️ Native Desktop Software Experience
No need to manage background terminal windows. When you close the browser window or tab, the background server and terminal close automatically.

---

## 🚀 Installation & Quick Start

ViralPulse AI Studio is designed to run in just 1-2 clicks with zero manual configuration.

### 🪟 Windows (Recommended)

#### Option 1: Native Desktop Software (1-Click Run - No Terminal / No Browser)
1. Download or clone this repository to any folder.
2. Double-click **`create_desktop_shortcut.py`** or run **`ViralPulse AI Studio.vbs`**.
   - A dedicated **ViralPulse AI Studio** icon will be placed directly on your Windows Desktop.
   - Simply double-click the Desktop icon or **`ViralPulse AI Studio.vbs`** to open the standalone app window.
   - **No Python installed?** Don't worry! Double-clicking **`ViralPulse AI Studio.bat`** automatically downloads the isolated portable Python runtime (~25MB) and starts the software with zero manual setup.

#### Option 2: Build a 100% Standalone `.exe` (For USB / Any PC)
To package the entire studio into a standalone executable that runs on any PC without Python:
```bash
python build_standalone_exe.py
```
This produces `dist/ViralPulse AI Studio/ViralPulse AI Studio.exe` which can be shared on a USB drive or copied to any computer.

#### Option 3: Traditional Script Launch
- Run **`Launch_ViralPulse.bat`** or **`Setup_Windows.bat`** to run in traditional browser-assisted mode.

---

### 📱 Multi-Device & Wi-Fi Access (Phone, Tablet, Laptop)

ViralPulse AI Studio can be accessed across any device connected to the same Wi-Fi network:
1. Start the software on your primary computer.
2. The software binds to `0.0.0.0` and displays your local network address (e.g., `http://192.168.1.15:8765`).
3. Open that address in Safari or Chrome on your **iPhone, Android, iPad, or another laptop**.
4. You can queue videos, review generated clips, and control the studio directly from your phone!

---

### 🐧 Linux

1. Open your terminal in the extracted folder:
   ```bash
   chmod +x setup_linux.sh launch_linux.sh
   ./setup_linux.sh
   ```
2. The script installs required packages and sets up a launcher.
3. To start the app anytime, simply run:
   ```bash
   ./launch_linux.sh
   ```

---

### 🍏 macOS

1. Double-click **`setup_mac.command`** in Finder to set up the Python virtual environment and Desktop shortcut.
2. For daily use, double-click **`launch_mac.command`** or the created Desktop shortcut. The app will open in Safari automatically.

---

## ⚙️ System Requirements

| Component | Minimum Requirement | Recommended |
|---|---|---|
| **Operating System** | Windows 10/11 (64-bit), Ubuntu 20.04+, macOS 11+ | Windows 11 (64-bit) |
| **Python** | Python 3.10 or higher | Python 3.11 / 3.12 |
| **RAM** | 8 GB | 16 GB or more |
| **FFmpeg** | Required for video rendering | Automatically detected or install via `winget install Gyan.FFmpeg` |
| **GPU** | Optional (CPU multi-threading supported) | NVIDIA GPU (NVENC acceleration enabled) |

---

## 🛠️ How to Use

1. **Paste a Link**: Insert any YouTube video URL or live stream link (Twitch / Kick / YouTube Live) into the composer box.
2. **AI Analysis**: The engine downloads the audio/video stream, analyzes engagement peaks or chat velocity, and extracts the best moments.
3. **Review & Customize**: Preview generated shorts, fine-tune subtitle colors, customize SEO titles and hashtags.
4. **Export & Share**: Download 1080x1920 MP4 clips individually or download all clips at once in a ZIP archive.

---

## 🤖 AI Configuration (Free & Premium Options)

ViralPulse AI Studio supports multiple AI providers:
- **Google Gemini (Recommended & 100% Free)**: Get a free API key at [Google AI Studio](https://aistudio.google.com/apikey). ViralPulse uses ultra-fast `gemini-flash-lite-latest` and `gemini-3.8-flash` models.
- **OpenAI**: Connect GPT-4o-mini or GPT-4o with your OpenAI API key.
- **Groq**: High-speed Llama-3.3-70B models with zero latency.
- **Anthropic Claude**: Connect Claude 3.5 Sonnet / Haiku.
- **Ollama (100% Offline)**: Run local open-source LLMs directly on your computer without internet access or API fees.

### How to configure your key:
1. Open ViralPulse AI Studio.
2. Go to **Settings -> AI Engine & Key**.
3. Choose your provider (e.g., Google Gemini), paste your key, and click **Save API Key**.
4. Your key is stored strictly on your local computer (`data/ai.json`) and is never committed or uploaded anywhere.

---

## ⌨️ Helpful Shortcuts & Tips

- `Ctrl + F5`: Hard-refresh the studio page to clear any cached assets.
- **Fresh Clean**: Click the red trash icon in the header bar to purge all cached temporary videos and free disk space.
- **Copy SEO**: Click the SEO copy button next to any clip to copy the optimized title, description, and hashtags directly to your clipboard.
