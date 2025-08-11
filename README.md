# 🤖 Discord Washing Machine Support Bot

An intelligent Discord bot that provides automated customer support for washing machine issues using AI-powered responses and automatic ticket creation.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-v2.3.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🧠 **AI-Powered Responses** - Uses Google Gemini for intelligent problem analysis
- 🔧 **Smart Troubleshooting** - Provides step-by-step solutions for common issues
- 🎫 **Automatic Ticket Creation** - Integrates with MantisHub via SOAP API
- 📊 **Smart Escalation** - Distinguishes between simple fixes and complex problems
- 💾 **Conversation Tracking** - Maintains user conversation history
- 🛡️ **Error Handling** - Graceful fallbacks when AI services are unavailable

## 🎯 How It Works

### For Simple Issues (Troubleshooting Response)
User: *"My clothes aren't getting clean"*

Bot Response:

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/de3d5d4f-21e7-4da1-b010-8b5056333437" />


### For Complex Issues (Automatic Ticket Creation)
User: *"My washing machine won't start at all"*

Bot Response:

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/1b623f67-f5d0-4e21-b07f-1f9069a14786" />


## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Google Gemini API Key
- MantisHub instance with SOAP API access

### Installation

1. **Clone the repository:**
git clone https://github.com/yourusername/washing-machine-bot.git
cd discord-washing-machine-bot

2. **Install dependencies:**
pip install -r requirements.txt

3. **Configure environment variables:**
Edit .env with your actual credentials

4. **Run the bot:**
python bot.py

