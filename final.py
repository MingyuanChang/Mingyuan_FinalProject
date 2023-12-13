import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

#open data
school_data = pd.read_csv("data/school_data.csv")

#create interface
st.set_page_config(layout="wide")
st.sidebar.title("Filters")

#select the visualization
vis=st.sidebar.radio("Select Your Question:",
                     options=["Question 1",
                              "Question 2",
                              "Question 3"])

if vis=="Question 1":
    #Create interface for Q1
    st.title("Question 1: In different years, what is the percentage of subsidized students in various public schools across different districts?")

    #分割DBN中的区号
    def extract_first_two_digits(value):
        if pd.notna(value):  # 检查值是否不是 NaN（如果是字符串则不需要此检查）
            return str(value)[:2]
        else:
            return None

    school_data['District Number'] = school_data['DBN'].apply(extract_first_two_digits)

    #合并frl_percent 和 fl_percent列并创建新列
    school_data['percentage'] = school_data['frl_percent'].combine_first(school_data['fl_percent'])
    school_data['percentage'] = school_data['percentage'].fillna(0)

    #转换年份数字
    school_data['schoolyear'] = school_data['schoolyear'].astype(str)
    school_data['schoolyear'] = school_data['schoolyear'].apply(lambda x: f"{x[:4]}-20{x[6:]}")

    # Add a selectbox to the sidebar for year selection
    st.sidebar.markdown("**School Year**")
    selected_year = st.sidebar.selectbox(
        'Select the School Year',
        options=school_data['schoolyear'].unique(),
    )

    # Add a selectbox to the sidebar for district selection
    st.sidebar.markdown("**District Number**")
    selected_district = st.sidebar.selectbox(
        'Select the District Number',
        options=sorted(school_data['District Number'].unique()),
    )

    # Add checkboxes to show only the top/bottom 10 rows
    st.sidebar.markdown("**Top 10 / Bottom 10**")
    show_top_10 = st.sidebar.checkbox("Show Top 10 Rows", value=False)
    show_bottom_10 = st.sidebar.checkbox("Show Bottom 10 Rows", value=False)

    filtered_df = school_data[(school_data['schoolyear'] == selected_year) &
                              (school_data['District Number'] == selected_district)]

    # Ensure 'percentage' column is of numeric type
    filtered_df['percentage'] = pd.to_numeric(filtered_df['percentage'], errors='coerce')

    # Sort the data by 'percentage' column in ascending order
    filtered_df = filtered_df.sort_values(by='percentage', ascending=False)

    # Display bar charts based on the checkboxes
    if show_top_10 and not show_bottom_10:
        st.subheader("Top 10 Rows")
        top_10_df = filtered_df.head(10)
        fig_top_10 = px.bar(top_10_df, x='Name', y='percentage', text="percentage", hover_name="percentage",
                            labels={'percentage': 'Percentage', 'Name': 'School Name'})
        st.plotly_chart(fig_top_10)

    elif show_bottom_10 and not show_top_10:
        st.subheader("Bottom 10 Rows")
        bottom_10_df = filtered_df.tail(10)
        fig_bottom_10 = px.bar(bottom_10_df, x='Name', y='percentage', text="percentage", hover_name="percentage",
                               labels={'percentage': 'Percentage', 'Name': 'School Name'})
        st.plotly_chart(fig_bottom_10)

    elif show_bottom_10 and show_top_10:
        st.subheader("Top 10 Rows")
        top_10_df = filtered_df.head(10)
        fig_top_10 = px.bar(top_10_df, x='Name', y='percentage', text="percentage", hover_name="percentage",
                               labels={'percentage': 'Percentage', 'Name': 'School Name'})
        st.plotly_chart(fig_top_10)

        st.subheader("Bottom 10 Rows")
        bottom_10_df = filtered_df.tail(10)
        fig_bottom_10 = px.bar(bottom_10_df, x='Name', y='percentage', text="percentage", hover_name="percentage",
                            labels={'percentage': 'Percentage', 'Name': 'School Name'})
        st.plotly_chart(fig_bottom_10)

    elif not show_top_10 and not show_bottom_10:
        st.subheader("All Rows")
        fig_all_rows = px.bar(filtered_df, x='Name', y='percentage', text="percentage", hover_name="percentage",
                              labels={'percentage': 'Percentage', 'Name': 'School Name'})
        st.plotly_chart(fig_all_rows)

    # Display a message if no data is available for the selected filters
    if filtered_df.empty and (show_top_10 or show_bottom_10):
        st.write("No data available for the selected filters.")

