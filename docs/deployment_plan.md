# Deployment Plan: Vault & Vignette

The architecture consists of a single **Streamlit Monolithic Application**. 

## Deployment Steps (Streamlit Community Cloud)

To deploy the application to Streamlit Community Cloud:

1. **Commit and Push:** Ensure all code, including the `data` and `ml_models` directories, is pushed to your GitHub repository.
2. **Sign In:** Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. **Deploy:** Click "New app", select your repository, branch, and set the Main file path to `app.py`.
4. **Environment:** No specific environment variables are required, as the app uses a local SQLite database that Streamlit will create in memory/ephemeral storage on startup.

**Note:** Streamlit Community Cloud has ephemeral storage. The uploaded ledgers and SQLite database will not persist across app reboots. This is acceptable since the app is designed for session-based analysis.
