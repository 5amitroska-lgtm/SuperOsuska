import streamlit as st

st.set_page_config(page_title="Osušky s menom", page_icon="🧵", layout="wide")

st.markdown(
    """
    <style>
    .hero {
        padding: 2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #f8e9df, #f3d9d2);
        margin-bottom: 1.5rem;
    }
    .product {
        padding: 1.2rem;
        border: 1px solid #eee;
        border-radius: 14px;
        background: #fff;
        min-height: 180px;
    }
    .product-icon {
        font-size: 2.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Osušky s menom</h1>
        <p>Osobný darček s výšivkou podľa vášho výberu.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Vyberte si osušku, zadajte meno a zvoľte farbu výšivky. "
    "Detaily a cenu vám potvrdíme pred dokončením objednávky."
)

st.subheader("Vyberte si osušku")

products = [
    {
        "name": "Osuška s lemom",
        "description": "Klasická osuška s ozdobným lemom.",
        "icon": "🧺",
    },
    {
        "name": "Osuška bez lemu",
        "description": "Jednoduchý, čistý vzhľad.",
        "icon": "🧵",
    },
    {
        "name": "Darčeková osuška",
        "description": "Osuška vhodná na osobné darovanie.",
        "icon": "🎁",
    },
]

cols = st.columns(3)
for col, product in zip(cols, products):
    with col:
        st.markdown(
            f"""
            <div class="product">
                <div class="product-icon">{product["icon"]}</div>
                <h3>{product["name"]}</h3>
                <p>{product["description"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
st.subheader("Prispôsobte si výšivku")

with st.form("order_form"):
    product_name = st.selectbox(
        "Typ osušky",
        [product["name"] for product in products],
    )
    name_to_embroider = st.text_input(
        "Meno na výšivku",
        max_chars=20,
        placeholder="Napríklad: Sofia",
    )
    thread_color = st.selectbox(
        "Farba nite",
        ["Biela", "Čierna", "Zlatá", "Ružová", "Modrá", "Iná"],
    )
    extra_details = st.text_area(
        "Poznámka k objednávke (nepovinné)",
        placeholder="Napíšte napríklad požadovaný typ písma.",
    )
    submitted = st.form_submit_button("Odoslať nezáväzný dopyt")

if submitted:
    if not name_to_embroider.strip():
        st.error("Zadajte meno, ktoré chcete vyšiť.")
    else:
        st.success("Ďakujeme! Toto je ukážkový formulár — objednávka sa zatiaľ nikam neodosiela.")
        st.write(f"**Osuška:** {product_name}")
        st.write(f"**Meno:** {name_to_embroider.strip()}")
        st.write(f"**Farba nite:** {thread_color}")
        if extra_details.strip():
            st.write(f"**Poznámka:** {extra_details.strip()}")

st.divider()
st.caption(
    "Doplňte sem svoje fotografie produktov, skutočné ceny, dodacie podmienky "
    "a kontaktné údaje. Formulár zatiaľ objednávky neukladá ani neodosiela."
)