elif vis == "Question 2":
    st.title("Question 2: In different years, how is the racial distribution among students in public schools across various districts?")
    st.title("")

    # Splitting DBN into district number
    def extract_first_two_digits(value):
        return str(value)[:2] if pd.notna(value) else None

    school_data['District Number'] = school_data['DBN'].apply(extract_first_two_digits)

    # Group by 'District Number' and sum the columns
    district_data = school_data.groupby('District Number').agg({
        'asian_num': 'sum',
        'black_num': 'sum',
        'hispanic_num': 'sum',
        'white_num': 'sum'
    }).reset_index()

    # Keep only the first row for each 'District Number' group
    district_data = district_data.drop_duplicates(subset='District Number', keep='first')

    # Merge the aggregated data with the original data
    school_data = school_data.merge(district_data, on='District Number', suffixes=('', '_sum'))

    # Convert schoolyear to a formatted string
    school_data['schoolyear'] = school_data['schoolyear'].astype(str)
    school_data['schoolyear'] = school_data['schoolyear'].apply(lambda x: f"{x[:4]}-20{x[6:]}")

    # Add a selectbox to the sidebar for year selection
    st.sidebar.markdown("**School Year**")
    selected_year = st.sidebar.selectbox(
        'Select the School Year',
        options=school_data['schoolyear'].unique(),
    )

    # Add a selectbox to the sidebar for district selection
    st.sidebar.markdown("**District Number**")
    selected_district = st.sidebar.multiselect(
        'Select the District Number',
        options=sorted(school_data['District Number'].unique()),
    )

    filtered_df2 = school_data[(school_data['schoolyear'] == selected_year) &
                               (school_data['District Number'].isin(selected_district))]

    # Rename columns
    filtered_df2 = filtered_df2.rename(columns={
        'asian_num_sum': 'Asian',
        'black_num_sum': 'Black',
        'hispanic_num_sum': 'Hispanic',
        'white_num_sum': 'White'
    })

    # Filtered data for pie charts
    pie_charts = []
    for district_number in selected_district:
        pie_data = filtered_df2[filtered_df2['District Number'] == district_number][
            ['Asian', 'Black', 'Hispanic', 'White']].sum()
        pie_chart = px.pie(pie_data, names=pie_data.index, values=pie_data.values, title=f'Racial Distribution - District {district_number}')
        pie_charts.append(pie_chart)

    # Display multiple pie charts
    for pie_chart in pie_charts:
        st.plotly_chart(pie_chart)

elif vis == "Question 3":
    st.title("Question 3: In different years, which district has the highest percentage of special education students?")
    st.title("")


    # 分割DBN中的区号
    def extract_first_two_digits(value):
        if pd.notna(value):  # 检查值是否不是 NaN（如果是字符串则不需要此检查）
            return str(value)[:2]
        else:
            return None


    school_data['District Number'] = school_data['DBN'].apply(extract_first_two_digits)

    # 合并frl_percent 和 fl_percent列并创建新列
    school_data['percentage'] = school_data['frl_percent'].combine_first(school_data['fl_percent'])
    school_data['percentage'] = school_data['percentage'].fillna(0)

    # 转换年份数字
    school_data['schoolyear'] = school_data['schoolyear'].astype(str)
    school_data['schoolyear'] = school_data['schoolyear'].apply(lambda x: f"{x[:4]}-20{x[6:]}")

    # 使用groupby和agg计算每个schoolyear中，不同的District Number的sped_percent平均值并保留一位小数
    aggregated_df = school_data.groupby(['schoolyear', 'District Number'])['sped_percent'].mean().reset_index()
    aggregated_df['sped_percent'] = aggregated_df['sped_percent'].round(1)

    # Add a selectbox to the sidebar for year selection
    st.sidebar.markdown("**School Year**")
    selected_year = st.sidebar.multiselect(
        'Select the School Year',
        options=school_data['schoolyear'].unique(),
    )

    # Add checkboxes to show only the top/bottom 10 rows
    st.sidebar.markdown("**Top 10 / Bottom 10**")
    show_top_10 = st.sidebar.checkbox("Show Top 10 Rows", value=False)
    show_bottom_10 = st.sidebar.checkbox("Show Bottom 10 Rows", value=False)

    for selected_year in selected_year:
        # Filter data based on selected year
        filtered_df3 = aggregated_df[aggregated_df['schoolyear'] == selected_year]

        # Rename the 'sped_percent' column to 'Special Education Percent'
        filtered_df3 = filtered_df3.rename(columns={'sped_percent': 'Special Education Percent'})

        # Ensure 'Special Education Percent' column is of numeric type
        filtered_df3['Special Education Percent'] = pd.to_numeric(filtered_df3['Special Education Percent'],
                                                                  errors='coerce')

        # Sort data frame by 'Special Education Percent' in descending order
        filtered_df3 = filtered_df3.sort_values(by='Special Education Percent', ascending=False)

        st.subheader(f"School Year: {selected_year}")

        if show_top_10 and not show_bottom_10:
            st.subheader("Top 10 Rows")
            top_10_df = filtered_df3.head(10)
            fig = px.bar(top_10_df, x="District Number", y="Special Education Percent",
                         text="Special Education Percent", hover_name="Special Education Percent")
            fig.update_xaxes(type='category')
            st.plotly_chart(fig)

        elif show_bottom_10 and not show_top_10:
            st.subheader("Bottom 10 Rows")
            bottom_10_df = filtered_df3.tail(10)
            fig = px.bar(bottom_10_df, x="District Number", y="Special Education Percent",
                         text="Special Education Percent", hover_name="Special Education Percent")
            fig.update_xaxes(type='category')
            st.plotly_chart(fig)

        elif show_top_10 and show_bottom_10:
            st.subheader("Top 10 Rows")
            top_10_df = filtered_df3.head(10)
            fig_top_10 = px.bar(top_10_df, x="District Number", y="Special Education Percent",
                                text="Special Education Percent", hover_name="Special Education Percent")
            fig_top_10.update_xaxes(type='category')
            st.plotly_chart(fig_top_10)

            st.subheader("Bottom 10 Rows")
            bottom_10_df = filtered_df3.tail(10)
            fig_bottom_10 = px.bar(bottom_10_df, x="District Number", y="Special Education Percent",
                                   text="Special Education Percent", hover_name="Special Education Percent")
            fig_bottom_10.update_xaxes(type='category')
            st.plotly_chart(fig_bottom_10)

        elif not show_top_10 and not show_bottom_10:
            st.subheader("All Rows")
            fig = px.bar(filtered_df3, x="District Number", y="Special Education Percent",
                         text="Special Education Percent", hover_name="Special Education Percent")
            fig.update_xaxes(type='category')
            st.plotly_chart(fig)


