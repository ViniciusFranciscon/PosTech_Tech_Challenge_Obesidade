import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "modelos", "modelo.pkl")

model = joblib.load(model_path)

st.set_page_config(
    page_title="Avaliação Clínica",
    page_icon="🏥",
    layout="wide"
)
DB_PATH = os.path.join(BASE_DIR, "..", "data", "database.csv")

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
        "Data", "Paciente", "Sexo", "Idade",
        "Altura", "Peso", "IMC", "Resultado"
    ])
    df_init.to_csv(DB_PATH, index=False)

st.title("Sistema de Avaliação de Obesidade")
st.markdown("### Ficha Médica Digital")

st.divider()

st.subheader("🪪 Identificação")

col1, col2 = st.columns(2)

with col1:
    nome = st.text_input("Nome do Paciente")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])

with col2:
    idade = st.number_input("Idade", 14, 100, 30)
    altura = st.number_input("Altura (m)", 1.20, 2.30, 1.70, step=0.01)

peso = st.number_input("Peso (kg)", 30.0, 250.0, 70.0, step=0.5)

imc = peso / (altura ** 2)
st.metric("IMC", round(imc, 2))

st.divider()

st.subheader("Histórico Clínico")

historico_familiar = st.radio(
    "Histórico familiar de obesidade",
    ["Sim", "Não"],
    horizontal=True
)

monitoramento_calorico = st.radio(
    "Monitora ingestão calórica?",
    ["Sim", "Não"],
    horizontal=True
)

st.divider()


st.subheader("Hábitos de Vida")

col1, col2 = st.columns(2)

with col1:
    consumo_calorico = st.radio(
        "Consumo frequente de alimentos calóricos",
        ["Sim", "Não"],
        horizontal=True
    )

    vegetais = st.selectbox(
        "Frequência de consumo de vegetais",
        ["1 - Raramente", "2 - Às vezes", "3 - Sempre"]
    )

    refeicoes = st.selectbox(
        "Número de refeições principais",
        ["1", "2", "3", "4 ou mais"]
    )

    lanches = st.selectbox(
        "Faz lanches entre refeições",
        ["no", "Sometimes", "Frequently", "Always"]
    )

with col2:
    agua = st.selectbox(
        "Consumo diário de água",
        ["1 - <1L", "2 - 1-2L", "3 - >2L"]
    )

    atividade = st.selectbox(
        "Frequência de atividade física",
        ["0 - Nenhuma", "1 - 1-2x/sem", "2 - 3-4x/sem", "3 - 5x ou mais"]
    )

    tempo_tela = st.selectbox(
        "Tempo diário de tela",
        ["0 - 0-2h", "1 - 3-5h", "2 - >5h"]
    )

    transporte = st.selectbox(
        "Meio de transporte",
        ["Automobile", "Motorbike", "Bike",
         "Public_Transportation", "Walking"]
    )

tabagismo = st.radio("Fuma?", ["Sim", "Não"], horizontal=True)

alcool = st.selectbox(
    "Consumo de álcool",
    ["no", "Sometimes", "Frequently", "Always"]
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
        "FCVC": int(vegetais[0]),
        "NCP": 4 if refeicoes == "4 ou mais" else int(refeicoes),
        "CAEC": lanches,
        "SMOKE": "yes" if tabagismo == "Sim" else "no",
        "CH2O": int(agua[0]),
        "SCC": "yes" if monitoramento_calorico == "Sim" else "no",
        "FAF": int(atividade[0]),
        "TUE": int(tempo_tela[0]),
        "CALC": alcool,
        "MTRANS": transporte
    }])

    resultado_modelo = model.predict(dados)[0]
    resultado = mapa_classes.get(resultado_modelo, resultado_modelo)

    st.subheader("Resultado")

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

    st.success("Registro salvo com sucesso.")

st.divider()

st.subheader("Histórico de Atendimentos")

df_hist = pd.read_csv(DB_PATH)

if not df_hist.empty:
    st.dataframe(df_hist, use_container_width=True)
else:
    st.write("Nenhum atendimento registrado.")