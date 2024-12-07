import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
)

st.set_page_config(page_title="Yaşam Koçu",
                   page_icon=":compass:",
                   initial_sidebar_state="expanded")


@st.cache_data(show_spinner=False, ttl=60*60*24)
def get_music_recommendations(mood):
    prompt = f"""                                     

    Sen bir müzik ve psikoloji uzmanısın. Kullanıcı, aşağıdaki ruh haliyle ilgili bir öneri istiyor:
    Ruh Hali: {mood}

    Bu ruh haline uygun 5 tane müzik önerisi yap.Önerilerinde şunlara dikkat et:
    - Kullanıcının duygu durumunu anlayan şarkılar seç.
    - Her şarkı için şarkının psikolojik etkisini açıkla.
    - Şarkının seçilme nedenini ve {mood} ruh haline nasıl katkı sağladığını duygusal olarak açıklayarak yaz

    Şarkıları şu formatta öner:
    Şarkı Adı - Sanatçı
    Açıklama: Neden bu şarkı seçildi ve {mood} ruh haline nasıl katkı sağlar?
    """

    try:
        response = model.generate_content(prompt)
        return response.text


    except Exception as e:
        st.error(f"Yapay zeka önerisi alınırken hata: {e}")
        return None


def music_recommendations_page():
    st.title("🎵 Mood'una Özel Müzik Önerileri")

    if "mood" not in st.session_state or not st.session_state.mood:
        st.warning("Lütfen önce ana sayfadan ruh halinizi seçiniz.")
        return

    mood = st.session_state.mood
    with st.spinner('Müzik önerileri yükleniyor...'):
        recommendations = get_music_recommendations(mood)


    if recommendations:
        st.subheader(f"{mood} Moduna Özel Müzik Listesi")

        st.markdown(recommendations)

    else:
        st.warning("Şu anda müzik önerisi alınamadı. Daha sonra tekrar deneyiniz.")


