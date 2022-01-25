import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

#-------------------------------------- CONSTANTS --------------------------------------#

COUNTRY_LIST = ["Brazil",
                "Canada",
                "France",
                "India",
                "Italy",
                "USA"]


LATLONG_COLUMN_NAMES = ["city",
                        "latitude",
                        "longitude"]

DATA_COLUMN_NAMES = ["Date",
                     "Country",
                     "City",
                     "Species",
                     "Count",
                     "Min",
                     "Max",
                     "Median",
                     "Variance"]

SPECIES_LIST = ["no2",
                "dew",
                "humidity",
                "temperature",
                "o3",
                "so2",
                "pm25",
                "pm10",
                "pressure",
                "windspeed",
                "windgust",
                "co"
                ]

MONTHS = ["01",
          "02",
          "03",
          "04",
          "05",
          "06",
          "07",
          "08",
          "09",
          "10",
          "11",
          "12"]

YEARS = ["2020", "2021"]


#-------------------------------------- FUNCTION DECLARATION --------------------------------------#

# EXTRACT LATLONG FOR EACH CITIES
def latlong_extract(current_country_city, latlong_list):
    city_list = []
    latlong_list.columns = LATLONG_COLUMN_NAMES

    for city in current_country_city:
        for a in latlong_list["city"]:
            if city == a:
                current_city = latlong_list[latlong_list["city"] == a]
                city_list.append(current_city)
    city_list = pd.concat(city_list)
    return city_list


# EXTRACT PARTICULATES DATA
def extract_particulate(country_data, species, start, end, city):
    particulate = country_data[country_data["Species"] == species]
    particulate = particulate[(particulate["Date"] >= start) & (particulate["Date"] <= end) & (particulate["City"] == city)]
    return particulate


# CHECK PARAMETERS AND EXTRACT DATA BASED ON PARAMETERS
def check_parameters(parameters, country_data, start, end, city):
    if len(parameters) == 0:
        st.error("Error: Please select at least 1 parameter.")

    else:
        current_data = []
        for param in parameters:
            param_data = extract_particulate(country_data, param, start, end, city)
            current_data.append(param_data)

        current_data = pd.concat(current_data)
        current_data = current_data.sort_values(["Date"], ascending=True)
        return current_data



# -------------------------------------- DATA PRE-PROCESSING -------------------------------------- #

# DATA CLEANING FOR EACH COUNTRY
brazil_data = pd.read_csv("brazil.csv")
brazil_data["Date"] = pd.to_datetime(brazil_data["Date"]).dt.date
brazil_data.columns = DATA_COLUMN_NAMES
brazil_city = brazil_data.City.unique()
brazil_latlong = pd.read_csv("brazil_latlong.csv")
brazil_latlong = brazil_latlong[["city", "lat", "lng"]]
brazil_city_latlong = latlong_extract(brazil_city, brazil_latlong)



canada_data = pd.read_csv("canada.csv")
canada_data["Date"] = pd.to_datetime(canada_data["Date"]).dt.date
canada_data.columns = DATA_COLUMN_NAMES
canada_city = canada_data.City.unique()
canada_latlong = pd.read_csv("canada_latlong.csv")
canada_latlong = canada_latlong[["city_ascii", "lat", "lng"]]
canada_city_latlong = latlong_extract(canada_city, canada_latlong)



france_data = pd.read_csv("france.csv")
france_data["Date"] = pd.to_datetime(france_data["Date"]).dt.date
france_data.columns = DATA_COLUMN_NAMES
france_city = france_data.City.unique()
france_latlong = pd.read_csv("france_latlong.csv")
france_latlong = france_latlong[["city", "lat", "lng"]]
france_city_latlong = latlong_extract(france_city, france_latlong)



india_data = pd.read_csv("india.csv")
india_data["Date"] = pd.to_datetime(india_data["Date"]).dt.date
india_data.columns = DATA_COLUMN_NAMES
india_city = india_data.City.unique()
india_latlong = pd.read_csv("india_latlong.csv")
india_latlong = india_latlong[["City", "Lat", "Long"]]
india_city_latlong = latlong_extract(india_city, india_latlong)



italy_data = pd.read_csv("italy.csv")
italy_data["Date"] = pd.to_datetime(italy_data["Date"]).dt.date
italy_data.columns = DATA_COLUMN_NAMES
italy_city = italy_data.City.unique()
italy_latlong = pd.read_csv("italy_latlong.csv")
italy_latlong = italy_latlong[["city", "lat", "lng"]]
italy_city_latlong = latlong_extract(italy_city, italy_latlong)



usa_data = pd.read_csv("usa.csv")
usa_data["Date"] = pd.to_datetime(usa_data["Date"]).dt.date
usa_data.columns = DATA_COLUMN_NAMES
usa_city = usa_data.City.unique()
usa_latlong = pd.read_csv("usa_latlong.csv")
usa_latlong = usa_latlong[["city_ascii", "lat", "lng"]]
usa_city_latlong = latlong_extract(usa_city, usa_latlong)



# COMBINE CITIES LATLONG
global_cities = [brazil_city_latlong, canada_city_latlong, france_city_latlong, india_city_latlong, italy_city_latlong, usa_city_latlong]
global_cities = pd.concat(global_cities)



# -------------------------------------- STREAMLIT CODE -------------------------------------- #

st.title(":cloud: Air Quality Dashboard :cloud:")



# SIDEBAR MENU
option = st.sidebar.selectbox(
    "Menu:",
    ["Main",
     "Air Quality Index",
     "Download"]
)



