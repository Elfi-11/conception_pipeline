from pyairtable import Api
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os

# Configuration
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_ID = os.getenv("BASE_ID")
TABLE_NAME = os.getenv("TABLE_NAME")

# Configuration Streamlit
st.set_page_config(
    page_title="Dashboard Données",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Personnalisation CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# En-tête
st.title("📊 Dashboard Données Airtable")
st.markdown("---")

# Connexion Airtable
try:
    api = Api(API_TOKEN)
    table = api.table(BASE_ID, TABLE_NAME)
    records = table.all()
    
    # Conversion en DataFrame
    data = []
    for record in records:
        row = record.get('fields', {})
        row['id'] = record.get('id', '')
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Afficher le nombre de records
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 Total Records", len(df))
    with col2:
        st.metric("📋 Colonnes", len(df.columns))
    with col3:
        st.metric("✅ Statut", "Connecté")
    
    st.markdown("---")
    
    # Onglets pour différentes vues
    tab1, tab2, tab3 = st.tabs(["📋 Tableau", "📊 Statistiques", "🔍 Détails"])
    
    with tab1:
        st.subheader("Données complètes")
        
        # Options de filtrage
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔎 Rechercher dans les données:")
        with col2:
            if st.button("🔄 Rafraîchir"):
                st.rerun()
        
        # Filtrer les données si recherche
        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
            df_filtered = df[mask]
        else:
            df_filtered = df
        
        # Afficher le tableau avec pagination
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=400
        )
        
        # Export CSV
        csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv,
            file_name=f"{TABLE_NAME}_donnees.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Statistiques")
        
        if len(df) > 0:
            # Colonnes numériques uniquement
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) > 0:
                # Afficher les stats pour les colonnes numériques
                for col in numeric_cols:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(f"{col} - Min", f"{df[col].min():.2f}")
                    with col2:
                        st.metric(f"{col} - Max", f"{df[col].max():.2f}")
                    with col3:
                        st.metric(f"{col} - Moyenne", f"{df[col].mean():.2f}")
                    with col4:
                        st.metric(f"{col} - Médiane", f"{df[col].median():.2f}")
            else:
                st.info("ℹ️ Aucune colonne numérique détectée")
    
    with tab3:
        st.subheader("Détails des colonnes")
        st.write(f"**Colonne** | **Type** | **Non-null** | **Uniques**")
        st.write("---|---|---|---")
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].notna().sum()
            unique = df[col].nunique()
            st.write(f"`{col}` | {dtype} | {non_null}/{len(df)} | {unique}")
    
    st.markdown("---")
    st.caption(f"Dernière actualisation: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    st.error(f"❌ Erreur de connexion: {str(e)}")
    st.info("Vérifiez vos variables d'environnement (API_TOKEN, BASE_ID, TABLE_NAME)")