def main():
    page = st.sidebar.radio("Sayfalar", ["Yaşam Koçu Önerileri", "Günün Müzik Önerileri"])

    if page == "Yaşam Koçu Önerileri":
        st.header("☘️ Yaşam Koçu Uygulamasına Hoşgeldiniz")
        st.sidebar.title("Yaşam Koçu Önerileri")

        st.subheader("Bugün nasıl hissediyorsunuz?")

        if "mood" not in st.session_state:
            st.session_state.mood = []

        st.session_state.mood = st.selectbox(
            "Bugünkü ruh halinizi seçininiz:",
            ["Mutlu", "Üzgün", "Heyecanlı", "Umutlu", "Karamsar", "Sinirli", "Bezgin"],
            key="mood_select"
        )

        st.subheader("Şu andaki mevcut durumunuzu seçiniz.")
        current_situation = st.radio(
            "",
            [
                "Öğrenciyim.",
                "Şu anda çalışmıyorum.",
                "Aktif olarak çalışıyorum.",
                "Şu anda çalışmıyorum ama iş arıyorum.",
                "Herhangi bir amacım yok, sadece bilgi almak için buradayım."
            ],
            index=None,
            horizontal=False,
        )

        student_info = None
        job_info = None
        experience = None
        future_request = None
        information_request = None

        if current_situation:
            if any(item in current_situation for item in
                   ["Aktif olarak çalışıyorum", "Şu anda çalışmıyorum ama iş arıyorum"]):
                st.subheader("Şu anda ne iş yapmaktasınız?")
                job_info = st.text_input("Hangi sektörde çalışmaktasınız/çalıştınız?")
                st.subheader("Kaç senelik deneyiminiz bulunmaktadır?")
                experience = st.number_input("Tecrübe yılınızı giriniz:", min_value=0, step=1)

            elif any(item in current_situation for item in
                     ["Öğrenciyim", "Herhangi bir amacım yok, sadece bilgi almak için buradayım.",
                      "Şu anda çalışmıyorum."]):
                if current_situation == "Öğrenciyim.":
                    st.subheader("Hangi bölümde okuyorsunuz?")
                    student_info = st.text_input("Bölümünüzü giriniz:")
                elif current_situation == "Herhangi bir amacım yok, sadece bilgi almak için buradayım.":
                    st.subheader("Hayatla ilgili ne konuda bilgi almak istemektesiniz?")
                    information_request = st.text_input("Öğrenmek istediğiniz konuyu belirtiniz:")

            st.subheader("Gelecekte ne yapmak istiyorsunuz?")
            future_request = st.text_input("Gelecekteki yaşam planlarınızı giriniz:")

        st.subheader("Kaç senelik yol haritası çıkartılmasını istersiniz?")
        roadmap_duration = st.radio(
            "",
            ["6 ay", "1 sene", "2 sene", "3 sene", "5 sene", "10 sene"],
            index=None,
            horizontal=False,
        )

        if st.button("Kişisel Önerilerimi Hazırla"):

            if st.session_state.mood and not current_situation:
                st.error("Lütfen tüm gerekli alanları doldurunuz.")
                return

            if current_situation == "Öğrenciyim.":

                if not student_info or not future_request or not roadmap_duration or not st.session_state.mood:
                    st.error("Lütfen tüm gerekli alanları doldurunuz.")
                else:

                    try:
                        prompt = f"""
                        Bir {student_info} öğrencisinin {roadmap_duration} için kariyer planlaması yapılacak. 
                        Öğrencinin mevcut durumu: {st.session_state.mood} duygusal durumda.
                        Gelecek hedefi: {future_request}
                        Detaylı bir yol haritası oluştur:
                        - Bölümüyle ilgili spesifik kariyer hedefleri
                        - Staj ve iş deneyimi için öneriler
                        - Kişisel gelişim ve beceri edinme stratejileri
                        - Duygusal durumuna yönelik motivasyon ve destek önerileri
                        - Alanı ile ilgili hedeflemesi gereken teknik yetkinlikler ve beceriler
                        """
                        response = model.generate_content(
                             f"Bir yaşam koçu olarak, kullanıcıya detaylı, motive edici ve pratik öneriler ver : {prompt}")
                        st.subheader("İşte Kişisel Önerileriniz:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Bir hata oluştu: {e}")

            elif current_situation == "Şu anda çalışmıyorum.":

                if not future_request or not roadmap_duration or not st.session_state.mood:
                      st.error("Lütfen tüm gerekli alanları doldurunuz.")
                else:
                    try:
                        prompt = f"""
                        Şu anda çalışmamakta ve {st.session_state.mood} duygusal durumda olan bir birey için {roadmap_duration} yaşam planı hazırla.
                        Gelecek hedefi: {future_request}
                        Kapsamlı bir yaşam yol haritası oluştur:
                        - {future_request} hedefine ulaşmak için kişisel gelişim stratejileri
                        - Boş zamanları değerlendirme ve kişisel büyüme önerileri
                        - Alternatif gelir kaynakları ve fırsatlar
                        - Psikolojik sağlık ve motivasyon destek yöntemleri
                        - Sosyal ilişkiler ve network geliştirme önerileri
                        - Beceri edinme ve kendini geliştirme yolları
                        """
                        response = model.generate_content(
                            f"Bir yaşam koçu olarak, kullanıcıya detaylı, motive edici ve pratik öneriler ver : {prompt}")
                        st.subheader("İşte Kişisel Önerileriniz:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Bir hata oluştu: {e}")

            elif current_situation == "Aktif olarak çalışıyorum.":

                if not job_info or not experience or not future_request or not roadmap_duration or not st.session_state.mood:
                     st.error("Lütfen tüm gerekli alanları doldurunuz.")
                else:
                    try:
                        prompt = f"""
                        {job_info} alanında {experience} yıl çalışan ve {st.session_state.mood} duygusal durumda olan bir profesyonel için {roadmap_duration} kariyer gelişim planı hazırla.
                         Gelecek hedefi: {future_request}
                         Detaylı yol haritası içersin:
                         - Mevcut pozisyonda ilerleme stratejileri
                         - Yan beceriler ve profesyonel gelişim önerileri
                         - Kariyer hedefleri için somut adımlar
                         - İş-yaşam dengesi için pratik öneriler
                         - Duygusal durumuna yönelik motivasyon stratejileri
                         """
                        response = model.generate_content(
                            f"Bir yaşam koçu olarak, kullanıcıya detaylı, motive edici ve pratik öneriler ver : {prompt}")
                        st.subheader("İşte Kişisel Önerileriniz:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Bir hata oluştu: {e}")

            elif current_situation == "Şu anda çalışmıyorum ama iş arıyorum.":

                if not job_info or not future_request or not roadmap_duration or not st.session_state.mood:
                    st.error("Lütfen tüm gerekli alanları doldurunuz.")
                else:
                    try:
                        prompt = f"""
                        {job_info} alanında iş arayan ve {st.session_state.mood} duygusal durumda olan bir birey için {roadmap_duration} kariyer planlaması hazırla.
                         Gelecek hedefi: {future_request}
                         Kapsamlı bir yol haritası oluştur:
                         - Hedeflenen iş alanında rekabetçi olma stratejileri
                         - Özgeçmiş ve mülakat hazırlığı önerileri
                         - Beceri geliştirme ve sertifikasyon önerileri
                         - Network ve iş bulma kanalları
                         - Motivasyon ve psikolojik destek yaklaşımları
                        """
                        response = model.generate_content(
                              f"Bir yaşam koçu olarak, kullanıcıya detaylı, motive edici ve pratik öneriler ver : {prompt}")
                        st.subheader("İşte Kişisel Önerileriniz:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Bir hata oluştu: {e}")

            else:
                try:
                    prompt = f"""
                    Bilgi talebi konusu: {information_request}
                    Kullanıcının mevcut duygu durumu: {st.session_state.mood}
                    Kullanıcının bilgi talebi için kapsamlı bir açıklama ve rehberlik sağla:
                    - Konuyla ilgili temel bilgiler
                    - Derinlemesine anlayış için kaynaklar
                    - Pratik öneriler ve içgörüler
                    - Gelecekte bu konuda ilerlemek için stratejiler
                    """
                    response = model.generate_content(
                        f"Bir yaşam koçu olarak, kullanıcıya detaylı, motive edici ve pratik öneriler ver : {prompt}")
                    st.subheader("İşte Kişisel Önerileriniz:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")


    elif page == "Günün Müzik Önerileri":
        st.sidebar.title("Günün Müzik Önerileri")
        music_recommendations_page()


if __name__ == "__main__":
    main()