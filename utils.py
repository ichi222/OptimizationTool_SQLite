import matplotlib.pyplot as plt
import streamlit as st

def plot_cost_vs_safety(costs, safety_margins):
    plt.figure()
    plt.plot(safety_margins, costs, marker='o')
    plt.xlabel("Safety Margin")
    plt.ylabel("Cost")
    plt.title("Cost vs Safety Margin")
    st.pyplot(plt)

def export_results(result_df):
    st.download_button(
        label="結果をCSVでダウンロード",
        data=result_df.to_csv(index=False),
        file_name="optimization_result.csv",
        mime="text/csv",
    )
