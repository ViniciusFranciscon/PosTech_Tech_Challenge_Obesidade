import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

st.set_page_config(
    page_title="Avaliação Clínica",
    page_icon="🏥",
    layout="wide"
)

MODEL_PATH = "modelo.pkl"
DB_PATH = "database.csv"

model = joblib.load(MODEL_PATH)


mapa_classes = {
    "Insufficient_Weight": "Abaixo do Peso",
    "Normal_Weight": "Peso Normal",
    "Overweight_Level_I": "Sobrepeso I",
    "Overweight_Level_II": "Sobrepeso II",
    "Obesity_Type_I": "Obesidade I",
    "Obesity_Type_II": "Obesidade II",
    "Obesity_Type_III": "Obesidade III"
}


if not os.path.exists(DB_PATH):
    df_init = pd.DataFrame(columns=[
        "Data",
        "Paciente",
        "Sexo",
        "Idade",
        "Altura",
        "Peso",
        "IMC",
        "Resultado"
    ])
    df_init.to_csv(DB_PATH, index=False)


st.title("Sistema de Avaliação de Obesidade")
st.markdown("### Ficha Médica Digital")

st.divider()

st.subheader("🪪 Identificação do Paciente")

col1, col2 = st.columns(2)

with col1:
    nome = st.text_input("Nome do Paciente")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])

with col2:
    idade = st.number_input("Idade (anos)", 1, 120, 30)
    altura = st.number_input("Altura (m)", 1.20, 2.30, 1.70, step=0.01)

peso = st.number_input("Peso (kg)", 30.0, 250.0, 70.0, step=0.5)

imc = peso / (altura ** 2)

st.metric("IMC", round(imc, 2))


if imc < 18.5:
    st.warning("Classificação IMC: Baixo Peso")
elif 18.5 <= imc < 25:
    st.success("Classificação IMC: Peso Normal")
elif 25 <= imc < 30:
    st.warning("Classificação IMC: Sobrepeso")
else:
    st.error("Classificação IMC: Obesidade")

st.divider()

st.subheader("Histórico")

historico_familiar = st.radio(
    "Histórico familiar de obesidade",
    ["Sim", "Não"],
    horizontal=True
)

st.divider()

st.subheader("Hábitos")

col1, col2 = st.columns(2)

with col1:
    consumo_calorico = st.radio(
        "Consumo frequente de alimentos calóricos",
        ["Sim", "Não"],
        horizontal=True
    )

    sedentarismo = st.radio(
        "Sedentarismo",
        ["Sim", "Não"],
        horizontal=True
    )

with col2:
    tabagismo = st.radio(
        "Fuma?",
        ["Sim", "Não"],
        horizontal=True
    )

    alcool = st.radio(
        "Consumo regular de álcool",
        ["Sim", "Não"],
        horizontal=True
    )

st.divider()


if st.button("Gerar Avaliação", use_container_width=True):

    dados = pd.DataFrame([{
        "Gender": "Male" if sexo == "Masculino" else "Female",
        "Age": idade,
        "Height": altura,
        "Weight": peso,
        "family_history": "yes" if historico_familiar == "Sim" else "no",
        "FAVC": "yes" if consumo_calorico == "Sim" else "no",
        "FCVC": 1.0,
        "NCP": 3.0,
        "CAEC": "Sometimes",
        "SMOKE": "yes" if tabagismo == "Sim" else "no",
        "CH2O": 2.0,
        "SCC": "no",
        "FAF": 0.0 if sedentarismo == "Sim" else 2.0,
        "TUE": 1.0,
        "CALC": "Frequently" if alcool == "Sim" else "no",
        "MTRANS": "Public_Transportation"
    }])

    resultado_modelo = model.predict(dados)[0]
    resultado = mapa_classes.get(resultado_modelo, resultado_modelo)

    st.subheader("📊 Resultado da Avaliação")

    if resultado == "Peso Normal":
        st.success(f"🟢 {resultado}")
    elif "Sobrepeso" in resultado:
        st.warning(f"🟡 {resultado}")
    elif "Obesidade" in resultado:
        st.error(f"🔴 {resultado}")
    else:
        st.info(f"🔵 {resultado}")

    novo_registro = pd.DataFrame([{
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Paciente": nome,
        "Sexo": sexo,
        "Idade": idade,
        "Altura": altura,
        "Peso": peso,
        "IMC": round(imc, 2),
        "Resultado": resultado
    }])

    df = pd.read_csv(DB_PATH)
    df = pd.concat([df, novo_registro], ignore_index=True)
    df.to_csv(DB_PATH, index=False)

    st.info("Registro salvo no histórico clínico.")

st.divider()

st.subheader("Histórico de Atendimentos")

df_hist = pd.read_csv(DB_PATH)

if not df_hist.empty:
    st.dataframe(df_hist, use_container_width=True)
else:
    st.write("Nenhum atendimento registrado.")