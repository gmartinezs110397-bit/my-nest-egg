# My Nest Egg

Private Streamlit app for planning credit card payments, personal debts, expenses, and payoff history.

## Run locally

```powershell
python -m streamlit run app.py
```

## Streamlit Cloud deploy

Entrypoint:

```text
app.py
```

Python dependencies are in:

```text
requirements.txt
```

Add this secret in Streamlit Cloud:

```toml
APP_PASSWORD = "your-4-digit-passcode"
```

The local `.streamlit/secrets.toml` file is intentionally ignored by git.
