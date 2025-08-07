import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# Inicializácia dát
if "work_log" not in st.session_state:
    st.session_state.work_log = []

# Základné vstupy
st.title("Evidencia Práce a Fakturácia")
st.markdown("---")

hourly_rate = st.number_input("Tvoja hodinová mzda (€):", min_value=1.0, value=5.0, step=0.5)
relationship_mode = st.checkbox("Mám holku")

st.markdown("---")

# Pridanie záznamu
st.header("Pridať nový záznam")
date_input = st.date_input("Dátum práce:", value=date.today())
day_of_week = calendar.day_name[date_input.weekday()]
is_today = date_input == date.today()

if is_today:
    worked_today = st.checkbox("Pracoval som dnes", value=True)
else:
    worked_today = st.checkbox(f"Pracoval som v tento deň ({day_of_week})?", value=False)

if worked_today:
    custom_hours = st.slider("Zaplatené hodiny (obvykle 11):", 0, 16, 11)
    break_minutes = st.slider("Prestávka (minúty):", 0, 60, 60, step=15)
    total_minutes = custom_hours * 60
    total_earnings = round((total_minutes / 60) * hourly_rate, 2)

    if st.button("Pridať záznam"):
        st.session_state.work_log.append({
            "date": date_input,
            "hours": custom_hours,
            "break_min": break_minutes,
            "earnings": total_earnings
        })
        st.success(f"Záznam pridaný: {date_input}, zárobok: {total_earnings} €")

# Extra vstup – budem pracovať v sobotu?
st.markdown("---")
st.header("Plán na sobotu")
plan_saturday = st.checkbox("Budem pracovať túto sobotu?")

if plan_saturday:
    upcoming_saturday = date.today() + timedelta((5 - date.today().weekday()) % 7)  # 5 = Saturday
    saturday_hours = st.slider("Koľko hodín budem robiť v sobotu?", 0, 16, 11)
    saturday_break = st.slider("Prestávka v sobotu (minúty):", 0, 60, 60, step=15)
    saturday_total = round(((saturday_hours * 60 - saturday_break) / 60) * hourly_rate, 2)
    
    if st.button("Pridať plánovanú sobotu"):
        st.session_state.work_log.append({
            "date": upcoming_saturday,
            "hours": saturday_hours,
            "break_min": saturday_break,
            "earnings": saturday_total
        })
        st.success(f"Sobota pridaná: {upcoming_saturday}, zárobok: {saturday_total} €")

# Zobrazenie a mazanie záznamov
st.markdown("---")
st.header("História práce")
df = pd.DataFrame(st.session_state.work_log)

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["day"] = df["date"].dt.day_name()
    st.dataframe(df)

    delete_idx = st.number_input("Zmazať záznam # (index)", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Zmazať záznam"):
        st.session_state.work_log.pop(delete_idx)
        st.success("Záznam zmazaný.")

# Výpočet fakturácie
st.markdown("---")
st.header("Týždenná Fakturácia")

if not df.empty:
    today = date.today()
    df_week = df[df["date"].dt.isocalendar().week == today.isocalendar().week]
    earnings_to_date = df_week[df_week["date"] <= pd.to_datetime(today)]["earnings"].sum()
    potential_weekly = df_week["earnings"].sum()

    st.write(f"Zárobok do dnešného dňa: **{earnings_to_date:.2f} €**")
    st.write(f"Potenciálny zárobok do konca týždňa: **{potential_weekly:.2f} €**")

    if relationship_mode:
        st.warning(f"O toľko prídeš (holka ti to zoberie): **{potential_weekly:.2f} €**")

# Turnus
st.markdown("---")
st.header("Turnusový režim")

with st.expander("Nastaviť turnus"):
    use_turnus = st.checkbox("Zapnúť turnusový režim")
    if use_turnus:
        turnus_name = st.text_input("Názov turnusu", value="August")
        turnus_start = st.date_input("Začiatok turnusu", value=date.today())
        turnus_end = st.date_input("Koniec turnusu", value=date.today() + timedelta(weeks=4))

        if turnus_start < turnus_end and not df.empty:
            df_turnus = df[(df["date"] >= pd.to_datetime(turnus_start)) & (df["date"] <= pd.to_datetime(turnus_end))]
            earnings_turnus = df_turnus["earnings"].sum()
            delta_days = (turnus_end - turnus_start).days + 1
            delta_weeks = delta_days // 7

            breakup_date = turnus_end + timedelta(days=7)

            st.success(f"Turnus **{turnus_name}** má {delta_days} dní, čo je približne {delta_weeks} týždňov.")
            st.info(f"Fakturovaná suma za turnus: **{earnings_turnus:.2f} €**")

            if relationship_mode:
                st.warning(f"Holka? prideš o: **{earnings_turnus:.2f} €**, nechá ťa cez mobil  **{breakup_date.strftime('%d.%m.%Y')}**")
    else:
        st.info("Zapni turnusový režim, ak chceš sledovať fakturáciu za konkrétne obdobie.")
