import streamlit as st
import pydeck as pdk
from abc import ABC, abstractmethod

# ================== DATA ==================

routes = {
    "Bulgaria → Germany": ["Sofia", "Belgrade", "Vienna", "Munich"]
}

city_info = {
    "Sofia": {
        "lat": 42.6977, "lon": 23.3219,
        "hotel": 70, "food": 20, "ticket": 10,
        "tip": "Visit the city center and Vitosha mountain."
    },
    "Belgrade": {
        "lat": 44.7866, "lon": 20.4489,
        "hotel": 65, "food": 22, "ticket": 8,
        "tip": "Kalemegdan and nightlife."
    },
    "Vienna": {
        "lat": 48.2082, "lon": 16.3738,
        "hotel": 90, "food": 30, "ticket": 18,
        "tip": "Palaces, museums, and classical music."
    },
    "Munich": {
        "lat": 48.1351, "lon": 11.5820,
        "hotel": 95, "food": 28, "ticket": 15,
        "tip": "Marienplatz and Bavarian beer."
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
        return "Car"


class Train(Transport):
    def __init__(self):
        super().__init__(0.18, 0.05)

    def name(self):
        return "Train"


class Plane(Transport):
    def __init__(self):
        super().__init__(0.45, 0.25)

    def name(self):
        return "Plane"

# ================== AI ASSISTANT ==================

def ai_assistant(city, question):
    q = question.lower()
    if "what" in q or "do" in q:
        return city_info[city]["tip"]
    if "food" in q:
        return "Try the local cuisine around the city center."
    return "Walking in the city center is always a good choice."

# ================== UI ==================

st.set_page_config(page_title="Interactive Travel Planner", layout="wide")
st.title("Interactive Travel Planner")

route = st.selectbox("Route", list(routes.keys()))
days = st.slider("Number of days", 1, 14, 4)
budget = st.number_input("Budget (BGN)", 300, 6000, 1500)
transport_choice = st.selectbox("Transport", ["Car", "Train", "Plane"])

transport = {"Car": Car(), "Train": Train(), "Plane": Plane()}[transport_choice]
cities = routes[route]
days_per_city = max(1, days // len(cities))

# ================== PYDECK MAP ==================

st.subheader("Travel Route Map")

path = [(city_info[c]["lon"], city_info[c]["lat"]) for c in cities]

layer = pdk.Layer(
    "PathLayer",
    data=[{"path": path}],
    get_path="path",
    get_color=[255, 0, 0],
    width_scale=20,
    width_min_pixels=4
)

view_state = pdk.ViewState(latitude=46, longitude=18, zoom=4)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# ================== COSTS ==================

total_food = total_hotel = total_tickets = 0

for c in cities:
    total_food += city_info[c]["food"] * days_per_city
    total_hotel += city_info[c]["hotel"] * days_per_city
    total_tickets += city_info[c]["ticket"]

distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
transport_cost = transport.cost(distance)
co2 = transport.emissions(distance)

total_cost = transport_cost + total_food + total_hotel + total_tickets + EXTRA_COSTS

st.subheader("Expenses")
st.write(f"{transport.name()} – {transport_cost:.2f} BGN")
st.write(f"Food – {total_food:.2f} BGN")
st.write(f"Hotels – {total_hotel:.2f} BGN")
st.write(f"Tickets – {total_tickets:.2f} BGN")
st.write(f"Extras – {EXTRA_COSTS:.2f} BGN")
st.write(f"CO₂ – {co2:.1f} kg")

st.markdown("---")
st.write(f"## Total: {total_cost:.2f} BGN")

# ================== RISK ANALYSIS ==================

st.subheader("Risk Analysis")

if total_cost > budget * 0.8:
    st.warning("⚠️ Budget is almost exceeded")

if co2 > 200:
    st.warning("⚠️ High CO₂ footprint")

if distance > 800:
    st.warning("⚠️ Long travel distance")

# ================== AI CHAT ==================

st.subheader("AI Travel Assistant")
city = st.selectbox("City", cities)
question = st.text_input("Ask a question")

if question:
    st.info(ai_assistant(city, question))

# ================== EXPORT (TXT) ==================

plan_text = f"""
TRAVEL PLAN

Route: {' -> '.join(cities)}
Transport: {transport.name()}
Total cost: {total_cost:.2f} BGN
CO₂ footprint: {co2:.1f} kg
"""

st.download_button(
    "Download Plan (TXT)",
    plan_text,
    file_name="travel_plan.txt",
    mime="text/plain"
)
