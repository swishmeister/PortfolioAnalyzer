# PortfolioAnalyzer

## Description
This tool is designed to perform financial analyses on a set of stocks by comparing their historical data against the S&P 500 index. It employs Monte Carlo simulations to visualize the risk-return trade-off and generates a comprehensive PDF report summarizing the findings.

## Features
**Stock Data Retrieval**: Fetches historical adjusted closing prices for user-input stock tickers.<br>
**Efficient Frontier Visualization**: Uses Monte Carlo simulations to plot the efficient frontier, helping users identify the optimal risk-return trade-off for various portfolio combinations.<br>
**Financial Metrics Calculation**:<br>
-**Sharpe Ratio**: Identifies the portfolio with the highest risk-adjusted return.<br>
-**Beta**: Measures the portfolio's volatility relative to the S&P 500.<br>
-**Alpha**: Assesses the portfolio's performance against the S&P 500.<br>
-**R-squared**: Measures how closely the portfolio's returns match the S&P 500's returns.<br>
**PDF Report Generation**: Compiles the analysis into a detailed report, saved as a PDF.<br>

## Dependencies
**yfinance**: For fetching stock data.<br>
**numpy**: For numerical operations.<br>
**pandas**: For data manipulation.<br>
**matplotlib**: For plotting the efficient frontier.<br>
**fpdf**: For generating the PDF report.<br>
**datetime**: For handling dates.<br>
