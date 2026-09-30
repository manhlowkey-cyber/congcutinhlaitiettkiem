import pandas as pd
import streamlit as st
st.image("logo.jpg")

st.set_page_config(page_title="Tính lãi gửi tiết kiệm", page_icon="💰", layout="centered")


def vnd(x: float) -> str:
    """Định dạng tiền VND: 1.234.567 ₫"""
    return f"{x:,.0f}".replace(",", ".") + " ₫"


def build_schedule(principal, rate, term, interest_type, payout):
    """
    Trả về danh sách các kỳ tính lãi.
    - Lãi đơn: lãi mỗi kỳ = gốc × lãi suất × số tháng của kỳ / 12 (gốc không đổi).
    - Lãi kép: lãi mỗi kỳ được nhập vào gốc để tính lãi kỳ sau.
      Với hình thức 'cuối kỳ', lãi được nhập gốc theo từng năm (12 tháng).
    """
    if payout == "Lãnh lãi hằng tháng":
        step = 1
    elif payout == "Lãnh lãi hằng quý":
        step = 3
    else:  # cuối kỳ
        step = term if interest_type == "Lãi đơn" else 12

    rows = []
    balance = principal
    cum_interest = 0.0
    remaining = term
    k = 1
    while remaining > 0:
        months = min(step, remaining)
        base = principal if interest_type == "Lãi đơn" else balance
        interest = base * rate * months / 12
        cum_interest += interest
        if interest_type == "Lãi kép":
            balance += interest
        rows.append(
            {
                "Kỳ": k,
                "Số tháng": months,
                "Tiền gốc tính lãi": base,
                "Tiền lãi kỳ này": interest,
                "Lãi cộng dồn": cum_interest,
                "Gốc + lãi cộng dồn": principal + cum_interest,
            }
        )
        remaining -= months
        k += 1
    return rows


st.title("💰 Tính lãi gửi tiết kiệm")
st.caption("Tính theo lãi đơn hoặc lãi kép, lãnh lãi theo tháng, quý hoặc cuối kỳ.")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        principal = st.number_input(
            "Số tiền gửi (VND)", min_value=0.0, value=100_000_000.0, step=1_000_000.0, format="%.0f"
        )
        term = st.number_input("Kỳ hạn (tháng)", min_value=1, max_value=600, value=12, step=1)
    with col2:
        rate_pct = st.number_input(
            "Lãi suất (%/năm)", min_value=0.0, max_value=100.0, value=6.0, step=0.05, format="%.2f"
        )
        interest_type = st.radio("Cách tính lãi", ["Lãi đơn", "Lãi kép"], horizontal=True)

    payout = st.selectbox(
        "Hình thức lãnh lãi",
        ["Lãnh lãi hằng tháng", "Lãnh lãi hằng quý", "Lãnh lãi cuối kỳ"],
        index=2,
    )
    submitted = st.form_submit_button("Tính lãi", type="primary", use_container_width=True)

if principal <= 0:
    st.error("Số tiền gửi phải lớn hơn 0.")
    st.stop()

rate = rate_pct / 100
rows = build_schedule(principal, rate, int(term), interest_type, payout)
df = pd.DataFrame(rows)

total_interest = df["Tiền lãi kỳ này"].sum()
total_amount = principal + total_interest
first_interest = df["Tiền lãi kỳ này"].iloc[0]

st.subheader("Kết quả")
label_periodic = {
    "Lãnh lãi hằng tháng": "Tiền lãi mỗi tháng",
    "Lãnh lãi hằng quý": "Tiền lãi mỗi quý",
    "Lãnh lãi cuối kỳ": "Tiền lãi cuối kỳ" if interest_type == "Lãi đơn" else "Tiền lãi năm đầu",
}[payout]
if interest_type == "Lãi kép" and payout != "Lãnh lãi cuối kỳ":
    label_periodic += " (kỳ đầu)"

c1, c2 = st.columns(2)
c1.metric(label_periodic, vnd(first_interest))
c2.metric("Tổng tiền lãi", vnd(total_interest))
c3, c4 = st.columns(2)
c3.metric("Tiền gốc", vnd(principal))
c4.metric("Tổng gốc và lãi", vnd(total_amount))

if interest_type == "Lãi kép":
    st.info(
        "Lãi kép: lãi mỗi kỳ được cộng vào gốc để tính lãi cho kỳ sau, nên tiền lãi tăng dần. "
        "Với hình thức lãnh lãi cuối kỳ, lãi được nhập gốc theo từng năm."
    )
else:
    st.info("Lãi đơn: lãi mỗi kỳ luôn tính trên số tiền gốc ban đầu.")

if len(df) > 1:
    st.subheader("Lãi từng kỳ")
    st.bar_chart(df.set_index("Kỳ")["Tiền lãi kỳ này"])

st.subheader("Bảng chi tiết")
show = df.copy()
for col in ["Tiền gốc tính lãi", "Tiền lãi kỳ này", "Lãi cộng dồn", "Gốc + lãi cộng dồn"]:
    show[col] = show[col].map(vnd)
st.dataframe(show, hide_index=True, use_container_width=True)

st.caption("Kết quả mang tính tham khảo. Lãi thực tế phụ thuộc quy định của từng ngân hàng.")
