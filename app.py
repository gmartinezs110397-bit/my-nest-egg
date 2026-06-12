from __future__ import annotations

import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "data" / "payment_data.json"


DEFAULT_DATA = {
    "settings": {
        "pay_date": date.today().isoformat(),
        "cash_now": 0.0,
        "reserve": 0.0,
        "groceries": 0.0,
        "sofi": 0.0,
        "mom_debt": 2444342.74,
        "mom_first": True,
        "strategy": "APR mas alto",
    },
    "cards": [
        {"Tarjeta": "Victoria Secret", "APR %": 31.24, "Cupo": 1000.0, "Saldo": 0.0, "Dia pago": 20, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Amex Blue", "APR %": 29.24, "Cupo": 1000.0, "Saldo": 893.0, "Dia pago": 9, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "TD", "APR %": 27.24, "Cupo": 1200.0, "Saldo": 1213.0, "Dia pago": 22, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Amex Amazon", "APR %": 26.49, "Cupo": 2100.0, "Saldo": 2819.0, "Dia pago": 20, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Discover", "APR %": 26.49, "Cupo": 3000.0, "Saldo": 2851.0, "Dia pago": 15, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Apple", "APR %": 26.24, "Cupo": 2000.0, "Saldo": 739.0, "Dia pago": 30, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": ""},
        {"Tarjeta": "Chase", "APR %": 0.0, "Cupo": 2500.0, "Saldo": 2052.0, "Dia pago": 8, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": "0% APR promo"},
        {"Tarjeta": "Bancolombia", "APR %": 0.0, "Cupo": 0.0, "Saldo": 1700000.0, "Dia pago": 3, "Minimo toca": False, "Minimo": 0.0, "Gasto extra": 0.0, "Notas": "COP"},
    ],
    "expenses": [
        {"Categoria": "Colombia", "Nombre": "Mom allowance", "Cuenta/Tarjeta": "Checking", "Monto quincena": 85.0, "Tipo": "Fijo", "Incluir": False, "Notas": ""},
        {"Categoria": "Colombia", "Nombre": "New apartment", "Cuenta/Tarjeta": "Bancolombia", "Monto quincena": 420.0, "Tipo": "Fijo", "Incluir": False, "Notas": "Apartar cada quincena"},
        {"Categoria": "Colombia", "Nombre": "Don Guillermo rent", "Cuenta/Tarjeta": "Checking", "Monto quincena": 440.0, "Tipo": "Fijo", "Incluir": False, "Notas": "Enviar completo a final de mes"},
        {"Categoria": "Zelle", "Nombre": "Innago / rent", "Cuenta/Tarjeta": "Checking", "Monto quincena": 1051.0, "Tipo": "Fijo", "Incluir": False, "Notas": "Apartar cada quincena"},
        {"Categoria": "Zelle", "Nombre": "Gym", "Cuenta/Tarjeta": "Checking", "Monto quincena": 80.0, "Tipo": "Fijo", "Incluir": False, "Notas": ""},
        {"Categoria": "TD", "Nombre": "Apple Bill / Cloud", "Cuenta/Tarjeta": "TD", "Monto quincena": 10.0, "Tipo": "Auto debit", "Incluir": False, "Notas": ""},
        {"Categoria": "TD", "Nombre": "Google Play / Gmail", "Cuenta/Tarjeta": "TD", "Monto quincena": 4.0, "Tipo": "Auto debit", "Incluir": False, "Notas": ""},
        {"Categoria": "Amex Amazon", "Nombre": "Amazon Prime", "Cuenta/Tarjeta": "Amex Amazon", "Monto quincena": 15.0, "Tipo": "Auto debit", "Incluir": False, "Notas": ""},
    ],
    "history": [],
}


st.set_page_config(page_title="My Nest Egg", page_icon="💳", layout="wide")


def money(value: float) -> str:
    return f"${float(value or 0):,.2f}"


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            data = deepcopy(DEFAULT_DATA)
            data.update(saved)
            data["settings"] = {**DEFAULT_DATA["settings"], **saved.get("settings", {})}
            return data
        except Exception:
            return deepcopy(DEFAULT_DATA)
    return deepcopy(DEFAULT_DATA)


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def require_password() -> None:
    password = st.secrets.get("APP_PASSWORD", "")
    if not password:
        return
    if st.session_state.get("authenticated"):
        return
    st.title("My Nest Egg")
    entered = st.text_input("Contraseña", type="password")
    if entered == password:
        st.session_state.authenticated = True
        st.rerun()
    if entered:
        st.error("Contraseña incorrecta.")
    st.stop()


def init_state() -> None:
    if "data" not in st.session_state:
        st.session_state.data = load_data()


def cards_df() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.data["cards"], columns=list(DEFAULT_DATA["cards"][0].keys()))


def expenses_df() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.data["expenses"], columns=list(DEFAULT_DATA["expenses"][0].keys()))


