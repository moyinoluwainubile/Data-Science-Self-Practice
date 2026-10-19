
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Page setup
st.set_page_config(
    page_title="Inventory Tracker",
    page_icon="📦",
    layout="centered",
)

# Connect to Firebase
@st.cache_resource
def get_database():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            dict(st.secrets["gcp_service_account"])
        )
        firebase_admin.initialize_app(cred)

    return firestore.client()


try:
    db = get_database()
    inventory_collection = db.collection("inventory_items")
except Exception as e:
    st.error("Could not connect to Firebase. Check your app Secrets.")
    st.exception(e)
    st.stop()


# Load inventory from Firestore
def load_inventory():
    items = {}
    for document in inventory_collection.stream():
        items[document.id] = document.to_dict()
    return items


inventories = load_inventory()

st.title("📦 Inventory Tracker")
st.write("Add, remove, update, and monitor your inventory.")

# Navigation menu
menu = st.sidebar.selectbox(
    "Inventory Menu",
    [
        "Add Inventory",
        "Remove Inventory",
        "Update Inventory",
        "Show All Inventories",
    ],
)


# 1. Add inventory
if menu == "Add Inventory":
    st.header("Add Inventory")

    with st.form("add_inventory_form"):
        inventory_id = st.text_input("Inventory ID").strip().lower()
        quantity = st.number_input(
            "Inventory Quantity", min_value=0, step=1
        )
        price = st.number_input(
            "Inventory Price",
            min_value=0.0,
            step=0.01,
            format="%.2f",
        )

        submitted = st.form_submit_button("Add Inventory")

        if submitted:
            if not inventory_id:
                st.error("Please enter an Inventory ID.")
            elif inventory_id in inventories:
                st.warning(
                    "This Inventory ID already exists. "
                    "Use Update Inventory to change its details."
                )
            else:
                inventory_collection.document(inventory_id).set(
                    {
                        "quantity": int(quantity),
                        "price": float(price),
                    }
                )
                st.success(f"{inventory_id} added successfully!")
                st.rerun()


# 2. Remove inventory
elif menu == "Remove Inventory":
    st.header("Remove Inventory")

    if not inventories:
        st.info("Your inventory is empty. Please add inventory first.")
    else:
        inventory_id = st.selectbox(
            "Select inventory to remove",
            list(inventories.keys()),
        )

        if st.button("Remove Inventory", type="primary"):
            inventory_collection.document(inventory_id).delete()
            st.success(f"{inventory_id} removed successfully!")
            st.rerun()


# 3. Update inventory
elif menu == "Update Inventory":
    st.header("Update Inventory")

    if not inventories:
        st.info("Your inventory is empty. Please add inventory first.")
    else:
        inventory_id = st.selectbox(
            "Select inventory to update",
            list(inventories.keys()),
        )

        current_item = inventories[inventory_id]

        st.write(f"Current quantity: {current_item['quantity']}")
        st.write(f"Current price: {current_item['price']:.2f}")

        update_type = st.radio(
            "What would you like to update?",
            ["Quantity", "Price"],
        )

        if update_type == "Quantity":
            new_quantity = st.number_input(
                "Enter new quantity",
                min_value=0,
                value=int(current_item["quantity"]),
                step=1,
                key="update_quantity",
            )

            if st.button("Update Quantity"):
                inventory_collection.document(inventory_id).update(
                    {"quantity": int(new_quantity)}
                )
                st.success("Quantity updated successfully!")
                st.rerun()

        else:
            new_price = st.number_input(
                "Enter new price",
                min_value=0.0,
                value=float(current_item["price"]),
                step=0.01,
                format="%.2f",
                key="update_price",
            )

            if st.button("Update Price"):
                inventory_collection.document(inventory_id).update(
                    {"price": float(new_price)}
                )
                st.success("Price updated successfully!")
                st.rerun()


# 4. Show all inventory
elif menu == "Show All Inventories":
    st.header("All Inventories")

    if not inventories:
        st.info("Your inventory is empty. Please add inventory first.")
    else:
        total_inventories_value = 0
        inventory_rows = []

        for inventory_id, inventory in inventories.items():
            quantity = int(inventory["quantity"])
            price = float(inventory["price"])
            item_value = quantity * price
            total_inventories_value += item_value

            inventory_rows.append(
                {
                    "Inventory ID": inventory_id,
                    "Quantity": quantity,
                    "Price": price,
                    "Total Item Value": item_value,
                    "Stock Status": (
                        "⚠️ Low Stock" if quantity < 5 else "In Stock"
                    ),
                }
            )

        st.dataframe(inventory_rows, use_container_width=True)

        st.metric(
            "Total Inventory Value",
            f"{total_inventories_value:,.2f}",
        )

        low_stock_items = [
            inventory_id
            for inventory_id, inventory in inventories.items()
            if int(inventory["quantity"]) < 5
        ]

        if low_stock_items:
            st.warning("Low-stock warning: Fewer than 5 items remain.")

            for inventory_id in low_stock_items:
                st.write(
                    f"- **{inventory_id}**: "
                    f"{inventories[inventory_id]['quantity']} left"
                )
        else:
            st.success("No low-stock items.")
