import streamlit as st
import pandas as pd
from abc import ABC, abstractmethod

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"]
}

city_info = {
    "София": {
        "hotel": ("Hotel Sofia Center", 70),
        "food": ("Традиционна българска кухня", 20),
        "sight": "Катедралата Александър Невски",
        "coords": [42.6977, 23.3219]
    },
    "Белград": {
        "hotel": ("Belgrade Inn", 65),
        "food": ("Сръбска скара", 22),
        "sight": "Калемегдан",
        "coords": [44.7866, 20.4489]
    },
    "Виена": {
        "hotel": ("Vienna City Hotel", 90),
        "food": ("Виенски шницел", 30),
        "sight": "Дворецът Шьонбрун",
        "coords": [48.2082, 16.3738]
    },
    "Мюнхен": {
        "hotel": ("Munich Central Hotel", 95),
        "food": ("Немска кухня", 28),
        "sight": "Мариенплац",
        "coords": [48.1351, 11.5820]
    }
}

DISTANCE_BETWEEN_CITIES = 300  # км

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

st.title("🌍 Интерактивен туристически планер")

route_choice = st.selectbox("Избери маршрут:", list(routes.keys()))
transport_choice = st.selectbox("Превозно средство:", ["Кола", "Влак", "Самолет"])

days = st.slider("Общ брой дни:", 1, 14, 6)
budget = st.number_input("Бюджет (лв):", 300, 8000, 1500)

traveler_type = st.radio(
    "Тип турист:",
    ["🎒 Бюджетен", "👨‍👩‍👧 Семеен", "💼 Бизнес"]
)

# ================== PLAN ==================

if st.button("🧭 Планирай пътуването"):
    cities = routes[route_choice]

    transport = {
        "Кола": Car(),
        "Влак": Train(),
        "Самолет": Plane()
    }[transport_choice]

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    # ================== DAYS ==================

    st.subheader("📅 Дни по градове")
    days_per_city = {}
    remaining_days = days

    for city in cities:
        d = st.number_input(
            f"Дни в {city}",
            1,
            remaining_days,
            value=max(1, days // len(cities))
        )
        days_per_city[city] = d
        remaining_days -= d

    # ================== COSTS ==================

    total_food = 0
    total_hotel = 0

    st.subheader("🏙️ Градове и разходи")

    for city in cities:
        info = city_info[city]
        d = days_per_city[city]

        hotel_price = info["hotel"][1]
        food_price = info["food"][1]

        if traveler_type == "🎒 Бюджетен":
            hotel_price *= 0.8
        elif traveler_type == "👨‍👩‍👧 Семеен":
            food_price *= 1.3
        elif traveler_type == "💼 Бизнес":
            hotel_price *= 1.4

        st.markdown(f"### 📍 {city}")
        st.write(f"🏨 {info['hotel'][0]} – {hotel_price:.2f} лв/нощ")
        st.write(f"🍽️ {info['food'][0]} – {food_price:.2f} лв/ден")
        st.write(f"🏛️ {info['sight']}")

        total_food += food_price * d
        total_hotel += hotel_price * d

    # ================== TRANSPORT ==================

    total_distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(total_distance)

    total_cost = total_food + total_hotel + transport_cost

    # ================== RESULTS ==================

    st.subheader("💰 Разходи")
    st.write(f"{transport.name()} Транспорт: {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна: {total_food:.2f} лв")
    st.write(f"🏨 Хотели: {total_hotel:.2f} лв")

    st.markdown("---")
    st.write(f"## 💵 Общо: **{total_cost:.2f} лв**")

    if total_cost <= budget:
        st.success("✅ Бюджетът е достатъчен!")
    else:
        st.error("❌ Бюджетът не достига!")

    # ================== CHART ==================

    st.subheader("📊 Графика на разходите")
    df = pd.DataFrame({
        "Категория": ["Транспорт", "Храна", "Хотели"],
        "Цена": [transport_cost, total_food, total_hotel]
    })
    st.bar_chart(df.set_index("Категория"))

    # ================== MAP ==================

    st.subheader("🗺️ Карта на маршрута")
    st.map([
        {"lat": city_info[c]["coords"][0], "lon": city_info[c]["coords"][1]}
        for c in cities
    ])
