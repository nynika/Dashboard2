import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Morning Meeting Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Set background color */
    .stApp {
        background-color: #f0f4f8;
    }
    .header{
        background-color: royalblue;
        color: white;
        border-radius: 5px;
        display: flex;
        text-align: center;
        justify-content:center;
        padding:10px 0px 2px;
    }
    .header1{
        background-color: none;
        color:royalblue ;
        border-radius: 5px;
        display: flex;
        text-align: center;
        justify-content:left;
        padding:10px 0px 2px;
    }
     .header2{
        background-color: orange;
        color:royalblue ;
        border-radius: 5px;
        display: flex;
        text-align: center;
        justify-content:left;
        padding:10px 0px 2px;
    }
    /* Header styling */
    h1, h2, h3, h4,p {
        background-color: royalblue;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Circle styling for metrics */
    .circle {
        display: inline-block;
        background-color: white;
        color: royalblue;
        border-radius: 50%;
        width: 80px;
        height: 60px;
        line-height: 40px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Modify plot titles */
    .plotly-title {
        color: royalblue;
    }
    </style>
""",
    unsafe_allow_html=True,
)


today = datetime.today().strftime("%Y-%m-%d")
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

otresponse = requests.get(f"http://192.168.15.3/NewHIS/api/his/Get_OT_Scheduleing")
if otresponse.status_code == 200:
    try:
        ot_data = pd.DataFrame(otresponse.json())
    except ValueError:
        st.error("Invalid JSON response for OPD Appointments")
        st.write(otresponse.text)
else:
    st.error(f"Error fetching OPD data: {otresponse.status_code}")

admissionresponse = requests.get(
    f"http://192.168.15.3/NewHIS/api/his/Get_ListOfAdmission?FromDate={yesterday}&ToDate={yesterday}"
)
if admissionresponse.status_code == 200:
    try:
        admission_data = pd.DataFrame(admissionresponse.json())
    except ValueError:
        st.error("Invalid JSON response for OPD Appointments")
        st.write(admissionresponse.text)
else:
    st.error(f"Error fetching OPD data: {admissionresponse.status_code}")


dischargeresponse = requests.get(
    f"http://192.168.15.3/NewHIS/api/his/Get_DischargeTrackingreport"
)
if dischargeresponse.status_code == 200:
    try:
        discharge_data = pd.DataFrame(dischargeresponse.json())
    except ValueError:
        st.error("Invalid JSON response for OPD Appointments")
        st.write(dischargeresponse.text)
else:
    st.error(f"Error fetching OPD data: {dischargeresponse.status_code}")


radiologyresponse = requests.get(
    f"http://192.168.15.3/NewHIS/api/his/Get_Radiologypatientsearch"
)
if radiologyresponse.status_code == 200:
    try:
        radiology_data = pd.DataFrame(radiologyresponse.json())
    except ValueError:
        st.error("Invalid JSON response for OPD Appointments")
        st.write(radiologyresponse.text)
else:
    st.error(f"Error fetching OPD data: {radiologyresponse.status_code}")

# Initialize opd_data to an empty DataFrame
opd_data = pd.DataFrame()
# Fetch OPD data from the API
opdresponse = requests.get(
    f"http://192.168.15.3/NewHIS/api/his/Get_Doctorwiseappointmentlist?FromDate={today}&ToDate={today}"
)

if opdresponse.status_code == 200:
    opd_data = pd.DataFrame(opdresponse.json())
    
    # Check if DataFrame is empty
    if opd_data.empty:
        st.warning("No OPD data found for the selected date range.")
    else:
        #st.write("Available columns in OPD Data:", opd_data.columns.tolist())
        
        # Use the actual column names returned
        if 'patientName' in opd_data.columns:
            opd_count = opd_data["patientName"].count()
            #st.write("OPD Count:", opd_count)
        else:
            st.error("Column 'patientName' does not exist in the OPD data. Check the available columns.")
else:
    st.error(f"Error fetching OPD data: {opdresponse.status_code}")
    st.write(opdresponse.text) 
    st.write("Raw API Response:", opdresponse.text)


bedstatusresponse = requests.get(
    f"http://192.168.15.3/NewHIS/api/his/Get_BedStatusViewDetails"
)
if bedstatusresponse.status_code == 200:
    try:
        bedstatus_data = pd.DataFrame(bedstatusresponse.json())
    except ValueError:
        st.error("Invalid JSON response for OPD Appointments")
        st.write(bedstatusresponse.text)
else:
    st.error(f"Error fetching OPD data: {bedstatusresponse.status_code}")


def display_header(title, count):
    st.markdown(
        f"""
        <div class="header">
        <h3>{title}</h3>
        <p class="circle">{count}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def display_titleheader(title):
    st.markdown(
        f"""
        <div class="header1">
        <h3>{title}</h3>
    """,
        unsafe_allow_html=True,
    )


display_titleheader("SLT Dashboard")


def create_columns(data, num_columns=3):
    cols = st.columns(num_columns)
    for i, col in enumerate(cols):
        if i < len(data):
            col.metric(label=data[i][0], value=data[i][1])

if "patientName" in opd_data.columns:
    opd_count = opd_data["patientName"].count()
else:
    st.warning("Column 'patientName' does not exist in OPD data.")
    opd_count = 0  # Or handle it as appropriate


currentappointment, currentadmission, right = st.columns(3)
with currentappointment:
    opd_count = opd_data["patientName"].count()
    display_header("OPD Appointments", opd_count)

    doctor_counts = (
        opd_data.groupby("doctorName")
        .size()
        .reset_index(name="Appointments")
        .sort_values(by="Appointments", ascending=False)
    )

    fig = px.bar(
        doctor_counts,
        x="doctorName",
        y="Appointments",
        text="Appointments",
        labels={"DoctorName": "doctorName", "Appointments": "Total Appointments"},
    )
    fig.update_layout(
        title="Live Appointments by Doctor",
        xaxis=dict(
            tickangle=45,
            rangeslider_visible=True,
            range=[-0.5, 10],
        ),
        title_font=dict(color="royalblue"),
    )
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

with currentadmission:
    ip_count = bedstatus_data.shape[0]
    display_header("IP Occupancy", ip_count)

    admission_counts = (
        bedstatus_data.groupby("doctorname")
        .size()
        .reset_index(name="Admissions")
        .sort_values(by="Admissions", ascending=False)
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=admission_counts["doctorname"],
            y=admission_counts["Admissions"],
            mode="lines",
            fill="tozeroy",
            name="Admissions",
            line=dict(color="royalblue", width=2),
        )
    )
    fig.update_layout(
        title="Current Admissions by Doctor",
        xaxis=dict(
            title="Doctor", tickangle=45, rangeslider_visible=True, range=[-0.5, 10]
        ),
        yaxis=dict(title="Number of Admissions"),
        transition=dict(duration=1000),
        title_font=dict(color="royalblue"),
    )

    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)


