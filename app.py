# app.py

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import requests
import pandas as pd
import os
import datetime
from datetime import datetime, timedelta
# import statsmodels

# Initialize the Dash app
# Commented out for testing
app = Dash(__name__) # , server=False)  # Standalone Dash app without own server

# Function to load data from the Flask server
def fetch_data():
    response = requests.get("http://127.0.0.1:5000/data")  # URL for Flask data route
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()  # Empty DataFrame in case of error

# Initial data load
data = fetch_data()

# Test Data Reading
# Specify the folder containing the CSV files
folder_path = '/Users/cameronrichards/Downloads/545_group_data'

# List all files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize an empty list to hold the DataFrames
dfs = []

# Loop through each CSV file and read it into a DataFrame
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = df = pd.read_csv(file_path, parse_dates=['salesdate'])
    dfs.append(df)

# Concatenate all the DataFrames into a single DataFrame
data = pd.concat(dfs, ignore_index=True)

data

# Layout for the Dash app
app.layout = html.Div([

    # Header section
    html.Div([
        html.H1("Sales Dashboard", style={'color': '#00457C', 'textAlign': 'center', 'font-family': 'Arial'}),
        html.Hr(style={'border': '1px solid #eaeaea'})
        ], style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.1)'}),
    
    # Boxes for displaying metrics
    html.H2("Last Week's Figures", style={'color': '#00457C', 'textAlign': 'center', 'font-family': 'Arial'}),

    html.Div([
        html.Div(id='freeship-percent-box', style={'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'backgroundColor': '#ffffff'}),
        html.Div(id='products-sold-box', style={'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'backgroundColor': '#ffffff'}),
        html.Div(id='avg-discount-box', style={'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'backgroundColor': '#ffffff'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '20px 0'}),
    

    html.H2("Overall Figures", style={'color': '#00457C', 'textAlign': 'center', 'font-family': 'Arial'}),
    
    # Filters section
    html.Div([
        html.Label("Select Regions:", style={'font-family': 'Arial'}),
        dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': region, 'value': region} for region in sorted(data['region'].unique())],
            multi=True,
            placeholder="Select regions..."
        ),
        html.Label("Select Date Range:", style={'marginTop': '20px', 'font-family': 'Arial'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date= data['salesdate'].min(),
            end_date=data['salesdate'].max(),
            display_format='YYYY-MM-DD'
        )
    ], style={'float': 'left', 'width': '25%', 'padding': '20px', 'backgroundColor': '#f4f4f4', 'borderRadius': '8px'}),

    # Main content section
    html.Div([
        # Sales Trend
        dcc.Graph(id='sales-trend'),

        # Sales by Region
        dcc.Graph(id='region-sales'),

        # Controls for Top Products
        html.Div([
            html.Label("Number of Top Products to Display:", style={'font-family': 'Arial'}),
            dcc.Slider(
                id='num-products-slider',
                min=1,
                max=20,
                step=1,
                value=10,  # Default to 10 products
                marks={i: str(i) for i in range(1, 21)}
            )
        ], style={'margin-top': '20px'}),

        # Top Products by Items Sold
        dcc.Graph(id='top-products'),

        html.Label("Select Number of Bins for Discount:", style={'marginTop': '20px', 'font-family': 'Arial'}),
        dcc.Slider(
            id='bin-slider',
            min=1,
            max=20,
            step=1,
            value=10,  # Default to 10 bins
            marks={i: str(i) for i in range(1, 21)}
        ),
        dcc.Graph(id='discount-impact')
        
    ], style={'float': 'right', 'width': '70%', 'padding': '5px'})
], style={'font-family': 'Arial', 'backgroundColor': '#fafafa'})

# Callback to update visualizations based on filters
@app.callback(
    [Output('sales-trend', 'figure'),
     Output('region-sales', 'figure'),
     Output('discount-impact', 'figure'),
     Output('top-products', 'figure'),
     Output('freeship-percent-box', 'children'),
     Output('products-sold-box', 'children'),
     Output('avg-discount-box', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('region-dropdown', 'value'),
     Input('bin-slider', 'value'),
     Input('num-products-slider', 'value')]
)
def update_graphs(start_date, end_date, selected_regions, num_bins, num_products):

    # Re-fetch data for each page reload

    # Commented out for testing
    # data = data  # fetch_data()

    # Filter based on user inputs
    filtered_data = data[(data['salesdate'] >= pd.to_datetime(start_date)) & 
                         (data['salesdate'] <= pd.to_datetime(end_date))]
    
    box_data = data

    if selected_regions:
        filtered_data = filtered_data[filtered_data['region'].isin(selected_regions)]

    # Visualizations
    # Daily Sales Trend Visualization
    daily_sales = filtered_data.groupby('salesdate')['itemssold'].sum().reset_index()
    sales_trend_fig = px.line(daily_sales, x='salesdate', y='itemssold', title="Items Sold Each Day",
                              labels={'salesdate': 'Sales Date', 'itemssold': 'Items Sold'})
    # Add trend line to the sales trend figure
    sales_trend_fig.add_trace(
        px.scatter(daily_sales, x='salesdate', y='itemssold', trendline="ols").data[1]
    )
    sales_trend_fig.data[-1].line.color = 'red'
    
    # Sales by Region Visualization
    region_sales = filtered_data.groupby('region')['itemssold'].sum().reset_index()
    region_sales_fig = px.bar(region_sales, x='region', y='itemssold', color='region', 
                            title="Total Items Sold by Region",
                            labels={'region': 'Region', 'itemssold': 'Items Sold'})

    # Average Discount Impact Visualization
    bins = pd.cut(filtered_data['discount'], bins=num_bins)
    filtered_data['discount_bin'] = bins.apply(lambda x: f"{x.left:.2f}-{x.right:.2f}")
    avg_sales_per_bin = filtered_data.groupby('discount_bin')['itemssold'].mean().reset_index()
    avg_sales_per_bin.columns = ['Discount Bin', 'Average Items Amount']
    average_discount_impact_fig = px.bar(avg_sales_per_bin, x='Discount Bin', y='Average Items Amount', labels={'Discount Bin': 'Discount Bin', 'Average Items Amount': 'Average Items Sold'}, title='Average Items per Bin')

    # Top Products Visualization
    top_products = filtered_data.groupby('productid')['itemssold'].sum().reset_index()
    top_products['productid'] = top_products['productid'].astype(str)
    top_products = top_products.sort_values('itemssold', ascending=False).head(num_products).reset_index(drop=True)
        
    top_products_fig = px.bar(top_products, x='productid', y='itemssold', 
                          title='Top Products Sold', 
                          category_orders={'productid': top_products['productid']},
                          labels={'productid': 'Product ID', 'itemssold': 'Items Sold'})

    # Add labels above each bar
    top_products_fig.update_traces(texttemplate='%{y}', textposition='outside')

    # Calculate metrics for the last week
    last_week = datetime.now() - timedelta(days=7)
    last_week_data = box_data[box_data['salesdate'] >= last_week]

    if last_week_data.empty:
        freeship_percent = "No data"
        products_sold = "No data"
        avg_discount = "No data"
    else:
        freeship_percent = f"Free Shipping: {last_week_data['freeship'].mean() * 100:.2f}%"
        products_sold = f"Products Sold: {last_week_data['productid'].count()}"
        avg_discount = f"Average Discount: {last_week_data['discount'].mean():.2f}%"

    # Return the figures
    return sales_trend_fig, region_sales_fig, average_discount_impact_fig, top_products_fig, freeship_percent, products_sold, avg_discount
    

# Run Dash app
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
