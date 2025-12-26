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
    page_title="Car Repair Invoice - Worker",
    page_icon="🔧",
    layout="wide"
)

# Simple styling with monogram
st.markdown("""
<style>
    .big-button {
        height: 60px;
        font-size: 18px !important;
    }
    .invoice-box {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .whatsapp-btn {
        background-color: #25D366 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        font-weight: bold !important;
    }
    .whatsapp-btn:hover {
        background-color: #128C7E !important;
    }
    .user-info {
        background: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .monogram-container {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1000;
    }
    .monogram {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 50px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .monogram-icon {
        font-size: 20px;
        margin-right: 8px;
    }
    .main-title {
        margin-top: 40px !important;
    }
    .profile-section {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #ddd;
    }
    .profile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
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
        'phone_number': '+92-XXX-XXXXXXX',
        'address': 'Your Workshop Address',
        'email': '',
        'website': '',
        'logo_text': '🔧 AUTO CARE',
        'owner_name': ''
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
    """Calculate today's statistics from saved invoices - FIXED: Only count labor as earnings"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    user_data_dir = get_user_data_dir()
    data_file = f"{user_data_dir}/invoices_{today}.json"

    # Default statistics
    stats = {
        'invoices_today': 0,
        'earnings_today': 0,  # Now this will only count labor
        'total_sales_today': 0,  # NEW: For total sales amount
        'average_invoice': 0,
        'items_sold': 0,
        'recent_invoices': [],
        'total_labor': 0,  # NEW: Total labor earnings
        'user_id': USER_ID  # Include user ID for reference
    }

    if not os.path.exists(data_file):
        return stats

    try:
        with open(data_file, 'r') as f:
            invoices = json.load(f)

        if not invoices or not isinstance(invoices, list):
            return stats

        # Calculate statistics - FIXED LOGIC
        total_sales = 0
        total_items = 0
        total_labor_earnings = 0

        for inv in invoices:
            if isinstance(inv, dict):
                # Total sales (parts + labor - discount)
                total_sales += inv.get('grand_total', 0)

                # Only labor counts as earnings (what the worker actually earns)
                total_labor_earnings += inv.get('labor', 0)

                total_items += len(inv.get('items', []))

        invoice_count = len(invoices)
        average_invoice = total_sales / invoice_count if invoice_count > 0 else 0

        # Get recent invoices (last 5)
        recent_invoices = invoices[-5:] if invoices else []

        stats.update({
            'invoices_today': invoice_count,
            'earnings_today': total_labor_earnings,  # FIXED: Only labor
            'total_sales_today': total_sales,  # Total sales amount
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
    """Get statistics from all time data - FIXED: Only count labor as earnings"""
    user_data_dir = get_user_data_dir()

    stats = {
        'total_invoices': 0,
        'total_earnings': 0,  # Only labor earnings
        'total_sales': 0,  # Total sales amount
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
                                    stats['total_sales'] += inv.get('grand_total', 0)  # Total sales
                                    stats['total_earnings'] += inv.get('labor', 0)  # Only labor earnings
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
    """Create WhatsApp message template using user's profile"""
    customer = invoice_data['customer_name']
    car = invoice_data['car_details']
    invoice_num = invoice_data['invoice_number']
    total = invoice_data['grand_total']
    date = datetime.datetime.now().strftime("%d/%m/%Y")

    message = f"""*Assalam-o-Alaikum!* 

🚗 *Car Repair Invoice - {USER_PROFILE['workshop_name']}*
--------------------------------
*Customer:* {customer}
*Car Details:* {car}
*Invoice #:* {invoice_num}
*Date:* {date}
*Total Amount:* Rs {total:,}

Invoice PDF is attached.

Thank you for choosing {USER_PROFILE['workshop_name']}!"""

    return urllib.parse.quote(message)


# ========================
# INITIALIZE SESSION STATE (User-Specific)
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
    'show_profile_edit': False  # NEW: Control profile edit mode
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

# Add monogram/logo at top left corner using user's profile
st.markdown(f"""
<div class="monogram-container">
    <div class="monogram">
        <span class="monogram-icon">🔧</span>
        <span>{USER_PROFILE['logo_text']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main title with space for monogram
st.markdown('<div class="main-title">', unsafe_allow_html=True)
st.title(f"🔧 {USER_PROFILE['workshop_name']} - Invoice System")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 1. QUICK START SECTION
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🆕 New Invoice", use_container_width=True, type="primary"):
        st.session_state.repair_items = []
        st.session_state.customer_name = ""
        st.session_state.car_details = ""
        st.rerun()

with col2:
    if st.button("💾 Save Draft", use_container_width=True):
        st.success("Draft saved to your personal storage!")

with col3:
    if st.button("📋 Recent Jobs", use_container_width=True):
        st.info(f"Showing your last 5 invoices")

st.markdown("---")

# 2. CUSTOMER & CAR INFO
st.subheader("1. Customer & Car Info")

# Get customer and car info
customer_name = st.text_input(
    "Customer Name",
    value=st.session_state.customer_name,
    placeholder="John Ali"
)

car_details = st.text_input(
    "Car Details",
    value=st.session_state.car_details,
    placeholder="Toyota Corolla 2018, White"
)

# Store in session state
st.session_state.customer_name = customer_name
st.session_state.car_details = car_details

st.markdown("---")

# 3. REPAIR ITEMS
st.subheader("2. Add Repair Work")

# Display existing items
if st.session_state.repair_items:
    st.markdown("**Current Items:**")

    # Create a table-like display
    for i, item in enumerate(st.session_state.repair_items):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.write(f"**{item['desc']}**")
        with col2:
            st.write(f"Qty: {item['qty']}")
        with col3:
            st.write(f"Rs {item['price']:,}")
        with col4:
            if st.button("❌ Remove", key=f"del_{i}"):
                st.session_state.repair_items.pop(i)
                st.rerun()

# Add new item
st.markdown("#### Add New Repair Item:")
new_col1, new_col2, new_col3, new_col4 = st.columns([3, 1, 1, 1])

with new_col1:
    new_desc = st.text_input(
        "What you fixed",
        label_visibility="collapsed",
        placeholder="e.g., Changed brake pads, Fixed AC",
        key="new_desc"
    )

with new_col2:
    new_qty = st.number_input(
        "Qty",
        min_value=1,
        value=1,
        label_visibility="collapsed",
        key="new_qty"
    )

with new_col3:
    new_price = st.number_input(
        "Price",
        min_value=0,
        value=1000,
        label_visibility="collapsed",
        key="new_price"
    )

with new_col4:
    if st.button("➕ Add", use_container_width=True, key="add_button"):
        if new_desc:
            st.session_state.repair_items.append({
                'desc': new_desc,
                'qty': int(new_qty),
                'price': float(new_price),
                'total': float(new_qty) * float(new_price)
            })
            st.rerun()

st.markdown("---")

# 4. QUICK CALCULATOR
st.subheader("3. Quick Calculator")

# Labor and discount inputs
st.session_state.labor = st.number_input(
    "Labor Charges (PKR) - Your Earnings",
    value=st.session_state.labor,
    step=500,
    key="labor_input"
)

st.session_state.discount = st.number_input(
    "Discount (PKR)",
    value=st.session_state.discount,
    step=100,
    key="discount_input"
)

if st.session_state.repair_items:
    # Calculate subtotal
    subtotal = 0
    for item in st.session_state.repair_items:
        subtotal += item['total']

    # Calculate total
    total = subtotal + st.session_state.labor - st.session_state.discount

    # Display totals SIMPLY
    st.markdown(f"""
    <div class="invoice-box">
        <h4>Invoice Summary</h4>
        <p><b>Parts Total:</b> Rs {subtotal:,}</p>
        <p><b>Labor (Your Earnings):</b> Rs {st.session_state.labor:,}</p>
        <p><b>Discount:</b> -Rs {st.session_state.discount:,}</p>
        <h3>TOTAL: Rs {total:,}</h3>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Add repair items above to see calculations")

# 5. GENERATE INVOICE
st.markdown("---")
st.subheader("4. Create Invoice")

# Check if we have items
has_items = len(st.session_state.repair_items) > 0
has_customer = st.session_state.customer_name.strip() != ""
has_car = st.session_state.car_details.strip() != ""

generate_button = st.button(
    "📄 GENERATE INVOICE",
    type="primary",
    use_container_width=True,
    disabled=not has_items,
    key="generate_btn"
)

if generate_button:
    # Validate inputs
    if not has_customer:
        st.error("Please enter customer name!")
        st.stop()

    if not has_car:
        st.error("Please enter car details!")
        st.stop()

    # Calculate totals again for PDF
    subtotal = 0
    for item in st.session_state.repair_items:
        subtotal += item['total']

    total = subtotal + st.session_state.labor - st.session_state.discount

    try:
        # Create invoice data for saving
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

        # Save invoice data for statistics
        save_invoice_data(invoice_data)

        # Create PDF with user's profile details
        pdf = FPDF()
        pdf.add_page()

        # Header with user's workshop name
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"{USER_PROFILE['workshop_name']}", 0, 1, 'C')
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "REPAIR INVOICE", 0, 1, 'C')

        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Customer: {st.session_state.customer_name}", 0, 1)
        pdf.cell(0, 10, f"Car: {st.session_state.car_details}", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 1)
        pdf.cell(0, 10, f"Invoice #: {invoice_number}", 0, 1)

        pdf.ln(10)

        # Items table header
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, "Description", 1, 0, 'C')
        pdf.cell(30, 10, "Qty", 1, 0, 'C')
        pdf.cell(30, 10, "Price (Rs)", 1, 0, 'C')
        pdf.cell(30, 10, "Total (Rs)", 1, 1, 'C')

        # Items table rows
        pdf.set_font("Arial", '', 12)
        for item in st.session_state.repair_items:
            desc = item['desc']
            if len(desc) > 40:
                desc = desc[:37] + "..."

            pdf.cell(100, 10, desc, 1, 0, 'L')
            pdf.cell(30, 10, str(item['qty']), 1, 0, 'C')
            pdf.cell(30, 10, f"{item['price']:,}", 1, 0, 'R')
            pdf.cell(30, 10, f"{item['total']:,}", 1, 1, 'R')

        pdf.ln(10)

        # Summary section
        pdf.set_font("Arial", '', 12)
        pdf.cell(140, 10, "Subtotal:", 0, 0, 'R')
        pdf.cell(50, 10, f"Rs {subtotal:,}", 0, 1, 'R')

        if st.session_state.labor > 0:
            pdf.cell(140, 10, "Labor Charges:", 0, 0, 'R')
            pdf.cell(50, 10, f"Rs {st.session_state.labor:,}", 0, 1, 'R')

        if st.session_state.discount > 0:
            pdf.cell(140, 10, "Discount:", 0, 0, 'R')
            pdf.cell(50, 10, f"- Rs {st.session_state.discount:,}", 0, 1, 'R')

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(140, 15, "GRAND TOTAL:", 0, 0, 'R')
        pdf.cell(50, 15, f"Rs {total:,}", 0, 1, 'R')

        pdf.ln(10)

        # Footer with user's contact details
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "Thank you for your business!", 0, 1, 'C')

        # Show owner name if set
        if USER_PROFILE['owner_name']:
            pdf.cell(0, 10, f"Owner: {USER_PROFILE['owner_name']}", 0, 1, 'C')

        # Show phone if set
        if USER_PROFILE['phone_number'] and USER_PROFILE['phone_number'] != '+92-XXX-XXXXXXX':
            pdf.cell(0, 10, f"Phone: {USER_PROFILE['phone_number']}", 0, 1, 'C')

        # Show workshop name
        pdf.cell(0, 10, f"{USER_PROFILE['workshop_name']}", 0, 1, 'C')

        # Show address if set
        if USER_PROFILE['address'] and USER_PROFILE['address'] != 'Your Workshop Address':
            pdf.set_font("Arial", '', 8)
            pdf.cell(0, 10, f"Address: {USER_PROFILE['address']}", 0, 1, 'C')

        # Show email if set
        if USER_PROFILE['email']:
            pdf.set_font("Arial", '', 8)
            pdf.cell(0, 10, f"Email: {USER_PROFILE['email']}", 0, 1, 'C')

        # Get user-specific invoices directory
        user_invoices_dir = get_user_invoices_dir()

        # Save PDF
        filename = f"invoice_{invoice_number}.pdf"
        filepath = os.path.join(user_invoices_dir, filename)
        pdf.output(filepath)

        # Store last invoice info
        st.session_state.last_invoice_path = filepath
        st.session_state.last_invoice_data = invoice_data

        # Update invoice counter and save it
        st.session_state.invoice_counter += 1
        save_user_invoice_counter(st.session_state.invoice_counter)

        # Show success message
        st.success(f"✅ Invoice {invoice_number} created successfully!")

        # Display download and WhatsApp buttons side by side
        col1, col2 = st.columns(2)

        with col1:
            with open(filepath, "rb") as f:
                st.download_button(
                    label="📥 DOWNLOAD PDF INVOICE",
                    data=f,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )

        with col2:
            # Create WhatsApp message link
            whatsapp_message = create_whatsapp_message(invoice_data)
            whatsapp_url = f"https://wa.me/?text={whatsapp_message}"

            st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                <button class="whatsapp-btn" style="width: 100%;">
                    📱 SEND TO WHATSAPP
                </button>
            </a>
            """, unsafe_allow_html=True)
            st.caption("Note: You'll need to attach the PDF manually in WhatsApp")

        # Show invoice summary
        st.markdown(f"""
        <div class="invoice-box">
            <h4>Invoice Details</h4>
            <p><b>Invoice #:</b> {invoice_number}</p>
            <p><b>Customer:</b> {st.session_state.customer_name}</p>
            <p><b>Car:</b> {st.session_state.car_details}</p>
            <p><b>Workshop:</b> {USER_PROFILE['workshop_name']}</p>
            <p><b>Your Earnings (Labor):</b> Rs {st.session_state.labor:,}</p>
            <p><b>Total Items:</b> {len(st.session_state.repair_items)}</p>
            <p><b>Grand Total:</b> Rs {total:,}</p>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()

    except Exception as e:
        st.error(f"Error creating invoice: {str(e)}")

# ========================
# SIDEBAR WITH REAL STATISTICS AND PROFILE EDITING
# ========================

# SIDEBAR - USER PROFILE SECTION
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Workshop Profile")

# Display current profile info
st.sidebar.markdown(f"""
<div class="profile-section">
    <div class="profile-header">
        <strong>{USER_PROFILE['workshop_name']}</strong>
        {"" if st.session_state.show_profile_edit else "✏️"}
    </div>
    <p><strong>Owner:</strong> {USER_PROFILE['owner_name'] or 'Not set'}</p>
    <p><strong>Phone:</strong> {USER_PROFILE['phone_number']}</p>
    <p><strong>Address:</strong> {USER_PROFILE['address'][:30]}...</p>
    {f'<p><strong>Email:</strong> {USER_PROFILE["email"]}</p>' if USER_PROFILE['email'] else ''}
</div>
""", unsafe_allow_html=True)

# Edit Profile Button
if not st.session_state.show_profile_edit:
    if st.sidebar.button("✏️ Edit Profile", use_container_width=True, type="secondary"):
        st.session_state.show_profile_edit = True
        st.rerun()

# PROFILE EDITING SECTION (Expandable in sidebar)
if st.session_state.show_profile_edit:
    with st.sidebar.expander("📝 Edit Workshop Details", expanded=True):
        st.write("**Update your workshop information:**")

        # Profile edit form
        with st.form("profile_edit_form"):
            workshop_name = st.text_input(
                "Workshop Name*",
                value=USER_PROFILE['workshop_name'],
                help="This appears on invoices"
            )

            owner_name = st.text_input(
                "Owner Name",
                value=USER_PROFILE['owner_name'],
                placeholder="Ali Ahmed",
                help="Your name (optional)"
            )

            phone_number = st.text_input(
                "Phone Number*",
                value=USER_PROFILE['phone_number'],
                placeholder="+92-300-1234567",
                help="Customer contact number"
            )

            address = st.text_area(
                "Workshop Address",
                value=USER_PROFILE['address'],
                placeholder="Shop #123, Main Road, City",
                help="Your workshop location"
            )

            email = st.text_input(
                "Email (Optional)",
                value=USER_PROFILE['email'],
                placeholder="workshop@email.com"
            )

            website = st.text_input(
                "Website (Optional)",
                value=USER_PROFILE['website'],
                placeholder="www.yourworkshop.com"
            )

            logo_text = st.text_input(
                "Logo Text",
                value=USER_PROFILE['logo_text'],
                placeholder="🔧 YOUR WORKSHOP",
                help="Text shown in top-left corner"
            )

            # Form buttons
            col1, col2 = st.columns(2)
            with col1:
                save_profile = st.form_submit_button("💾 Save", type="primary")
            with col2:
                cancel_profile = st.form_submit_button("❌ Cancel")

            if save_profile:
                if not workshop_name.strip() or not phone_number.strip():
                    st.error("Workshop Name and Phone Number are required!")
                else:
                    # Update profile
                    new_profile = {
                        'workshop_name': workshop_name,
                        'owner_name': owner_name,
                        'phone_number': phone_number,
                        'address': address,
                        'email': email,
                        'website': website,
                        'logo_text': logo_text
                    }

                    # Save to file
                    save_user_profile(new_profile)

                    # Update session state
                    st.session_state.show_profile_edit = False

                    # Show success message in sidebar
                    st.success("✅ Profile updated!")
                    st.info("Refreshing page...")
                    st.rerun()

            if cancel_profile:
                st.session_state.show_profile_edit = False
                st.rerun()

st.sidebar.markdown("---")

# SIDEBAR - TODAY'S WORK STATISTICS
st.sidebar.title("📊 Today's Work")

# Get real-time statistics for current user
today_stats = get_today_statistics()
all_time_stats = get_all_time_statistics()

# Today's Statistics Cards
st.sidebar.markdown(f"""
<div class="stat-card">
    <h4 style="margin:0; color:white;">Your Invoices Today</h4>
    <h2 style="margin:5px 0; color:white;">{today_stats['invoices_today']}</h2>
    <small>Generated today by you</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
    <h4 style="margin:0; color:white;">Your Earnings (Labor)</h4>
    <h2 style="margin:5px 0; color:white;">Rs {today_stats['earnings_today']:,.0f}</h2>
    <small>From {today_stats['invoices_today']} invoices</small>
</div>
""", unsafe_allow_html=True)

# Additional metrics
col1, col2 = st.sidebar.columns(2)
with col1:
    if today_stats['invoices_today'] > 0:
        avg_labor = today_stats['total_labor'] / today_stats['invoices_today']
        st.metric("Avg. Labor", f"Rs {avg_labor:,.0f}")
    else:
        st.metric("Avg. Labor", "Rs 0")

with col2:
    st.metric("Total Sales", f"Rs {today_stats['total_sales_today']:,.0f}")

st.sidebar.markdown("---")

# SIDEBAR - RECENT INVOICES
st.sidebar.subheader("📋 Your Recent Invoices")

recent_invoices = today_stats.get('recent_invoices', [])

if recent_invoices:
    for inv in reversed(recent_invoices[-3:]):
        if isinstance(inv, dict):
            with st.sidebar.expander(
                    f"{inv.get('invoice_number', 'N/A')} - {inv.get('customer_name', 'Unknown')[:15]}..."):
                st.write(f"**Car:** {inv.get('car_details', 'N/A')[:20]}")
                st.write(f"**Total:** Rs {inv.get('grand_total', 0):,}")
                st.write(f"**Labor:** Rs {inv.get('labor', 0):,}")
                date_str = inv.get('date', '')
                if date_str:
                    time_part = date_str.split()[1][:5] if ' ' in date_str else ''
                    st.write(f"**Time:** {time_part}")
else:
    st.sidebar.info("No invoices today")

st.sidebar.markdown("---")

# SIDEBAR - ALL TIME STATISTICS
st.sidebar.subheader("📈 Your All Time Stats")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Your Invoices", all_time_stats['total_invoices'])
with col2:
    st.metric("Your Earnings", f"Rs {all_time_stats['total_earnings']:,.0f}")

st.sidebar.write(f"**Total Sales:** Rs {all_time_stats['total_sales']:,.0f}")
st.sidebar.write(f"**Active Days:** {all_time_stats['days_active']}")
if all_time_stats['days_active'] > 0:
    st.sidebar.write(f"**Avg. Daily Earnings:** Rs {all_time_stats['average_daily']:,.0f}")
else:
    st.sidebar.write(f"**Avg. Daily Earnings:** Rs 0")

st.sidebar.markdown("---")

# SIDEBAR - QUICK ACTIONS
st.sidebar.title("⚡ Quick Actions")
if st.sidebar.button("🔄 Clear Current Invoice", use_container_width=True):
    st.session_state.repair_items = []
    st.session_state.customer_name = ""
    st.session_state.car_details = ""
    st.session_state.labor = 1500
    st.session_state.discount = 0
    st.rerun()

if st.sidebar.button("📊 View Your Report", use_container_width=True):
    with st.sidebar:
        st.info(f"**Your Today's Report**")
        st.write(f"- Invoices: {today_stats['invoices_today']}")
        st.write(f"- Your Earnings (Labor): Rs {today_stats['earnings_today']:,}")
        st.write(f"- Total Sales: Rs {today_stats['total_sales_today']:,}")
        st.write(f"- Items Sold: {today_stats['items_sold']}")

if st.sidebar.button("🧹 Clear Your Today's Data", use_container_width=True):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    user_data_dir = get_user_data_dir()
    data_file = f"{user_data_dir}/invoices_{today}.json"
    if os.path.exists(data_file):
        os.remove(data_file)
        st.sidebar.success("Your today's data cleared!")
        st.rerun()

# SIDEBAR - CURRENT WORK STATUS
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Current Work")
st.sidebar.write(f"**Workshop:** {USER_PROFILE['workshop_name'][:20]}")
st.sidebar.write(f"**Next Invoice #:** INV-{st.session_state.invoice_counter:04d}")
st.sidebar.write(f"**Items in Cart:** {len(st.session_state.repair_items)}")
if st.session_state.customer_name:
    st.sidebar.write(f"**Customer:** {st.session_state.customer_name[:20]}")
else:
    st.sidebar.write(f"**Customer:** None")

# Footer note about multi-user support
st.sidebar.markdown("---")
st.sidebar.caption("🔒 **Note:** Your data is stored separately from other users. Each user has their own workspace.")