import yfinance as yf
import pandas as pd
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# =====================
# KONFIGURATION
# =====================
EMAIL = "mgl@godtfredlarsen.com"
TO_EMAIL = "mgl@godtfredlarsen.com"

# ✅ samme som dit virkende program
PASSWORD = os.environ.get("EMAIL_PASSWORD")

tickers = [
    "NOVO-B.CO","DSV.CO","DANSKE.CO","MAERSK-B.CO","MAERSK-A.CO",
    "ORSTED.CO","VWS.CO","CARL-B.CO","GMAB.CO","TRYG.CO",
    "COLO-B.CO","DEMANT.CO","NKT.CO","PNDORA.CO",
    "ALSYDB.CO","ROCK-B.CO","ISS.CO","FLS.CO","ZEAL.CO",
    "RBREW.CO","AMBU-B.CO","BAVA.CO","GN.CO","NSIS-B.CO"
]

# =====================
# DATA
# =====================
end_date = datetime.today()
start_date = end_date - timedelta(weeks=12)

data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    threads=False
)

# Brug Close (stabil)
if isinstance(data.columns, pd.MultiIndex):
    data = data["Close"]
else:
    data = data["Close"]

start_prices = data.iloc[0]
end_prices = data.iloc[-1]

# =====================
# BEREGNING
# =====================
returns = ((end_prices / start_prices) - 1) * 100
returns = returns.dropna()

# =====================
# FORMAT (ALLE AKTIER + KOLONNER + LINJER)
# =====================
def format_table(returns, start_prices, end_prices):
    lines = []
    
    header = f"{'Nr':<4}{'Aktie':<15}{'Start':>10}{'Slut':>10}{'Afkast':>10}"
    lines.append(header)
    lines.append("-" * len(header))

    sorted_returns = returns.sort_values(ascending=False)

    for i, (ticker, value) in enumerate(sorted_returns.items(), start=1):
        start = start_prices[ticker]
        end = end_prices[ticker]

        lines.append(f"{i:<4}{ticker:<15}{start:>10.2f}{end:>10.2f}{value:>9.2f}%")

        # ✅ Linje efter nr. 5
        if i == 5:
            lines.append("-" * len(header))

        # ✅ Linje efter nr. 19
        if i == 19:
            lines.append("-" * len(header))

    return "\n".join(lines)

date_str = end_date.strftime("%d %B %Y")

# =====================
# EMAIL TEKST
# =====================
email_text = f"""Momentum C25 – uge ({date_str})

Hej Michael,

Her er ugens momentum-rangering (12 uger):

{format_table(returns, start_prices, end_prices)}

Mvh
"""

# =====================
# SEND EMAIL (samme som virker hos dig)
# =====================
msg = MIMEText(email_text)
msg['From'] = EMAIL
msg['To'] = TO_EMAIL
msg['Subject'] = "Momentum C25"

if PASSWORD and PASSWORD.strip():
    try:
        server = smtplib.SMTP("send.one.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        server.quit()

        print("MAIL SENDT ✅")
    except Exception as e:
        print("MAIL FEJL:", e)
else:
    print("PASSWORD PROBLEM")
