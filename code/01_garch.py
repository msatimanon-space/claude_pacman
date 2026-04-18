"""GARCH(1,1) volatility model for SET Index."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from arch import arch_model
from scipy.stats import t as student_t

SEED = 42
TICKER = "^SET.BK"
START = "2020-01-01"
END = "2026-03-31"

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "output" / "figures"
TBL_DIR = ROOT / "output" / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TBL_DIR.mkdir(parents=True, exist_ok=True)


def fetch_prices(ticker: str, start: str, end: str) -> pd.Series:
    data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if data.empty:
        raise RuntimeError(f"ไม่สามารถดึงข้อมูลของ {ticker} ได้")
    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.dropna()


def main() -> None:
    np.random.seed(SEED)

    prices = fetch_prices(TICKER, START, END)
    log_returns = np.log(prices / prices.shift(1)).dropna() * 100.0

    model = arch_model(
        log_returns,
        mean="Constant",
        vol="GARCH",
        p=1,
        q=1,
        dist="t",
    )
    res = model.fit(disp="off")

    forecast = res.forecast(horizon=1, reshape=False)
    mu = float(res.params["mu"])
    sigma_next = float(np.sqrt(forecast.variance.values[-1, 0]))
    nu = float(res.params["nu"])

    q95 = student_t.ppf(0.05, df=nu)
    q99 = student_t.ppf(0.01, df=nu)
    var_95 = -(mu + sigma_next * q95)
    var_99 = -(mu + sigma_next * q99)

    cond_vol = res.conditional_volatility
    rolling_vol = log_returns.rolling(window=20).std()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(cond_vol.index, cond_vol.values, label="GARCH(1,1) Conditional Vol", color="#c0392b", linewidth=1.4)
    ax.plot(rolling_vol.index, rolling_vol.values, label="Rolling 20-day Std", color="#2c3e50", linewidth=1.0, alpha=0.8)
    ax.set_title("SET Index — Conditional Volatility (GARCH(1,1), Student's-t)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility (%)")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig_path = FIG_DIR / "garch_vol.png"
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)

    params = res.params
    pvalues = res.pvalues
    std_err = res.std_err
    tvalues = res.tvalues
    params_df = pd.DataFrame(
        {
            "parameter": params.index,
            "estimate": params.values,
            "std_error": std_err.values,
            "t_value": tvalues.values,
            "p_value": pvalues.values,
        }
    )
    tbl_path = TBL_DIR / "garch_params.csv"
    params_df.to_csv(tbl_path, index=False)

    print("=" * 60)
    print("สรุปผลแบบจำลอง GARCH(1,1) สำหรับดัชนี SET")
    print("=" * 60)
    print(f"ช่วงข้อมูล              : {log_returns.index[0].date()}  ถึง  {log_returns.index[-1].date()}")
    print(f"จำนวนวันซื้อขาย         : {len(log_returns):,}")
    print(f"ผลตอบแทนเฉลี่ยต่อวัน    : {log_returns.mean():.4f} %")
    print(f"ส่วนเบี่ยงเบนมาตรฐาน   : {log_returns.std():.4f} %")
    print("-" * 60)
    print("พารามิเตอร์ของ GARCH(1,1):")
    for name, value in params.items():
        print(f"  {name:8s} = {value: .6f}   (p-value = {pvalues[name]:.4f})")
    print("-" * 60)
    print(f"Log-likelihood          : {res.loglikelihood:.3f}")
    print(f"AIC                     : {res.aic:.3f}")
    print(f"BIC                     : {res.bic:.3f}")
    print("-" * 60)
    print(f"ความผันผวนพยากรณ์ 1 วัน : {sigma_next:.4f} %")
    print(f"VaR 95% (1 วันข้างหน้า) : {var_95:.4f} %")
    print(f"VaR 99% (1 วันข้างหน้า) : {var_99:.4f} %")
    print("-" * 60)
    print(f"บันทึกกราฟไว้ที่         : {fig_path.relative_to(ROOT)}")
    print(f"บันทึกตารางพารามิเตอร์   : {tbl_path.relative_to(ROOT)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
