import streamlit as st
from agent import app_graph  # <--- Direct import! No requests.post needed

st.set_page_config(page_title="C++ Complexity Analyzer", layout="wide")

st.title("📊 C++ Algorithmic Analyzer")
st.markdown("Parallel Agents: **Time** | **Space** | **Readability**")

# Default Code
default_code = """
#include <iostream>
#include <vector>
using namespace std;

void do_stuff(vector<int> &a) {
    int n = a.size();
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < n-i-1; j++) {
            if(a[j] > a[j+1]) {
                swap(a[j], a[j+1]);
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
        with st.spinner("Analyzing code structure and complexity..."):
            try:
                # --- CHANGED: Run directly instead of calling API ---
                initial_state = {"code": code_input, "reviews": []}
                result = app_graph.invoke(initial_state)
                # ----------------------------------------------------
                
                reviews = result.get("reviews", [])
                final_report = result.get("final_report", "")
                
                # Display Logic
                col1, col2, col3 = st.columns(3)
                
                # Safe search for reviews
                time_rev = next((r for r in reviews if "Time" in r), "Processing...")
                space_rev = next((r for r in reviews if "Space" in r), "Processing...")
                read_rev = next((r for r in reviews if "Readability" in r), "Processing...")

                with col1:
                    st.info("Time Complexity")
                    # Clean up the text for display
                    st.markdown(time_rev.replace("⏱️ **Time Complexity:**", "").strip())
                
                with col2:
                    st.success("Space Complexity")
                    st.markdown(space_rev.replace("💾 **Space Complexity:**", "").strip())

                with col3:
                    st.warning("Readability")
                    st.markdown(read_rev.replace("👀 **Readability:**", "").strip())
                
                st.divider()
                st.subheader("🏆 Final Score & Feedback")
                st.markdown(final_report)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")