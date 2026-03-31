# Core Python imports
import datetime  # Used for date handling in deals and monthly reports
import json      # Used for data export/import functionality
import os        # Used for checking file existence in load_data()
from collections import defaultdict  # Used for organizing trash data and metrics
from typing import Dict, List  # Used for type hints in Deal class
import calendar  # Used for sorting months in plot_revenue_trend
import traceback  # Used for printing stack traces in exception handling

# GUI and Visualization imports
import tkinter as tk  # Main GUI framework for the dashboard
from tkinter import ttk  # Themed widgets for tabbed interface
import matplotlib.pyplot as plt  # Base plotting library for analytics
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embeds matplotlib in tkinter
from matplotlib.figure import Figure  # Used for creating figure instances
import numpy as np  # Used for array operations in plotting
import math  # Used for mathematical operations in EnhancedGraph
import turtle  # Used for drawing graphs in EnhancedGraph

class GraphManager:
    def __init__(self, root, trash_system):
        self.root = root
        self.trash_system = trash_system
        self.root.title("Trash Management Analytics Dashboard")
        self.root.geometry("1200x800")
        
        # Define colors for different categories
        self.colors = {
            "Plastic": "red",
            "Metal": "grey",
            "Books & Copies": "blue",
            "Electronics": "black",
            "Cloths": "purple",
            "Glass": "orange",
            "Household Waste": "green",
            "Dump Waste": "yellow"
        }
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_category_comparison_tab()
        self.create_revenue_trend_tab()
        self.create_distribution_analysis_tab()
        self.create_performance_analysis_tab()
        
        # Use a built-in style instead of seaborn
        plt.style.use('bmh')  # Alternative built-in style that works well for data visualization

    # Rest of the GraphManager class remains the same...
    def create_category_comparison_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Category Comparison')
        
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # Calculate data
        category_totals = defaultdict(float)
        for month_data in self.trash_system.trash_data.values():
            for category, amount in month_data.items():
                category_totals[category] += amount
        
        categories = list(category_totals.keys())
        values = list(category_totals.values())
        
        # Get colors for each category
        bar_colors = [self.colors.get(category, '#808080') for category in categories]
        
        # Create bar chart
        bars = ax.bar(categories, values, color=bar_colors)
        
        # Customize chart
        ax.set_title('Category-wise Waste Collection Comparison', pad=20, fontsize=14)
        ax.set_xlabel('Waste Categories', fontsize=12)
        ax.set_ylabel('Total Quantity (kg)', fontsize=12)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}kg',
                   ha='center', va='bottom')
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        fig.tight_layout()
        
        # Add to tab
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_revenue_trend_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Revenue Trend')
        
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # Calculate monthly revenue
        monthly_revenue = defaultdict(float)
        for deal in self.trash_system.deals:
            month = deal.date.split('-')[1]  # Extract month from date
            monthly_revenue[month] += deal.amount
        
        months = sorted(monthly_revenue.keys())
        revenue = [monthly_revenue[m] for m in months]
        
        # Create line chart
        line = ax.plot(months, revenue, marker='o', linewidth=2, markersize=8, color='#4ECDC4')
        
        # Customize chart
        ax.set_title('Monthly Revenue Trend', pad=20, fontsize=14)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Revenue (₹)', fontsize=12)
        
        # Add value labels
        for x, y in zip(months, revenue):
            ax.text(x, y, f'₹{y:,.0f}', ha='center', va='bottom')
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        fig.tight_layout()
        
        # Add to tab
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_distribution_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Distribution Analysis')
        
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # Calculate distribution
        industry_total = sum(deal.quantity for deal in self.trash_system.deals 
                           if deal.deal_type == "industry")
        self_total = sum(deal.quantity for deal in self.trash_system.deals 
                        if deal.deal_type == "self")
        
        # Create pie chart
        labels = ['Industry', 'Self Storage']
        sizes = [industry_total, self_total]
        colors = ['#4ECDC4', '#FF6B6B']
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
               startangle=90)
        
        # Customize chart
        ax.set_title('Waste Distribution Analysis', pad=20, fontsize=14)
        
        # Add legend
        ax.legend(title="Distribution Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        fig.tight_layout()
        
        # Add to tab
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_performance_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Performance Analysis')
        
        fig = Figure(figsize=(12, 6))
        ax1 = fig.add_subplot(111)
        
        # Calculate metrics by category
        category_metrics = defaultdict(lambda: {"quantity": 0, "revenue": 0})
        for deal in self.trash_system.deals:
            category_metrics[deal.category]["quantity"] += deal.quantity
            category_metrics[deal.category]["revenue"] += deal.amount
        
        categories = list(category_metrics.keys())
        quantities = [metrics["quantity"] for metrics in category_metrics.values()]
        revenues = [metrics["revenue"] for metrics in category_metrics.values()]
        
        # Create bar chart for quantities
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, quantities, width, label='Quantity (kg)', 
                       color=[self.colors.get(cat, '#808080') for cat in categories])
        ax2 = ax1.twinx()
        bars2 = ax2.bar(x + width/2, revenues, width, label='Revenue (₹)', color='#FF6B6B')
        
        # Customize chart
        ax1.set_title('Category Performance Analysis', pad=20, fontsize=14)
        ax1.set_xlabel('Categories', fontsize=12)
        ax1.set_ylabel('Quantity (kg)', fontsize=12)
        ax2.set_ylabel('Revenue (₹)', fontsize=12)
        
        # Set x-axis labels
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, rotation=45, ha='right')
        
        # Add value labels
        def autolabel(bars, ax):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom')
        
        autolabel(bars1, ax1)
        autolabel(bars2, ax2)
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        fig.tight_layout()
        
        # Add to tab
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show(self):
        self.root.mainloop()


