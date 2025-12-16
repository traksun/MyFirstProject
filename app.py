import streamlit as st
from abc import ABC, abstractmethod
import pandas as pd
import folium
from streamlit_folium import st_folium

# ================== DATA ==================
routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"],
    "България → Италия": ["София", "Любляна", "Венеция", "Рим"]
}

city_info = {
    "София": {"hotel": ("Hotel Sofia Center", 70), "food": ("Традиционна българска кухня", 20), "sight": "Катедралата Александър Невски", "entry_fee": 10, "coords": (42.6977, 23.3219)},
    "Белград": {"hotel": ("Belgrade Inn", 65), "food": ("Сръбска скара", 22), "sight": "Калемегдан", "entry_fee": 8, "coords": (44.8176, 20.4569)},
    "Виена": {"hotel": ("Vienna City Hotel", 90), "food": ("Виенски шницел", 30), "sight": "Дворецът Шьонбрун", "entry_fee": 15, "coords": (48.2082, 16.3738)},
    "Мюнхен": {"hotel": ("Munich Central Hotel", 95), "food": ("Немска кухня", 28), "sight": "Мариенплац", "entry_fee": 12, "coords": (48.1351, 11.5820)},
    "Любляна": {"hotel": ("Ljubljana Hotel", 80), "food": ("Словенска кухня", 25), "sight": "Замъкът Любляна", "entry_fee": 10, "coords": (46.0569, 14.5058)},
    "Венеция": {"hotel": ("Venice Hotel", 100), "food": ("Италианска кухня", 35), "sight": "Площад Сан Марко", "entry_fee": 18, "coords": (45.4408, 12.3155)},
    "Рим": {"hotel": ("Rome Central Hotel", 110), "food": ("Паста и пица", 30), "sight": "Колизеум", "entry_fee": 20, "coords": (41.9028, 12.4964)}
}

DISTANCE_BETWEEN_CITIES = 300  # км (опростено)

# ================== OOP ==================
class Transport(ABC):
    def __init__(self, price_per_km):
        self.price_per_km = price_per_km

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def travel_time(self, distance):
        pass

    def travel_cost(self, distance):
        return distance * self.price_per_km

class Car(Transport):
    def __init__(self):
        super().__init__(0.25)

    def name(self):
        return "🚗 Кола"

    def travel_time(self, distance):
        return distance / 80

class Train(Transport):
    def __init__(self):
        super().__init__(0.18)

    def name(self):
        return "🚆 Влак"

    def travel_time(self, distance):
        return distance / 120

class Plane(Transport):
    def __init__(self):
        super().__init__(0.45)

    def name(self):
        return "✈️ Самолет"

    def travel_time(self, distance):
        return distance / 600

# ================== UI ==================
st.title("🌍 Интерактивен туристически планер")

route_choice = st.selectbox("Избери маршрут:", list(routes.keys()))
transport_choice = st.selectbox("Превозно средство:", ["Кола", "Влак", "Самолет"])
days = st.slider("Брой дни за пътуването:", 1, 10, 4)
budget = st.number_input("Твоят бюджет (лв):", 300, 5000, 1500)

if st.button("Планирай пътуването 🧭"):

    cities = routes[route_choice]

    # Избор на транспорт
    transport = {"Кола": Car(), "Влак": Train(), "Самолет": Plane()}[transport_choice]

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    total_food_cost = 0
    total_hotel_cost = 0
    total_entry_cost = 0

    st.subheader("🏙️ Спирки и предложения")
    for city in cities:
        info = city_info[city]
        st.markdown(f"### 📍 {city}")
        st.write(f"🏨 **Хотел:** {info['hotel'][0]} – {info['hotel'][1]} лв/нощ")
        st.write(f"🍽️ **Храна:** {info['food'][0]} – {info['food'][1]} лв/ден")
        st.write(f"🏛️ **Забележителност:** {info['sight']} – вход: {info['entry_fee']} лв")
        total_food_cost += info['food'][1] * days
        total_hotel_cost += info['hotel'][1] * days
        total_entry_cost += info['entry_fee'] * days

    # ================== COST CALCULATION ==================
    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)
    travel_time = transport.travel_time(total_distance)
    total_cost = transport_cost + total_food_cost + total_hotel_cost + total_entry_cost

    st.subheader("💰 Разходи")
    st.write(f"{transport.name()} – транспорт: {transport_cost:.2f} лв, време: {travel_time:.2f} ч")
    st.write(f"🍽️ Храна: {total_food_cost:.2f} лв")
    st.write(f"🏨 Хотели: {total_hotel_cost:.2f} лв")
    st.write(f"🏛️ Забележителности: {total_entry_cost:.2f} лв")

    st.markdown("---")
    st.write(f"## 💵 Общ бюджет: **{total_cost:.2f} лв**")
    st.success("✅ Бюджетът е достатъчен! Приятно пътуване ✨") if total_cost <= budget else st.error("❌ Бюджетът не достига.")

    # ================== BUDGET CHART ==================
    st.subheader("📊 Разпределение на разходите")
    costs = pd.DataFrame({
        "Категория": ["Транспорт", "Хотели", "Храна", "Забележителности"],
        "Цена": [transport_cost, total_hotel_cost, total_food_cost, total_entry_cost]
    })
    st.bar_chart(costs.set_index("Категория"))

    # ================== MAP ==================
    st.subheader("🗺️ Маршрут на картата")
    start_coords = city_info[cities[0]]["coords"]
    m = folium.Map(location=start_coords, zoom_start=5)

    # Добавяне на маркери и линии
    prev_coords = None
    for city in cities:
        coords = city_info[city]["coords"]
        folium.Marker(coords, popup=f"{city}: {city_info[city]['sight']}").add_to(m)
        if prev_coords:
            folium.PolyLine([prev_coords, coords], color="blue", weight=3, opacity=0.7).add_to(m)
        prev_coords = coords

    st_folium(m, width=700, height=500)