with right:
    admission_count = admission_data[admission_data["uhid"] == "Admitted"].shape[0]
    discharge_count = discharge_data[discharge_data["uhid"] == "Discharged"].shape[0]
    admission_count = admission_data.shape[0]
    discharge_count = discharge_data.shape[0]

    st.write("admission", admission_count, "Discharge", discharge_count)

    bubble_data = {
        "Category": ["Admissions", "Discharges"],
        "Count": [admission_count, discharge_count],
        "Size": [admission_count, discharge_count],
    }

    fig_bubble = px.line(
        bubble_data,
        x="Category",
        y="Count",
        markers=True,
        title="Yesterday Admissions & Discharges",
        labels={"Count": "Count", "Category": "Category"},
    )

    st.plotly_chart(fig_bubble, use_container_width=True)


left1, middle1, right1 = st.columns(3)
with left1:
    ward_counts = (
        bedstatus_data.groupby("ward")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    ward_total = ward_counts["Count"].sum()
    display_header("Ward Occupancy", ward_total)

    fig = px.bar(
        ward_counts,
        x="ward",
        y="Count",
        text="Count",
        title="Ward Breakdown",
    )
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            rangeslider_visible=True,
            range=[-0.5, 10],
        ),
    )
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)


with middle1:
    icu_counts = (
        bedstatus_data[bedstatus_data["ward"].str.contains("ICU")]
        .groupby("ward")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    icu_total = icu_counts["Count"].sum()
    display_header("ICU Occupancy", icu_total)

    fig = px.line(
        icu_counts,
        x="ward",
        y="Count",
        text="Count",
        markers=True,
        title="ICU Occupancy",
    )
    fig.update_layout(
        xaxis=dict(tickangle=45),
        transition=dict(duration=1000),
    )
    st.plotly_chart(fig, use_container_width=True)

with right1:

    liver_departments = [
        "Hepatology",
        "Pediatric Hepatology",
        "Liver Disease and Transplantation",
    ]

    bedstatus_data["speciality"] = bedstatus_data["speciality"].apply(
        lambda x: "Liver" if x in liver_departments else "Non-Liver"
    )

    liver_count = bedstatus_data[bedstatus_data["speciality"] == "Liver"].shape[0]
    non_liver_count = bedstatus_data[bedstatus_data["speciality"] == "Non-Liver"].shape[
        0
    ]

    fig_pie = px.pie(
        names=["Liver", "Non-Liver"],
        values=[liver_count, non_liver_count],
        title="Liver vs Non-Liver Split",
    )

    display_header("Liver Occupancy", liver_count)
    st.plotly_chart(fig_pie, use_container_width=True)

    create_columns([("Liver", liver_count), ("Non-Liver", non_liver_count)])

left2, middle2 = st.columns(2)
with left2:
    ot_counts = (
        ot_data.groupby("departmentName")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    ot_total = ot_counts["Count"].sum()
    display_header("Operation Theater", ot_total)

    fig = px.bar(
        ot_counts,
        x="departmentName",
        y="Count",
        text="Count",
        title="OT Bookings",
    )
    fig.update_layout(xaxis=dict(tickangle=45))
    st.plotly_chart(fig, use_container_width=True)

with middle2:
    radiology_counts = (
        radiology_data.groupby("departmentName")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    radiology_total = radiology_counts["Count"].sum()
    display_header("Modality", radiology_total)

    fig = px.bar(
        radiology_counts,
        x="departmentName",
        y="Count",
        text="Count",
        title="Radiology Bookings",
    )
    fig.update_layout(xaxis=dict(tickangle=45))
    st.plotly_chart(fig, use_container_width=True)
ward1, ward2, ward3 = st.columns(3)
with ward1:
    ward_counts = (
        bedstatus_data.groupby("bedtype")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    ward_total = ward_counts["Count"].sum()
    display_header("Bed Category", ward_total)

    fig = px.bar(
        ward_counts,
        x="bedtype",
        y="Count",
        text="Count",
        title="Ward Breakdown",
    )
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            rangeslider_visible=True,
            range=[-0.5, 10],
        ),
    )
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)
with ward2:
    ward_counts = (
        bedstatus_data.groupby("nationality")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    ward_total = ward_counts["Count"].sum()
    display_header("Nationality", ward_total)

    fig = px.bar(
        ward_counts,
        x="nationality",
        y="Count",
        text="Count",
        title="Nationality Breakdown",
    )
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            rangeslider_visible=True,
            range=[-0.5, 10],
        ),
    )
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)
with ward3:
    ward_counts = (
        bedstatus_data.groupby("patType")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    ward_total = ward_counts["Count"].sum()
    display_header("Admission Type", ward_total)

    fig = px.bar(
        ward_counts,
        x="patType",
        y="Count",
        text="Count",
        title="Ward Breakdown",
    )
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            rangeslider_visible=True,
            range=[-0.5, 10],
        ),
    )
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