def included_expenses(expenses: pd.DataFrame) -> pd.DataFrame:
    if expenses.empty:
        return expenses
    return expenses[expenses["Incluir"].fillna(False)]


def card_auto_debit(card_name: str, expenses: pd.DataFrame) -> float:
    inc = included_expenses(expenses)
    if inc.empty:
        return 0.0
    return float(inc.loc[inc["Cuenta/Tarjeta"].str.lower() == card_name.lower(), "Monto quincena"].sum())


def is_card_account(account: str, cards: pd.DataFrame) -> bool:
    names = set(cards["Tarjeta"].astype(str).str.lower())
    return str(account).lower() in names


def calculate_plan(settings: dict, cards: pd.DataFrame, expenses: pd.DataFrame) -> dict:
    cards = cards.copy()
    expenses = expenses.copy()
    if cards.empty:
        cards = pd.DataFrame(columns=DEFAULT_DATA["cards"][0].keys())
    if expenses.empty:
        expenses = pd.DataFrame(columns=DEFAULT_DATA["expenses"][0].keys())

    for col in ["APR %", "Cupo", "Saldo", "Minimo", "Gasto extra"]:
        cards[col] = pd.to_numeric(cards[col], errors="coerce").fillna(0.0)
    for col in ["Monto quincena"]:
        expenses[col] = pd.to_numeric(expenses[col], errors="coerce").fillna(0.0)

    included = included_expenses(expenses)
    checking_total = 0.0
    if not included.empty:
        checking_total = float(
            included.loc[~included["Cuenta/Tarjeta"].apply(lambda account: is_card_account(account, cards)), "Monto quincena"].sum()
        )

    rows = []
    for _, card in cards.iterrows():
        auto_debit = card_auto_debit(str(card["Tarjeta"]), expenses)
        minimum = float(card["Minimo"]) if bool(card["Minimo toca"]) else 0.0
        extra = float(card["Gasto extra"])
        required = minimum + auto_debit + extra
        rows.append(
            {
                "Tarjeta": card["Tarjeta"],
                "Minimo si toca": minimum,
                "Debitos auto": auto_debit,
                "Gastos extra": extra,
                "Pago exacto ahora": required,
                "APR %": float(card["APR %"]),
                "Saldo": float(card["Saldo"]),
                "Payoff con SoFi": bool(float(settings["sofi"]) >= float(card["Saldo"]) > 0),
                "Notas": card.get("Notas", ""),
            }
        )
    card_plan = pd.DataFrame(rows)

    available = max(0.0, float(settings["cash_now"]) - float(settings["reserve"]) - float(settings["groceries"]))
    card_required = float(card_plan["Pago exacto ahora"].sum()) if not card_plan.empty else 0.0
    after_required = available - checking_total - card_required
    mom_payment = min(max(0.0, after_required), float(settings["mom_debt"])) if settings.get("mom_first") else 0.0
    card_extra = max(0.0, after_required - mom_payment)

    active_cards = card_plan[card_plan["Saldo"] > 0].copy()
    target = None
    if not active_cards.empty:
        if settings.get("strategy") == "Saldo mas bajo":
            target = active_cards.sort_values("Saldo", ascending=True).iloc[0]
        else:
            target = active_cards.sort_values("APR %", ascending=False).iloc[0]

    account_rows = []
    if not included.empty:
        account_rows.extend(
            included.groupby("Cuenta/Tarjeta", dropna=False)["Monto quincena"]
            .sum()
            .reset_index()
            .rename(columns={"Cuenta/Tarjeta": "Cuenta / tarjeta", "Monto quincena": "Monto"})
            .to_dict("records")
        )
    account_rows.extend(
        card_plan.loc[card_plan["Pago exacto ahora"] > 0, ["Tarjeta", "Pago exacto ahora"]]
        .rename(columns={"Tarjeta": "Cuenta / tarjeta", "Pago exacto ahora": "Monto"})
        .to_dict("records")
    )
    account_plan = pd.DataFrame(account_rows)
    if not account_plan.empty:
        account_plan = account_plan.groupby("Cuenta / tarjeta", dropna=False)["Monto"].sum().reset_index()
        account_plan = account_plan.sort_values("Monto", ascending=False)

    return {
        "available": available,
        "checking_total": checking_total,
        "card_required": card_required,
        "after_required": after_required,
        "mom_payment": mom_payment,
        "card_extra": card_extra,
        "target": target,
        "card_plan": card_plan,
        "account_plan": account_plan,
    }


