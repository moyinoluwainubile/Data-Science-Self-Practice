
import requests
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth

st.set_page_config(
    page_title="Inventory Tracker",
    page_icon="📦",
    layout="centered",
)

API_KEY = st.secrets["firebase_web_api_key"]
AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"
REFRESH_URL = "https://securetoken.googleapis.com/v1/token"


@st.cache_resource
def get_database():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            dict(st.secrets["gcp_service_account"])
        )
        firebase_admin.initialize_app(cred)

    return firestore.client()


db = get_database()


def firebase_auth(action, payload):
    response = requests.post(
        f"{AUTH_URL}:{action}?key={API_KEY}",
        json=payload,
        timeout=20,
    )
    data = response.json()

    if not response.ok:
        message = data.get("error", {}).get(
            "message", "Authentication failed."
        )
        raise ValueError(message)

    return data


def save_login(data):
    st.session_state["id_token"] = data["idToken"]
    st.session_state["refresh_token"] = data["refreshToken"]
    st.session_state["user_email"] = data.get("email", "")


def logout():
    for key in ("id_token", "refresh_token", "user_email", "user_uid"):
        st.session_state.pop(key, None)


def get_user_uid():
    token = st.session_state.get("id_token")
    if not token:
        return None

    try:
        decoded = auth.verify_id_token(token)
        st.session_state["user_uid"] = decoded["uid"]
        return decoded["uid"]

    except Exception:
        # Attempt to refresh an expired ID token.
        refresh_token = st.session_state.get("refresh_token")
        if not refresh_token:
            logout()
            return None

        try:
            response = requests.post(
                REFRESH_URL,
                params={"key": API_KEY},
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                timeout=20,
            )
            data = response.json()

            if not response.ok:
                logout()
                return None

            st.session_state["id_token"] = data["id_token"]
            st.session_state["refresh_token"] = data.get(
                "refresh_token", refresh_token
            )

            decoded = auth.verify_id_token(data["id_token"])
            st.session_state["user_uid"] = decoded["uid"]
            return decoded["uid"]

        except Exception:
            logout()
            return None


def show_auth_screen():
    st.title("📦 Inventory Tracker")
    st.write("Sign in or create an account to manage your private inventory.")

    login_tab, signup_tab = st.tabs(["Sign in", "Create account"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted:
            try:
                data = firebase_auth(
                    "signInWithPassword",
                    {
                        "email": email.strip(),
                        "password": password,
                        "returnSecureToken": True,
                    },
                )
                save_login(data)
                st.rerun()
            except ValueError as e:
                st.error(f"Sign-in failed: {e}")
            except requests.RequestException:
                st.error("Could not reach Firebase. Please try again.")

    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("Email address", key="signup_email")
            password = st.text_input(
                "Password (at least 6 characters)",
                type="password",
                key="signup_password",
            )
            confirm = st.text_input(
                "Confirm password", type="password"
            )
            submitted = st.form_submit_button(
                "Create account", use_container_width=True
            )

        if submitted:
            if password != confirm:
                st.error("The passwords do not match.")
            elif len(password) < 6:
                st.error("Use a password with at least 6 characters.")
            else:
                try:
                    data = firebase_auth(
                        "signUp",
                        {
                            "email": email.strip(),
                            "password": password,
                            "returnSecureToken": True,
                        },
                    )
                    save_login(data)
                    st.rerun()
                except ValueError as e:
                    st.error(f"Account creation failed: {e}")
                except requests.RequestException:
                    st.error("Could not reach Firebase. Please try again.")


uid = get_user_uid()

if not uid:
    show_auth_screen()
    st.stop()


# Each authenticated user gets a separate Firestore subcollection.
inventory_collection = (
    db.collection("users")
    .document(uid)
    .collection("inventory_items")
)


def load_inventory():
    return {
        document.id: document.to_dict()
        for document in inventory_collection.stream()
    }



st.title("📦 Inventory Tracker")
st.caption(f"Signed in as {st.session_state.get('user_email', '')}")

if st.sidebar.button("Sign out"):
    logout()
    st.rerun()

page = st.sidebar.radio(
    "Inventory Menu",
    [
        "Add Inventory",
        "Update Inventory",
        "Remove Inventory",
        "Show All Inventories",
    ],
)

inventory_collection = (
    db.collection("users")
    .document(uid)
    .collection("inventory_items")
)

inventories = load_inventory()

if page == "Add Inventory":
    st.subheader("Add Inventory")

    with st.form("add_inventory_form"):
        inventory_id = st.text_input("Inventory name or ID").strip().lower()
        quantity = st.number_input("Quantity", min_value=0, step=1)
        price = st.number_input("Price per item", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Add inventory")

    if submitted:
        if not inventory_id:
            st.error("Enter an inventory name or ID.")
        elif inventory_id in inventories:
            st.error("This item already exists in your inventory.")
        else:
            inventory_collection.document(inventory_id).set({
                "quantity": int(quantity),
                "price": float(price),
            })
            st.success("Inventory added.")
            st.rerun()

elif page == "Update Inventory":
    st.subheader("Update Inventory")

    if inventories:
        selected = st.selectbox(
            "Choose an item to update",
            list(inventories),
        )

        update_type = st.radio(
            "What do you want to update?",
            ["Quantity", "Price"],
            horizontal=True,
        )

        if update_type == "Quantity":
            new_value = st.number_input(
                "New quantity",
                min_value=0,
                step=1,
                value=int(inventories[selected].get("quantity", 0)),
            )
            field = "quantity"
            value = int(new_value)
        else:
            new_value = st.number_input(
                "New price",
                min_value=0.0,
                step=0.01,
                value=float(inventories[selected].get("price", 0.0)),
            )
            field = "price"
            value = float(new_value)

        if st.button("Save update"):
            inventory_collection.document(selected).update({field: value})
            st.success("Inventory updated.")
            st.rerun()
    else:
        st.info("Your inventory is empty.")

elif page == "Remove Inventory":
    st.subheader("Remove Inventory")

    if inventories:
        remove_id = st.selectbox(
            "Choose an item to remove",
            list(inventories),
        )

        if st.button("Remove item"):
            inventory_collection.document(remove_id).delete()
            st.success("Inventory item removed.")
            st.rerun()
    else:
        st.info("Your inventory is empty.")

elif page == "Show All Inventories":
    st.subheader("Show All Inventories")

    if inventories:
        rows = [
            {
                "Inventory ID": item_id,
                "Quantity": details.get("quantity", 0),
                "Price": details.get("price", 0.0),
                "Total Value": (
                    details.get("quantity", 0)
                    * details.get("price", 0.0)
                ),
            }
            for item_id, details in inventories.items()
        ]

        st.dataframe(rows, use_container_width=True)

        total_value = sum(row["Total Value"] for row in rows)
        st.metric("Total Inventory Value", f"{total_value:,.2f}")

        low_stock = [
            row["Inventory ID"]
            for row in rows
            if row["Quantity"] < 5
        ]

        if low_stock:
            st.warning("Low stock: " + ", ".join(low_stock))
    else:
        st.info("Your inventory is empty.")
