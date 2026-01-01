import streamlit as st
import datetime
from fpdf import FPDF
import os
import json
import urllib.parse
import hashlib

# ========================
# ONE-PAGE WORKER APP
# ========================

st.set_page_config(
    page_title="AutoInvoice Pro - Car Repair Billing",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Modern Styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }

    /* Title styling */
    .main-title {
        text-align: center;
        color: #2E4057;
        padding-bottom: 1rem;
        border-bottom: 3px solid #FF6B35;
        margin-bottom: 2rem !important;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Card styling */
    .invoice-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }

    .invoice-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }

    /* Profile card */
    .profile-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* Input field styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }

    /* WhatsApp button */
    .whatsapp-btn {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100%;
        text-align: center;
        text-decoration: none;
        display: block;
        transition: all 0.3s ease;
    }

    .whatsapp-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
        color: white !important;
        text-decoration: none !important;
    }

    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        background: #FF6B35;
        color: white;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }

    /* Section headers */
    .section-header {
        color: #2E4057;
        border-left: 4px solid #FF6B35;
        padding-left: 12px;
        margin: 1.5rem 0 1rem 0;
    }

    /* Item table */
    .item-row {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border-left: 3px solid #667eea;
    }

    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Warning/Info box */
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ========================
# USER ID MANAGEMENT (For Multi-User Support)
# ========================

def get_user_id():
    """
    Get unique user identifier for data separation
    Uses Streamlit's session ID to create unique user folders
    """
    try:
        # Get session ID from Streamlit context
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx and hasattr(ctx, 'session_id'):
            session_id = ctx.session_id
            # Create a short hash from session ID
            user_hash = hashlib.md5(session_id.encode()).hexdigest()[:8]
            return f"user_{user_hash}"
    except:
        pass

    # Fallback for testing or when session ID is not available
    return "default_user"


# Get current user ID
USER_ID = get_user_id()


# ========================
# USER PROFILE MANAGEMENT
# ========================

def get_user_profile_dir():
    """Get user-specific profile directory"""
    profile_dir = f"profiles/users/{USER_ID}"
    os.makedirs(profile_dir, exist_ok=True)
    return profile_dir


def get_default_profile():
    """Get default profile settings"""
    return {
        'workshop_name': 'Auto Care Workshop',
        'phone_number': '+92-300-1234567',
        'address': 'Main Road, Karachi',
        'email': '',
        'website': '',
        'owner_name': 'Your Name',
        'tax_rate': 0,
        'currency': 'PKR'
    }


def load_user_profile():
    """Load user profile from file"""
    profile_dir = get_user_profile_dir()
    profile_file = f"{profile_dir}/profile.json"

    if os.path.exists(profile_file):
        try:
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
                # Merge with defaults for any missing fields
                default_profile = get_default_profile()
                return {**default_profile, **profile_data}
        except:
            pass

    # Return default profile if no file exists
    return get_default_profile()


def save_user_profile(profile_data):
    """Save user profile to file"""
    profile_dir = get_user_profile_dir()
    profile_file = f"{profile_dir}/profile.json"

    with open(profile_file, 'w') as f:
        json.dump(profile_data, f, indent=2)

    return True


# Load user profile
USER_PROFILE = load_user_profile()


# ========================
# DATA MANAGEMENT FUNCTIONS (User-Specific)
# ========================

def get_user_data_dir():
    """Get user-specific data directory"""
    user_dir = f"data/users/{USER_ID}"
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def get_user_invoices_dir():
    """Get user-specific invoices directory"""
    invoices_dir = f"invoices/users/{USER_ID}"
    os.makedirs(invoices_dir, exist_ok=True)
    return invoices_dir


