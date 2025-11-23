import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys
import os
sys.path.append("..") 
from supabase_manager import fetch_all_responses
st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("📊 Dashboard Analitik Orange Wallet")
st.markdown("---")
pass_admin=os.getenv("ADMIN_PASS")
def map_sentiment_score(val):
    """Mengubah teks kualitatif menjadi skor angka (1-5) untuk perhitungan rata-rata."""
    mapping = {
        'Sangat Mudah': 5, 'Mudah': 4, 'Biasa': 3, 'Sulit': 2, 'Sangat Sulit': 1,
        'Sangat Puas': 5, 'Puas': 4, 'Kecewa': 2, 'Sangat Kecewa': 1,
        'Sangat Intuitif': 5, 'Cukup Jelas': 3, 'Membingungkan': 1,
        'Cepat': 5, 'Lambat': 1
    }
    return mapping.get(val, 3)

def generate_wordcloud(text_data):
    """Membuat WordCloud dari list teks."""
    if not text_data:
        return None
    text = " ".join([str(t) for t in text_data if str(t) != 'nan' and str(t) != '-'])
    if not text.strip():
        return None
    
    wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(text)
    return wc

if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

if not st.session_state['admin_logged_in']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        password = st.text_input("🔑 Masukkan Password Admin:", type="password")
        if st.button("Login"):
            if password == pass_admin:
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("Password Salah")
else:
    if st.sidebar.button("Logout"):
        st.session_state['admin_logged_in'] = False
        st.rerun()

    df = fetch_all_responses()

    if df.empty:
        st.warning("📭 Belum ada data responden yang masuk.")
    else:
        st.subheader("📈 Ringkasan Performa")
        
        df['score_topup'] = df['topup_score'].apply(map_sentiment_score)
        df['score_transfer'] = df['transfer_score'].apply(map_sentiment_score)
        df['score_split'] = df['split_score'].apply(map_sentiment_score)
        df['score_shared'] = df['shared_score'].apply(map_sentiment_score)
        df['score_satisfaction'] = df['kepuasan_akhir'].apply(map_sentiment_score)
        
        total_user = len(df)
        avg_satisfaction = df['score_satisfaction'].mean()
        
        retention_count = df[df['niat_penggunaan'].str.contains('Ya', na=False)].shape[0]
        retention_rate = (retention_count / total_user) * 100 if total_user > 0 else 0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Responden", f"{total_user} Orang")
        kpi2.metric("Rata-rata Kepuasan", f"{avg_satisfaction:.1f} / 5.0", delta_color="normal")
        kpi3.metric("Potential Retention", f"{retention_rate:.1f}%")
        kpi4.metric("Fitur Terpopuler", df[['score_topup', 'score_transfer', 'score_split', 'score_shared']].mean().idxmax().replace('score_', '').title())

        st.markdown("---")

        col_radar, col_bar = st.columns([1, 1])
        
        with col_radar:
            st.subheader("🕸️ Peta Kekuatan Fitur (Radar Chart)")
            
            radar_data = pd.DataFrame({
                'Fitur': ['Top Up', 'Transfer', 'Split Bill', 'Shared Wallet', 'Navigasi UI', 'Performa App'],
                'Skor': [
                    df['score_topup'].mean(),
                    df['score_transfer'].mean(),
                    df['score_split'].mean(),
                    df['score_shared'].mean(),
                    df['ui_navigasi'].apply(map_sentiment_score).mean(),
                    df['ui_performa'].apply(map_sentiment_score).mean()
                ]
            })
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=radar_data['Skor'],
                theta=radar_data['Fitur'],
                fill='toself',
                name='Rata-rata Skor'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption("*Skala 1-5 (Semakin luas jaring, semakin baik performa keseluruhan)*")

        with col_bar:
            st.subheader("📊 Distribusi Kepuasan Akhir")
            
            sat_counts = df['kepuasan_akhir'].value_counts().reset_index()
            sat_counts.columns = ['Kepuasan', 'Jumlah']
            
            fig_bar = px.bar(sat_counts, x='Kepuasan', y='Jumlah', 
                             color='Jumlah', color_continuous_scale='Oranges')
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("##### Insight Niat Penggunaan")
            use_counts = df['niat_penggunaan'].value_counts()
            fig_pie = px.pie(values=use_counts.values, names=use_counts.index, hole=0.4)
            fig_pie.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        st.subheader("☁️ Apa Kata Mereka? (Word Cloud)")
        
        wc_col1, wc_col2 = st.columns(2)
        
        with wc_col1:
            st.markdown("**Feedback: Top Up & Transfer**")
            text_trx = list(df['topup_feedback'].dropna()) + list(df['transfer_feedback'].dropna())
            wc_trx = generate_wordcloud(text_trx)
            if wc_trx:
                fig_wc, ax = plt.subplots()
                ax.imshow(wc_trx, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig_wc)
            else:
                st.info("Belum cukup data teks.")

        with wc_col2:
            st.markdown("**Feedback: Pesan Terakhir**")
            text_final = list(df['pesan_akhir'].dropna())
            wc_final = generate_wordcloud(text_final)
            if wc_final:
                fig_wc2, ax = plt.subplots()
                ax.imshow(wc_final, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig_wc2)
            else:
                st.info("Belum cukup data teks.")

        st.markdown("---")

        st.subheader("🗃️ Data Mentah")
        
        all_cols = df.columns.tolist()
        selected_cols = st.multiselect("Pilih Kolom:", all_cols, default=['timestamp', 'nama', 'kepuasan_akhir', 'pesan_akhir'])
        
        st.dataframe(df[selected_cols], use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Data Lengkap (CSV)",
            csv,
            "hasil_survei_orange_wallet.csv",
            "text/csv"
        )