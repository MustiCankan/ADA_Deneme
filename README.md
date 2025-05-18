![ADA Logo](./logo.png)

# ADASpirit
ADA is a digital AI assistant tool created by Spirit AI. It is designed to handle automated conversations, such as restaurant reservations and customer service interactions, using state-of-the-art large language models (LLMs) and messaging APIs like Twilio WhatsApp.

🚀 Quick Start

Before starting the project, set up your virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```
To run in the google adk envrionment
```bash
adk web
```

The project strucure will be :
```bash
ADASpirit/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI main application
│   ├── agents.py       # LLM agent configurations
│   ├── tools.py        # Utility tools (e.g., reservation maker)
│   └── database.py     # Optional: database connection (e.g., SQLite/PostgreSQL)
├── tests/
│   └── test_app.py     # Unit and integration tests
├── .env.example        # Environment variables template
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── LICENSE
```

🖥️ How It Works
	•	ADA listens for incoming WhatsApp messages via the Twilio API.
	•	The system collects structured reservation information:
	•	Name
	•	Date (YYYY-MM-DD)
	•	Time (HH:MM)
	•	Party size
	•	Missing fields are automatically prompted to the user.
	•	Once all data is collected, ADA formats it as JSON and sends it to the reservation_maker tool.
	•	ADA relays confirmation or error messages back to the user.
⚙️ Environment Setup

Create a .env file in the project root with the following keys:
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_NUMBER=whatsapp:+your_twilio_number
TO_NUMBER=whatsapp:+destination_number
GOOGLE_API_KEY=your_google_api_key
```

🧪 Running the App

```bash
uvicorn ada.agent:app --reload
ngrok http 8000 # in the other terminal
```

📝 Features (Planned & Implemented)
	•	WhatsApp integration via Twilio API
	•	Structured data collection flow
	•	LLM-powered conversation engine (Gemini / GPT)
	•	Google Sheets / Database integration for reservation storage
	•	Admin dashboard for monitoring reservations
	•	Multi-language support

👥 Contributing
	1.	Fork the repository.
	2.	Create a new branch: git checkout -b feature/my-feature.
	3.	Commit your changes: git commit -m 'Add new feature'.
	4.	Push to the branch: git push origin feature/my-feature.
	5.	Open a pull request.

📄 License

This project is licensed under the MIT License.