gen1, age = st.columns(2)
with gen1:
    ward_counts = (
        bedstatus_data.groupby("gender")
        .size()
        .reset_index(name="Count")
        .sort_values(by="Count", ascending=False)
    )
    ward_total = ward_counts["Count"].sum()
    display_header("Gender", ward_total)

    fig = px.pie(
        ward_counts,
        names="gender",
        values="Count",
        title="GENDER Breakdown",
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            rangeslider_visible=False,
            range=[-0.5, 10],
        ),
        transition=dict(duration=1000),
    )

    st.plotly_chart(fig, use_container_width=True)
with age:
    age_Data = bedstatus_data

    def convert_age(age_str):
        age_str = age_str.strip()
        if age_str.endswith("A"):
            return int(age_str[:-1])
        elif age_str.endswith("m"):
            return int(age_str[:-1]) / 12
        else:
            return None

    bedstatus_data["AgeInYears"] = bedstatus_data["age"].apply(convert_age)

    bedstatus_data["AgeGroup"] = bedstatus_data["AgeInYears"].apply(
        lambda x: "Adult" if x >= 18 else "Paediatric"
    )

    age_group_counts = bedstatus_data["AgeGroup"].value_counts().reset_index()
    age_group_counts.columns = ["AgeGroup", "Count"]

    ward_total = age_group_counts["Count"].sum()
    display_header("Adult vs Paediatric", ward_total)

    fig = px.pie(
        age_group_counts,
        names="AgeGroup",
        values="Count",
        title="Age Group Breakdown (Adult vs Paediatric)",
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            rangeslider_visible=False,
            range=[-0.5, 10],
        ),
        transition=dict(duration=1000),
    )

    st.plotly_chart(fig, use_container_width=True)