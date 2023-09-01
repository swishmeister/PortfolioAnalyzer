import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# Input tickers
tickers = input("Enter the tickers separated by space: ").split()

# Fetch Stock Data
start_date = '2018-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')

data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

# Fetch S&P 500 index data
sp500 = yf.download('^GSPC', start=start_date, end=end_date)['Adj Close'].pct_change().dropna()

# Calculate daily returns, annual returns, and annual covariance matrix
daily_returns = data.pct_change().dropna()
if isinstance(daily_returns, pd.Series):
    daily_returns = daily_returns.to_frame()

mean_daily_returns = daily_returns.mean()
annual_returns = mean_daily_returns * 252
annual_cov_matrix = daily_returns.cov() * 252

# Monte Carlo Simulations
num_portfolios = 10000
results = np.zeros((4, num_portfolios))
risk_free_rate = 0.01

for i in range(num_portfolios):
    weights = np.random.random(len(tickers))
    weights /= np.sum(weights)

    portfolio_return = np.sum(annual_returns * weights)
    portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(annual_cov_matrix, weights)))
    results[0, i] = portfolio_return
    results[1, i] = portfolio_stddev
    results[2, i] = (portfolio_return - risk_free_rate) / portfolio_stddev
    results[3, i] = np.sum(weights * mean_daily_returns) * 252

# Extract Results & Plot Efficient Frontier
return_sharpe_max = results[0, results[2].argmax()]
risk_sharpe_max = results[1, results[2].argmax()]

return_stddev_min = results[0, results[1].argmin()]
risk_stddev_min = results[1, results[1].argmin()]

plt.figure(figsize=(12, 8))
plt.scatter(results[1, :], results[0, :], c=results[2, :], cmap='YlGnBu', marker='o')
plt.title('Efficient Frontier with Monte Carlo Simulation')
plt.xlabel('Annualized Volatility')
plt.ylabel('Annualized Returns')
plt.colorbar(label='Sharpe Ratio')

plt.scatter(risk_stddev_min, return_stddev_min, c='yellow', marker='*', s=100, label='Minimum Volatility Portfolio')
plt.scatter(risk_sharpe_max, return_sharpe_max, c='red', marker='*', s=100, label='Maximum Sharpe Ratio Portfolio')
plt.legend()

# User input for custom weights
print("\nWould you like to input specific weights for the stocks? (yes/no)")
choice = input().lower()

custom_weights = None

if choice == 'yes':
    custom_weights = []

    for ticker in tickers:
        weight = float(input(f"Enter weight for {ticker} (as a fraction between 0 and 1): "))
        custom_weights.append(weight)

    custom_weights = np.array(custom_weights) / np.sum(custom_weights)
    custom_return = np.sum(mean_daily_returns * custom_weights) * 252
    custom_stddev = np.sqrt(np.dot(custom_weights.T, np.dot(annual_cov_matrix, custom_weights)))
    plt.scatter(custom_stddev, custom_return, c='green', marker='*', s=100, label='Custom Portfolio')
    plt.legend()

plt.savefig("efficient_frontier.png")


# PDF Generation
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Stock Portfolio Analysis Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Data from {start_date} to {end_date}', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Display weights
weights_text = ""
for idx, ticker in enumerate(tickers):
    if custom_weights is not None:
        weights_text += f"{ticker}: {custom_weights[idx] * 100:.2f}% "
    else:
        weights_text += f"{ticker}: {100 / len(tickers):.2f}% "

plt.close()

pdf.ln(10)
pdf.set_font('Arial', '', 10)
pdf.multi_cell(0, 10, "Portfolio:\n" + weights_text)

# Efficient Frontier Image
pdf.ln(10)
pdf.image("efficient_frontier.png", x=10, y=None, w=190)

# Summary/Findings
pdf.ln(10)
pdf.set_font('Arial', '', 10)
pdf.multi_cell(0, 10, f"Portfolio with Maximum Sharpe Ratio:\nAnnual Return: {return_sharpe_max:.2%}\nAnnual Volatility: {risk_sharpe_max:.2%}\n\nPortfolio with Minimum Standard Deviation:\nAnnual Return: {return_stddev_min:.2%}\nAnnual Volatility: {risk_stddev_min:.2%}")

# Calculate individual stock betas relative to S&P 500
betas = []
for ticker in tickers:
    cov_with_market = daily_returns[ticker].cov(sp500)
    market_var = sp500.var()
    betas.append(cov_with_market / market_var)

# Calculate beta
if custom_weights is not None:
    portfolio_beta = np.sum(np.array(betas) * custom_weights)
else:
    equal_weights = np.array([1./len(tickers)]*len(tickers))
    portfolio_beta = np.sum(np.array(betas) * equal_weights)

pdf.ln(10)
pdf.multi_cell(0, 10, f"Portfolio Beta relative to S&P 500: {portfolio_beta:.2f}")

# Calculate Alpha
benchmark_return = sp500.mean() * 252  # Annualized Benchmark Return
expected_portfolio_return = risk_free_rate + portfolio_beta * (benchmark_return - risk_free_rate)
alpha = return_sharpe_max - expected_portfolio_return  # using the portfolio with max Sharpe Ratio as an example

pdf.ln(10)
pdf.multi_cell(0, 10, f"Portfolio Alpha relateive to S&P 500: {alpha:.2%}")

# Calculate R^2
correlation_with_benchmark = daily_returns[tickers].mean(axis=1).corr(sp500)
r_squared = correlation_with_benchmark**2

pdf.ln(10)
pdf.multi_cell(0, 10, f"R-squared with S&P 500: {r_squared:.2f}")


# Save the report
print("\nWould you like to save the report as a PDF? (yes/no)")
choice = input().lower()

if choice == 'yes':
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Portfolio_Analysis_Report_{timestamp}.pdf"
    pdf.output(filename)
    print(f"Report saved as {filename}")