def save_invoice_data(invoice_data):
    """Save invoice data to JSON file for statistics (User-specific)"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    user_data_dir = get_user_data_dir()
    data_file = f"{user_data_dir}/invoices_{today}.json"

    # Load existing data or create new
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except:
            data = []
    else:
        data = []

    # Add new invoice
    data.append(invoice_data)

    # Save back to file
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

    return True


def get_today_statistics():
    """Calculate today's statistics from saved invoices"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    user_data_dir = get_user_data_dir()
    data_file = f"{user_data_dir}/invoices_{today}.json"

    # Default statistics
    stats = {
        'invoices_today': 0,
        'earnings_today': 0,
        'total_sales_today': 0,
        'average_invoice': 0,
        'items_sold': 0,
        'recent_invoices': [],
        'total_labor': 0,
        'user_id': USER_ID
    }

    if not os.path.exists(data_file):
        return stats

    try:
        with open(data_file, 'r') as f:
            invoices = json.load(f)

        if not invoices or not isinstance(invoices, list):
            return stats

        # Calculate statistics
        total_sales = 0
        total_items = 0
        total_labor_earnings = 0

        for inv in invoices:
            if isinstance(inv, dict):
                total_sales += inv.get('grand_total', 0)
                total_labor_earnings += inv.get('labor', 0)
                total_items += len(inv.get('items', []))

        invoice_count = len(invoices)
        average_invoice = total_sales / invoice_count if invoice_count > 0 else 0

        # Get recent invoices (last 5)
        recent_invoices = invoices[-5:] if invoices else []

        stats.update({
            'invoices_today': invoice_count,
            'earnings_today': total_labor_earnings,
            'total_sales_today': total_sales,
            'average_invoice': average_invoice,
            'items_sold': total_items,
            'recent_invoices': recent_invoices,
            'total_labor': total_labor_earnings
        })

        return stats

    except Exception as e:
        print(f"Error reading statistics for user {USER_ID}: {e}")
        return stats


def get_all_time_statistics():
    """Get statistics from all time data"""
    user_data_dir = get_user_data_dir()

    stats = {
        'total_invoices': 0,
        'total_earnings': 0,
        'total_sales': 0,
        'days_active': 0,
        'average_daily': 0,
        'user_id': USER_ID
    }

    if not os.path.exists(user_data_dir):
        return stats

    try:
        invoice_files = []

        # Get all invoice files for this user
        for file in os.listdir(user_data_dir):
            if file.startswith("invoices_") and file.endswith(".json"):
                invoice_files.append(file)

                try:
                    with open(os.path.join(user_data_dir, file), 'r') as f:
                        invoices = json.load(f)
                        if isinstance(invoices, list):
                            stats['total_invoices'] += len(invoices)
                            for inv in invoices:
                                if isinstance(inv, dict):
                                    stats['total_sales'] += inv.get('grand_total', 0)
                                    stats['total_earnings'] += inv.get('labor', 0)
                except:
                    pass

        stats['days_active'] = len(invoice_files)
        stats['average_daily'] = stats['total_earnings'] / stats['days_active'] if stats['days_active'] > 0 else 0

        return stats

    except Exception as e:
        print(f"Error reading all-time stats for user {USER_ID}: {e}")
        return stats


def get_user_invoice_counter():
    """Get user-specific invoice counter"""
    user_data_dir = get_user_data_dir()
    counter_file = f"{user_data_dir}/invoice_counter.json"

    if os.path.exists(counter_file):
        try:
            with open(counter_file, 'r') as f:
                data = json.load(f)
                return data.get('counter', 1000)
        except:
            pass

    # If no counter exists, start from 1000 + total invoices
    all_stats = get_all_time_statistics()
    return 1000 + all_stats['total_invoices']


def save_user_invoice_counter(counter_value):
    """Save user-specific invoice counter"""
    user_data_dir = get_user_data_dir()
    counter_file = f"{user_data_dir}/invoice_counter.json"

    with open(counter_file, 'w') as f:
        json.dump({'counter': counter_value}, f, indent=2)


