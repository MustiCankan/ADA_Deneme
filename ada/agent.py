import os
import asyncio
import warnings
from fastapi import FastAPI, Form, Depends


# Google adk
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts

# SQL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
from .models import Conversation, SessionLocal
from .utils import send_message, logger

# Time Imports
import datetime
from zoneinfo import ZoneInfo

# API Keys 
from dotenv import load_dotenv
load_dotenv()

# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)  # Or logging.INFO

print("Libraries imported.")

# Add Agent Model
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Starting with Gemini

# Adding API Keys
os.environ["GOOGLE_API_KEY"] = ""

# ✅ Get environment variables using os.environ.get
db_user           = os.environ.get("DB_USER")
db_password       = os.environ.get("DB_PASSWORD")
whatsapp_number   = os.getenv("TO_NUMBER")


# FastAPI for Wp messaging 
app = FastAPI()

# Dependency for database session
def get_db_session(): # Renamed from get_db for clarity when called directly
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tool for getting today's information

def get_current_time_in_turkey() -> str:
    """
    Provides the current date and time in Turkey.
    Useful for determining today's date for reservations if the user doesn't specify one.
    Returns a string with the current date in YYYY-MM-DD format and current time.
    """
    print("--- Tool: get_current_time_in_turkey called  ---") # Log tool execution
    try:
        tz_identifier = "Europe/Istanbul" # Standard timezone identifier
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        report = (
            f'The current date in Turkey is {now.strftime("%Y-%m-%d")}. '
            f'The current time is {now.strftime("%H:%M:%S %Z%z")}.'
        )
        return report
    except Exception as e:
        logger.error(f"Error in get_current_time_in_turkey: {e}")
        return "I'm having trouble getting the current time right now."

# SQL Database Tool for making reservations

def reservation_maker(
    name: str,
    surname: str,
    date: str,
    time: str,
    reservation_type: str,
    party_size: int
) -> str:
    """
    Saves the reservation to the database and returns a confirmation message.
    """
    db_session_gen = get_db_session()
    db = next(db_session_gen)
    print("--- Tool: reservation_maker called  ---") # Log tool execution
    try:
        # The 'sender' in Conversation model. Using whatsapp_number (bot's number) as per original structure.
        # Ideally, this would be a user-specific identifier (e.g., USER_ID).
        # The 'message' will store a summary of the reservation details.
        # The 'response' will store the confirmation message returned by this tool.
        reservation_details_summary = (
            f"Reservation for: {name} {surname}, Date: {date}, Time: {time}, "
            f"Type: {reservation_type}, Guests: {party_size}"
        )
        confirmation_message = (
            f"OK! I've successfully made a reservation for {name} {surname} on {date} at {time} "
            f"for {party_size} guest(s) for {reservation_type}. "
            f"Have a fun! See you soon!"
        )

        conv = Conversation(
            sender=whatsapp_number,
            name = name,
            surname = surname,
            date =  date,
            time =  time,
            reservation_type = reservation_type,
            party_size = str(party_size)
        )
        db.add(conv)
        db.commit()
        logger.info(f"Reservation for {name} {surname} stored in database (Conversation #{conv.id}).")
        return confirmation_message
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemyError storing reservation in database: {e}")
        return f"I'm sorry, there was a database error trying to make your reservation. Please try again later."
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in reservation_maker: {e}")
        return "An unexpected error occurred while trying to make your reservation. Please try again."
    finally:
        try:
            next(db_session_gen, None) # Ensure the finally block of get_db_session is called
        except StopIteration:
            pass
        # db.close() # Already handled by get_db_session's finally block

# TODO: Add here farewell agent 


