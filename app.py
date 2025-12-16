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
    "София": {"lat": 42.6977, "lon": 23.3219, "tip": "Посети центъра и Витоша."},
    "Белград": {"lat": 44.7866, "lon": 20.4489, "tip": "Калемегдан и нощният живот."},
    "Виена": {"lat": 48.2082, "lon": 16.3738, "tip": "Музеи и дворци."},
    "Мюнхен": {"lat": 48.1351, "lon": 11.5820, "tip": "Мариенплац и бирарии."}
}

DISTANCE_BETWEEN_CITIES = 300

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price, co2):
        self.price = price
        self.co2 = co2

    def cost(self, dist): return dist * self.price
    def emissions(self, dist): return dist * self.co2

    @abstractmethod
    def name(self): pass


class Car(Transport):
    def __init__(self): super().__init__(0.25, 0.18)
    def name(self): return "🚗 Кола"


class Train(Transport):
    def __init__(self): super().__init__(0.18, 0.05)
    def name(self): return "🚆 Влак"


class Plane(Transport):
    def __init__(self): super().__init__(0.45, 0.25)
    def name(self): return "✈️ Самолет"

# ================== AI ASSISTANT ==================

def ai_assistant(city, question):
    if "какво" in question.lower():
        return city_info[city]["tip"]
    return "Опитай местната кухня и централните зони."

# ================== PDF ==================

def generate_pdf(cities, transport, cost):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Туристически план", ln=True)

    for c in cities:
        pdf.cell(0, 10, f"- {c}", ln=True)

    pdf.cell(0, 10, f"Транспорт: {transport.name()}", ln=True)
    pdf.cell(0, 10, f"Обща цена: {cost:.2f} лв", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# ================== UI ==================

st.set_page_config("Туристически планер", layout="wide")
st.title("🌍 Интерактивен туристически планер")

days = st.slider("📅 Брой дни", 1, 14, 4)
budget = st.number_input("💰 Бюджет", 300, 6000, 1500)
transport_choice = st.selectbox("🚍 Транспорт", ["Кола", "Влак", "Самолет"])

transport = {"Кола": Car(), "Влак": Train(), "Самолет": Plane()}[transport_choice]
cities = routes["България → Германия"]

# ================== PYDECK MAP ==================

coords = [(city_info[c]["lon"], city_info[c]["lat"]) for c in cities]

layer = pdk.Layer(
    "PathLayer",
    data=[{"path": coords}],
    get_path="path",
    width_scale=20,
    width_min_pixels=4,
    get_color=[255, 0, 0]
)

view = pdk.ViewState(latitude=46, longitude=18, zoom=4)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

# ================== COSTS ==================

distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
cost = transport.cost(distance)
co2 = transport.emissions(distance)

st.subheader("💰 Разходи")
st.write(f"{transport.name()} – {cost:.2f} лв")
st.write(f"🌱 CO₂ – {co2:.1f} kg")

# ================== RISK ANALYSIS ==================

st.subheader("⚠️ Риск анализ")

if cost > budget * 0.8:
    st.warning("Бюджетът е почти изчерпан")

if co2 > 200:
    st.warning("Висок CO₂ отпечатък")

if distance > 800:
    st.warning("Дълъг маршрут")

# ================== AI CHAT ==================

st.subheader("🤖 AI туристически асистент")
city = st.selectbox("Град", cities)
question = st.text_input("Въпрос")

if question:
    st.info(ai_assistant(city, question))

# ================== PDF ==================

pdf_data = generate_pdf(cities, transport, cost)
st.download_button("📄 Изтегли PDF", pdf_data, "plan.pdf")