def create_whatsapp_message(invoice_data):
    """Create WhatsApp message template"""
    customer = invoice_data['customer_name']
    car = invoice_data['car_details']
    invoice_num = invoice_data['invoice_number']
    total = invoice_data['grand_total']
    date = datetime.datetime.now().strftime("%d/%m/%Y")

    message = f"""*Assalam-o-Alaikum!* 

🚗 *Car Repair Invoice - {USER_PROFILE['workshop_name']}*
────────────────────────────
*Customer:* {customer}
*Car Details:* {car}
*Invoice #:* {invoice_num}
*Date:* {date}
*Total Amount:* {USER_PROFILE['currency']} {total:,}

📄 Invoice PDF is attached.

Thank you for choosing {USER_PROFILE['workshop_name']}!"""

    return urllib.parse.quote(message)


# ========================
# INITIALIZE SESSION STATE
# ========================

# Initialize with default values
defaults = {
    'repair_items': [],
    'customer_name': "",
    'car_details': "",
    'labor': 1500,
    'discount': 0,
    'last_invoice_path': None,
    'last_invoice_data': None,
    'show_profile_edit': False,
    'new_desc': "",  # FIX: Store new item description separately
    'new_qty': 1,  # FIX: Store new item quantity
    'new_price': 1000,  # FIX: Store new item price
}

for key, default_value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Initialize user-specific invoice counter
if 'invoice_counter' not in st.session_state:
    st.session_state.invoice_counter = get_user_invoice_counter()

# ========================
# MAIN APP LAYOUT
# ========================

# Main title with professional design
st.markdown("""
<div class="main-title">
    <h1 style="margin-bottom: 0.5rem;">🚗 AutoInvoice Pro</h1>
    <p style="color: #666; font-size: 1.1rem; margin-top: 0;">Professional Car Repair Billing System</p>
</div>
""", unsafe_allow_html=True)

# Quick Stats Bar
today_stats = get_today_statistics()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Invoices Today", today_stats['invoices_today'])
with col2:
    st.metric("💰 Earnings", f"Rs {today_stats['earnings_today']:,}")
with col3:
    st.metric("📈 Total Sales", f"Rs {today_stats['total_sales_today']:,}")
with col4:
    st.metric("🛠️ Items Sold", today_stats['items_sold'])

st.markdown("---")

