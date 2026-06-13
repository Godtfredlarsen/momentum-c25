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

# ✅ Samme som dit virkende program
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

# ✅ Stabil løsning
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
# HTML TABEL (PERFEKTE KOLONNER)
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
        start = start_prices[ticker]
        end = end_prices[ticker]

        html += f"""
        <tr>
            <td>{i}</td>
            <td>{ticker}</td>
            <td>{start:.2f}</td>
            <td>{end:.2f}</td>
            <td>{value:.2f}%</td>
        </tr>
        """

        # ✅ Linje efter nr. 5
        if i == 5:
            html += """
            <tr>
                <td colspan="5"><hr style="border:2px solid black;"></td>
            </tr>
            """

        # ✅ Linje efter nr. 19
        if i == 19:
            html += """
            <tr>
                <td colspan="5"><hr style="border:2px solid black;"></td>
            </tr>
            """

    html += "</table>"

    return html

date_str = end_date.strftime("%d %B %Y")

# =====================
# EMAIL INDHOLD (HTML)
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
# SEND EMAIL (samme metode som virker)
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
