import streamlit as st
import math


class MortgageCalculator:
    TYPES = [
        "Monthly Mortgage Estimation",
        "Home Affordability Estimation",
        "Upfront Costs Estimation",
    ]

    def __init__(self):
        self.render()

    def render(self):
        # Sidebar
        with st.sidebar:
            st.title("Calculators :1234:")
            self.select_page()

        # Main
        st.title("Mortgage Calculator :house:")
        if self.page == "Monthly Mortgage Estimation":
            return self.show_monthly_mortgage()
        if self.page == "Home Affordability Estimation":
            return self.show_home_affordability()
        if self.page == "Upfront Costs Estimation":
            return self.show_upfront_costs()

    def select_page(self):
        self.page = st.selectbox("*Select a calculator: :point_down:", self.TYPES)

    def show_monthly_mortgage(self):
        # Data Input
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

        # Calculations
        monthly_payment = self.calculate_monthly_payment(
            loan_amount, interest_rate, loan_tenure
        )

        # Display
        st.subheader("Monthly Mortgage Payment")
        st.write(f"${monthly_payment:,.2f} per month")

    def show_home_affordability(self):
        # Data Input
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)
        annual_income = st.number_input(
            "Annual Income ($)", min_value=20000, value=75000, step=1000
        )
        monthly_debts = st.number_input(
            "Monthly Debts ($)", min_value=0, value=500, step=50
        )
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.1, value=3.5)
        loan_tenure = st.number_input(
            "Loan Tenure (Years)", min_value=5, value=30, step=1
        )

        # Calculations
        max_home_price = self.calculate_home_affordability(
            annual_income, monthly_debts, interest_rate, loan_tenure
        )

        # Display
        st.subheader("Home Affordability")
        st.write(f"You can afford a home worth up to ${max_home_price:,.2f}")

    def show_upfront_costs(self):
        # Data Input
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

        # Calculations
        down_payment = self.calculate_down_payment(home_price, down_payment_percent)
        closing_costs = self.calculate_closing_costs(home_price, closing_costs_percent)
        total_upfront_costs = down_payment + closing_costs

        # Display
        st.subheader("Upfront Costs")
        st.write(f"Down Payment: ${down_payment:,.2f}")
        st.write(f"Closing Costs: ${closing_costs:,.2f}")
        st.write(f"Total Upfront Costs: ${total_upfront_costs:,.2f}")

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
        self, annual_income, monthly_debts, interest_rate, loan_tenure
    ):
        max_monthly_payment = (annual_income / 12) * 0.28 - monthly_debts
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

    def display_calculations(self, calculations):
        st.subheader("Calculations Summary")
        for key, value in calculations.items():
            st.write(f"{key}: ${value:,.2f}")

    # def display_results(self, input_data):
    #     with st.sidebar:
    #         # Toggle for automatic check
    #         auto_check = st.checkbox("Always Check Results")

    #         st.divider()

    #         if auto_check or st.button("Check Results"):
    #             result = self.calculate_results

    #             if "Slightly High" in result:
    #                 return st.warning(f"### Result >>> {result}")
    #             if "Pass" in result:
    #                 return st.success(f"### Result >>> {result}")
    #             if "Failed" in result:
    #                 return st.error(f"### Result >>> {result}")

    # def calculate_results(self, input_data):
    #     return ":red[_Failed_] :red_circle::poop:"
    #     return ":orange[_Pass (Slightly High)_] :large_orange_circle:"
    #     return ":green[_Pass_] :large_green_circle::ok_hand:"


if __name__ == "__main__":
    st.set_page_config("Mortgage Calculator", page_icon=":house:")
    MortgageCalculator()
