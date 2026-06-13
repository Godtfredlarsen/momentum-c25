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
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = "mgl@godtfredlarsen.com"

tickers = [
    "NOVO-B.CO","DSV.CO","DANSKE.CO","MAERSK-B.CO","MAERSK-A.CO",
    "ORSTED.CO","VWS.CO","CARL-B.CO","GMAB.CO","TRYG.CO",
    "COLO-B.CO","DEMANT.CO","NKT.CO","JYSK.CO","PNDORA.CO",
    "ALSYDB.CO","ROCK-B.CO","ISS.CO","FLS.CO","ZEAL.CO",
    "RBREW.CO","AMBU-B.CO","BAVA.CO","GN.CO","NSIS-B.CO"
]

# =====================
# DATA
# =====================
end_date = datetime.today()
start_date = end_date - timedelta(weeks=12)

data = yf.download(tickers, start=start_date, end=end_date)

# ✅ ROBUST DATA HANDLING (Close virker altid)
if isinstance(data.columns, pd.MultiIndex):
    data = data["Close"]
elif "Close" in data.columns:
    data = data["Close"]
else:
    raise Exception("Close data ikke fundet")

# =====================
# PRISER
# =====================
start_prices = data.iloc[0]
end_prices = data.iloc[-1]

# =====================
# BEREGNING
# =====================
returns = ((end_prices / start_prices) - 1) * 100
returns = returns.dropna()

top5 = returns.sort_values(ascending=False).head(5)
bottom5 = returns.sort_values(ascending=True).head(5)

# =====================
# FORMAT (KOLONNER)
# =====================
def format_table(series):
    lines = []
    header = f"{'Aktie':<15}{'Start':>10}{'Slut':>10}{'Afkast':>10}"
    lines.append(header)
    lines.append("-" * len(header))
    
    for ticker, value in series.items():
        start = start_prices[ticker]
        end = end_prices[ticker]
        lines.append(f"{ticker:<15}{start:>10.2f}{end:>10.2f}{value:>9.2f}%")
    
    return "\n".join(lines)

date_str = end_date.strftime("%d %B %Y")

email_text = f"""Momentum C25 – uge ({date_str})

Hej Michael,

Her er ugens momentum-beregning (12 uger bagud fra fredag):

📈 LONG (5 stærkeste aktier):
{format_table(top5)}

📉 SHORT (5 svageste aktier):
{format_table(bottom5)}

Mvh
"""

# =====================
# SEND EMAIL (ONE.COM FIX)
# =====================
msg = MIMEText(email_text)
msg["Subject"] = "Momentum C25"
msg["From"] = EMAIL
msg["To"] = TO_EMAIL

with smtplib.SMTP_SSL("send.one.com", 465) as server:
    server.login(EMAIL, EMAIL_PASSWORD)
    server.send_message(msg)

print("E-mail sendt ✅")
