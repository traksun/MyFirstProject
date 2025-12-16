import streamlit as st
from abc import ABC, abstractmethod
import pandas as pd

# ================== DATA ==================

routes = {
    "България → Германия": ["София", "Белград", "Виена", "Мюнхен"]
}

city_info = {
    "София": {
        "hotel": ("Hotel Sofia Center", 70),
        "food": ("Традиционна българска кухня", 20),
        "sight": "Катедралата Александър Невски",
        "ticket": 10,
        "lat": 42.6977,
        "lon": 23.3219
    },
    "Белград": {
        "hotel": ("Belgrade Inn", 65),
        "food": ("Сръбска скара", 22),
        "sight": "Калемегдан",
        "ticket": 8,
        "lat": 44.7866,
        "lon": 20.4489
    },
    "Виена": {
        "hotel": ("Vienna City Hotel", 90),
        "food": ("Виенски шницел", 30),
        "sight": "Дворецът Шьонбрун",
        "ticket": 18,
        "lat": 48.2082,
        "lon": 16.3738
    },
    "Мюнхен": {
        "hotel": ("Munich Central Hotel", 95),
        "food": ("Немска кухня", 28),
        "sight": "Мариенплац",
        "ticket": 15,
        "lat": 48.1351,
        "lon": 11.5820
    }
}

DISTANCE_BETWEEN_CITIES = 300
EXTRA_COSTS = 50

# ================== OOP ==================

class Transport(ABC):
    def __init__(self, price_per_km, co2_per_km):
        self.price_per_km = price_per_km
        self.co2_per_km = co2_per_km

    @abstractmethod
    def name(self):
        pass

    def travel_cost(self, distance):
        return distance * self.price_per_km

    def co2_emissions(self, distance):
        return distance * self.co2_per_km


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


# ================== SMART LOGIC ==================

def recommend_transport(budget, days):
    if budget < 800:
        return Train()
    elif days <= 3:
        return Plane()
    return Car()


def profile_multiplier(profile):
    return {"🎒 Бекпекър": 0.85, "💼 Бизнес": 1.25}.get(profile, 1.0)


# ================== UI ==================

st.set_page_config(page_title="Туристически планер", layout="wide")
st.title("🌍 Интерактивен туристически планер")

route_choice = st.selectbox("🗺️ Избери маршрут:", list(routes.keys()))
profile = st.selectbox("👤 Тип пътуване:", ["🎒 Бекпекър", "👨‍👩‍👧 Семейство", "💼 Бизнес"])
days = st.slider("📅 Брой дни:", 1, 14, 4)
budget = st.number_input("💰 Бюджет (лв):", 300, 6000, 1500)

smart_mode = st.checkbox("🤖 Автоматична препоръка за транспорт")

transport_choice = st.selectbox(
    "🚍 Превозно средство:",
    ["Кола", "Влак", "Самолет"],
    disabled=smart_mode
)

if st.button("🧭 Планирай пътуването"):

    cities = routes[route_choice]
    days_per_city = max(1, days // len(cities))
    multiplier = profile_multiplier(profile)

    transport = recommend_transport(budget, days) if smart_mode else {
        "Кола": Car(),
        "Влак": Train(),
        "Самолет": Plane()
    }[transport_choice]

    st.subheader("🗺️ Маршрут")
    st.write(" ➡️ ".join(cities))

    # ================== MAP ==================
    st.subheader("🗺️ Интерактивна карта на маршрута")

    map_data = pd.DataFrame([
        {"lat": city_info[city]["lat"], "lon": city_info[city]["lon"]}
        for city in cities
    ])

    st.map(map_data)

    # ================== CITY DETAILS ==================
    total_food = total_hotel = total_tickets = 0

    st.subheader("🏙️ Спирки")

    for city in cities:
        info = city_info[city]

        with st.expander(f"📍 {city}"):
            st.write(f"🏨 {info['hotel'][0]} – {info['hotel'][1]} лв/нощ")
            st.write(f"🍽️ {info['food'][0]} – {info['food'][1]} лв/ден")
            st.write(f"🏛️ {info['sight']} – {info['ticket']} лв")
            st.write(f"⏱️ Дни: {days_per_city}")

        total_food += info['food'][1] * days_per_city
        total_hotel += info['hotel'][1] * days_per_city
        total_tickets += info['ticket']

    # ================== COSTS ==================
    distance = DISTANCE_BETWEEN_CITIES * (len(cities) - 1)
    transport_cost = transport.travel_cost(distance)
    co2 = transport.co2_emissions(distance)

    total_cost = (transport_cost + total_food + total_hotel + total_tickets + EXTRA_COSTS) * multiplier

    st.subheader("💰 Разходи")
    st.write(f"{transport.name()} – {transport_cost:.2f} лв")
    st.write(f"🍽️ Храна – {total_food:.2f} лв")
    st.write(f"🏨 Хотели – {total_hotel:.2f} лв")
    st.write(f"🎟️ Входове – {total_tickets:.2f} лв")
    st.write(f"🛍️ Допълнителни – {EXTRA_COSTS:.2f} лв")
    st.write(f"🌱 CO₂ отпечатък – {co2:.1f} kg")

    st.markdown("---")
    st.write(f"## 💵 Общо: **{total_cost:.2f} лв**")

    if total_cost <= budget:
        st.success("✅ Бюджетът е достатъчен!")
    else:
        st.error("❌ Бюджетът не достига.")

    rating = st.slider("⭐ Оцени плана:", 1, 5)
    st.write("⭐" * rating)