class Deal:
    def __init__(self, company: str, category: str, quantity: float, amount: float, date: str, deal_type: str = "industry"):
        self.company = company
        self.category = category
        self.quantity = quantity
        self.amount = amount
        self.date = date
        self.deal_type = deal_type  # 'industry' or 'self'

    def to_dict(self) -> dict:
        return {
            'company': self.company,
            'category': self.category,
            'quantity': self.quantity,
            'amount': self.amount,
            'date': self.date,
            'deal_type': self.deal_type
        }

class EnhancedGraph:
    def __init__(self):
        try:
            self.screen = turtle.Screen()
            self.screen.clear()
            self.screen.title("Trash Management Analytics")
            self.screen.setup(1200, 800)
            self.screen.bgcolor("white")
            self.t = turtle.Turtle()
            self.t.speed(0)
            self.t.hideturtle()
            
            # Add event handler for 'q' key
            self.screen.onkey(self.exit_graph, 'q')
            self.screen.listen()
            
        except Exception as e:
            print(f"Error initializing graph: {str(e)}")
            self.screen = None

    def exit_graph(self):
        """Exit the graph window"""
        if self.screen:
            self.screen.bye()

    def draw_legend(self, items, x, y):
        """Draw legend with items in format [(label, color)]"""
        self.t.penup()
        original_y = y
        
        # Find the longest label for spacing
        max_label_length = max(len(item[0]) for item in items)
        box_size = 20
        spacing = max_label_length * 10 + 40
        
        for label, color in items:
            # Draw colored box
            self.t.goto(x, y)
            self.t.fillcolor(color)
            self.t.begin_fill()
            for _ in range(4):
                self.t.forward(box_size)
                self.t.right(90)
            self.t.end_fill()
            
            # Write label
            self.t.goto(x + box_size + 10, y)
            self.t.write(label, align="left", font=("Arial", 10, "normal"))
            y -= 30
        
        # Draw border around legend
        self.t.goto(x - 10, original_y + 10)
        self.t.pendown()
        self.t.color("black")
        height = (len(items) * 30) + 20
        width = spacing + 20
        for _ in range(2):
            self.t.forward(width)
            self.t.right(90)
            self.t.forward(height)
            self.t.right(90)
        self.t.penup()

    def draw_axis(self, origin_x, origin_y, x_length, y_length, title=""):
        """Draw coordinate axis with detailed labels and grid"""
        self.t.clear()
        self.t.penup()
        
        # Draw title
        self.t.goto(0, y_length + 30)
        self.t.write(title, align="center", font=("Arial", 14, "bold"))
        
        # Draw exit instruction
        self.t.goto(0, y_length + 60)
        self.t.write("Press 'q' to exit the chart", align="center", font=("Arial", 10, "normal"))
        
        # Draw grid
        self.draw_grid(origin_x, origin_y, x_length, y_length)
        
        # Draw main axes
        self.t.pensize(2)
        self.t.color("black")
        
        # X-axis
        self.t.goto(origin_x, origin_y)
        self.t.pendown()
        self.t.forward(x_length)
        self.t.stamp()
        
        # Y-axis
        self.t.penup()
        self.t.goto(origin_x, origin_y)
        self.t.pendown()
        self.t.left(90)
        self.t.forward(y_length)
        self.t.stamp()
        
        # Reset orientation and pen size
        self.t.setheading(0)
        self.t.pensize(1)

    def draw_grid(self, origin_x, origin_y, x_length, y_length):
        """Draw grid lines with measurements"""
        self.t.pensize(0.5)
        self.t.color("gray")
        
        # Vertical grid lines
        for x in range(origin_x, origin_x + x_length + 1, 100):
            self.t.penup()
            self.t.goto(x, origin_y)
            self.t.pendown()
            self.t.goto(x, origin_y + y_length)
            
            # Draw measurement
            self.t.penup()
            self.t.goto(x, origin_y - 20)
            self.t.write(str(x - origin_x), align="center")
        
        # Horizontal grid lines
        for y in range(origin_y, origin_y + y_length + 1, 100):
            self.t.penup()
            self.t.goto(origin_x, y)
            self.t.pendown()
            self.t.goto(origin_x + x_length, y)
            
            # Draw measurement
            self.t.penup()
            self.t.goto(origin_x - 30, y)
            self.t.write(str(y - origin_y), align="right")

    def draw_bar(self, x, y, width, height, color, label, value):
        """Draw a single bar with label and value"""
        self.t.penup()
        self.t.goto(x, y)
        self.t.fillcolor(color)
        self.t.begin_fill()
        
        # Draw bar
        for _ in range(2):
            self.t.forward(width)
            self.t.left(90)
            self.t.forward(height)
            self.t.left(90)
        self.t.end_fill()
        
        # Draw label
        self.t.goto(x + width/2, y - 20)
        self.t.write(label, align="center", font=("Arial", 8, "normal"))
        
        # Draw value
        self.t.goto(x + width/2, y + height + 10)
        self.t.write(f"{value:.1f}", align="center", font=("Arial", 8, "normal"))

    def draw_pie_slice(self, radius, angle, color, label, percentage):
        """Draw a pie slice with label and percentage"""
        self.t.fillcolor(color)
        self.t.begin_fill()
        self.t.circle(radius, angle)
        self.t.goto(0, 0)
        self.t.end_fill()
        
        # Calculate label position
        midpoint_angle = angle / 2
        label_radius = radius * 1.3
        x = label_radius * math.cos(math.radians(midpoint_angle))
        y = label_radius * math.sin(math.radians(midpoint_angle))
        
        # Draw label
        self.t.penup()
        self.t.goto(x, y)
        self.t.write(f"{label}: {percentage:.1f}%", align="center", font=("Arial", 10, "normal"))
        
