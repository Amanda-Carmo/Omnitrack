
import streamlit as st
from streamlit_option_menu import option_menu

async def build_interface():

    selected = option_menu(
        menu_title = None,
        options = ['Home', 'Apps', 'Messages'],
        icons = ['home', 'apps', 'message'],
        menu_icon = 'menu',
        default_index = 0,
        orientation = 'horizontal',
    )

    if selected == 'Home':
        st.title("Omnitrack Interface")
        st.write("This is the interface for Omnitrack.")

    if selected == 'Apps':
        st.title("Your Apps")

    if selected == 'Messages':
        st.title("Choose a message")
        msg1 = st.button("Call caregiver")
        msg2 = st.button("Message caregiver")
        msg3 = st.button("Call doctor")

        st.write(msg1, msg2, msg3)

        if msg1:
            st.write("Calling caregiver...")
        if msg2:
            st.write("Messaging caregiver...")
        if msg3:
            st.write("Calling doctor...")


#     return

# build_interface()
