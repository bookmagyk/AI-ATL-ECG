import streamlit as st
from io import StringIO
import numpy as np
import automatic_ecg_diagnosis_master.predict as predict
import google.generativeai as palm
import google.ai.generativelanguage as gen_lang
import matplotlib.pyplot as plt

#configuration
np.set_printoptions(suppress=True)
palm.configure(api_key='AIzaSyBvMkWvomihQQf6ehjPhuup4nLoKOVcoUk')
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name

def call_api(age, sex, data):
    global model
    sex = "male" if sex == "M" else "female"
    
    prompt = """Pretend you are a cardiologist.You have an ECG interpreting machine learning model that classified a patient's ECG data and provided percentage likelihoods for each condition 1dAVb, RBBB, LBBB, SB, AF,  ST.
    
    Here are what the acronyms mean:
    1dAVb: 1st degree AV block
    RBBB: right bundle branch block
    LBBB: left bundle branch block 
    SB: sinus bradycardia 
    AF: atrial fibrillation
    ST: sinus tachycardia 

    If a patient had the percentage likelihood of each condition below,
    what would you recommend about the patient's further tests and/or treatment? 
    This patient is """ + str(age) +""" years old and """ + sex + """. 
    These are percentages so for example, 0.13239485 means 13%.

    1dAVb: """ + str(data[0]) + """
    RBBB: """+ str(data[1]) + """
    LBBB: """+ str(data[2]) + """
    SB: """+ str(data[3]) +"""
    AF: """ + str(data[4]) + """
    ST: """+ str(data[5])

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        safety_settings=[
        {
            "category": gen_lang.HarmCategory.HARM_CATEGORY_MEDICAL,
            "threshold": gen_lang.SafetySetting.HarmBlockThreshold.BLOCK_NONE,
        },],
        temperature=0,
        # The maximum length of the response
        max_output_tokens=800,)
    
    return completion.result

## streamlight code

st.title('Automatic ECG diagnosis')
st.subheader('A tool to view and analyze ECG data, backed by a deep neural network for classification', divider='blue')
uploaded_file = st.file_uploader("Upload your DICOM file (.dcm)")

age = st.number_input("Patient age", min_value = 0, max_value = 120, value=60)
sex  = st.selectbox("Patient sex", ["Male", "Female"])

#ECG_image = st.image()

sample_array = {"1dAVb": 13.239485, "RBBB": 0.546861, "LBBB": 0.006619, "SB": 0.052661, "AF": 0.131343, "ST": 0.000431}

st.bar_chart(data=sample_array, color="#e9a56b")
#makes the prediction
if st.button('Submit'):
    # data = predict.make_prediction(path_to_hdf5 = "./automatic_ecg_diagnosis_master/data/ecg_tracings.hdf5", 
                                #    path_to_model = "./automatic_ecg_diagnosis_master/model/model.hdf5")
    data = np.array([0.17332049, 0.00245664, 0.000086,   0.00004635, 0.00205241, 0.00007277])
    st.text(data)
    percent_data = np.round(data * 100.0, 2).astype(np.float16)
    st.text(percent_data)
    result = call_api(age, sex, data)
    st.text(result)
    
    

