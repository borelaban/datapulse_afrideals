import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stNumberInput, .stTextInput, .stSelectbox {
        margin-bottom: 1rem;
    }
    .stAlert {
        padding: 1rem;
    }
    .metric-box {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class MarketSizeEstimator:
    def __init__(self):
        self.market_data = {}
        self.company_data = pd.DataFrame(columns=[
            'name', 'sector', 'employees', 'years_established', 
            'capex', 'revenue', 'revenue_source', 'confidence'
        ])
    
    def add_market_data(self, sector: str, total_market_size: float, 
                       known_companies: Dict[str, float]):
        """Register market size data for a sector"""
        X = sum(known_companies.values())
        Z = total_market_size - X
        
        remaining_companies = len(self.company_data[
            (self.company_data['sector'] == sector) & 
            (~self.company_data['name'].isin(known_companies.keys()))
        ])
        
        self.market_data[sector] = {
            'Y': total_market_size,
            'X': X,
            'Z': Z,
            'known_companies': known_companies,
            'avg_small_player_revenue': Z / remaining_companies if remaining_companies else 0
        }
    
    def estimate_company_revenue(self, company_name: str, 
                               indicators: Dict[str, float]):
        """Estimate revenue for a company within the Z segment"""
        sector = self.company_data.loc[
            self.company_data['name'] == company_name, 'sector'].iloc[0]
        
        if sector not in self.market_data:
            raise ValueError(f"No market data for sector: {sector}")
            
        md = self.market_data[sector]
        
        # If company is in known players list
        if company_name in md['known_companies']:
            return {
                'revenue': md['known_companies'][company_name],
                'source': 'reported',
                'confidence': 'high'
            }
        
        # Calculate weight based on indicators
        weights = self._calculate_weights(indicators)
        estimated_revenue = md['avg_small_player_revenue'] * weights['total']
        
        # Quality check - shouldn't exceed remaining Z
        sector_companies = self.company_data[self.company_data['sector'] == sector]
        current_z_sum = sector_companies[
            ~sector_companies['name'].isin(md['known_companies'].keys())
        ]['revenue'].sum()
        
        if current_z_sum + estimated_revenue > md['Z']:
            raise ValueError(
                f"Estimation would exceed remaining Z market size ({md['Z']}) "
                f"for sector {sector}. Current Z sum: {current_z_sum}"
            )
        
        return {
            'revenue': estimated_revenue,
            'source': 'estimated',
            'confidence': 'medium',
            'weights': weights
        }
    
    def _calculate_weights(self, indicators: Dict[str, float]):
        """Calculate composite weighting based on company indicators"""
        weights = {
            'employees': min(indicators.get('employees', 0) / 100, 3),
            'capex': min(indicators.get('capex', 0) / 1e6, 2),
            'age': min(indicators.get('years_established', 0) / 10, 1.5)
        }
        
        if 'market_share_estimate' in indicators:
            return {
                'total': indicators['market_share_estimate'],
                'primary_factor': 'market_share'
            }
        
        total = 0.5 * weights['employees'] + 0.3 * weights['capex'] + 0.2 * weights['age']
        return {
            'total': max(0.1, min(total, 3)),
            'factors': weights
        }

# Initialize estimator in session state
if 'estimator' not in st.session_state:
    st.session_state.estimator = MarketSizeEstimator()

# App title
st.title("African Companies Financial Estimator")
st.markdown("""
Estimate revenues for African companies using market-size methodology:
1. **Y** = Total market size (from industry reports)
2. **X** = Known players' revenue (public data)
3. **Z** = Remaining market (Y - X)
""")

# Sidebar for market data input
with st.sidebar:
    st.header("Market Data Configuration")
    
    with st.form("market_data_form"):
        sector = st.text_input("Sector Name", "Pharmaceuticals")
        total_market = st.number_input("Total Market Size (Y, USD millions)", 
                                     min_value=1.0, value=100.0)
        
        st.subheader("Major Players (X)")
        col1, col2 = st.columns(2)
        known_companies = {}
        
        with col1:
            company1 = st.text_input("Company 1", "MarketLeader1")
            revenue1 = st.number_input("Revenue (USD M)", key="r1", value=20.0)
            known_companies[company1] = revenue1 * 1e6
            
        with col2:
            company2 = st.text_input("Company 2", "MarketLeader2")
            revenue2 = st.number_input("Revenue (USD M)", key="r2", value=15.0)
            known_companies[company2] = revenue2 * 1e6
        
        if st.form_submit_button("Save Market Data"):
            st.session_state.estimator.add_market_data(
                sector=sector,
                total_market_size=total_market * 1e6,
                known_companies=known_companies
            )
            st.success(f"Market data saved for {sector} sector")

# Main content area
tab1, tab2, tab3 = st.tabs(["Add Companies", "Run Estimates", "Market Analysis"])

with tab1:
    st.header("Add Companies to Dataset")
    
    with st.form("company_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Company Name", "PharmaCo1")
            sector = st.selectbox(
                "Sector",
                list(st.session_state.estimator.market_data.keys()) + ["New Sector"],
                index=0
            )
            employees = st.number_input("Number of Employees", min_value=1, value=50)
        
        with col2:
            years_established = st.number_input("Years Established", min_value=0, value=5)
            capex = st.number_input("Annual Capex (USD thousands)", min_value=0.0, value=500.0)
            market_share = st.number_input("Market Share Estimate (%)", min_value=0.0, max_value=100.0, value=0.0)
        
        if st.form_submit_button("Add Company"):
            new_company = {
                'name': name,
                'sector': sector,
                'employees': employees,
                'years_established': years_established,
                'capex': capex * 1000,
                'market_share_estimate': market_share / 100 if market_share else None,
                'revenue': None,
                'revenue_source': None,
                'confidence': None
            }
            
            # Add to DataFrame
            index = len(st.session_state.estimator.company_data)
            for col, value in new_company.items():
                st.session_state.estimator.company_data.loc[index, col] = value
            
            st.success(f"Added {name} to dataset")

with tab2:
    st.header("Run Revenue Estimates")
    
    if not st.session_state.estimator.company_data.empty:
        # Display companies needing estimates
        companies_to_estimate = st.session_state.estimator.company_data[
            st.session_state.estimator.company_data['revenue'].isna()
        ]
        
        if not companies_to_estimate.empty:
            st.write("Companies needing revenue estimates:")
            st.dataframe(companies_to_estimate[['name', 'sector', 'employees']])
            
            if st.button("Run All Estimates"):
                progress_bar = st.progress(0)
                results = []
                
                for i, row in companies_to_estimate.iterrows():
                    try:
                        indicators = {
                            'employees': row['employees'],
                            'years_established': row['years_established'],
                            'capex': row['capex'],
                            'market_share_estimate': row.get('market_share_estimate')
                        }
                        
                        result = st.session_state.estimator.estimate_company_revenue(
                            company_name=row['name'],
                            indicators=indicators
                        )
                        
                        # Update company data
                        st.session_state.estimator.company_data.at[i, 'revenue'] = result['revenue']
                        st.session_state.estimator.company_data.at[i, 'revenue_source'] = result['source']
                        st.session_state.estimator.company_data.at[i, 'confidence'] = result['confidence']
                        
                        results.append({
                            'Company': row['name'],
                            'Revenue (USD M)': result['revenue'] / 1e6,
                            'Source': result['source'],
                            'Confidence': result['confidence']
                        })
                    
                    except ValueError as e:
                        results.append({
                            'Company': row['name'],
                            'Revenue (USD M)': "Error",
                            'Source': "Failed",
                            'Confidence': str(e)
                        })
                    
                    progress_bar.progress((i + 1) / len(companies_to_estimate))
                
                st.success("Estimation complete!")
                st.dataframe(pd.DataFrame(results))
        
        # Show current data
        st.subheader("Current Company Data")
        display_df = st.session_state.estimator.company_data.copy()
        display_df['revenue'] = display_df['revenue'].apply(
            lambda x: f"{x/1e6:.2f}M" if pd.notna(x) else "Not estimated")
        st.dataframe(display_df)
        
        # Export options
        st.download_button(
            label="Download Data as CSV",
            data=st.session_state.estimator.company_data.to_csv(index=False),
            file_name="african_companies_estimates.csv",
            mime="text/csv"
        )
    else:
        st.warning("No companies added yet. Add companies in the first tab.")

with tab3:
    st.header("Market Analysis")
    
    if st.session_state.estimator.market_data:
        selected_sector = st.selectbox(
            "Select Sector to Analyze",
            list(st.session_state.estimator.market_data.keys())
        )
        
        md = st.session_state.estimator.market_data[selected_sector]
        
        # Market composition metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Market Size (Y)", f"${md['Y']/1e6:.1f}M")
        col2.metric("Major Players (X)", f"${md['X']/1e6:.1f}M ({md['X']/md['Y']:.0%})")
        col3.metric("Remaining Market (Z)", f"${md['Z']/1e6:.1f}M ({md['Z']/md['Y']:.0%})")
        
        # Visualization
        st.subheader("Market Composition")
        chart_data = pd.DataFrame({
            'Segment': ['Major Players (X)', 'Remaining Market (Z)'],
            'Value': [md['X'], md['Z']]
        })
        st.bar_chart(chart_data.set_index('Segment'))
        
        # List known players
        st.subheader("Major Players in Sector")
        known_players = pd.DataFrame.from_dict(md['known_companies'], orient='index', 
                                              columns=['Revenue']).sort_values('Revenue', ascending=False)
        known_players['Revenue (USD M)'] = known_players['Revenue'] / 1e6
        st.dataframe(known_players[['Revenue (USD M)']].style.format({'Revenue (USD M)': "{:.1f}"}))
    else:
        st.warning("No market data configured yet. Add market data in the sidebar.")

# Footer
st.markdown("---")
st.caption("African Companies Financial Estimator Method 1 | Market-Size Methodology")