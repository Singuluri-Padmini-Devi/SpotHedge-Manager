# 🛡️ Spot Exposure Hedging Bot

A Telegram-based risk management bot for automatically monitoring and hedging spot positions using perpetual futures. Designed to simulate professional trading tools with risk analytics, interactive commands, and real-time alerts.

---

## 🚀 Features

- 📉 **Delta Risk Calculation** and threshold-based auto hedging
- 🤖 Telegram bot with rich commands and inline buttons
- 🧮 **Portfolio Analytics** – VaR, Max Drawdown, Delta Exposure
- 📊 **Hedge History and Analytics** logging
- 📡 Background monitoring with alerts when thresholds are breached
- 💬 Commands include `/start`, `/hedge`, `/setrisk`, `/portfolio_risk`, and more

---

## 🛠️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/spot-hedging-bot.git
   cd spot-hedging-bot
   ```
2. **Install required Python packages**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the bot**
   ```bash
   python bot/telegram_bot.py
   ```
4. **Interact using Telegram**
   - Go to your Telegram bot (created with BotFather)
   - Use commands like:
     - `/start`
     - `/setrisk 2.5`
     - `/hedge 3.0`
     - `/hedge_status BTCUSDT`
     - `/hedge_analytics`
     - `/portfolio_risk 3.0`
     - `/menu`

---

## 📂 Folder Structure

```
spot-hedging-bot/
├── bot/
├── config/
├── exchanges/
├── hedging/
├── risk_engine/
├── hedge_logs.db (auto-created)
├── hedging_bot.log (auto-created)
├── requirements.txt
└── README.md
```

---

## 📊 Sample Commands

- `/setrisk 2.5` – Set your delta threshold
- `/hedge 3.0` – Trigger an auto-hedge if risk exceeds threshold
- `/hedge_history` – View full hedge log
- `/hedge_analytics` – View cost, total hedges, average delta
- `/portfolio_risk 3.0` – View VaR and Max Drawdown
- `/menu` – View quick action buttons

---
---

## 👨‍💻 Developer

**Padmini Devi Singaluri**  
Full-Stack Developer | Python & AI Enthusiast  
