import os

# UPDATE IMPLEMENTATION PLAN
path = r'docs\implementation_plan.md'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('React', 'Streamlit')
    text = text.replace('Vite', 'Streamlit')
    text = text.replace('Zustand', 'Streamlit Session State')
    text = text.replace('Recharts', 'Plotly')
    text = text.replace('npx create-vite', 'pip install streamlit')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated implementation_plan.md')

# UPDATE CONVENTIONS
path = r'docs\conventions.md'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('React 18+ via Vite', 'Streamlit')
    text = text.replace('Zustand for global state', 'Streamlit Session State (st.session_state)')
    text = text.replace('Vanilla CSS with custom properties', 'Streamlit themes & native styling')
    text = text.replace('framer-motion', 'Streamlit native transitions')
    text = text.replace('recharts', 'Plotly or st.bar_chart')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated conventions.md')

# UPDATE DECISIONS
path = r'docs\decisions.md'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('React + Vite for the Frontend', 'Streamlit for the Frontend')
    text = text.replace('Build the frontend as a Single Page Application (SPA) using React and Vite', 'Build the frontend as a Streamlit application')
    text = text.replace('Requires running a separate Node server during development', '100% Python stack, zero Node.js required')
    text = text.replace('Allows utilization of robust charting libraries like `recharts`.', 'Leverages Plotly for interactive visualization within Python.')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated decisions.md')