# Main Agent
root_agent = Agent(
    name="ada",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Restoran için rezervasyon alır ve veritabanına kaydeder.",
    instruction=(
        """
        Rezervasyon alabilen yardımcı bir asistan olarak görev yapıyorsun. Sen ADA’sın, Spirit AI rezervasyon asistanısın.
        Müşteriyi sıcak bir şekilde karşıla ve nasıl yardımcı olabileceğini sor.

    
        Aşağıdaki bilgileri toplaman gerekiyor:
        - name (isim)
        - surname (soyadı)
        - date (tarih, YYYY-MM-DD formatında olmalı)
        - time (saat, HH:MM formatında olmalı)
        - reservation_type (rezervasyon tipi, örneğin: loca, bakcstage, sahne)
        - party_size (kişi sayısı, bir sayı olmalı)

        Bu alanlardan herhangi biri eksikse, kullanıcıya nazikçe sor (örn. "Harika! Hangi tarih için rezervasyon yapmak istersiniz?"). Eğer bu bilgi daha önceden verildiyse onu tekrardan sorma.
        Eğer bugün için rezervasyon istiyorsa `get_current_time_in_turkey` aracını kullan.
        Tüm bilgiler tamamsa, bütün bilgilerin olduğu bir onaylama mesaji gönder. Eğer onaylarsa,`reservation_maker` aracını rezervasyonu kullanarak veri tabanına gönder.

        (Not: `party_size` bir sayı olmalıdır, tırnak içinde olmamalıdır.)
        JSON'dan sonra başka hiçbir şey yazma. Araç rezervasyonu kaydedecek ve dönen onayı kullanıcıya iletmeni sağlayacak. Bu onayı olduğu gibi kullanıcıya ilet.
        Eğer kullanıcı sadece "merhaba", "selam" gibi bir selam verirse, kendini tanıt ("Merhaba, ben ADA, Spirit AI rezervasyon asistanıyım. Size nasıl yardımcı olabilirim?") ve ne yapabileceğini sor.
        Eğer kullanıcı bugünün tarihini veya saatini sorarsa, `get_current_time_in_turkey` aracını kullan ve bilgiyi kullanıcıya ilet.
        Kullanıcıya karşı her zaman kibar ve profesyonel ol. Anlaşılmayan bir şey olursa açıklama iste.
        """
    ),
    tools=[reservation_maker, get_current_time_in_turkey]
)

print(f"Agent '{root_agent.name}' created using model '{AGENT_MODEL}'.")


# @title Setup Session Service and Runner

# --- Session Management ---
# Key Concept: SessionService stores conversation history & state.
# InMemorySessionService is simple, non-persistent storage for this tutorial.
session_service = InMemorySessionService()


# TODO: Check the session and brainstrom 
#  Getting Whatsapp Message and Running the LLM Model Here
APP_NAME = "ADA_Restaurant_Bot" # More descriptive App Name
USER_ID = "user_whatsapp_default" # Placeholder, should be dynamic per user
SESSION_ID = "session_default" # Placeholder, should be dynamic per user session

# Create the specific session where the conversation will happen
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)

# Create the specific session (this might be better done per request for unique sessions)
# For simplicity in this script, a single session is reused.
# In a production app, you'd likely create/retrieve sessions dynamically.
try:
    session = session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    print(f"Existing session retrieved: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
except Exception: # Replace with specific ADK SessionNotFound error if available
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"New session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")



runner = Runner(
    agent=root_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)
print(f"Runner created for agent '{runner.agent.name}'.")

# @title Define Agent Interaction Function

async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # Key Concept: run_async executes the agent logic and yields Events.
  # We iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found

  print(f"<<< Agent Response: {final_response_text}")
  return final_response_text


# We need an async function to await our interaction helper
async def run_conversation():
    await call_agent_async("Merhaba, rezervasyon yapmak istiyordum.",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
    
    await call_agent_async("Merhaba, adınız nedir?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
    
    await call_agent_async("Merhaba, ben Mustafa Cankan. Bugün akşam 4'de 8 kişi mekanınıza gelecez.",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
    await call_agent_async("Bugün tarihi nedir?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
    

# TODO: Update this part more reliable
# Sending messages through Whatsapp
@app.post("/message")         # ← corrected decorator
async def reply(
    Body: str = Form(),     # Form(...) makes body required
):
    try:
        chat_response = await call_agent_async(Body,
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
        
        # Send back via WhatsApp
        send_message(whatsapp_number, chat_response)

        # It’s better to return JSON so clients don’t choke on empty bodies
        return {"status": "ok", "message": chat_response}
    
    except Exception as e:
         print(f"An error occurred: {e}")


