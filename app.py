import streamlit as st
import pandas as pd

# Page title
st.title("Bank Customer Churn Analysis")

try:
    # Load data
    df = pd.read_csv("Churn_Modelling.csv")

    # Convert nullable dtypes to standard dtypes for Streamlit compatibility
    for col in df.columns:
        if str(df[col].dtype) in ['Int64', 'Float64']:
            df[col] = df[col].astype(str(df[col].dtype).lower())

    # Tabs
    tab1, tab2, tab3 = st.tabs(
        ["Dashboard", "Prediction Model", "Business Insights"]
    )

    # ===================== DASHBOARD TAB =====================
    with tab1:

        st.header("Customer Churn Dashboard")

        # Dataset preview
        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        # Dataset info
        st.subheader("Dataset Info")
        st.write("Shape:", df.shape)
        st.write("Data Types:")
        st.write(df.dtypes)
        st.write("Missing Values:")
        st.write(df.isnull().sum())

        # KPIs
        st.subheader("Key Metrics")

        col1, col2, col3 = st.columns(3)

        total_customers = len(df)
        churned = df['Exited'].sum()
        churn_rate = churned / total_customers * 100

        col1.metric("Total Customers", total_customers)
        col2.metric("Churned Customers", churned)
        col3.metric("Churn Rate (%)", round(churn_rate, 2))

        # Activity churn
        st.subheader("Churn by Activity Status")
        activity_churn = df.groupby('IsActiveMember')['Exited'].mean() * 100
        st.bar_chart(activity_churn)

        # Products churn
        st.subheader("Churn by Number of Products")
        products_churn = df.groupby('NumOfProducts')['Exited'].mean() * 100
        st.bar_chart(products_churn)

        # Geography churn
        st.subheader("Churn by Geography")
        geo_churn = df.groupby('Geography')['Exited'].mean() * 100
        st.bar_chart(geo_churn)

        # Balance segmentation
        st.subheader("Churn by Balance Segment")
        df['BalanceGroup'] = pd.qcut(df['Balance'], 4, duplicates='drop').astype(str)
        balance_churn = df.groupby('BalanceGroup')['Exited'].mean() * 100
        st.bar_chart(balance_churn)

    # ===================== ML TAB =====================
    with tab2:

        st.header("Churn Prediction Model")

        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

        # Prepare data
        model_df = df.copy()
        model_df = model_df.drop(['RowNumber', 'CustomerId', 'Surname'], axis=1)
        model_df = pd.get_dummies(model_df, drop_first=True)

        X = model_df.drop('Exited', axis=1)
        y = model_df['Exited']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        # Balanced RandomForest
        model = RandomForestClassifier(
            n_estimators=200,
            class_weight='balanced',
            random_state=42
        )

        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, preds)
        roc_score = roc_auc_score(y_test, probs)

        col1, col2 = st.columns(2)
        col1.metric("Accuracy (%)", round(accuracy * 100, 2))
        col2.metric("ROC-AUC", round(roc_score, 3))

        st.subheader("Classification Report")

        report_dict = classification_report(y_test, preds, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose()

        st.dataframe(report_df.style.format("{:.2f}"))

        # Feature importance
        st.subheader("Top Churn Drivers")

        importance_df = pd.DataFrame({
            "Feature": X.columns,
            "Importance": model.feature_importances_
        }).sort_values(by="Importance", ascending=False).head(10)

        st.bar_chart(importance_df.set_index("Feature"))

        st.divider()
        st.subheader("Predict Customer Churn")

        st.write("Enter customer details to predict churn probability.")

        # ---------- User Inputs ----------
        credit_score = st.slider("Credit Score", 300, 900, 650)
        age = st.slider("Age", 18, 80, 40)
        tenure = st.slider("Tenure (Years)", 0, 10, 3)
        balance = st.number_input("Balance", value=50000.0)
        num_products = st.selectbox("Number of Products", [1,2,3,4])
        has_card = st.selectbox("Has Credit Card", [0,1])
        active_member = st.selectbox("Active Member", [0,1])
        salary = st.number_input("Estimated Salary", value=50000.0)
        
        geography = st.selectbox("Geography", ["France", "Germany", "Spain"])
        gender = st.selectbox("Gender", ["Male", "Female"])

        # ---------- Prepare Input ----------
        input_dict = {
            "CreditScore": credit_score,
            "Age": age,
            "Tenure": tenure,
            "Balance": balance,
            "NumOfProducts": num_products,
            "HasCrCard": has_card,
            "IsActiveMember": active_member,
            "EstimatedSalary": salary
        }

        input_df = pd.DataFrame([input_dict])
        
        # Dummy encode same way
        input_df = pd.get_dummies(input_df)
        
        # Align columns with training data
        input_df = input_df.reindex(columns=X.columns, fill_value=0)
        
        # ---------- Prediction ----------
        if st.button("Predict Churn"):

            # Predict probability (NOT class)
            prob = model.predict_proba(input_df)[0][1]
        
            st.subheader("Prediction Result")
        
            st.progress(float(prob))
        
            if prob >= 0.7:
                st.error(f"High churn risk ({prob:.2%})")
            elif prob >= 0.4:
                st.warning(f"Moderate churn risk ({prob:.2%})")
            else:
                st.success(f"Low churn risk ({prob:.2%})")


             

        
# ===================== INSIGHTS TAB =====================
    with tab3:
     st.header("📊 Business Insights & Recommendations")

     st.subheader("🔎 Key Churn Drivers")

     st.info("""
     • Older customers show slightly higher churn probability.
     • Inactive members churn nearly 2× more than active customers.
     • Customers with 1 product churn more — weak engagement.
     • Very high balance doesn't guarantee retention.
     • Germany region shows highest churn risk.
     """)     
     st.subheader("📉 Risk Segments Identified")     
     st.warning("""
     HIGH RISK:
     - Non-active members
     - Customers with only 1 product
     - Mid credit score customers     
     MODERATE RISK:
     - Older age group
     - Medium balance customers
     """)     
     st.subheader("💡 Business Recommendations")     
     st.success("""
     1. Improve customer engagement programs.
     2. Cross-sell carefully (avoid product overload).
     3. Target Germany region with retention offers.
     4. Focus loyalty benefits on inactive customers.
     5. Early churn alerts using prediction model.
     """)     
     st.subheader("🧠 Model Insight Summary")     
     st.write("""
     The ML model indicates Age, Balance, Credit Score,
     and Activity Status as the strongest churn predictors.
     This supports targeted retention strategies.
     """)

except FileNotFoundError:
    st.error("Dataset file not found. Check CSV location.")
