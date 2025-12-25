import streamlit as st
import datetime
from fpdf import FPDF
import os
import json

# ========================
# ONE-PAGE WORKER APP
# ========================

st.set_page_config(
    page_title="Car Repair Invoice - Worker",
    page_icon="🔧",
    layout="wide"
)

# Simple styling
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
</style>
""", unsafe_allow_html=True)


# ========================
# DATA MANAGEMENT FUNCTIONS
# ========================

def save_invoice_data(invoice_data):
    """Save invoice data to JSON file for statistics"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    data_file = f"data/invoices_{today}.json"

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

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
    data_file = f"data/invoices_{today}.json"

    # Default statistics
    stats = {
        'invoices_today': 0,
        'earnings_today': 0,
        'average_invoice': 0,
        'items_sold': 0,
        'recent_invoices': []  # Always include this key
    }

    if not os.path.exists(data_file):
        return stats

    try:
        with open(data_file, 'r') as f:
            invoices = json.load(f)

        if not invoices or not isinstance(invoices, list):
            return stats

        # Calculate statistics
        total_earnings = 0
        total_items = 0

        for inv in invoices:
            if isinstance(inv, dict):
                total_earnings += inv.get('grand_total', 0)
                total_items += len(inv.get('items', []))

        invoice_count = len(invoices)
        average_invoice = total_earnings / invoice_count if invoice_count > 0 else 0

        # Get recent invoices (last 5)
        recent_invoices = invoices[-5:] if invoices else []

        stats.update({
            'invoices_today': invoice_count,
            'earnings_today': total_earnings,
            'average_invoice': average_invoice,
            'items_sold': total_items,
            'recent_invoices': recent_invoices
        })

        return stats

    except Exception as e:
        print(f"Error reading statistics: {e}")
        return stats


def get_all_time_statistics():
    """Get statistics from all time data"""
    data_dir = "data"

    stats = {
        'total_invoices': 0,
        'total_earnings': 0,
        'days_active': 0,
        'average_daily': 0
    }

    if not os.path.exists(data_dir):
        return stats

    try:
        invoice_files = []

        # Get all invoice files
        for file in os.listdir(data_dir):
            if file.startswith("invoices_") and file.endswith(".json"):
                invoice_files.append(file)

                try:
                    with open(os.path.join(data_dir, file), 'r') as f:
                        invoices = json.load(f)
                        if isinstance(invoices, list):
                            stats['total_invoices'] += len(invoices)
                            for inv in invoices:
                                if isinstance(inv, dict):
                                    stats['total_earnings'] += inv.get('grand_total', 0)
                except:
                    pass

        stats['days_active'] = len(invoice_files)
        stats['average_daily'] = stats['total_earnings'] / stats['days_active'] if stats['days_active'] > 0 else 0

        return stats

    except Exception as e:
        print(f"Error reading all-time stats: {e}")
        return stats


# ========================
# INITIALIZE SESSION STATE
# ========================

# Initialize with default values
defaults = {
    'repair_items': [],
    'invoice_counter': 1000,
    'customer_name': "",
    'car_details': "",
    'labor': 1500,
    'discount': 0
}

for key, default_value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Update invoice counter based on existing data
try:
    all_stats = get_all_time_statistics()
    st.session_state.invoice_counter = 1000 + all_stats['total_invoices']
except:
    pass  # Keep default value

# ========================
# MAIN APP LAYOUT
# ========================

st.title("🔧 Car Repair Invoice - Worker's Tool")
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
        st.success("Draft saved!")

with col3:
    if st.button("📋 Recent Jobs", use_container_width=True):
        st.info("Showing last 5 invoices")

st.markdown("---")

# 2. CUSTOMER & CAR INFO (SIMPLE!)
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

# 3. REPAIR ITEMS (MOST IMPORTANT PART FOR WORKER)
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

# 4. QUICK CALCULATOR (WORKER NEEDS THIS!)
st.subheader("3. Quick Calculator")