# 1. QUICK ACTIONS SECTION
st.markdown('<h3 class="section-header">Quick Actions</h3>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🆕 **New Invoice**", use_container_width=True, type="primary"):
        st.session_state.repair_items = []
        st.session_state.customer_name = ""
        st.session_state.car_details = ""
        st.session_state.new_desc = ""
        st.rerun()

with col2:
    if st.button("📋 **Recent Jobs**", use_container_width=True):
        st.info(f"Showing last {len(today_stats['recent_invoices'])} invoices")

with col3:
    if st.button("⚙️ **Settings**", use_container_width=True):
        st.session_state.show_profile_edit = True
        st.rerun()

with col4:
    if st.button("🧹 **Clear All**", use_container_width=True):
        st.session_state.repair_items = []
        st.session_state.customer_name = ""
        st.session_state.car_details = ""
        st.session_state.labor = 1500
        st.session_state.discount = 0
        st.session_state.new_desc = ""
        st.success("All fields cleared!")
        st.rerun()

st.markdown("---")

# 2. CUSTOMER & CAR INFO
st.markdown('<h3 class="section-header">Customer & Vehicle Details</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    customer_name = st.text_input(
        "**Customer Name**",
        value=st.session_state.customer_name,
        placeholder="Enter customer name...",
        key="customer_input"
    )
    st.session_state.customer_name = customer_name

with col2:
    car_details = st.text_input(
        "**Vehicle Details**",
        value=st.session_state.car_details,
        placeholder="e.g., Toyota Corolla 2018, White, ABC-123",
        key="car_input"
    )
    st.session_state.car_details = car_details

st.markdown("---")

# 3. REPAIR ITEMS SECTION (FIXED VERSION)
st.markdown('<h3 class="section-header">Repair Items & Services</h3>', unsafe_allow_html=True)

# Display current items in a nice card
if st.session_state.repair_items:
    st.markdown("### 📦 Current Items")
    for i, item in enumerate(st.session_state.repair_items):
        with st.container():
            cols = st.columns([3, 1, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{item['desc']}**")
            with cols[1]:
                st.markdown(f"`Qty: {item['qty']}`")
            with cols[2]:
                st.markdown(f"`Price: Rs {item['price']:,}`")
            with cols[3]:
                st.markdown(f"`Total: Rs {item['total']:,}`")
            with cols[4]:
                if st.button("🗑️", key=f"remove_{i}", help="Remove item"):
                    st.session_state.repair_items.pop(i)
                    st.rerun()
            st.divider()

# Add new item - FIXED: Clear inputs after adding
st.markdown("### ➕ Add New Item")

col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    new_desc = st.text_input(
        "Description",
        value=st.session_state.new_desc,  # FIX: Use session state
        placeholder="e.g., Brake pads replacement, AC repair...",
        label_visibility="collapsed",
        key="item_desc_input"
    )

with col2:
    new_qty = st.number_input(
        "Quantity",
        min_value=1,
        value=st.session_state.new_qty,
        label_visibility="collapsed",
        key="item_qty_input"
    )

with col3:
    new_price = st.number_input(
        "Price (Rs)",
        min_value=0,
        value=st.session_state.new_price,
        step=100,
        label_visibility="collapsed",
        key="item_price_input"
    )

with col4:
    st.write("")  # Spacing
    st.write("")
    if st.button("➕ **Add Item**", use_container_width=True, key="add_item_btn"):
        if new_desc.strip():
            st.session_state.repair_items.append({
                'desc': new_desc.strip(),
                'qty': int(new_qty),
                'price': float(new_price),
                'total': float(new_qty) * float(new_price)
            })
            # FIX: Clear the input fields
            st.session_state.new_desc = ""
            st.session_state.new_qty = 1
            st.session_state.new_price = 1000
            st.rerun()
        else:
            st.warning("Please enter item description")

st.markdown("---")

# 4. CALCULATIONS SECTION
st.markdown('<h3 class="section-header">Invoice Calculation</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.session_state.labor = st.number_input(
        "**Labor Charges (Rs)**",
        value=st.session_state.labor,
        min_value=0,
        step=500,
        help="Your service charges"
    )

with col2:
    st.session_state.discount = st.number_input(
        "**Discount (Rs)**",
        value=st.session_state.discount,
        min_value=0,
        step=100,
        help="Any discount for customer"
    )

# Calculate and display totals
if st.session_state.repair_items:
    subtotal = sum(item['total'] for item in st.session_state.repair_items)
    total = subtotal + st.session_state.labor - st.session_state.discount

    st.markdown("""
    <div class="invoice-card">
        <h4 style="color: #2E4057; margin-bottom: 1rem;">Invoice Summary</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
            <div><strong>Parts Total:</strong></div>
            <div style="text-align: right;">Rs {:,}</div>
            <div><strong>Labor Charges:</strong></div>
            <div style="text-align: right;">Rs {:,}</div>
            <div><strong>Discount:</strong></div>
            <div style="text-align: right; color: #d32f2f;">- Rs {:,}</div>
            <div style="border-top: 2px solid #E0E0E0; padding-top: 0.5rem; font-size: 1.2em;"><strong>GRAND TOTAL:</strong></div>
            <div style="border-top: 2px solid #E0E0E0; padding-top: 0.5rem; text-align: right; font-size: 1.2em; color: #FF6B35; font-weight: bold;">Rs {:,}</div>
        </div>
    </div>
    """.format(subtotal, st.session_state.labor, st.session_state.discount, total), unsafe_allow_html=True)
else:
    st.info("ℹ️ Add repair items above to see invoice calculation")

st.markdown("---")

# 5. GENERATE INVOICE SECTION
st.markdown('<h3 class="section-header">Generate Invoice</h3>', unsafe_allow_html=True)

# Validation checks
has_items = len(st.session_state.repair_items) > 0
has_customer = st.session_state.customer_name.strip() != ""
has_car = st.session_state.car_details.strip() != ""

if not has_items:
    st.warning("Please add at least one repair item")
if not has_customer:
    st.warning("Please enter customer name")
if not has_car:
    st.warning("Please enter vehicle details")

generate_col1, generate_col2 = st.columns([2, 1])

with generate_col1:
    if st.button(
            "📄 **GENERATE INVOICE PDF**",
            type="primary",
            use_container_width=True,
            disabled=not (has_items and has_customer and has_car),
            key="generate_main_btn"
    ):
        # Calculate totals
        subtotal = sum(item['total'] for item in st.session_state.repair_items)
        total = subtotal + st.session_state.labor - st.session_state.discount

        try:
            # Create invoice data
            invoice_number = f"INV-{st.session_state.invoice_counter:04d}"
            invoice_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            invoice_data = {
                'invoice_number': invoice_number,
                'customer_name': st.session_state.customer_name,
                'car_details': st.session_state.car_details,
                'date': invoice_date,
                'items': st.session_state.repair_items.copy(),
                'subtotal': subtotal,
                'labor': st.session_state.labor,
                'discount': st.session_state.discount,
                'grand_total': total,
                'user_id': USER_ID,
                'workshop_name': USER_PROFILE['workshop_name']
            }

            # Save invoice data
            save_invoice_data(invoice_data)

            # Create PDF
            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_font("Arial", 'B', 20)
            pdf.cell(0, 15, USER_PROFILE['workshop_name'], 0, 1, 'C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, "Professional Auto Repair Services", 0, 1, 'C')

            pdf.ln(10)

            # Invoice details
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "INVOICE", 0, 1, 'L')
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 7, f"Invoice #: {invoice_number}", 0, 1)
            pdf.cell(0, 7, f"Date: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 1)

            pdf.ln(5)

            # Customer info
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Customer Details", 0, 1)
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 7, f"Name: {st.session_state.customer_name}", 0, 1)
            pdf.cell(0, 7, f"Vehicle: {st.session_state.car_details}", 0, 1)

            pdf.ln(10)

            # Items table
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(100, 10, "Description", 1, 0, 'C')
            pdf.cell(25, 10, "Qty", 1, 0, 'C')
            pdf.cell(30, 10, "Price (Rs)", 1, 0, 'C')
            pdf.cell(35, 10, "Total (Rs)", 1, 1, 'C')

            pdf.set_font("Arial", '', 10)
            for item in st.session_state.repair_items:
                desc = item['desc']
                if len(desc) > 40:
                    desc = desc[:37] + "..."

                pdf.cell(100, 8, desc, 1, 0, 'L')
                pdf.cell(25, 8, str(item['qty']), 1, 0, 'C')
                pdf.cell(30, 8, f"{item['price']:,}", 1, 0, 'R')
                pdf.cell(35, 8, f"{item['total']:,}", 1, 1, 'R')

            pdf.ln(10)

            # Summary
            pdf.set_font("Arial", '', 11)
            pdf.cell(140, 8, "Subtotal:", 0, 0, 'R')
            pdf.cell(50, 8, f"Rs {subtotal:,}", 0, 1, 'R')

            if st.session_state.labor > 0:
                pdf.cell(140, 8, "Labor Charges:", 0, 0, 'R')
                pdf.cell(50, 8, f"Rs {st.session_state.labor:,}", 0, 1, 'R')

            if st.session_state.discount > 0:
                pdf.cell(140, 8, "Discount:", 0, 0, 'R')
                pdf.cell(50, 8, f"- Rs {st.session_state.discount:,}", 0, 1, 'R')

            pdf.set_font("Arial", 'B', 13)
            pdf.cell(140, 12, "GRAND TOTAL:", 0, 0, 'R')
            pdf.cell(50, 12, f"Rs {total:,}", 0, 1, 'R')

            pdf.ln(15)

            # Footer
            pdf.set_font("Arial", 'I', 9)
            pdf.cell(0, 6, "Thank you for your business!", 0, 1, 'C')

            if USER_PROFILE['phone_number'] and USER_PROFILE['phone_number'] != '+92-300-1234567':
                pdf.cell(0, 6, f"Phone: {USER_PROFILE['phone_number']}", 0, 1, 'C')

            pdf.cell(0, 6, USER_PROFILE['workshop_name'], 0, 1, 'C')

            if USER_PROFILE['address']:
                pdf.set_font("Arial", '', 8)
                pdf.cell(0, 6, f"Address: {USER_PROFILE['address']}", 0, 1, 'C')

            # Save PDF
            user_invoices_dir = get_user_invoices_dir()
            filename = f"invoice_{invoice_number}.pdf"
            filepath = os.path.join(user_invoices_dir, filename)
            pdf.output(filepath)

            # Update session state
            st.session_state.last_invoice_path = filepath
            st.session_state.last_invoice_data = invoice_data
            st.session_state.invoice_counter += 1
            save_user_invoice_counter(st.session_state.invoice_counter)

            # Show success
            st.markdown(f"""
            <div class="success-box">
                <h4 style="margin-top: 0;">✅ Invoice Generated Successfully!</h4>
                <p><strong>Invoice #:</strong> {invoice_number}</p>
                <p><strong>Customer:</strong> {st.session_state.customer_name}</p>
                <p><strong>Total Amount:</strong> Rs {total:,}</p>
            </div>
            """, unsafe_allow_html=True)

            # Download and WhatsApp buttons
            col1, col2 = st.columns(2)

            with col1:
                with open(filepath, "rb") as f:
                    st.download_button(
                        label="📥 **Download PDF**",
                        data=f,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )

            with col2:
                whatsapp_message = create_whatsapp_message(invoice_data)
                whatsapp_url = f"https://wa.me/?text={whatsapp_message}"

                st.markdown(f"""
                <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                    <button class="whatsapp-btn">
                        📱 **Send via WhatsApp**
                    </button>
                </a>
                """, unsafe_allow_html=True)

            st.balloons()

        except Exception as e:
            st.error(f"Error creating invoice: {str(e)}")

with generate_col2:
    if st.button("🔄 **Reset Form**", use_container_width=True, type="secondary"):
        st.session_state.repair_items = []
        st.session_state.customer_name = ""
        st.session_state.car_details = ""
        st.session_state.labor = 1500
        st.session_state.discount = 0
        st.session_state.new_desc = ""
        st.session_state.new_qty = 1
        st.session_state.new_price = 1000
        st.success("Form reset successfully!")
        st.rerun()

# ========================
# SIDEBAR LAYOUT
# ========================

# SIDEBAR - WORKSHOP PROFILE
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #2E4057;">🏢 Workshop Profile</h2>
    </div>
    """, unsafe_allow_html=True)

    # Profile display
    st.markdown(f"""
    <div class="profile-card">
        <h4 style="color: #2E4057; margin-top: 0;">{USER_PROFILE['workshop_name']}</h4>
        <p>👤 <strong>Owner:</strong> {USER_PROFILE['owner_name']}</p>
        <p>📞 <strong>Phone:</strong> {USER_PROFILE['phone_number']}</p>
        <p>📍 <strong>Address:</strong> {USER_PROFILE['address'][:30]}...</p>
        {f'<p>📧 <strong>Email:</strong> {USER_PROFILE["email"]}</p>' if USER_PROFILE['email'] else ''}
    </div>
    """, unsafe_allow_html=True)

    # Edit Profile Button
    if not st.session_state.show_profile_edit:
        if st.button("✏️ **Edit Profile**", use_container_width=True, type="secondary"):
            st.session_state.show_profile_edit = True
            st.rerun()

    # Profile Edit Form
    if st.session_state.show_profile_edit:
        with st.expander("📝 Edit Workshop Details", expanded=True):
            with st.form("profile_form"):
                st.write("**Update your workshop information:**")

                workshop_name = st.text_input(
                    "Workshop Name*",
                    value=USER_PROFILE['workshop_name']
                )

                owner_name = st.text_input(
                    "Owner Name",
                    value=USER_PROFILE['owner_name']
                )

                phone_number = st.text_input(
                    "Phone Number*",
                    value=USER_PROFILE['phone_number']
                )

                address = st.text_area(
                    "Address",
                    value=USER_PROFILE['address']
                )

                email = st.text_input(
                    "Email",
                    value=USER_PROFILE['email']
                )

                col1, col2 = st.columns(2)
                with col1:
                    save = st.form_submit_button("💾 **Save**", type="primary")
                with col2:
                    cancel = st.form_submit_button("❌ **Cancel**")

                if save:
                    if workshop_name.strip() and phone_number.strip():
                        new_profile = {
                            'workshop_name': workshop_name,
                            'owner_name': owner_name,
                            'phone_number': phone_number,
                            'address': address,
                            'email': email,
                            'website': USER_PROFILE.get('website', ''),
                            'tax_rate': USER_PROFILE.get('tax_rate', 0),
                            'currency': USER_PROFILE.get('currency', 'PKR')
                        }
                        save_user_profile(new_profile)
                        st.session_state.show_profile_edit = False
                        st.success("✅ Profile updated!")
                        st.rerun()
                    else:
                        st.error("Workshop name and phone number are required!")

                if cancel:
                    st.session_state.show_profile_edit = False
                    st.rerun()

    st.markdown("---")

    # SIDEBAR - TODAY'S STATISTICS
    st.markdown("""
    <div style="text-align: center;">
        <h3 style="color: #2E4057;">📊 Today's Summary</h3>
    </div>
    """, unsafe_allow_html=True)

    # Stats cards
    st.markdown(f"""
    <div class="stat-card">
        <h4 style="margin:0; color:white;">Invoices Today</h4>
        <h2 style="margin:5px 0; color:white;">{today_stats['invoices_today']}</h2>
        <small>Generated today</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h4 style="margin:0; color:white;">Your Earnings</h4>
        <h2 style="margin:5px 0; color:white;">Rs {today_stats['earnings_today']:,.0f}</h2>
        <small>Labor charges only</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # SIDEBAR - QUICK ACTIONS
    st.markdown("""
    <div style="text-align: center;">
        <h3 style="color: #2E4057;">⚡ Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📋 **View Report**", use_container_width=True):
        with st.expander("📈 Today's Report"):
            st.write(f"**Invoices:** {today_stats['invoices_today']}")
            st.write(f"**Earnings:** Rs {today_stats['earnings_today']:,}")
            st.write(f"**Total Sales:** Rs {today_stats['total_sales_today']:,}")
            st.write(f"**Items Sold:** {today_stats['items_sold']}")

    if st.button("🗑️ **Clear Today's Data**", use_container_width=True):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        user_data_dir = get_user_data_dir()
        data_file = f"{user_data_dir}/invoices_{today}.json"
        if os.path.exists(data_file):
            os.remove(data_file)
            st.success("Today's data cleared!")
            st.rerun()

    st.markdown("---")

    # SIDEBAR - CURRENT WORK
    st.markdown("""
    <div style="text-align: center;">
        <h3 style="color: #2E4057;">🛠️ Current Work</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <p><strong>Next Invoice #:</strong> INV-{st.session_state.invoice_counter:04d}</p>
        <p><strong>Items in Cart:</strong> {len(st.session_state.repair_items)}</p>
        {f'<p><strong>Customer:</strong> {st.session_state.customer_name[:20]}</p>' if st.session_state.customer_name else '<p><strong>Customer:</strong> None</p>'}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">
        <p>🔒 <strong>AutoInvoice Pro</strong></p>
        <p>v1.0 • Professional Billing System</p>
    </div>
    """, unsafe_allow_html=True)