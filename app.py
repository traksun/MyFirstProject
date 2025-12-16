import streamlit as st
from abc import ABC, abstractmethod
import random

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"]
}

city_info = {
    "София": {
        "hotel": ("Hotel Sofia Center", 70),
        "food": ("Традиционна българска кухня", 20),
        "sight": "Катедралата Александър Невски"
    },
    "Белград": {
        "hotel": ("Belgrade Inn", 65),
        "food": ("Сръбска скара", 22),
        "sight": "Калемегдан"
    },
    "Виена": {
        "hotel": ("Vienna City Hotel", 90),
        "food": ("Виенски шницел", 30),
        "sight": "Дворецът Шьонбрун"
    },
    "Мюнхен": {
        "hotel": ("Munich Central Hotel", 95),
        "food": ("Немска кухня", 28),
        "sight": "Мариенплац"
    }
}

DISTANCE_BETWEEN_CITIES = 300  # км (опростено)

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price_per_km):
        self.price_per_km = price_per_km

    @abstractmethod
    def name(self):
        pass

    def travel_cost(self, distance):
        return distance * self.price_per_km

class Car(Transport):
    def __init__(self):
        super().__init__(0.25)

    def name(self):
        return "🚗 Кола"

class Train(Transport):
    def __init__(self):
        super().__init__(0.18)

    def name(self):
        return "🚆 Влак"

class Plane(Transport):
    def __init__(self):
        super().__init__(0.45)

    def name(self):
        return "✈️ Самолет"

# ================== UI ==================

st.title("🌍 Интерактивен туристически планер с иновации")

route_choice = st.selectbox(
    "Избери маршрут:",
    list(routes.keys())
)

transport_choice = st.selectbox(
    "Превозно средство:",
    ["Кола", "Влак", "Самолет"]
)

# Брой дни за всеки град
cities = routes[route_choice]
days_per_city = {}
st.subheader("📅 Задай брой дни за всеки град")
for city in cities:
    days_per_city[city] = st.slider(f"{city}:", 1, 5, 1)

budget = st.number_input("Твоят бюджет (лв):", 300, 5000, 1500)

if st.button("Планирай пътуването 🧭"):

    # Избор на транспорт
    if transport_choice == "Кола":
        transport = Car()
    elif transport_choice == "Влак":
        transport = Train()
    else:
        transport = Plane()

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    # ================== CITY DETAILS ==================
    st.subheader("🏙️ Спирки и предложения")

    total_food_cost = 0
    total_hotel_cost = 0

    # Списък за графика
    city_names = []
    city_costs = []

    for city in cities:
        info = city_info[city]
        city_days = days_per_city[city]

        st.markdown(f"### 📍 {city}")
        st.write(f"🏨 **Хотел:** {info['hotel'][0]} – {info['hotel'][1]} лв/нощ")
        st.write(f"🍽️ **Храна:** {info['food'][0]} – {info['food'][1]} лв/ден")
        st.write(f"🏛️ **Забележителност:** {info['sight']}")

        # Случайна допълнителна активност
        extras = ["Пешеходна обиколка", "Местен музикален концерт", "Кулинарен тур", "Музейна визита"]
        extra_activity = random.choice(extras)
        st.info(f"🎯 Препоръчана допълнителна активност: {extra_activity}")

        total_food_cost += info['food'][1] * city_days
        total_hotel_cost += info['hotel'][1] * city_days

        city_names.append(city)
        city_costs.append(info['food'][1] * city_days + info['hotel'][1] * city_days)

    # ================== COST CALCULATION ==================
    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)
    total_cost = transport_cost + total_food_cost + total_hotel_cost

    # ================== RESULTS ==================
    st.subheader("💰 Разходи")
    st.write(f"{transport.name()} – транспорт: {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {total_food_cost:.2f} лв")
    st.write(f"🏨 Хотели: {total_hotel_cost:.2f} лв")
    st.markdown("---")
    st.write(f"## 💵 Общ бюджет: **{total_cost:.2f} лв**")

    if total_cost <= budget:
        st.success("✅ Бюджетът е достатъчен! Приятно пътуване ✨")
    else:
        st.error("❌ Бюджетът не достига. Помисли за по-евтин транспорт или по-малко дни.")

    # ================== BAR CHART ==================
    st.subheader("📊 Разходи по градове")
    st.bar_chart(data=dict(zip(city_names, city_costs)))

    # ================== ASCII/Emoji карта ==================
    st.subheader("🗺️ Маршрут (символична карта)")
    map_line = " ➡️ ".join([f"🏙️ {city}" for city in cities])
    st.text(map_line)