def save_tables(cards: pd.DataFrame, expenses: pd.DataFrame) -> None:
    st.session_state.data["cards"] = cards.fillna("").to_dict("records")
    st.session_state.data["expenses"] = expenses.fillna("").to_dict("records")
    save_data(st.session_state.data)


def settings_panel() -> dict:
    settings = st.session_state.data["settings"]
    st.subheader("Pago de hoy")
    col1, col2, col3 = st.columns(3)
    with col1:
        settings["pay_date"] = st.date_input("Fecha de pago", value=date.fromisoformat(settings["pay_date"])).isoformat()
        settings["cash_now"] = st.number_input("Dinero en cuenta hoy", value=float(settings["cash_now"]), min_value=0.0, step=50.0)
        settings["reserve"] = st.number_input("Colchón que no toco", value=float(settings["reserve"]), min_value=0.0, step=25.0)
    with col2:
        settings["groceries"] = st.number_input("Mercado planeado", value=float(settings["groceries"]), min_value=0.0, step=25.0)
        settings["sofi"] = st.number_input("Disponible en SoFi", value=float(settings["sofi"]), min_value=0.0, step=50.0)
        settings["mom_debt"] = st.number_input("Deuda mamá pendiente", value=float(settings["mom_debt"]), min_value=0.0, step=100.0)
    with col3:
        settings["mom_first"] = st.toggle("Si sobra, mamá primero", value=bool(settings["mom_first"]))
        settings["strategy"] = st.selectbox("Estrategia para extra a tarjetas", ["APR mas alto", "Saldo mas bajo"], index=0 if settings["strategy"] == "APR mas alto" else 1)
        if st.button("Guardar cambios", type="primary", use_container_width=True):
            save_data(st.session_state.data)
            st.success("Guardado.")
    return settings


