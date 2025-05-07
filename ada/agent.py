import os
import asyncio
import warnings
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts

# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")



# This agent will control tools and the storage 
root_agent = Agent(
    name="ava",
    model="gemini-2.0-flash",
    description="Restoran için rezervasyon alır ve veritabanına kaydeder.",
    instruction=(
        """
        Rezervasyon alabilen yardımcı bir asistan olarak görev yapıyorsun. Sen AVA’sın, Spirit AI rezervasyon asistanı. 
        Aşağıdaki bilgileri toplamalısın:
        - name (isim)
        - date (tarih, YYYY-MM-DD formatında)
        - time (saat, HH:MM formatında)
        - party_size (kişi sayısı)

        Bu alanlardan herhangi biri eksikse, kullanıcıya özel olarak sor (örn. "Hangi tarih için rezervasyon yapmak istersiniz?").
        Tüm dört bilgi tamamsa, sadece aşağıdaki JSON’u çıktı olarak vererek reservation_maker aracını çağır:
        
        ```json
        {"name": "...", "date": "YYYY-MM-DD", "time": "HH:MM", "party_size": "..."}
        ```
        
        ve başka hiçbir şey yazma. Araç rezervasyonu kaydedecek ve dönen onayı kullanıcıya iletmeni sağlayacak.
        """
    ),
)

# Adjust the runner 


