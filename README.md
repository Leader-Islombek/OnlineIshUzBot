# BotIshla 🇺🇿🤖

**Telegram bot** that automatically scrapes new job listings from Freelancer.com, translates them to Uzbek, and posts them to your Telegram channel. Built with ❤️ for O‘zbek freelancing community.

---

## 🚀 Features

- 🔎 Scrapes latest 15 job posts from Freelancer.com
- 💬 Translates job titles & descriptions to O‘zbek
- 💰 Converts $USD to approximate UZS value
- 📢 Posts summaries to Telegram channel
- 🔁 Repeats job fetching every 6 hours
- 🔐 Admin-only commands

---

## 🧪 Technologies

- `python-telegram-bot`
- `aiohttp`, `BeautifulSoup`
- `GoogleTranslator` (via `deep-translator`)
- `Coqui-TTS` (optional)
- `dotenv` for secret configs
- Python 3.11+

---

## ⚙️ Local Setup

```bash
git clone https://github.com/yourusername/botishla.git
cd botishla
pip install -r requirements.txt

Create a .env file:

BOT_TOKEN=your_telegram_bot_token
CHANNEL_ID=@yourchannel
ADMIN_ID=your_admin_id

Then run:
python bot.py


🧭 Render Deployment
Create render.yaml file:
services:
  - type: web
    name: botishla
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python bot.py"
    autoDeploy: true
    envVars:
      - key: BOT_TOKEN
        sync: false
      - key: CHANNEL_ID
        sync: false
      - key: ADMIN_ID
        sync: false


Push your repo to GitHub and connect it on Render.com.

👨‍💻 Commands
| Command | Description | 
| /start | Manually trigger job summary (admin only) | 
| /status | Show bot status timestamp | 
| /summary | Re-send latest jobs (admin only) | 



📌 Notes
- All sent job IDs are cached in sent_jobs.json
- Google Translate fallback used if TTS fails
- .env should be kept private & added to .gitignore


📬 Feedback & Contributions
Pull requests and issues are welcome!
Dev by Islombek with 💡 to support Uzbek freelancers.