def render_plan(plan: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Disponible real", money(plan["available"]))
    c2.metric("Checking / efectivo", money(plan["checking_total"]))
    c3.metric("Tarjetas obligatorio", money(plan["card_required"]))
    c4.metric("Sobra después", money(plan["after_required"]))

    if plan["after_required"] < 0:
        st.error(f"Falta {money(abs(plan['after_required']))} para cubrir lo obligatorio sin tocar el colchón.")
    elif plan["card_extra"] > 0:
        st.success("Hay dinero extra después de cubrir lo obligatorio.")
    else:
        st.info("Lo obligatorio queda cubierto, sin extra adicional.")

    left, right = st.columns([1, 1.25])
    with left:
        st.markdown("#### Apartar / pagar por cuenta")
        if plan["account_plan"].empty:
            st.caption("Marca gastos o mínimos para ver pagos.")
        else:
            st.dataframe(plan["account_plan"], use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Qué pagar en cada tarjeta")
        shown = plan["card_plan"][["Tarjeta", "Minimo si toca", "Debitos auto", "Gastos extra", "Pago exacto ahora", "Payoff con SoFi", "Notas"]]
        st.dataframe(shown, use_container_width=True, hide_index=True)

    st.markdown("#### Recomendación de extra")
    target = plan["target"]
    if plan["mom_payment"] > 0:
        st.write(f"Primero mamá: **{money(plan['mom_payment'])}**.")
    if target is not None and plan["card_extra"] > 0:
        extra = min(float(plan["card_extra"]), float(target["Saldo"]))
        st.write(f"Después, extra sugerido a **{target['Tarjeta']}**: **{money(extra)}**.")
    payoff = plan["card_plan"].loc[plan["card_plan"]["Payoff con SoFi"], "Tarjeta"].tolist()
    if payoff:
        st.write("Con SoFi podrías pagar completa: **" + ", ".join(payoff) + "**.")


def main() -> None:
    require_password()
    init_state()

    st.title("My Nest Egg")
    st.caption("Herramienta personal para decidir qué pagar en cada quincena.")

    settings = settings_panel()

    tab_plan, tab_cards, tab_expenses, tab_history, tab_data = st.tabs(["Plan", "Tarjetas", "Gastos", "Historial", "Datos"])

    with tab_cards:
        st.subheader("Tarjetas")
        cards = st.data_editor(
            cards_df(),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Minimo toca": st.column_config.CheckboxColumn(),
                "APR %": st.column_config.NumberColumn(format="%.2f"),
                "Cupo": st.column_config.NumberColumn(format="$%.2f"),
                "Saldo": st.column_config.NumberColumn(format="$%.2f"),
                "Minimo": st.column_config.NumberColumn(format="$%.2f"),
                "Gasto extra": st.column_config.NumberColumn(format="$%.2f"),
            },
            key="cards_editor",
        )
        if st.button("Guardar tarjetas", type="primary"):
            save_tables(cards, expenses_df())
            st.success("Tarjetas guardadas.")

    with tab_expenses:
        st.subheader("Gastos y débitos")
        expenses = st.data_editor(
            expenses_df(),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Incluir": st.column_config.CheckboxColumn(),
                "Monto quincena": st.column_config.NumberColumn(format="$%.2f"),
                "Tipo": st.column_config.SelectboxColumn(options=["Fijo", "Variable", "Auto debit"]),
            },
            key="expenses_editor",
        )
        if st.button("Guardar gastos", type="primary"):
            save_tables(cards_df(), expenses)
            st.success("Gastos guardados.")

    current_cards = cards_df()
    current_expenses = expenses_df()
    plan = calculate_plan(settings, current_cards, current_expenses)

    with tab_plan:
        render_plan(plan)
        if st.button("Guardar cierre de esta quincena", type="primary"):
            target_name = plan["target"]["Tarjeta"] if plan["target"] is not None else ""
            st.session_state.data["history"].append(
                {
                    "Fecha": settings["pay_date"],
                    "Cuenta inicial": settings["cash_now"],
                    "Obligatorio": plan["checking_total"] + plan["card_required"],
                    "Mama": plan["mom_payment"],
                    "Extra tarjetas": plan["card_extra"],
                    "Tarjeta extra": target_name,
                }
            )
            save_data(st.session_state.data)
            st.success("Cierre guardado.")

    with tab_history:
        st.subheader("Historial")
        history = pd.DataFrame(st.session_state.data["history"])
        if history.empty:
            st.info("Todavía no hay cierres guardados.")
        else:
            st.dataframe(history, use_container_width=True, hide_index=True)
        if st.button("Limpiar historial"):
            st.session_state.data["history"] = []
            save_data(st.session_state.data)
            st.rerun()

    with tab_data:
        st.subheader("Respaldo")
        payload = json.dumps(st.session_state.data, indent=2, ensure_ascii=False)
        st.download_button("Descargar respaldo JSON", payload, file_name="my_nest_egg_respaldo.json", mime="application/json")
        uploaded = st.file_uploader("Importar respaldo JSON", type=["json"])
        if uploaded and st.button("Importar respaldo"):
            st.session_state.data = json.loads(uploaded.read().decode("utf-8"))
            save_data(st.session_state.data)
            st.success("Respaldo importado.")
            st.rerun()
        st.warning("Si publicas esta app, protege el acceso con APP_PASSWORD en Streamlit secrets.")

    save_data(st.session_state.data)


if __name__ == "__main__":
    main()
