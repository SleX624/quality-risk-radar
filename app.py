from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Quality Risk Radar",
    page_icon="💊",
    layout="wide",
)

st.title("Quality Risk Radar")
st.caption(
    "Мониторинг событий контроля качества лекарственных средств"
)

DATA_PATH = Path(
    "data/processed/mart_manufacturer_drug_month_monitoring.parquet"
)

if not DATA_PATH.exists():
    st.error(
        "Файл данных не найден. "
        "Сначала запустите ноутбук 06_simple_monitoring.ipynb "
        "и сохраните витрину."
    )
    st.stop()


@st.cache_data
def load_data():
    mart = pd.read_parquet(DATA_PATH)

    mart["event_month"] = pd.to_datetime(mart["event_month"])
    mart = mart.sort_values(
        ["manufacturer", "drug_name", "event_month"]
    )

    mart["events_prev_month"] = (
        mart.groupby(["manufacturer", "drug_name"])["events_count"]
        .shift(1)
    )

    mart["events_change"] = (
        mart["events_count"] - mart["events_prev_month"]
    )

    mart["is_spike"] = (
        (mart["events_count"] >= 3)
        & (mart["events_count"] >= 2 * mart["events_prev_month"])
    ).astype(int)

    return mart


mart = load_data()

month = st.selectbox(
    "Месяц",
    sorted(mart["event_month"].unique(), reverse=True),
    format_func=lambda value: value.strftime("%Y-%m"),
)

month_data = mart[mart["event_month"] == month]

col1, col2, col3 = st.columns(3)

col1.metric(
    "События",
    int(month_data["events_count"].sum()),
)

col2.metric(
    "Производители",
    int(month_data["manufacturer"].nunique()),
)

col3.metric(
    "Препараты",
    int(month_data["drug_name"].nunique()),
)

st.info(
    """
    **Как читать данные**

    - **События** — число событий контроля качества в выбранном месяце.
    - **Предыдущий месяц** — число событий у той же пары «производитель + препарат» месяцем ранее.
    - **Изменение** — разница между текущим и предыдущим месяцем.
    - **Всплеск** — минимум 3 события и рост минимум в 2 раза относительно предыдущего месяца.

    Проект не доказывает недоброкачественность препарата
    и не заменяет регуляторные решения.
    """
)

show_only_spikes = st.toggle(
    "Показывать только всплески",
    value=False,
)

if show_only_spikes:
    month_data = month_data[
        month_data["is_spike"] == 1
    ]

st.subheader("Топ-20 препаратов по числу событий")

top_drugs = (
    month_data
    .sort_values("events_count", ascending=False)
    .head(20)
)

st.dataframe(
    top_drugs[
        [
            "manufacturer",
            "drug_name",
            "events_count",
            "events_prev_month",
            "events_change",
            "is_spike",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "manufacturer": st.column_config.Column(
            "Производитель",
            width="large",
        ),
        "drug_name": st.column_config.Column(
            "Препарат",
            width="large",
        ),
        "events_count": st.column_config.NumberColumn(
            "События",
            help="Число событий в выбранном месяце",
        ),
        "events_prev_month": st.column_config.NumberColumn(
            "Предыдущий месяц",
            help="Число событий месяцем ранее",
        ),
        "events_change": st.column_config.NumberColumn(
            "Изменение",
            help="Разница с предыдущим месяцем",
        ),
        "is_spike": st.column_config.CheckboxColumn(
            "Всплеск",
            help="Минимум 3 события и рост минимум в 2 раза",
        ),
    },
)

st.subheader("Динамика событий по месяцам")

monthly = (
    mart.groupby("event_month", as_index=False)
    .agg(events_count=("events_count", "sum"))
    .sort_values("event_month")
)

st.line_chart(
    monthly,
    x="event_month",
    y="events_count",
    use_container_width=True,
)

st.subheader("Детали по производителю")

manufacturers = sorted(
    month_data["manufacturer"].unique()
)

selected_manufacturer = st.selectbox(
    "Производитель",
    manufacturers,
)

manufacturer_data = month_data[
    month_data["manufacturer"] == selected_manufacturer
]

st.dataframe(
    manufacturer_data[
        [
            "drug_name",
            "events_count",
            "events_prev_month",
            "events_change",
            "is_spike",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Динамика препарата")

drug_names = sorted(
    manufacturer_data["drug_name"].unique()
)

if drug_names:
    selected_drug = st.selectbox(
        "Препарат",
        drug_names,
    )

    drug_history = mart[
        (mart["manufacturer"] == selected_manufacturer)
        & (mart["drug_name"] == selected_drug)
    ].sort_values("event_month")

    st.line_chart(
        drug_history,
        x="event_month",
        y="events_count",
        use_container_width=True,
    )

st.divider()

st.caption(
    """
    **Ограничения:** проект использует открытые данные Росздравнадзора
    и предназначен для аналитической приоритизации.
    Он не является медицинским, юридическим или регуляторным заключением.
    """
)