# Labor and discount inputs
st.session_state.labor = st.number_input(
    "Labor Charges (PKR)",
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
        <p><b>Labor:</b> Rs {st.session_state.labor:,}</p>
        <p><b>Discount:</b> -Rs {st.session_state.discount:,}</p>
        <h3>TOTAL: Rs {total:,}</h3>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Add repair items above to see calculations")

# 5. GENERATE INVOICE (SIMPLE PDF)
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
            'items': st.session_state.repair_items.copy(),  # Copy to avoid reference issues
            'subtotal': subtotal,
            'labor': st.session_state.labor,
            'discount': st.session_state.discount,
            'grand_total': total
        }

        # Save invoice data for statistics
        save_invoice_data(invoice_data)

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "CAR REPAIR INVOICE", 0, 1, 'C')

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

        # Footer
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "Thank you for your business!", 0, 1, 'C')
        pdf.cell(0, 10, "Phone: +92-XXX-XXXXXXX", 0, 1, 'C')
        pdf.cell(0, 10, "Workshop: AutoCare Repair Center", 0, 1, 'C')

        # Create invoices directory if it doesn't exist
        os.makedirs("invoices", exist_ok=True)

        # Save PDF
        filename = f"invoice_{invoice_number}.pdf"
        filepath = os.path.join("invoices", filename)
        pdf.output(filepath)

        # Update invoice counter
        st.session_state.invoice_counter += 1

        # Show success message
        st.success(f"✅ Invoice {invoice_number} created successfully!")

        # Download button
        with open(filepath, "rb") as f:
            st.download_button(
                label="📥 DOWNLOAD PDF INVOICE",
                data=f,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )

        # Show invoice summary
        st.markdown(f"""
        <div class="invoice-box">
            <h4>Invoice Details</h4>
            <p><b>Invoice #:</b> {invoice_number}</p>
            <p><b>Customer:</b> {st.session_state.customer_name}</p>
            <p><b>Car:</b> {st.session_state.car_details}</p>
            <p><b>Total Items:</b> {len(st.session_state.repair_items)}</p>
            <p><b>Grand Total:</b> Rs {total:,}</p>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()

    except Exception as e:
        st.error(f"Error creating invoice: {str(e)}")

# 6. WORKER'S QUICK NOTES SECTION
st.markdown("---")
with st.expander("📝 Worker's Notes & Draft Messages"):
    # Pre-written messages for quick copy-paste
    st.markdown("**Quick Messages for WhatsApp:**")

    messages = [
        "Assalam-o-Alaikum! Your car is ready for pickup. Total: Rs {amount}",
        "Assalam-o-Alaikum! Need approval for additional repair. Estimate: Rs {amount}",
        "Assalam-o-Alaikum! Part arrived. Can complete repair today.",
        "Assalam-o-Alaikum! Car wash completed. Ready for delivery."
    ]

    for i, msg in enumerate(messages):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.code(msg, language="text")
        with col2:
            if st.button("Copy", key=f"copy_{i}"):
                st.info("Message copied to clipboard (simulated)")
                st.write(msg)

# ========================
# SIDEBAR WITH REAL STATISTICS
# ========================

# Get real-time statistics
today_stats = get_today_statistics()
all_time_stats = get_all_time_statistics()

st.sidebar.title("📊 Today's Work")

# Today's Statistics Cards
st.sidebar.markdown(f"""
<div class="stat-card">
    <h4 style="margin:0; color:white;">Invoices Today</h4>
    <h2 style="margin:5px 0; color:white;">{today_stats['invoices_today']}</h2>
    <small>Generated today</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
    <h4 style="margin:0; color:white;">Earnings Today</h4>
    <h2 style="margin:5px 0; color:white;">Rs {today_stats['earnings_today']:,.0f}</h2>
    <small>From {today_stats['items_sold']} items</small>
</div>
""", unsafe_allow_html=True)

# Additional metrics
col1, col2 = st.sidebar.columns(2)
with col1:
    if today_stats['invoices_today'] > 0:
        st.metric("Avg. Invoice", f"Rs {today_stats['average_invoice']:,.0f}")
    else:
        st.metric("Avg. Invoice", "Rs 0")
with col2:
    st.metric("Items Sold", today_stats['items_sold'])

st.sidebar.markdown("---")

# Recent Invoices
st.sidebar.subheader("📋 Recent Invoices")

# Check if recent_invoices exists and has data
recent_invoices = today_stats.get('recent_invoices', [])

if recent_invoices:
    # Show last 3 invoices in reverse order (newest first)
    for inv in reversed(recent_invoices[-3:]):
        if isinstance(inv, dict):
            with st.sidebar.expander(
                    f"{inv.get('invoice_number', 'N/A')} - {inv.get('customer_name', 'Unknown')[:15]}..."):
                st.write(f"**Car:** {inv.get('car_details', 'N/A')[:20]}")
                st.write(f"**Total:** Rs {inv.get('grand_total', 0):,}")
                date_str = inv.get('date', '')
                if date_str:
                    time_part = date_str.split()[1][:5] if ' ' in date_str else ''
                    st.write(f"**Time:** {time_part}")
else:
    st.sidebar.info("No invoices today")

st.sidebar.markdown("---")

# All Time Statistics
st.sidebar.subheader("📈 All Time Stats")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Total Invoices", all_time_stats['total_invoices'])
with col2:
    st.metric("Total Earnings", f"Rs {all_time_stats['total_earnings']:,.0f}")

st.sidebar.write(f"**Active Days:** {all_time_stats['days_active']}")
if all_time_stats['days_active'] > 0:
    st.sidebar.write(f"**Avg. Daily:** Rs {all_time_stats['average_daily']:,.0f}")
else:
    st.sidebar.write(f"**Avg. Daily:** Rs 0")

st.sidebar.markdown("---")

# Quick Actions
st.sidebar.title("⚡ Quick Actions")
if st.sidebar.button("🔄 Clear All", use_container_width=True):
    st.session_state.repair_items = []
    st.session_state.customer_name = ""
    st.session_state.car_details = ""
    st.session_state.labor = 1500
    st.session_state.discount = 0
    st.rerun()

if st.sidebar.button("📊 View Reports", use_container_width=True):
    with st.sidebar:
        st.info("**Today's Report**")
        st.write(f"- Invoices: {today_stats['invoices_today']}")
        st.write(f"- Earnings: Rs {today_stats['earnings_today']:,}")
        st.write(f"- Items Sold: {today_stats['items_sold']}")

if st.sidebar.button("🧹 Clear Today's Data", use_container_width=True):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    data_file = f"data/invoices_{today}.json"
    if os.path.exists(data_file):
        os.remove(data_file)
        st.sidebar.success("Today's data cleared!")
        st.rerun()

# Current Work Status
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Current Work")
st.sidebar.write(f"**Next Invoice #:** INV-{st.session_state.invoice_counter:04d}")
st.sidebar.write(f"**Items in Cart:** {len(st.session_state.repair_items)}")
if st.session_state.customer_name:
    st.sidebar.write(f"**Customer:** {st.session_state.customer_name[:20]}...")
else:
    st.sidebar.write(f"**Customer:** None")

# Data directory info
if st.sidebar.checkbox("Show Data Info", value=False):
    with st.sidebar.expander("📁 Data Information"):
        if os.path.exists("data"):
            files = os.listdir("data")
            st.write(f"**Data Files:** {len(files)}")
            for file in files[:5]:  # Show first 5 files
                st.write(f"- {file}")
            if len(files) > 5:
                st.write(f"... and {len(files) - 5} more")
        else:
            st.write("**Data Directory:** Not created yet")
        st.write(f"**Today:** {datetime.datetime.now().strftime('%Y-%m-%d')}")