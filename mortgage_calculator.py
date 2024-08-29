import streamlit as st
import math
import plotly.express as px


class MortgageCalculator:
    """A Streamlit app for various mortgage-related calculations."""

    TYPES = [
        "Monthly Mortgage Estimation",
        "Home Affordability Estimation",
        "Upfront Costs Estimation",
    ]

    def __init__(self):
        st.session_state.setdefault("auto_check", True)
        st.session_state.setdefault("check_results", False)
        self.render()

    def render(self):
        # Reset check results
        st.session_state.check_results = False

        # Sidebar
        with st.sidebar:
            st.title("Calculators :1234:")
            self.page = st.selectbox("*Select an option: :point_down:", self.TYPES)
            self.auto_check = st.checkbox(
                "Always Check Results", value=st.session_state.auto_check
            )
            st.divider()

            if not self.auto_check:
                self.check_button()

        # Main
        st.title("Mortgage Calculator :house:")
        if self.page == "Monthly Mortgage Estimation":
            return self.show_monthly_mortgage()
        if self.page == "Home Affordability Estimation":
            return self.show_home_affordability()
        if self.page == "Upfront Costs Estimation":
            return self.show_upfront_costs()

    def check_button(self):
        if st.button("Check Results"):
            st.session_state.check_results = True

    def show_monthly_mortgage(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        loan_amount = st.number_input(
            "Loan Amount ($)", min_value=10000, value=300000, step=100000
        )
        interest_rate = st.number_input(
            "Interest Rate (%)", min_value=1.0, value=3.9, step=0.01
        )
        loan_tenure = st.number_input(
            "Loan Tenure (Years)", min_value=5, value=35, step=1
        )
        square_feet = st.number_input(
            "Total Square Feet", min_value=100, value=2000, step=100
        )
        maintenance_fees_per_sqft = st.number_input(
            "Maintenance Fees per Square Foot ($)", min_value=0.0, value=0.5, step=0.05
        )

        if self.auto_check or st.session_state.check_results:
            monthly_payment = self.calculate_monthly_payment(
                loan_amount, interest_rate, loan_tenure
            )
            maintenance_cost = square_feet * maintenance_fees_per_sqft
            total_monthly_payment = monthly_payment + maintenance_cost

            self.display_results(
                {
                    "Monthly Mortgage Payment": f"${monthly_payment:,.2f}",
                    "Maintenance Cost": f"${maintenance_cost:,.2f}",
                    "Total Monthly Payment": f"${total_monthly_payment:,.2f}",
                }
            )

    def show_home_affordability(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        monthly_income = st.number_input(
            "Monthly Income ($)", min_value=2000, value=7500, step=100
        )
        monthly_debts = st.number_input(
            "Monthly Debts ($)", min_value=0, value=500, step=50
        )
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.1, value=3.5)
        loan_tenure = st.number_input(
            "Loan Tenure (Years)", min_value=5, value=30, step=1
        )

        if self.auto_check or st.session_state.check_results:
            max_home_price = self.calculate_home_affordability(
                monthly_income, monthly_debts, interest_rate, loan_tenure
            )

            # Create a range of incomes for visualization
            incomes = list(
                range(3000, 15001, 1000)
            )  # Monthly incomes from 3k to MYR 15k
            affordabilities = [
                self.calculate_home_affordability(
                    income, monthly_debts, interest_rate, loan_tenure
                )
                for income in incomes
            ]

            fig = px.bar(
                x=incomes,
                y=affordabilities,
                labels={"x": "Monthly Income ($)", "y": "Maximum Home Price ($)"},
            )
            fig.update_layout(title="Home Affordability vs. Monthly Income")

            st.plotly_chart(fig)

            self.display_results({"Maximum Home Price": f"${max_home_price:,.2f}"})

    def show_upfront_costs(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        home_price = st.number_input(
            "Home Price ($)", min_value=50000, value=300000, step=10000
        )
        down_payment_percent = st.number_input(
            "Down Payment (%)", min_value=5, value=20, step=1
        )
        closing_costs_percent = st.number_input(
            "Closing Costs (%)", min_value=1.0, value=3.0, step=0.5
        )

        if self.auto_check or st.session_state.check_results:
            down_payment = self.calculate_down_payment(home_price, down_payment_percent)
            closing_costs = self.calculate_closing_costs(
                home_price, closing_costs_percent
            )
            total_upfront_costs = down_payment + closing_costs

            fig = px.pie(
                names=["Down Payment", "Closing Costs"],
                values=[down_payment, closing_costs],
                hole=0.4,
                labels={"names": "Category", "values": "Amount ($)"},
            )
            fig.update_layout(title="Upfront Costs Distribution")

            st.plotly_chart(fig)

            self.display_results(
                {
                    "Down Payment": f"${down_payment:,.2f}",
                    "Closing Costs": f"${closing_costs:,.2f}",
                    "Total Upfront Costs": f"${total_upfront_costs:,.2f}",
                }
            )

    # Utility Methods for Calculations
    def calculate_monthly_payment(self, loan_amount, interest_rate, loan_tenure):
        monthly_rate = interest_rate / 100 / 12
        num_payments = loan_tenure * 12

        if interest_rate == 0:
            return loan_amount / num_payments

        return (
            loan_amount
            * (monthly_rate * math.pow(1 + monthly_rate, num_payments))
            / (math.pow(1 + monthly_rate, num_payments) - 1)
        )

    def calculate_home_affordability(
        self, monthly_income, monthly_debts, interest_rate, loan_tenure
    ):
        # Assuming a debt-to-income ratio of 30%
        max_monthly_payment = (monthly_income * 0.30) - monthly_debts
        max_loan = (
            max_monthly_payment
            * (math.pow(1 + interest_rate / 100 / 12, loan_tenure * 12) - 1)
            / (
                interest_rate
                / 100
                / 12
                * math.pow(1 + interest_rate / 100 / 12, loan_tenure * 12)
            )
        )

        return max_loan

    def calculate_down_payment(self, home_price, down_payment_percent):
        return home_price * down_payment_percent / 100

    def calculate_closing_costs(self, home_price, closing_costs_percent):
        return home_price * closing_costs_percent / 100

    def display_results(self, results):
        with st.sidebar:
            st.subheader("Results", divider=True)

            for key, value in results.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{key}:**")
                with col2:
                    st.markdown(f"{value}")
            st.markdown("---")


if __name__ == "__main__":
    st.set_page_config("Mortgage Calculator", page_icon=":house:")
    MortgageCalculator()