class TrashManagementSystem:

    def __init__(self):
        self.company_name = "Ujjain Trash Control Pvt Ltd"
        self.trash_categories = {
            1: "Plastic",
            2: "Metal",
            3: "Books & Copies",
            4: "Electronics",
            5: "Cloths",
            6: "Glass",
            7: "Household Waste",
            8: "Dump Waste"
        }
        
        self.category_colors = {
            "Plastic": "#FF6B6B",
            "Metal": "#4ECDC4",
            "Books & Copies": "#45B7D1",
            "Electronics": "#96CEB4",
            "Cloths": "#FFEEAD",
            "Glass": "#D4A5A5",
            "Household Waste": "#9B9B9B",
            "Dump Waste": "#6C7A89"
        }

        self.industry_clients = {
            "Plastic": ["Plastic World", "EcoPlast Industries"],
            "Metal": ["Anant Metal Industry", "MetalScrap Co."],
            "Books & Copies": ["Paper Recyclers", "Book Bank"],
            "Electronics": ["E-Waste Solutions", "Tech Recyclers"],
            "Cloths": ["Textile Recycling Co.", "Fabric World"],
            "Glass": ["Glass Recyclers Ltd", "Crystal Clean"],
            "Household Waste": ["Waste Management Inc", "Green Solutions"],
            "Dump Waste": ["Municipal Waste Facility"]
        }
        
        self.trash_data = defaultdict(lambda: defaultdict(float))
        self.deals = []
        self.load_data()

    def menu(self):
        """Main menu of the Trash Management System"""
        while True:
            try:
                print(f"\n=== {self.company_name} ===")
                print("1. Insert Trash Data")
                print("2. View Data")
                print("3. Industry Section")
                print("4. Analytics Dashboard")
                print("5. Exit")
                
                choice = int(input("Enter your choice (1-5): "))
                
                if choice == 1:
                    self.insert_trash()
                elif choice == 2:
                    self.view_data()
                elif choice == 3:
                    self.industry_section()
                elif choice == 4:
                    self.analytics_dashboard()
                elif choice == 5:
                    print("Thank you for using the system!")
                    return
                else:
                    print("Invalid choice!")
                    
            except ValueError:
                print("Please enter valid numbers!")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again.")    
                
                

            self.trash_data = defaultdict(lambda: defaultdict(int))
            self.deals = []
            self.load_data()
        
                
    def load_data(self):
        """Load data from file if it exists"""
        try:
            if os.path.exists("trash_management_export.json"):
                with open("trash_management_export.json", 'r') as f:
                    data = json.load(f)
                    self.trash_data = defaultdict(lambda: defaultdict(int), data.get('trash_data', {}))
                    self.deals = [Deal(**deal_data) for deal_data in data.get('deals', [])]
        except Exception as e:
            print(f"Error loading data: {str(e)}")    

    def distribute_quantity(self, category: str, total_quantity: float) -> None:
        """Distribute the total quantity among selected clients and self storage"""
        remaining_quantity = total_quantity
        deals_to_add = []

        while remaining_quantity > 0:
            print(f"\nRemaining quantity to distribute: {remaining_quantity:.2f} kg")
            print("\nSelect distribution option:")
            print("Available Industry Clients:")
            clients = self.industry_clients[category]
            for idx, client in enumerate(clients, 1):
                print(f"{idx}. {client}")
            print(f"{len(clients) + 1}. Self Storage")

            try:
                option = int(input("Select option: "))
                if option < 1 or option > len(clients) + 1:
                    print("Invalid option!")
                    continue

                quantity = float(input("Enter quantity to distribute: "))
                if quantity > remaining_quantity:
                    print("Quantity exceeds remaining amount!")
                    continue

                if option <= len(clients):
                    # Industry client
                    client = clients[option - 1]
                    rate = float(input("Enter rate per kg (₹): "))
                    amount = quantity * rate
                    
                    deal = Deal(
                        company=client,
                        category=category,
                        quantity=quantity,
                        amount=amount,
                        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        deal_type="industry"
                    )
                else:
                    # Self storage
                    deal = Deal(
                        company="Self Storage",
                        category=category,
                        quantity=quantity,
                        amount=0,  # No monetary transaction for self storage
                        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        deal_type="self"
                    )

                deals_to_add.append(deal)
                remaining_quantity -= quantity

            except ValueError:
                print("Please enter valid numbers!")
                continue

        # Add all deals after successful distribution
        self.deals.extend(deals_to_add)

    def insert_trash(self):
        """Insert new trash data with quantity distribution"""
        try:
            print("\n=== Insert Trash Data ===")
            print("Available Categories:")
            for id_, category in self.trash_categories.items():
                print(f"{id_}. {category}")

            category_id = int(input("\nEnter category number: "))
            if category_id not in self.trash_categories:
                print("Invalid category!")
                return

            total_quantity = float(input("Enter total quantity (in kg): "))
            if total_quantity <= 0:
                print("Quantity must be positive!")
                return

            # Get current month and category
            current_month = datetime.datetime.now().strftime("%B")
            category = self.trash_categories[category_id]
            
            # Update trash data
            self.trash_data[current_month][category] += total_quantity

            # Distribute the quantity
            self.distribute_quantity(category, total_quantity)

            print(f"\nData inserted and distributed successfully!")

        except ValueError:
            print("Please enter valid numbers!")
        except Exception as e:
            print(f"Error inserting data: {str(e)}")


    def plot_distribution_analysis(self):
        """Plot distribution analysis with improved error handling"""
        try:
            graph = EnhancedGraph()
            if not graph.screen:
                return

            # Calculate totals by deal type with validation
            industry_total = sum(deal.quantity for deal in self.deals 
                               if deal.deal_type == "industry" and deal.quantity is not None)
            self_total = sum(deal.quantity for deal in self.deals 
                           if deal.deal_type == "self" and deal.quantity is not None)
            total = industry_total + self_total

            if total == 0:
                print("No data available for distribution analysis!")
                return

            # Draw axis
            graph.draw_axis(-400, -200, 800, 400, "Distribution Analysis: Industry vs Self Storage")

            # Draw pie chart
            graph.t.penup()
            graph.t.goto(0, 0)
            
            # Draw industry portion
            industry_angle = (industry_total / total) * 360
            graph.t.fillcolor("#4ECDC4")
            graph.t.begin_fill()
            graph.t.circle(150, industry_angle)
            graph.t.goto(0, 0)
            graph.t.end_fill()

            # Draw self storage portion
            graph.t.fillcolor("#FF6B6B")
            graph.t.begin_fill()
            graph.t.circle(150, 360 - industry_angle)
            graph.t.goto(0, 0)
            graph.t.end_fill()

            # Add legend
            legend_items = [
                ("Industry", "#4ECDC4"),
                ("Self Storage", "#FF6B6B")
            ]
            graph.draw_legend(legend_items, 200, 150)

            # Add percentages
            industry_percent = (industry_total / total) * 100
            self_percent = (self_total / total) * 100
            
            graph.t.goto(0, -250)
            graph.t.write(f"Industry: {industry_percent:.1f}% ({industry_total:.1f}kg)", align="center")
            graph.t.goto(0, -280)
            graph.t.write(f"Self Storage: {self_percent:.1f}% ({self_total:.1f}kg)", align="center")

            print("\nPress 'q' to exit the chart window")
            graph.screen.mainloop()

        except Exception as e:
            print(f"Error displaying distribution analysis: {str(e)}")
   
    def plot_category_performance(self):
        """Plot category performance with revenue and quantity metrics"""
        try:
            graph = EnhancedGraph()
            if not graph.screen:
                return

            # Calculate metrics by category
            category_metrics = defaultdict(lambda: {"quantity": 0, "revenue": 0})
            for deal in self.deals:
                category_metrics[deal.category]["quantity"] += deal.quantity
                category_metrics[deal.category]["revenue"] += deal.amount

            if not category_metrics:
                print("No data to display!")
                return

            # Draw axis
            graph.draw_axis(-400, -200, 800, 400, "Category Performance Analysis")

            # Plot dual-axis chart
            x = -350
            max_quantity = max(m["quantity"] for m in category_metrics.values())
            max_revenue = max(m["revenue"] for m in category_metrics.values())
            
            quantity_scale = 300 / max_quantity if max_quantity > 0 else 1
            revenue_scale = 300 / max_revenue if max_revenue > 0 else 1

            for category, metrics in category_metrics.items():
                # Quantity bar
                quantity_height = metrics["quantity"] * quantity_scale
                graph.t.penup()
                graph.t.goto(x, -200)
                graph.t.fillcolor(self.category_colors[category])
                graph.t.begin_fill()
                for _ in range(2):
                    graph.t.forward(30)
                    graph.t.left(90)
                    graph.t.forward(quantity_height)
                    graph.t.left(90)
                graph.t.end_fill()

                # Revenue line
                revenue_height = metrics["revenue"] * revenue_scale
                graph.t.penup()
                graph.t.goto(x + 15, -200 + revenue_height)
                graph.t.dot(8, "red")

                # Labels
                graph.t.goto(x + 15, -220)
                graph.t.write(category[:8], align="center")
                graph.t.goto(x + 15, -200 + quantity_height + 10)
                graph.t.write(f"{metrics['quantity']:.1f}kg", align="center")
                graph.t.goto(x + 15, -200 + revenue_height + 30)
                graph.t.write(f"₹{metrics['revenue']:,.0f}", align="center")

                x += 70

            # Add legend
            legend_items = [
                ("Quantity", self.category_colors["Plastic"]),
                ("Revenue", "red")
            ]
            graph.draw_legend(legend_items, 200, 150)

            graph.screen.exitonclick()

        except Exception as e:
            print(f"Error displaying category performance: {str(e)}")
            
            
    def analytics_dashboard(self):
        """Enhanced analytics dashboard with all options and tabbed interface"""
        while True:
            print("\n=== Analytics Dashboard ===")
            print("1. View Monthly Report")
            print("2. Category Comparison Chart")
            print("3. Revenue Trend Analysis")
            print("4. Distribution Analysis")
            print("5. Category Performance")
            print("6. Export Data")
            print("7. Open All Charts (Tabbed View)")
            print("8. Back to Main Menu")
        
            try:
                choice = int(input("Enter your choice (1-8): "))
            
                if choice == 1:
                    print(self.generate_monthly_report())
                
                elif choice == 2:
                    root = tk.Tk()
                    root.title("Category Comparison")
                    graph_manager = GraphManager(root, self)
                    graph_manager.create_category_comparison_tab()
                    root.mainloop()
                
                elif choice == 3:
                    root = tk.Tk()
                    root.title("Revenue Trend")
                    graph_manager = GraphManager(root, self)
                    graph_manager.create_revenue_trend_tab()
                    root.mainloop()
                
                elif choice == 4:
                    root = tk.Tk()
                    root.title("Distribution Analysis")
                    graph_manager = GraphManager(root, self)
                    graph_manager.create_distribution_analysis_tab()
                    root.mainloop()
                
                elif choice == 5:
                    root = tk.Tk()
                    root.title("Category Performance")
                    graph_manager = GraphManager(root, self)
                    graph_manager.create_performance_analysis_tab()
                    root.mainloop()
                
                elif choice == 6:
                    self.export_data()
                
                elif choice == 7:
                # Open all charts in tabbed view
                    root = tk.Tk()
                    graph_manager = GraphManager(root, self)
                    graph_manager.show()
                
                elif choice == 8:
                    return  # Exit the method and return to main menu
                
                else:
                    print("Invalid choice!")
                
            except ValueError:
                print("Please enter valid numbers!")
            except Exception as e:
                print(f"Error in analytics dashboard: {str(e)}")
                traceback.print_exc()
            
    def view_data(self):
        """View trash data and deals"""
        try:
            print("\n=== View Data ===")
            print("1. View Trash Data")
            print("2. View Deals")
            choice = int(input("Enter your choice (1-2): "))

            if choice == 1:
                print("\nTrash Data by Month:")
                for month, categories in self.trash_data.items():
                    print(f"\n{month}:")
                    for category, quantity in categories.items():
                        print(f"{category:<15}: {quantity:>8.2f} kg")

            elif choice == 2:
                print("\nDeals:")
                for deal in self.deals:
                    print(f"\nCompany: {deal.company}")
                    print(f"Category: {deal.category}")
                    print(f"Quantity: {deal.quantity:.2f} kg")
                    print(f"Amount: ₹{deal.amount:,.2f}")
                    print(f"Date: {deal.date}")
            else:
                print("Invalid choice!")

        except ValueError:
            print("Please enter valid numbers!")
        except Exception as e:
            print(f"Error viewing data: {str(e)}")

    def industry_section(self):
        """View and manage industry clients"""
        try:
            print("\n=== Industry Section ===")
            print("Industry Clients by Category:")
            
            for category, clients in self.industry_clients.items():
                print(f"\n{category}:")
                for client in clients:
                    # Calculate total business with this client
                    total_quantity = sum(deal.quantity for deal in self.deals if deal.company == client)
                    total_amount = sum(deal.amount for deal in self.deals if deal.company == client)
                    
                    print(f"\n  {client}")
                    print(f"  Total Business: {total_quantity:.2f} kg")
                    print(f"  Total Revenue: ₹{total_amount:,.2f}")

        except Exception as e:
            print(f"Error in industry section: {str(e)}")

    def generate_monthly_report(self) -> str:
        """Generate a detailed monthly report"""
        current_month = datetime.datetime.now().strftime("%B %Y")
        report = f"\n=== Monthly Report for {current_month} ===\n\n"
        
        # Calculate totals
        monthly_data = self.trash_data[datetime.datetime.now().strftime("%B")]
        total_quantity = sum(monthly_data.values())
        
        # Category breakdown
        report += "Category Breakdown:\n"
        for category, quantity in monthly_data.items():
            percentage = (quantity / total_quantity * 100) if total_quantity > 0 else 0
            report += f"{category:<15}: {quantity:>8.2f} kg ({percentage:>6.2f}%)\n"
        
        # Deal summary
        current_month_deals = [
            deal for deal in self.deals 
            if deal.date.startswith(datetime.datetime.now().strftime("%Y-%m"))
        ]
        total_revenue = sum(deal.amount for deal in current_month_deals)
        
        report += f"\nTotal Deals: {len(current_month_deals)}"
        report += f"\nTotal Revenue: ₹{total_revenue:,.2f}"
        
        return report

         
    def export_data(self, filename: str = "trash_management_export.json"):
        """Export all data to a formatted JSON file"""
        try:
            export_data = {
                'company_info': {
                    'name': self.company_name,
                    'export_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                'trash_data': dict(self.trash_data),
                'deals': [deal.to_dict() for deal in self.deals]
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=4)
            print(f"\nData successfully exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            
    def plot_category_comparison(self):
        """Plot a comparative bar chart for different categories"""
        try:
            graph = EnhancedGraph()
            if not graph.screen:
                return
                
            # Calculate totals for each category
            category_totals = defaultdict(float)
            for month_data in self.trash_data.values():
                for category, amount in month_data.items():
                    category_totals[category] += amount
                    
            if not category_totals:
                print("No data to display!")
                return   
            # Draw axis
            graph.draw_axis(-400, -200, 800, 400)
            
            # Plot bars
            x = -350
            max_amount = max(category_totals.values())
            scale_factor = 300 / max_amount if max_amount > 0 else 1
            
            for category, total in category_totals.items():
                height = total * scale_factor
                
                # Draw bar
                graph.t.penup()
                graph.t.goto(x, -200)
                graph.t.fillcolor(self.category_colors[category])
                graph.t.begin_fill()
                
                for _ in range(2):
                    graph.t.forward(40)
                    graph.t.left(90)
                    graph.t.forward(height)
                    graph.t.left(90)
                    
                graph.t.end_fill()
                
                # Write labels
                graph.t.goto(x + 20, -220)
                graph.t.write(category[:8], align="center")
                graph.t.goto(x + 20, -200 + height + 10)
                graph.t.write(f"{total:.1f}kg", align="center")
                
                x += 60
                
            graph.screen.exitonclick()
            
        except Exception as e:
            print(f"Error displaying category comparison: {str(e)}")


    def plot_category_performance(self):
        """Plot category performance with improved error handling"""
        try:
            graph = EnhancedGraph()
            if not graph.screen:
                return

            # Calculate metrics by category with validation
            category_metrics = defaultdict(lambda: {"quantity": 0, "revenue": 0})
            for deal in self.deals:
                if deal.quantity is not None and deal.amount is not None:
                    category_metrics[deal.category]["quantity"] += deal.quantity
                    category_metrics[deal.category]["revenue"] += deal.amount

            if not category_metrics:
                print("No data to display!")
                return

            # Draw axis
            graph.draw_axis(-400, -200, 800, 400, "Category Performance Analysis")

            # Plot dual-axis chart
            x = -350
            max_quantity = max(m["quantity"] for m in category_metrics.values())
            max_revenue = max(m["revenue"] for m in category_metrics.values())
            
            # Prevent division by zero
            quantity_scale = 300 / max_quantity if max_quantity > 0 else 1
            revenue_scale = 300 / max_revenue if max_revenue > 0 else 1

            for category, metrics in category_metrics.items():
                # Skip categories with no data
                if metrics["quantity"] == 0 and metrics["revenue"] == 0:
                    continue

                # Quantity bar
                quantity_height = metrics["quantity"] * quantity_scale
                graph.t.penup()
                graph.t.goto(x, -200)
                graph.t.fillcolor(self.category_colors.get(category, "#808080"))  # Default color if category not found
                graph.t.begin_fill()
                for _ in range(2):
                    graph.t.forward(30)
                    graph.t.left(90)
                    graph.t.forward(quantity_height)
                    graph.t.left(90)
                graph.t.end_fill()

                # Revenue line
                revenue_height = metrics["revenue"] * revenue_scale
                graph.t.penup()
                graph.t.goto(x + 15, -200 + revenue_height)
                graph.t.dot(8, "red")

                # Labels
                graph.t.goto(x + 15, -220)
                graph.t.write(category[:8], align="center")
                graph.t.goto(x + 15, -200 + quantity_height + 10)
                graph.t.write(f"{metrics['quantity']:.1f}kg", align="center")
                graph.t.goto(x + 15, -200 + revenue_height + 30)
                graph.t.write(f"₹{metrics['revenue']:,.0f}", align="center")

                x += 70

            # Add legend
            legend_items = [
                ("Quantity", "#4ECDC4"),
                ("Revenue", "red")
            ]
            graph.draw_legend(legend_items, 200, 150)

            print("\nPress 'q' to exit the chart window")
            graph.screen.mainloop()

        except Exception as e:
            print(f"Error displaying category performance: {str(e)}")

   
    def plot_revenue_trend(self):
        """Plot monthly revenue trend with improved error handling"""
        try:
            graph = EnhancedGraph()
            if not graph.screen:
                return
                
            # Calculate monthly revenue with error checking
            monthly_revenue = defaultdict(float)
            for deal in self.deals:
                try:
                    month = datetime.datetime.strptime(deal.date, "%Y-%m-%d %H:%M:%S").strftime("%B")
                    if deal.amount is not None:  # Add validation
                        monthly_revenue[month] += deal.amount
                except (ValueError, AttributeError) as e:
                    print(f"Skipping invalid deal data: {e}")
                
            if not monthly_revenue:
                print("No revenue data to display!")
                return
                
            # Draw axis
            graph.draw_axis(-400, -200, 800, 400, "Monthly Revenue Trend")
            
            # Plot line graph
            months = sorted(monthly_revenue.keys(),
                          key=lambda x: list(calendar.month_name).index(x))
            
            if not months:  # Additional check
                print("No valid months to display!")
                return
                
            max_revenue = max(monthly_revenue.values())
            if max_revenue == 0:  # Prevent division by zero
                scale_factor = 1
            else:
                scale_factor = 300 / max_revenue
            
            x_step = 700 / (len(months) - 1) if len(months) > 1 else 700
            x = -350
            
            graph.t.penup()
            first_point = True
            
            for month in months:
                y = monthly_revenue[month] * scale_factor - 200
                
                if first_point:
                    graph.t.goto(x, y)
                    first_point = False
                else:
                    graph.t.pendown()
                    graph.t.goto(x, y)
                    
                # Draw point
                graph.t.dot(8, "red")
                
                # Write labels
                graph.t.penup()
                graph.t.goto(x, -220)
                graph.t.write(month[:3], align="center")
                graph.t.goto(x, y + 10)
                graph.t.write(f"₹{monthly_revenue[month]:,.0f}", align="center")
                
                x += x_step
            
            print("\nPress 'q' to exit the chart window")
            graph.screen.mainloop()
            
        except Exception as e:
            print(f"Error displaying revenue trend: {str(e)}")


if __name__ == "__main__":
    try:
        system = TrashManagementSystem()
        system.menu()
    except Exception as e:
        print(f"Critical error: {str(e)}")
        print("System shutting down...")
        traceback.print_exc()