# AI Stock Advisor

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow)
![SQLite](https://img.shields.io/badge/SQLite-DB-0769AD?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

## Table of Contents

- [AI Stock Advisor](#ai-stock-advisor)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Project Structure](#project-structure)
  - [Setup and Installation (Local)](#setup-and-installation-local)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create and Activate Virtual Environment](#2-create-and-activate-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Set Up Environment Variables](#4-set-up-environment-variables)
    - [5. Train the LSTM Model](#5-train-the-lstm-model)
  - [Running the Application (Local)](#running-the-application-local)
  - [Deployment](#deployment)
    - [Streamlit Community Cloud](#streamlit-community-cloud)
    - [Render](#render)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

---

## Introduction

The **AI Stock Advisor** is a powerful Streamlit web application designed to provide users with comprehensive stock analysis, real-time news, future price predictions, market volatility insights, and intelligent Buy/Sell/Hold recommendations. Leveraging machine learning (LSTM models) and various financial APIs, this tool aims to empower users with data-driven insights for better trading decisions.

The application features a robust authentication system with email verification and role-based access control, ensuring a personalized and secure user experience.

## Features

* **User Authentication:**
    * Secure Sign Up & Login with password hashing.
    * Email Verification via One-Time Passwords (OTP).
    * Password Reset functionality.
    * User activity logging.
* **Data Fetching:**
    * Live and historical stock price data (Open, High, Low, Close, Volume) using `yfinance`.
    * Dynamic period selection for charts (1d, 5d, 1mo, 6mo, 1y, etc., like Google Finance).
* **Technical Indicators:**
    * Correct calculation and display of Relative Strength Index (RSI).
    * Correct calculation and display of Moving Average Convergence Divergence (MACD).
* **Interactive Charts:**
    * Detailed Candlestick charts with overlaid indicators using `mplfinance` and `Plotly`.
    * Google Finance-like interactive charts for in-depth analysis.
* **Live News & Headlines:**
    * Fetches real-time news and headlines for the entered ticker symbol using NewsAPI.
    * Clickable links to read full articles from source websites.
    * Basic sentiment analysis of news articles.
* **Price Prediction:**
    * Predicts future stock prices for the ticker using a trained LSTM (Long Short-Term Memory) neural network model based on historical prices and news sentiment.
* **Market Volatility:**
    * Calculates and displays current market volatility.
* **Buy/Sell/Hold Recommendations:**
    * Provides AI-driven recommendations based on price predictions, technical indicators, news sentiment, and market volatility.
* **User Permission-driven AI Execution Flow:**
    * Features like price prediction and AI recommendations are gated based on user roles (e.g., 'Free' vs. 'Premium' users).

## Tech Stack

* **Frontend/Web Framework:** [Streamlit](https://streamlit.io/)
* **Backend/Core Logic:** Python 3.9+
* **Data Handling:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Stock Data:** [yfinance](https://pypi.org/project/yfinance/)
* **Technical Analysis:** [TA-Lib](https://technical-analysis-library-in-python.readthedocs.io/en/latest/) (via `ta` library)
* **Machine Learning:** [TensorFlow](https://www.tensorflow.org/) / [Keras](https://keras.io/) (for LSTM)
* **Data Preprocessing:** [Scikit-learn](https://scikit-learn.org/)
* **Database:** [SQLite3](https://docs.python.org/3/library/sqlite3.html) (for user management, activity logs, OTPs)
* **Password Hashing:** [Bcrypt](https://pypi.org/project/bcrypt/)
* **Email Sending:** Python's built-in `smtplib`
* **API Interactions:** [Requests](https://docs.python-requests.org/en/master/)
* **News API:** [NewsAPI.org](https://newsapi.org/)
* **Charting Libraries:** [Plotly](https://plotly.com/python/) (for interactive charts), [mplfinance](https://pypi.org/project/mplfinance/) (for static candlesticks)
* **Environment Variables:** [python-dotenv](https://pypi.org/project/python-dotenv/)
* **Testing:** [Pytest](https://pytest.org/), [pytest-mock](https://pypi.org/project/pytest-mock/)

## Project Structure

The project follows a modular and organized structure to separate concerns:

```

your_project/
├── app.py                         \# Main Streamlit application
├── .env                           \# Environment variables (API keys, DB creds) - KEEP LOCAL
├── runtime.txt                    \# Python runtime version (e.g., for Heroku/Render)
