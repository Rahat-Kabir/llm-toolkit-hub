import streamlit as st
from phi.assistant import Assistant
from phi.agent import Agent
from phi.llm.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
import os

class StockAnalysisApp:
    def __init__(self):
        """Initialize the Stock Analysis Application with its core components"""
        # Initialize session state for API key validation
        if 'api_key_verified' not in st.session_state:
            st.session_state.api_key_verified = False
        if 'assistant' not in st.session_state:
            st.session_state.assistant = None
            
        self.setup_page()
        
    def setup_page(self):
        """Configure the Streamlit page with title and description"""
        st.set_page_config(
            page_title="Advanced Stock Analysis",
            page_icon="💸",
            layout="wide"
        )
        
    def verify_api_key(self, api_key):
        """Verify the OpenAI API key by attempting to create an assistant"""
        try:
            # Attempt to create an assistant with the provided key
            assistant = Assistant(
                llm=OpenAIChat(
                    model="gpt-4o",
                    api_key=api_key
                ),
                tools=[YFinanceTools(
                    stock_price=True,
                    analyst_recommendations=True,
                    company_info=True,
                    company_news=True
                )],
                show_tool_calls=True,
            )
            # Store the assistant in session state for reuse
            st.session_state.assistant = assistant
            st.session_state.api_key_verified = True
            return True
        except Exception as e:
            st.session_state.api_key_verified = False
            return False
    
    def show_sidebar_form(self):
        """Display the API key verification form in the sidebar"""
        with st.sidebar:
            st.title("Authentication")
            with st.form("api_key_form"):
                api_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Enter your OpenAI API key to access the analysis tools"
                )
                submitted = st.form_submit_button("Verify API Key")
                
                if submitted:
                    if api_key:
                        with st.spinner("Verifying API key..."):
                            if self.verify_api_key(api_key):
                                st.success("API key verified successfully!")
                            else:
                                st.error("Invalid API key. Please check and try again.")
                    else:
                        st.error("Please enter an API key.")
            
            if st.session_state.api_key_verified:
                st.sidebar.success("✅ API Key Status: Verified")
            
            # Add additional sidebar information
            with st.expander("About"):
                st.write("""
                This tool provides AI-powered stock analysis using OpenAI's GPT-4 
                and real-time market data. Compare stocks, analyze trends, and 
                get detailed insights to make informed investment decisions.
                """)
    
    def create_analysis_tabs(self):
        """Create tabs for different types of analysis"""
        tab1, tab2, tab3 = st.tabs([
            "Stock Comparison", 
            "Single Stock Analysis", 
            "Market Insights"
        ])
        return tab1, tab2, tab3
    
    def handle_stock_comparison(self, tab):
        """Handle the stock comparison functionality"""
        with tab:
            col1, col2 = st.columns(2)
            with col1:
                stock1 = st.text_input(
                    "First Stock Symbol",
                    placeholder="e.g., AAPL"
                )
            with col2:
                stock2 = st.text_input(
                    "Second Stock Symbol",
                    placeholder="e.g., MSFT"
                )
            
            if stock1 and stock2:
                analysis_type = st.selectbox(
                    "Choose Analysis Type",
                    ["Full Comparison", "Price Analysis", "Fundamentals", "News"]
                )
                
                if st.button("Generate Analysis"):
                    with st.spinner(f"Analyzing {stock1} and {stock2}..."):
                        query = self.generate_query(stock1, stock2, analysis_type)
                        response = st.session_state.assistant.run(query, stream=False)
                        st.markdown(response)
    
    def handle_single_stock(self, tab):
        """Handle single stock analysis functionality"""
        with tab:
            stock = st.text_input(
                "Enter Stock Symbol",
                placeholder="e.g., GOOGL"
            )
            
            if stock:
                metrics = st.multiselect(
                    "Select Metrics",
                    ["Price Trends", "Analyst Recommendations", "Company Info", "Recent News"]
                )
                
                if st.button("Analyze"):
                    with st.spinner(f"Analyzing {stock}..."):
                        query = f"Analyze {stock} focusing on {', '.join(metrics)}"
                        response = st.session_state.assistant.run(query, stream=False)
                        st.markdown(response)
    
    def generate_query(self, stock1, stock2, analysis_type):
        """Generate appropriate query based on analysis type"""
        queries = {
            "Full Comparison": f"Provide a comprehensive comparison between {stock1} and {stock2} including price trends, fundamentals, and market sentiment.",
            "Price Analysis": f"Compare price performance and technical indicators for {stock1} and {stock2}.",
            "Fundamentals": f"Compare key fundamental metrics and financial health of {stock1} and {stock2}.",
            "News": f"Compare recent news and market sentiment for {stock1} and {stock2}."
        }
        return queries.get(analysis_type, queries["Full Comparison"])
    
    def show_main_content(self):
        """Display the main content of the application"""
        st.title("AI Investment Analysis Dashboard 💸")
        st.caption("""
        Comprehensive stock analysis tool powered by AI. Compare stocks, 
        get real-time insights, and generate detailed investment reports.
        """)
        
        tab1, tab2, tab3 = self.create_analysis_tabs()
        self.handle_stock_comparison(tab1)
        self.handle_single_stock(tab2)
        
        with tab3:
            st.info("Market Insights feature coming soon!")
    
    def run(self):
        """Main application loop"""
        # Show the sidebar form for API key verification
        self.show_sidebar_form()
        
        # Only show main content if API key is verified
        if st.session_state.api_key_verified:
            self.show_main_content()
        else:
            st.warning("Please enter your OpenAI API key in the sidebar to begin.")

if __name__ == "__main__":
    app = StockAnalysisApp()
    app.run()