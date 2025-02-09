import streamlit as st


def main():

    # sidebar
    page_get_data = st.Page("sidebar/page_get_data.py", title="Data", icon=":material/build:")    

    pg = st.navigation(
        {
            "대시보드": [
                page_get_data
            ]
        }
    )

    st.set_page_config(page_title="EZ 네이버 부동산", page_icon="🪙")
    pg.run()

    # Sidebar width
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                width: 150px !important; # Set the width to your desired value
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()