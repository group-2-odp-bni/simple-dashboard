import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv 
import os 
from local_db_manager import save_survey_response

st.set_page_config(
    page_title="Survei Aplikasi Orange Wallet", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

load_dotenv() 

SMTP_CONFIG = {}
try:
    SMTP_CONFIG = {
        "PASSWORD": os.getenv("SMTP_PASSWORD"),
        "MAIL": os.getenv("SMTP_MAIL"),
        "HOST": os.getenv("SMTP_HOST"),
        "PORT": int(os.getenv("SMTP_PORT") or 587),
    }
except Exception:
    pass

def send_survey_email(recipient_email, recipient_name, survey_data):
    """Mengirim email ringkasan ke pengisi survei."""
    if not all(SMTP_CONFIG.values()):
        st.error("Konfigurasi email server belum lengkap.")
        return False

    try:
        subject = "🎉 Terima Kasih! Ringkasan Hasil Survei Orange Wallet"
        
        data_display = "\n".join([
            f"- {k.replace('_', ' ').title().replace('Va', 'VA')}: {v}" 
            for k, v in survey_data.items() 
            if k not in ['nama', 'email', 'anonim', 'timestamp']
        ])

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Halo {recipient_name},</h2>
            <p>Terima kasih telah mencoba dan memberikan masukan untuk <strong>Orange Wallet</strong>.</p>
            <hr>
            <h3>Ringkasan Jawaban Anda:</h3>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">{data_display}</pre>
            <hr>
            <p>Salam hangat,<br>Tim Orange Wallet BNI</p>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_CONFIG["MAIL"]
        msg['To'] = recipient_email
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(SMTP_CONFIG["HOST"], SMTP_CONFIG["PORT"])
        server.starttls()
        server.login(SMTP_CONFIG["MAIL"], SMTP_CONFIG["PASSWORD"])
        server.sendmail(SMTP_CONFIG["MAIL"], recipient_email, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Gagal mengirim email: {e}")
        return False
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'data' not in st.session_state:
    st.session_state.data = {}

def next_page(): st.session_state.page += 1
def prev_page(): st.session_state.page -= 1
def reset_survey():
    st.session_state.data = {}
    st.session_state.page = 1
    st.rerun()

st.markdown("""
<style>
    /* Memastikan iframe memenuhi kontainer kolom */
    iframe {
        width: 100% !important;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Styling Tombol Utama (Merah Orange BNI style) */
    .stButton > button {
        background-color: #FF5500; 
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
    }
    .stButton > button:hover {
        background-color: #CC4400;
        color: white;
    }

    /* Styling Tombol Back (Tombol kedua/bawah biasanya di container) */
    div[data-testid="stVerticalBlock"] > div > div > button[kind="secondary"] {
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #d6d6d6;
    }
</style>
""", unsafe_allow_html=True)


def page_1_intro():
    st.title("🍊 Survei Kepuasan Orange Wallet")
    st.markdown("---")
    
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.subheader("1. Data Pengisi")
        is_anon = st.checkbox("Isi secara **Anonim**", value=(st.session_state.data.get('anonim') == 'Ya'))
        
        with st.container(border=True):
            if not is_anon:
                st.info("Hasil survei akan dikirim ke email Anda.")
                nama = st.text_input("Nama Lengkap", value=st.session_state.data.get('nama', ''))
                email = st.text_input("Email", value=st.session_state.data.get('email', ''))
                st.session_state.data.update({'nama': nama, 'email': email, 'anonim': 'Tidak'})
            else:
                st.success("Identitas Anda disembunyikan.")
                st.session_state.data.update({'nama': 'Anonim', 'email': '-', 'anonim': 'Ya'})

        allow_next = True
        if not is_anon and (not st.session_state.data.get('nama') or not st.session_state.data.get('email')):
            allow_next = False
            st.warning("Mohon lengkapi data diri atau pilih Anonim.")
        
        if allow_next:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Mulai Uji Coba (Next) ➡️", on_click=next_page, use_container_width=True)

    with col_right:
        st.subheader("Preview Aplikasi")
        st.caption("Silakan eksplorasi halaman login/profil di sini.")
        st.components.v1.iframe("https://app.orangebybni.my.id", height=700, scrolling=True)



def page_2_flow_topup_transfer():
    st.header("Bagian 2/5: Uji Coba Top Up & Transfer")
    st.progress(25)
    
    with st.form("form_p2"):
        col_sim, col_q = st.columns([1, 1], gap="medium")
        
        with col_sim:
            st.subheader("📱 Simulator Aplikasi")
            st.info("Gunakan area ini untuk mencoba fitur.")
            
            st.markdown("**1. App Utama (Transfer & Top Up Menu)**")
            st.components.v1.iframe("https://app.orangebybni.my.id", height=850, scrolling=True)
            
            st.markdown("---")
            
            st.markdown("**2. Halaman Virtual Account (Simulasi)**")
            st.components.v1.iframe("https://va-payment-481374538659.asia-southeast2.run.app/", height=500, scrolling=True)

        with col_q:
            st.subheader("📝 Lembar Evaluasi")
            
            st.markdown("#### A. Fitur Top Up")
            q_topup = st.radio("Kemudahan alur Top Up (sampai dapat VA):", 
                             ['Sangat Mudah', 'Mudah', 'Biasa', 'Sulit', 'Sangat Sulit'],
                             index=None, key="q_topup")
            feed_topup = st.text_area("Kendala/Saran Top Up:", key="feed_topup")
            
            st.markdown("---")
            
            st.markdown("#### B. Fitur Transfer")
            q_trf = st.radio("Kemudahan alur Transfer:", 
                           ['Sangat Mudah', 'Mudah', 'Biasa', 'Sulit', 'Sangat Sulit'],
                           index=None, key="q_trf")
            feed_trf = st.text_area("Kendala/Saran Transfer:", key="feed_trf")

            st.markdown("<br><br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Simpan & Lanjut ➡️", use_container_width=True)
            
            if submitted:
                if not q_topup or not q_trf:
                    st.error("⚠️ Mohon isi penilaian kemudahan (Radio Button) sebelum lanjut.")
                else:
                    st.session_state.data.update({
                        'topup_score': q_topup, 'topup_feedback': feed_topup,
                        'transfer_score': q_trf, 'transfer_feedback': feed_trf
                    })
                    next_page()

    st.button("⬅️ Kembali", on_click=prev_page)



def page_3_flow_advanced():
    st.header("Bagian 3/5: Split Bill & Shared Wallet")
    st.progress(50)
    
    with st.form("form_p3"):
        col_sim, col_q = st.columns([1, 1], gap="medium")
        
        with col_sim:
            st.subheader("📱 Simulator Aplikasi")
            st.info("Coba menu 'Split Bill' atau 'Create Wallet' > 'Shared'.")
            st.components.v1.iframe("https://app.orangebybni.my.id", height=850, scrolling=True)

        with col_q:
            st.subheader("📝 Lembar Evaluasi")
            
            st.markdown("#### A. Split Bill")
            q_split = st.radio("Kemudahan Split Bill:", 
                             ['Sangat Mudah', 'Mudah', 'Biasa', 'Sulit', 'Sangat Sulit'],
                             index=None, key="q_split")
            feed_split = st.text_area("Saran Split Bill:", key="feed_split")
            
            st.markdown("---")
            
            st.markdown("#### B. Shared Wallet")
            q_shared = st.radio("Kemudahan Shared Wallet:", 
                              ['Sangat Mudah', 'Mudah', 'Biasa', 'Sulit', 'Sangat Sulit'],
                              index=None, key="q_shared")
            feed_shared = st.text_area("Saran Shared Wallet:", key="feed_shared")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Simpan & Lanjut ➡️", use_container_width=True)
            
            if submitted:
                if not q_split or not q_shared:
                    st.error("⚠️ Mohon isi penilaian kemudahan sebelum lanjut.")
                else:
                    st.session_state.data.update({
                        'split_score': q_split, 'split_feedback': feed_split,
                        'shared_score': q_shared, 'shared_feedback': feed_shared
                    })
                    next_page()

    st.button("⬅️ Kembali", on_click=prev_page)


def page_4_uiux():
    st.header("Bagian 4/5: Penilaian UI/UX & Perbandingan")
    st.progress(75)
    
    with st.form("form_p4"):
        st.markdown("#### 1. Pengalaman Pengguna (UX)")
        col1, col2 = st.columns(2)
        with col1:
            nav = st.radio("Navigasi Menu:", ['Sangat Intuitif', 'Cukup Jelas', 'Membingungkan'], index=None)
        with col2:
            perf = st.radio("Kecepatan Loading:", ['Cepat', 'Biasa', 'Lambat'], index=None)
            
        st.markdown("---")
        st.markdown("#### 2. Perbandingan Kompetitor")
        competitor = st.selectbox("Wallet Lain yang sering dipakai:", 
                                ['GoPay', 'OVO', 'DANA', 'ShopeePay', 'LinkAja', 'Lainnya'])
        
        comp_feature = st.text_area(f"Fitur {competitor} yang wajib ada di Orange Wallet:")
        
        submitted = st.form_submit_button("Simpan & Lanjut ➡️", use_container_width=True)
        
        if submitted:
            if not nav or not perf:
                st.error("Mohon lengkapi penilaian UX.")
            else:
                st.session_state.data.update({
                    'ui_navigasi': nav, 'ui_performa': perf,
                    'kompetitor_nama': competitor, 'kompetitor_fitur': comp_feature
                })
                next_page()
                
    st.button("⬅️ Kembali", on_click=prev_page)



def page_5_final():
    st.header("Bagian 5/5: Kesimpulan")
    st.progress(100)
    
    with st.form("form_final"):
        st.markdown("### Kesimpulan Akhir")
        
        final_sat = st.select_slider("Kepuasan Keseluruhan:", 
                                   options=['Sangat Kecewa', 'Kecewa', 'Biasa', 'Puas', 'Sangat Puas'],
                                   value='Biasa')
        
        final_use = st.radio("Apakah akan menggunakan Orange Wallet kedepannya?",
                           ['Ya, Pasti', 'Mungkin', 'Tidak'], index=None)
        
        final_msg = st.text_area("Pesan Terakhir untuk Tim Developer:")
        
        submitted = st.form_submit_button("🎉 KIRIM SURVEI", use_container_width=True)
        
        if submitted:
            if not final_use:
                st.error("Mohon jawab pertanyaan niat penggunaan.")
            else:
                st.session_state.data.update({
                    'kepuasan_akhir': final_sat,
                    'niat_penggunaan': final_use,
                    'pesan_akhir': final_msg
                })
                
                data_final = st.session_state.data
                
                db_status = save_survey_response(data_final)
                
                mail_status = True
                if data_final.get('anonim') == 'Tidak':
                    with st.spinner("Mengirim email ringkasan..."):
                        mail_status = send_survey_email(data_final['email'], data_final['nama'], data_final)
                
                if db_status:
                    st.success("✅ Data berhasil disimpan!")
                else:
                    st.warning("⚠️ Data tersimpan lokal (Gagal koneksi DB), namun survei selesai.")
                    
                if mail_status and data_final.get('anonim') == 'Tidak':
                    st.info(f"📧 Email ringkasan telah dikirim ke {data_final['email']}")
                
                st.balloons()
                st.write("---")
                st.json(data_final, expanded=False)
                
                st.form_submit_button("Isi Survei Baru uatng", on_click=reset_survey)

    st.button("⬅️ Kembali", on_click=prev_page)



def main():
    pg = st.session_state.page
    if pg == 1: page_1_intro()
    elif pg == 2: page_2_flow_topup_transfer()
    elif pg == 3: page_3_flow_advanced()
    elif pg == 4: page_4_uiux()
    elif pg == 5: page_5_final()

if __name__ == '__main__':
    main()