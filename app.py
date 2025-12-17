import streamlit as st
import requests

st.set_page_config(page_title="C++ Complexity Analyzer", layout="wide")

st.title("📊 C++ Algorithmic Analyzer")
st.markdown("Parallel Agents: **Time** | **Space** | **Readability**")

# Default Code: O(n^2) Bubble Sort (Bad Performance)
default_code = """
#include <iostream>
#include <vector>
using namespace std;

// Function to sort data
void do_stuff(vector<int> &a) {
    int n = a.size();
    // Nested loops = O(n^2)
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < n-i-1; j++) {
            if(a[j] > a[j+1]) {
                int temp = a[j];
                a[j] = a[j+1];
                a[j+1] = temp;
            }
        }
    }
}
"""

code_input = st.text_area("Paste C++ Code:", height=300, value=default_code)

if st.button("Calculate Complexity & Score"):
    if not code_input:
        st.warning("Please enter some code.")
    else:
        with st.spinner("Calculating Big-O Notation and Readability..."):
            try:
                response = requests.post(
                    "http://localhost:8000/evaluate", 
                    json={"code": code_input}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reviews = data.get("reviews", [])
                    
                    # Create columns for metrics
                    col1, col2, col3 = st.columns(3)
                    
                    # Sort reviews into columns based on keywords
                    time_rev = next((r for r in reviews if "Time" in r), "Processing...")
                    space_rev = next((r for r in reviews if "Space" in r), "Processing...")
                    read_rev = next((r for r in reviews if "Readability" in r), "Processing...")

                    with col1:
                        st.info("Time Complexity")
                        st.markdown(time_rev.replace("⏱️ **Time Complexity:**", "").strip())
                    
                    with col2:
                        st.success("Space Complexity")
                        st.markdown(space_rev.replace("💾 **Space Complexity:**", "").strip())

                    with col3:
                        st.warning("Readability")
                        st.markdown(read_rev.replace("👀 **Readability:**", "").strip())
                    
                    st.divider()
                    st.subheader("🏆 Final Score & Feedback")
                    st.markdown(data.get("final_report"))
                    
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Backend offline. Please run 'python api.py'")