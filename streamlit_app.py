import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
candidates_df = pd.read_csv('candidates_with_phase.csv')
results_df = pd.read_csv('results_2024.csv')
winners_df = pd.read_csv('results_2024_winners.csv')
data_df = pd.read_csv('STATE2.csv')

# Merge datasets
merged_df1 = results_df.merge(candidates_df, 
                               left_on=['State', 'PC No', 'Candidate', 'Party'], 
                               right_on=['State', 'Constituency_No', 'Candidate Name', 'Party'])

merged_df = merged_df1.merge(winners_df, 
                               left_on=['State', 'PC No'], 
                               right_on=['State', 'PC No'])

# Selecting and renaming necessary columns to avoid confusion
merged_df = merged_df.rename(columns={
    'PC Name_x': 'PC Name',
    'Party_x': 'Party',
    'Total Votes': 'Total Votes'
})

# Convert 'Total Votes' to numeric, forcing errors to NaN, then fill NaNs with 0
merged_df['Total Votes'] = pd.to_numeric(merged_df['Total Votes'], errors='coerce').fillna(0)

# Streamlit app layout with sidebar
st.set_page_config(page_title='2024 Election Results Dashboard', layout='wide')

# Apply CSS styles to improve the visual appearance
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color:  #FFFFFF;
    }
    .reportview-container {
        background: #e0e4e7;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar content for Election Results
st.sidebar.title('2024 Election Results Dashboard')
st.sidebar.markdown('Explore the 2024 election results by state, constituency, party, and more.')

# Filters for election results
states = sorted(merged_df['State'].unique())  # Sort states alphabetically
selected_state = st.sidebar.selectbox('Select State', states)

filtered_df = merged_df[merged_df['State'] == selected_state]

# Additional Filters with Select All Option
parties = sorted(filtered_df['Party'].unique())  # Sort parties alphabetically
parties = ['Select All'] + list(parties)
selected_party = st.sidebar.multiselect('Select Party', parties, default='Select All')

if 'Select All' in selected_party:
    selected_party = filtered_df['Party'].unique()

candidates = sorted(filtered_df['Candidate Name'].unique())  # Sort candidates alphabetically
candidates = ['Select All'] + list(candidates)
selected_candidate = st.sidebar.multiselect('Select Candidate', candidates, default='Select All')

if 'Select All' in selected_candidate:
    selected_candidate = filtered_df['Candidate Name'].unique()

filtered_df = filtered_df[
    (filtered_df['Party'].isin(selected_party)) &
    (filtered_df['Candidate Name'].isin(selected_candidate))
]

# Constituency-wise results
st.header('Constituency-wise Election Results')
st.markdown("#### Visualize the election results for each constituency within the selected state.")
if not filtered_df.empty:
    fig = px.bar(filtered_df, x='PC Name', y='Total Votes', color='Party', barmode='group',
                  hover_data=['Candidate Name', 'Gender', 'Age', 'Application Status'])
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected filters.")

# Party performance
st.header('Party Performance Analysis')
st.markdown("#### Analyze the performance of each party based on total votes.")
if not filtered_df.empty:
    # Aggregate votes by party
    party_performance = filtered_df.groupby('Party')['Total Votes'].sum().reset_index()

    # Ensure there are no zero or missing values
    party_performance = party_performance[party_performance['Total Votes'] > 0]

    if not party_performance.empty:
        fig = px.pie(party_performance, values='Total Votes', names='Party', title='Party Performance')
        st.plotly_chart(fig)
    else:
        st.write("No votes recorded for parties in the selected filters.")
else:
    st.write("No data available for party performance in the selected filters.")

# Winning candidate profile
st.header('Winning Candidate Profile')
st.markdown(f"#### View the profile of winning candidates in {selected_state}.")
if not filtered_df.empty:
    winning_candidates_state = winners_df[winners_df['State'] == selected_state]  # Filter winners for the selected state
    winning_candidates_state = winning_candidates_state[['Winning Candidate', 'Winning Party', 'State', 'Margin Votes']].drop_duplicates()
    st.write(winning_candidates_state)
else:
    st.write(f"No data available for winning candidate profiles in {selected_state}.")

# State-wise summary
st.header('State-wise Summary')
st.markdown("#### Get a summary of election results by state.")
if not filtered_df.empty:
    state_summary = filtered_df.groupby(['State', 'Party'])['Total Votes'].sum().reset_index()
    fig = px.treemap(state_summary, path=['State', 'Party'], values='Total Votes', title='State-wise Summary of Results')
    st.plotly_chart(fig)
else:
    st.write("No data available for state-wise summary.")

# Voter Turnout Dashboard
st.sidebar.title('Voter Turnout Dashboard')
st.sidebar.markdown('Explore voter turnout and demographics data.')

# Show raw voter turnout data
if st.sidebar.checkbox('Show Raw Voter Data'):
    st.subheader('Raw Voter Data')
    st.write(data_df)

# Filters for voter turnout
states_voter = sorted(data_df['State/UT'].unique())
selected_state_voter = st.sidebar.selectbox('Select State/UT', states_voter)

# Filter the dataframe based on the selected state
filtered_voter_df = data_df[data_df['State/UT'] == selected_state_voter]

# Voter Turnout Visualization
st.header(f'Voter Turnout in {selected_state_voter}')
st.markdown("#### Voter turnout by gender")
if not filtered_voter_df.empty:
    # Create a bar chart for voter turnout
    fig_turnout = px.bar(filtered_voter_df, 
                          x='PC', 
                          y=['Male', 'Female', 'Others'], 
                          title='Voter Turnout by Gender',
                          labels={'value': 'Number of Voters', 'variable': 'Gender'},
                          barmode='group')
    st.plotly_chart(fig_turnout)
else:
    st.write("No data available for the selected state.")

# Total Voter Turnout
total_voters = filtered_voter_df['Total'].sum()
st.subheader('Total Voter Turnout')
st.write(f'Total Voters: {total_voters}')

# Voter Demographics Visualization
st.header(f'Voter Demographics in {selected_state_voter}')
if not filtered_voter_df.empty:
    # Prepare data for the pie chart
    demographics_data = {
        'Gender': ['Male', 'Female', 'Others'],
        'Count': [filtered_voter_df['Male'].sum(), filtered_voter_df['Female'].sum(), filtered_voter_df['Others'].sum()]
    }
    demographics_df = pd.DataFrame(demographics_data)

    fig_demographics = px.pie(demographics_df, 
                               names='Gender', 
                               values='Count', 
                               title='Voter Demographics Distribution',
                               color_discrete_sequence=px.colors.qualitative.Set1)
    st.plotly_chart(fig_demographics)
else:
    st.write("No demographic data available for the selected state.")

# Download option for filtered election results
st.sidebar.header('Download Election Data')
csv_election = filtered_df.to_csv(index=False)
st.sidebar.download_button(label='Download Election Data CSV', data=csv_election, file_name=f'{selected_state}_election_results.csv', mime='text/csv')

# Download option for filtered voter data
st.sidebar.header('Download Voter Data')
csv_voter = filtered_voter_df.to_csv(index=False)
st.sidebar.download_button(label='Download Voter Data CSV', data=csv_voter, file_name=f'{selected_state_voter}_voter_data.csv', mime='text/csv')
