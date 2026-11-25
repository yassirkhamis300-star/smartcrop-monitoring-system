import customtkinter as ctk
import csv

from tkinter import filedialog, messagebox
from statistics import mean

from modules.database import (
    create_database,
    get_latest_record,
    get_recent_records,
    get_record_count,
    get_all_records
)

from analysis import analyse_crop_conditions

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ---------------- CONFIGURATION ----------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class SmartCropDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SmartCrop Monitoring System")
        self.geometry("1250x780")
        self.minsize(1000, 650)

        create_database()

        self.records = []
        self.total_records = 0
        self.current_page = "Dashboard"
        self.analytics_period = "Last 50 Records"

        self.dashboard_labels = {}
        self.live_labels = {}

        self.create_layout()

        # refresh_data() schedules the next refresh itself.
        self.refresh_data()

    # ---------------- MAIN LAYOUT ----------------

    def create_layout(self):

        self.sidebar = ctk.CTkFrame(self, width=210)
        self.sidebar.pack(
            side="left",
            fill="y",
            padx=10,
            pady=10
        )

        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="SMARTCROP",
            font=("Arial", 24, "bold"),
            text_color="#35D07F"
        ).pack(pady=25)

        menus = [
            "Dashboard",
            "Live Monitoring",
            "Analytics",
            "Database Records",
            "Alerts",
            "Settings"
        ]

        for menu in menus:
            ctk.CTkButton(
                self.sidebar,
                text=menu,
                height=42,
                command=lambda page=menu: self.navigate(page)
            ).pack(
                fill="x",
                padx=12,
                pady=7
            )

        self.main_area = ctk.CTkFrame(self)
        self.main_area.pack(
            side="right",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.show_dashboard()

    # ---------------- NAVIGATION ----------------

    def clear_page(self):

        for widget in self.main_area.winfo_children():
            widget.destroy()

        self.dashboard_labels = {}
        self.live_labels = {}

    def navigate(self, page):

        self.current_page = page

        if page == "Dashboard":
            self.show_dashboard()

        elif page == "Live Monitoring":
            self.show_live_monitoring()

        elif page == "Analytics":
            self.show_analytics()

        elif page == "Database Records":
            self.show_database_records()

        elif page == "Alerts":
            self.show_alerts()

        elif page == "Settings":
            self.show_settings()

    # ---------------- DATABASE REFRESH ----------------

    def refresh_data(self):

        try:
            # Load a limited number of recent records for normal pages.
            self.records = get_recent_records(500)
            self.total_records = get_record_count()

            if self.current_page == "Dashboard":
                self.update_dashboard()

            elif self.current_page == "Live Monitoring":
                self.update_live_monitoring()

        except Exception as error:
            print("Database refresh error:", error)

        finally:
            # Schedule exactly one next refresh.
            if self.winfo_exists():
                self.after(5000, self.refresh_data)

    # ---------------- SENSOR ANALYSIS HELPERS ----------------

    def get_analysis_for_record(self, record):

        sensor_data = {
            "timestamp": record[1],
            "temperature": record[2],
            "humidity": record[3],
            "soil_moisture": record[4],
            "leaf_wetness": record[5]
        }

        return analyse_crop_conditions(sensor_data)

    def format_recommendations(self, recommendations):

        if not recommendations:
            return "No recommendations available."

        return "\n".join(
            f"• {recommendation}"
            for recommendation in recommendations
        )

    # ---------------- DASHBOARD ----------------

    def show_dashboard(self):

        self.clear_page()

        ctk.CTkLabel(
            self.main_area,
            text="SMARTCROP DASHBOARD",
            font=("Arial", 26, "bold")
        ).pack(pady=20)

        cards = ctk.CTkFrame(self.main_area)
        cards.pack(
            fill="x",
            padx=15,
            pady=15
        )

        sensors = [
            ("Temperature", "°C"),
            ("Air Humidity", "%"),
            ("Soil Moisture", "%"),
            ("Leaf Wetness", "%")
        ]

        sensor_keys = [
            "temperature",
            "humidity",
            "soil_moisture",
            "leaf_wetness"
        ]

        for (name, unit), key in zip(sensors, sensor_keys):

            card = ctk.CTkFrame(cards)
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=7,
                pady=10
            )

            ctk.CTkLabel(
                card,
                text=name,
                font=("Arial", 14, "bold")
            ).pack(pady=10)

            value_label = ctk.CTkLabel(
                card,
                text="Loading...",
                font=("Arial", 24, "bold"),
                text_color="#35D07F"
            )
            value_label.pack(pady=15)

            self.dashboard_labels[key] = (value_label, unit)

        self.dashboard_status = ctk.CTkLabel(
            self.main_area,
            text="SYSTEM STATUS: Loading...",
            font=("Arial", 22, "bold"),
            text_color="#35D07F"
        )
        self.dashboard_status.pack(pady=15)

        self.dashboard_recommendations = ctk.CTkLabel(
            self.main_area,
            text="SMART RECOMMENDATIONS\nLoading...",
            font=("Arial", 15),
            justify="left",
            wraplength=850
        )
        self.dashboard_recommendations.pack(
            fill="x",
            padx=25,
            pady=12
        )

        self.dashboard_total = ctk.CTkLabel(
            self.main_area,
            text="Total Database Records: 0",
            font=("Arial", 17)
        )
        self.dashboard_total.pack(pady=8)

        self.dashboard_time = ctk.CTkLabel(
            self.main_area,
            text="Last Updated: Waiting...",
            font=("Arial", 14)
        )
        self.dashboard_time.pack(pady=8)

        self.update_dashboard()

    def update_dashboard(self):

        latest = get_latest_record()

        if latest is None:
            self.dashboard_status.configure(
                text="No sensor data available"
            )
            self.dashboard_recommendations.configure(
                text="SMART RECOMMENDATIONS\nWaiting for sensor data..."
            )
            return

        sensor_values = {
            "temperature": latest[2],
            "humidity": latest[3],
            "soil_moisture": latest[4],
            "leaf_wetness": latest[5]
        }

        for key, value in sensor_values.items():
            if key in self.dashboard_labels:
                label, unit = self.dashboard_labels[key]
                label.configure(text=f"{value} {unit}")

        status, warnings, recommendations = (
            self.get_analysis_for_record(latest)
        )

        self.dashboard_status.configure(
            text=f"SYSTEM STATUS: {status}"
        )

        recommendation_text = self.format_recommendations(
            recommendations
        )

        self.dashboard_recommendations.configure(
            text="SMART RECOMMENDATIONS\n\n" + recommendation_text
        )

        self.dashboard_total.configure(
            text=f"Total Database Records: {self.total_records}"
        )

        self.dashboard_time.configure(
            text=f"Last Updated: {latest[1]}"
        )

    # ---------------- LIVE MONITORING ----------------

    def show_live_monitoring(self):

        self.clear_page()

        ctk.CTkLabel(
            self.main_area,
            text="LIVE SENSOR MONITORING",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        sensors = [
            ("Temperature", "temperature", "°C"),
            ("Air Humidity", "humidity", "%"),
            ("Soil Moisture", "soil_moisture", "%"),
            ("Leaf Wetness", "leaf_wetness", "%")
        ]

        for name, key, unit in sensors:

            label = ctk.CTkLabel(
                self.main_area,
                text=f"{name}: Loading...",
                font=("Arial", 20)
            )
            label.pack(pady=12)

            self.live_labels[key] = (label, unit)

        self.live_status = ctk.CTkLabel(
            self.main_area,
            text="System Status: Loading...",
            font=("Arial", 22, "bold")
        )
        self.live_status.pack(pady=15)

        self.live_recommendations = ctk.CTkLabel(
            self.main_area,
            text="SMART RECOMMENDATIONS\nLoading...",
            font=("Arial", 15),
            justify="left",
            wraplength=850
        )
        self.live_recommendations.pack(
            fill="x",
            padx=25,
            pady=12
        )

        self.update_live_monitoring()

    def update_live_monitoring(self):

        latest = get_latest_record()

        if latest is None:
            self.live_status.configure(
                text="System Status: No sensor data available"
            )
            self.live_recommendations.configure(
                text="SMART RECOMMENDATIONS\nWaiting for sensor data..."
            )
            return

        values = {
            "temperature": latest[2],
            "humidity": latest[3],
            "soil_moisture": latest[4],
            "leaf_wetness": latest[5]
        }

        for key, value in values.items():
            if key in self.live_labels:
                label, unit = self.live_labels[key]
                label.configure(
                    text=f"{key.replace('_', ' ').title()}: {value} {unit}"
                )

        status, warnings, recommendations = (
            self.get_analysis_for_record(latest)
        )

        self.live_status.configure(
            text=f"System Status: {status}"
        )

        self.live_recommendations.configure(
            text=(
                "SMART RECOMMENDATIONS\n\n"
                + self.format_recommendations(recommendations)
            )
        )

    # ---------------- ANALYTICS ----------------

    def show_analytics(self):

        self.clear_page()

        ctk.CTkLabel(
            self.main_area,
            text="SMARTCROP ANALYTICS",
            font=("Arial", 26, "bold")
        ).pack(pady=10)

        filter_frame = ctk.CTkFrame(self.main_area)
        filter_frame.pack(
            fill="x",
            padx=10,
            pady=8
        )

        ctk.CTkLabel(
            filter_frame,
            text="Analysis Period:"
        ).pack(side="left", padx=10)

        period_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=[
                "Last 20 Records",
                "Last 50 Records",
                "Last 100 Records",
                "All Records"
            ],
            command=self.change_analytics_period
        )
        period_menu.set(self.analytics_period)
        period_menu.pack(side="left", padx=10)

        ctk.CTkButton(
            filter_frame,
            text="Export CSV",
            command=self.export_analytics
        ).pack(side="right", padx=10)

        if self.analytics_period == "Last 20 Records":
            selected = self.records[:20]

        elif self.analytics_period == "Last 100 Records":
            selected = self.records[:100]

        elif self.analytics_period == "All Records":
            selected = get_all_records()

        else:
            selected = self.records[:50]

        selected = list(reversed(selected))

        if not selected:
            ctk.CTkLabel(
                self.main_area,
                text="No records available for analysis."
            ).pack(pady=30)
            return

        # Sensor statistics
        ctk.CTkLabel(
            self.main_area,
            text="SENSOR STATISTICS",
            font=("Arial", 20, "bold")
        ).pack(pady=8)

        stats_frame = ctk.CTkFrame(self.main_area)
        stats_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        sensor_columns = [
            ("Temperature", 2, "°C"),
            ("Humidity", 3, "%"),
            ("Soil Moisture", 4, "%"),
            ("Leaf Wetness", 5, "%")
        ]

        for name, column, unit in sensor_columns:

            values = [
                float(record[column])
                for record in selected
                if record[column] is not None
            ]

            if not values:
                continue

            card = ctk.CTkFrame(stats_frame)
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5,
                pady=8
            )

            ctk.CTkLabel(
                card,
                text=name,
                font=("Arial", 13, "bold")
            ).pack(pady=5)

            ctk.CTkLabel(
                card,
                text=f"Average: {mean(values):.2f}{unit}"
            ).pack(pady=3)

            ctk.CTkLabel(
                card,
                text=f"Minimum: {min(values):.2f}{unit}"
            ).pack(pady=3)

            ctk.CTkLabel(
                card,
                text=f"Maximum: {max(values):.2f}{unit}"
            ).pack(pady=3)

        # Trend analysis
        trend_frame = ctk.CTkFrame(self.main_area)
        trend_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ctk.CTkLabel(
            trend_frame,
            text="TREND ANALYSIS",
            font=("Arial", 17, "bold")
        ).pack(pady=5)

        for name, column, unit in sensor_columns:

            values = [
                float(record[column])
                for record in selected
                if record[column] is not None
            ]

            if len(values) < 2:
                trend = "Not enough data"
            elif values[-1] > values[0]:
                trend = "Increasing"
            elif values[-1] < values[0]:
                trend = "Decreasing"
            else:
                trend = "Stable"

            ctk.CTkLabel(
                trend_frame,
                text=f"{name}: {trend}",
                font=("Arial", 13)
            ).pack(side="left", padx=12, pady=5)

        # Graphs
        graph_frame = ctk.CTkFrame(self.main_area)
        graph_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        figure = Figure(figsize=(9, 5), dpi=80)

        x_values = [
            record[1][11:19]
            for record in selected
        ]

        graph_details = [
            ("Temperature", 2, "°C"),
            ("Air Humidity", 3, "%"),
            ("Soil Moisture", 4, "%"),
            ("Leaf Wetness", 5, "%")
        ]

        for index, (name, column, unit) in enumerate(
            graph_details, 1
        ):

            axis = figure.add_subplot(2, 2, index)

            y_values = [
                record[column]
                for record in selected
            ]

            axis.plot(
                x_values,
                y_values,
                marker="o",
                markersize=2
            )

            axis.set_title(name)
            axis.set_ylabel(unit)
            axis.set_xlabel("Time")
            axis.grid(True)

            if len(x_values) > 8:
                axis.set_xticks(
                    x_values[::max(1, len(x_values) // 5)]
                )

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(
            figure,
            master=graph_frame
        )
        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def change_analytics_period(self, value):

        self.analytics_period = value
        self.show_analytics()

    # ---------------- EXPORT CSV ----------------

    def export_analytics(self):

        try:
            all_records = get_all_records()

            if not all_records:
                messagebox.showwarning(
                    "No Data",
                    "There are no records to export."
                )
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                initialfile="smartcrop_analytics.csv"
            )

            if not file_path:
                return

            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "ID",
                    "Timestamp",
                    "Temperature",
                    "Humidity",
                    "Soil Moisture",
                    "Leaf Wetness",
                    "System Status"
                ])

                writer.writerows(all_records)

            messagebox.showinfo(
                "Export Successful",
                "Analytics data exported successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Export Error",
                str(error)
            )

    # ---------------- DATABASE RECORDS ----------------

    def show_database_records(self):

        self.clear_page()

        ctk.CTkLabel(
            self.main_area,
            text="DATABASE RECORDS",
            font=("Arial", 25, "bold")
        ).pack(pady=15)

        records = self.records[:100]

        if not records:
            ctk.CTkLabel(
                self.main_area,
                text="No database records found."
            ).pack(pady=20)
            return

        table = ctk.CTkScrollableFrame(self.main_area)
        table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        headers = [
            "ID",
            "Timestamp",
            "Temp",
            "Humidity",
            "Soil",
            "Leaf",
            "Status"
        ]

        for index, header in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=header,
                font=("Arial", 12, "bold")
            ).grid(
                row=0,
                column=index,
                padx=5,
                pady=8
            )

        for row_index, record in enumerate(records, 1):
            for column_index, value in enumerate(record):
                ctk.CTkLabel(
                    table,
                    text=str(value),
                    font=("Arial", 11)
                ).grid(
                    row=row_index,
                    column=column_index,
                    padx=5,
                    pady=5
                )

    # ---------------- ALERTS ----------------

    def show_alerts(self):

        self.clear_page()

        ctk.CTkLabel(
            self.main_area,
            text="SYSTEM ALERTS",
            font=("Arial", 25, "bold")
        ).pack(pady=15)

        alerts = [
            record for record in self.records
            if record[6] != "NORMAL"
        ]

        if not alerts:
            ctk.CTkLabel(
                self.main_area,
                text="No alerts found."
            ).pack(pady=20)
            return

        frame = ctk.CTkScrollableFrame(self.main_area)
        frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        for record in alerts[:100]:
            ctk.CTkLabel(
                frame,
                text=(
                    f"ID: {record[0]} | "
                    f"Time: {record[1]} | "
                    f"Status: {record[6]}"
                ),
                font=("Arial", 13)
            ).pack(
                anchor="w",
                pady=7
            )

    # ---------------- SETTINGS ----------------

    def show_settings(self):

        self.clear_page()

        ctk.CTkLabel(
            self.main_area,
            text="SYSTEM SETTINGS",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        information = [
            "System: SmartCrop Monitoring System",
            "Crop: Cucumber",
            "Database: SQLite",
            "Interface: CustomTkinter",
            "Graph Library: Matplotlib",
            "Monitoring Mode: Sensor Simulation",
            "Refresh Interval: 5 Seconds",
            "Maximum Recent Records: 500"
        ]

        for item in information:
            ctk.CTkLabel(
                self.main_area,
                text=item,
                font=("Arial", 16)
            ).pack(
                anchor="w",
                padx=30,
                pady=10
            )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    app = SmartCropDashboard()
    app.mainloop()
