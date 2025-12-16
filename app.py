import streamlit as st
import pandas as pd
import pydeck as pdk
from abc import ABC, abstractmethod
from fpdf import FPDF

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
    return "Разходи се в централните части на града."

# ================== PDF ==================

def generate_pdf(cities, transport, total_cost):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Туристически план", ln=True)
    pdf.ln(5)

    for c in cities:
        pdf.cell(0, 10, f"- {c}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"Транспорт: {transport.name()}", ln=True)
    pdf.cell(0, 10, f"Обща цена: {total_cost:.2f} лв", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# ================== UI ==================

st.set_page_config(page_title="Туристически планер", layout="wide")
st.title("🌍 Интерактивен туристически планер")

route = st.selectbox("🗺️ Маршрут", list(routes.keys()))
days = st.slider("📅 Брой дни", 1, 14, 4)
budget = st.number_input("💰 Бюджет (лв)", 300, 6000, 1500)
transport_choice = st.selectbox("🚍 Транспорт", ["Кола", "Влак", "Самолет"])

transport = {"Кола": Car(), "Влак": Train(), "Самолет": Plane()}[transport_choice]
cities = routes[route]
days_per_city = max(1, days // len(cities))

# ================== MAP (PYDECK) ==================

st.subheader("🗺️ Маршрут")

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

st.subheader("💰 Разходи")
st.write(f"{transport.name()} – {transport_cost:.2f} лв")
st.write(f"🍽️ Храна – {total_food:.2f} лв")
st.write(f"🏨 Хотели – {total_hotel:.2f} лв")
st.write(f"🎟️ Входове – {total_tickets:.2f} лв")
st.write(f"🛍️ Допълнителни – {EXTRA_COSTS:.2f} лв")
st.write(f"🌱 CO₂ – {co2:.1f} kg")

st.markdown("---")
st.write(f"## 💵 Общо: **{total_cost:.2f} лв**")

# ================== RISK ANALYSIS ==================

st.subheader("⚠️ Риск анализ")

if total_cost > budget * 0.8:
    st.warning("Бюджетът е почти изчерпан")

if co2 > 200:
    st.warning("Висок CO₂ отпечатък")

if distance > 800:
    st.warning("Дълъг маршрут")

# ================== AI CHAT ==================

st.subheader("🤖 AI туристически асистент")
city = st.selectbox("Град", cities)
question = st.text_input("Задай въпрос")

if question:
    st.info(ai_assistant(city, question))

# ================== PDF ==================

pdf = generate_pdf(cities, transport, total_cost)
st.download_button("📄 Изтегли PDF план", pdf, "travel_plan.pdf")
