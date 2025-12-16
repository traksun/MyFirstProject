import streamlit as st
import pydeck as pdk
from abc import ABC, abstractmethod

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"]
}

city_info = {
    "София": {
        "lat": 42.6977, "lon": 23.3219,
        "hotel": 70, "food": 20, "ticket": 10,
        "tip": "Посети центъра и Витоша."
    },
    "Белград": {
        "lat": 44.7866, "lon": 20.4489,
        "hotel": 65, "food": 22, "ticket": 8,
        "tip": "Калемегдан и нощният живот."
    },
    "Виена": {
        "lat": 48.2082, "lon": 16.3738,
        "hotel": 90, "food": 30, "ticket": 18,
        "tip": "Дворци, музеи и класическа музика."
    },
    "Мюнхен": {
        "lat": 48.1351, "lon": 11.5820,
        "hotel": 95, "food": 28, "ticket": 15,
        "tip": "Мариенплац и баварска бира."
    }
}

DISTANCE_BETWEEN_CITIES = 300
EXTRA_COSTS = 50

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price_per_km, co2_per_km):
        self.price = price_per_km
        self.co2 = co2_per_km

    def cost(self, distance):
        return distance * self.price

    def emissions(self, distance):
        return distance * self.co2

    @abstractmethod
    def name(self):
        pass


class Car(Transport):
    def __init__(self):
        super().__init__(0.25, 0.18)

    def name(self):
        return "🚗 Кола"


class Train(Transport):
    def __init__(self):
        super().__init__(0.18, 0.05)

    def name(self):
        return "🚆 Влак"


class Plane(Transport):
    def __init__(self):
        super().__init__(0.45, 0.25)

    def name(self):
        return "✈️ Самолет"

# ================== AI ASSISTANT ==================

def ai_assistant(city, question):
    q = question.lower()
    if "какво" in q or "правя" in q:
        return city_info[city]["tip"]
    if "храна" in q:
        return "Опитай местната кухня около центъра."
    return "Разходка из централните части е добър избор."

# ================== UI ==================

st.set_page_config(page_title="Туристически планер", layout="wide")
st.title("🌍 Интерактивен туристически планер")

route = st.selectbox("🗺️ Маршрут", list(routes.keys()))
days = st.slider("📅 Брой дни", 1, 14, 4)
budget = st.number_input("💰 Бюд_
