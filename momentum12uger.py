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

if isinstance(data.columns, pd.MultiIndex):
    data = data["Close"]
else:
    data = data["Close"]

# ✅ Brug første og sidste gyldige pris (meget vigtigt)
start_prices = data.ffill().iloc[0]
end_prices = data.ffill().iloc[-1]

# =====================
# BEREGNING
# =====================
returns = ((end_prices / start_prices) - 1) * 100

# ✅ BEHOLD alle aktier – ingen dropna!
# (vi håndterer NaN senere i visning)

# =====================
# HTML TABEL
# =====================
def format_html_table(returns, start_prices, end_prices):

    sorted_returns = returns.sort_values(ascending=False)

    html = """
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <tr>
            <th>Nr</th>
            <th>Aktie</th>
            <th>Start</th>
            <th>Slut</th>
            <th>Afkast</th>
        </tr>
    """

    for i, (ticker, value) in enumerate(sorted_returns.items(), start=1):

        start = start_prices.get(ticker, None)
        end = end_prices.get(ticker, None)

        # ✅ håndtér manglende data
        if pd.isna(value) or pd.isna(start) or pd.isna(end):
            afkast_str = "N/A"
            start_str = "N/A"
            end_str = "N/A"
        else:
            afkast_str = f"{value:.2f}%"
            start_str = f"{start:.2f}"
            end_str = f"{end:.2f}"

        html += f"""
        <tr>
            <td>{i}</td>
            <td>{ticker}</td>
            <td>{start_str}</td>
            <td>{end_str}</td>
            <td>{afkast_str}</td>
        </tr>
        """

        # visuel opdeling (valgfrit)
        if i == 5 or i == 19:
            html += """
            <tr>
                <td colspan="5"><hr style="border:2px solid black;"></td>
            </tr>
            """

    html += "</table>"

    return html

# =====================
# EMAIL
# =====================
email_html = f"""
<html>
<body>

Hej Michael,<br><br>

Her er ugens momentum-rangering (12 uger):<br><br>

{format_html_table(returns, start_prices, end_prices)}

<br><br>
Mvh

</body>
</html>
"""

# =====================
# SEND EMAIL
# =====================
msg = MIMEText(email_html, "html")
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