# -------------------------------------- HOMEPAGE CODE -------------------------------------- #

if option == "Main":
    st.write("Air quality is a measure of how clean or polluted the air is. Monitoring air quality is important because polluted air can be bad for our health and the health of the environment. ")
    st.write("This dashboard shows an analysis on the air quality across 6 countries (**Brazil, Canada, France, India, Italy and USA**) for the year 2020 - 2021.")


    # WORLD MAP WITH CITIES HIGHLIGHTED
    st.map(global_cities)



    # LATEST DATA BY EACH CITY AND COUNTRY
    st.header("Latest Data :earth_americas:")
    country_option = st.selectbox("Select a country:", COUNTRY_LIST).lower()


    # Create dataframe for the latest data of the selected country
    data_to_show = globals()[country_option + "_data"].sort_values(["Date"], ascending=True)
    last_date = data_to_show.iloc[-1, 0]
    data_to_show = data_to_show[data_to_show["Date"] == last_date].sort_values(["Date", "City"], ascending=True)
    data_to_show = data_to_show[["City", "Species", "Count", "Min", "Max"]]

    st.subheader(f"Data for {last_date}")

    # Plot histogram using Altair library
    chart1 = alt.Chart(data_to_show).mark_bar(opacity=0.7).encode(
        x=alt.X("City:N", title=f"{country_option.upper()} CITIES", axis=alt.Axis(labels=False)),
        y=alt.Y("Count:Q", title="Count"),
        color=alt.Color("City:N"),
        facet=alt.Facet("Species:N", columns=2),
        tooltip=["City", "Species", "Count"]
    ).properties(width=300, height=300
    ).interactive()

    st.write(chart1)



# -------------------------------------- OVERVIEW PAGE CODE -------------------------------------- #

elif option == "Air Quality Index":
    st.header(":cloud: Air Quality Index :cloud:")

    country_option1 = st.selectbox("Select a country:", COUNTRY_LIST, key="country1").lower()
    city_option1 = st.selectbox("Select a city:", globals()[country_option1 + "_city"], key="city1")
    year_option = st.selectbox("Select year:", YEARS, key="year")
    month_option = st.selectbox("Select month:", MONTHS, key="month")
    species_options = st.multiselect("Select air quality parameters:", SPECIES_LIST, key="species2", default=["no2"])

    # Create dataframe based on selected parameters (country, year, month and species)
    date_start1 = "1/" + month_option + "/" + year_option
    date_start1 = datetime.strptime(date_start1, "%d/%m/%Y").date()

    # Date end set
    if month_option == "01" or month_option == "03" or month_option == "05" or month_option == "07" or month_option == "08" or month_option == "10" or month_option == "12":
        date_end1 = "31/" + month_option + "/" + year_option
    elif month_option == "02":
        date_end1 = "28/" + month_option + "/" + year_option
    else:
        date_end1 = "30/" + month_option + "/" + year_option


    date_end1 = datetime.strptime(date_end1, "%d/%m/%Y").date()

    data_to_show2 = check_parameters(species_options, globals()[country_option1 + "_data"], date_start1, date_end1, city_option1)
    data_to_show2["Mean"] = (data_to_show2["Min"] + data_to_show2["Max"]) / 2


    # Display chart using Altair library
    hover2 = alt.selection(
        type="single",
        fields=["Date"],
        nearest=True,
        on="mouseover",
        empty="none",
        clear="mouseout"
    )

    base_chart2 = alt.Chart(data_to_show2).mark_line().encode(
        x="Date:T",
        y="Mean:Q",
        color="Species:N",
        tooltip=["Date"]
    ).properties(title=f"{month_option}-{year_option} Air Quality for {city_option1}, {country_option1.upper()}", width=800, height=600)

    line = base_chart2.mark_line(interpolate="monotone").encode(
        alt.Y("Mean:Q")
    )

    area = base_chart2.mark_area(opacity=0.3).encode(
        alt.Y("Max:Q", axis=alt.Axis(title="Daily Min-Max-Mean value")),
        alt.Y2("Min:Q")
    )

    points2 = base_chart2.mark_point().encode(opacity=alt.condition(hover2, alt.value(1), alt.value(0)))

    text2 = base_chart2.mark_text(align="left", dx=5, dy=-5).encode(
        text=alt.condition(hover2, "Mean", alt.value(" "))
    )

    tooltips2 = alt.Chart(data_to_show2).transform_pivot("Species", "Mean", groupby=["Date"]
                                                        ).mark_rule(strokeWidth=2, color="red").encode(
        x="Date:T", opacity=alt.condition(hover2, alt.value(3), alt.value(0))
    ).add_selection(hover2)

    chart2 = alt.layer(area, line, points2, text2, tooltips2)
    st.write(chart2)



# -------------------------------------- DOWNLOAD PAGE CODE -------------------------------------- #

else:
    st.header("Download")
    st.write("You can download the data used in this analysis.")

    download_data = st.radio(
        "Select country data:", COUNTRY_LIST).lower()


    @st.cache
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(globals()[download_data + "_data"])

    st.download_button(
        label="Download",
        data=csv,
        file_name=f"{download_data}.csv",
        mime='text/csv'
    )



st.sidebar.subheader("About this app")
st.sidebar.caption("This is a web app demo using [streamlit](https://streamlit.io/) library. It is hosted on [heroku](https://www.heroku.com/).")
st.sidebar.caption("For more info, please contact: [SarahMelina] (https://www.linkedin.com/in/sarahmelina/) on LinkedIn or see the code [here](https://github.com/mewowlina/air-quality).")