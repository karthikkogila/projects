
import pandas as pd
import numpy as np
import matplotlib as plt
import streamlit as st
import tensorflow as tf
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
dict_sex={'Female(0)':0,'Male(1)':1}
dict_cp={'Typical Angina(0)':0,'Atypical Angina(1)':1,'Non-anginal Pain(2)':2,'Asymptomatic(3)':3}
dict_fbs={'Normal Blood Sugar(0)':0,'High Blood Sugar(0)':1}
dict_restecg={'Normal ECG(0)':0,'ST-T Wave Abnormality(1)':1,'Left Ventricular Hypertrophy (LVH)(2)':2}
dict_exang={'No (No Angina During Exercise)(0)':0,'Yes (Angina During Exercise)(1)':1}
dict_slope={'Upsloping(0)':0,'Flat (Horizontal)(1)':1,'Downsloping(2)':2}
dict_ca={'No vessels colored(0)':0,'One vessel colored(1)':1,'Two vessels colored(2)':2,'Three vessels colored(3)':3,'Four vessels colored (rare)(4)':4}
dict_thal={'Normal(1)':1,'Fixed Defect(2)':2,'Reversible Defect(3)':3}
st.title('HEART DESEASE PREDICTION')
age=st.number_input('Enter Age of pationt ',1,150,25,5)
sex=st.selectbox('Gender',list(dict_sex.keys()))
cp=st.selectbox('Type of chest pain',list(dict_cp.keys()))
trestbps=st.number_input('Resting Blood Pressure (in mm Hg)',100,200,step=10)
chol=st.number_input('Serum Cholesterol level (in mg/dl)',100,400,step=10)
fbs=st.selectbox('Fasting Blood Sugar ',list(dict_fbs.keys()))
restecg=st.selectbox('ECG',list(dict_restecg.keys()))
thalach=st.number_input('Max Heart Rate',60,200,step=5)
exang=st.selectbox('Angina During Exercise',list(dict_exang.keys()))
oldpeak=st.number_input('heart’s electrical activity drops during exercise',0.0,6.0,step=0.1)
slope=st.selectbox('Slope of the ST segment during peak exercise (from ECG test)',list(dict_slope.keys()))
ca=st.selectbox('blood vessels are visible and functioning properly',list(dict_ca.keys()))
thal=st.selectbox('Thalassemia test result (blood disorder / oxygen-carrying capacity test)',list(dict_thal.keys()))
if st.button('submit'):
    data=pd.read_csv('heart.csv')
    x=data.drop(columns='target')
    y=data['target']
    col=x.columns
    x=np.array(x,dtype=np.float32)
    y=np.array(y,dtype=np.float32)
    x_train,x_val,y_train,y_val=train_test_split(x,y,test_size=0.2,random_state=42,stratify=y)
    scaler=StandardScaler()
    x_train=scaler.fit_transform(x_train)
    x_val=scaler.transform(x_val)
    x_test=scaler.transform(x_test)
    class_weights = {0: len(y_train[y_train==1])/len(y_train), 1: len(y_train[y_train==0])/len(y_train)}

    tf.random.set_seed(42)
    np.random.seed(42)
    model=tf.keras.Sequential([
        tf.keras.layers.Input(shape=(x_train.shape[1],)),
        tf.keras.layers.Dense(128,activation='relu',kernel_regularizer=tf.keras.regularizers.l2(0.001)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64,activation='relu',kernel_regularizer=tf.keras.regularizers.l2(0.001)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Dense(32,activation='relu',kernel_regularizer=tf.keras.regularizers.l2(0.001)),
        tf.keras.layers.BatchNormalization(),
        
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1,activation='sigmoid')
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        loss = tf.keras.losses.BinaryCrossentropy(label_smoothing=0.05),
        metrics=[tf.keras.metrics.BinaryAccuracy(name='accuracy'),
                tf.keras.metrics.AUC(name='auc'),
                ]
    )
    callbacks = [
        tf.keras.callbacks.EarlyStopping( monitor='val_auc',patience=10,restore_best_weights=True,mode='max'),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_auc',patience=4,factor=0.5,mode='max'),
        tf.keras.callbacks.ModelCheckpoint('best_model.h5', monitor='val_auc', save_best_only=True, mode='max')
    ]
    model.fit(x_train,y_train,epochs=32,batch_size=64,validation_data=(x_val,y_val),callbacks=callbacks,verbose=1,)
    model.load_weights('best_model.h5')  
    y_pred=model.predict(x_test)
    y_pred=(y_pred>0.5).astype(int)
    tr_loss,tr_ac,tr_auc=model.evaluate(x_train,y_train)
    te_loss,te_ac,te_uac=model.evaluate(x_test,y_test)
    accuracy=accuracy_score(y_test,y_pred)
    user = [
        age, dict_sex[sex], dict_cp[cp], trestbps, chol, dict_fbs[fbs],
        dict_restecg[restecg], thalach, dict_exang[exang], oldpeak,
        dict_slope[slope], dict_ca[ca], dict_thal[thal]
    ]
    udf = pd.DataFrame([user], columns=col)
    user_sc = scaler.transform(udf)   
    u_pred = model.predict(user_sc)[0]
    if u_pred == 1:
        st.warning(f'High Risk Of Heart Disease ')
    else:
        st.success(f'Low Risk Of Heart Disease ')
