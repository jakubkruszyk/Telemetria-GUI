from Telemetry.globals import *
import PySimpleGUI as sg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PlotWindow:
    # =====================================================================================================================================
    # layouts for gui sections
    # =====================================================================================================================================
    def side_menu_layout(self):
        return [[sg.Text("Layout Type")],
                [sg.Combo(values=PLOT_LAYOUT_TYPES, default_value=self.selected_plot_layout, key="-layout_type-",
                          enable_events=True)],
                [sg.Text("Data source")],
                [sg.Combo(values=DATA_SOURCES, default_value=self.selected_data_source, key="-data_source-",
                          enable_events=True)],
                [sg.Button("Create new window")],
                [sg.Button("Destroy all")]
                ]

    def single_plot_layout(self, num):
        sub_layout = [[sg.Combo(values=AVAILABLE_PLOTS, default_value=AVAILABLE_PLOTS[0], key=f"-plot_{num}_source-")],
                      [sg.Canvas(key=f"-plot_{num}-", background_color="black")]]
        return sg.Column(layout=sub_layout, background_color="white")

    def top_menu_layout(self):
        return [[sg.Button("Connect"), sg.Button("Import"), sg.Button("Export")]]

    # =====================================================================================================================================
    # variables for work parameters
    # =====================================================================================================================================
    selected_plot_layout = PLOT_LAYOUT_TYPES[1]
    selected_data_source = DATA_SOURCES[0]
    plots_sources = {0: "None"}

    connected = False
    re_plot_ready = False

    plots_layout = None
    window = None

    # variables for plotting
    figs = []
    axs = []
    lines = []
    fig_aggs = []

    # data for plotting
    default_x = np.linspace(0, 20, 150)
    default_y = [0 for _ in default_x]
    plot_y = None
    plot_x = None

    # =====================================================================================================================================
    # init
    # =====================================================================================================================================
    def __init__(self):
        self.plots_layout = [[self.single_plot_layout(0)]]
        self.plot_y = [0 for _ in self.default_x]
        self.plot_x = np.linspace(-20, 0, 150)
        self.plot_x = self.plot_x.tolist()

    # =====================================================================================================================================
    # methods for managing window
    # =====================================================================================================================================
    def update_layout(self):
        self.plots_layout = []
        dim = self.selected_plot_layout.split("x")
        self.plots_layout = [[self.single_plot_layout(int(dim[1]) * row + col) for col in range(int(dim[1]))]
                             for row in range(int(dim[0]))]
        self.create_window()

    def create_window(self):
        # set build-in graphic theme
        sg.theme(GUI_THEME)

        # create new layout and window
        whole_layout = [[sg.Column(self.top_menu_layout(), expand_x=True, key="-top_menu-", size=(0, TOP_MENU_SIZE),
                                   vertical_alignment="center")],
                        [sg.HorizontalSeparator()],
                        [sg.Column(self.side_menu_layout(), vertical_alignment="top", key="-side_menu-",
                                   size=(SIDE_MENU_WIDTH, 1), expand_y=True),
                         sg.VerticalSeparator(),
                         sg.Column(self.plots_layout, key="-plots-")]
                        ]
        self.window = sg.Window(WINDOW_TITLE, layout=whole_layout, finalize=True, resizable=True)
        self.window.maximize()

        # resize plots to fill the screen
        window_size = self.window.get_screen_size()
        dim = self.selected_plot_layout.split("x")
        x_size = int((window_size[0] - SIDE_MENU_WIDTH) / int(dim[1]) - 2 * PLOTS_PADDING)
        y_size = int((window_size[1] - TOP_MENU_SIZE) / int(dim[0]) - 2 * PLOTS_PADDING - PLOTS_Y_OFFSET)
        for i in range(int(dim[0]) * int(dim[1])):
            self.window[f"-plot_{i}-"].set_size((x_size, y_size))

    def read_window(self):
        event, values = self.window.read(timeout=20)
        if event == "-layout_type-":
            # saving parameters that changed and cleaning flags
            self.selected_plot_layout = values["-layout_type-"]
            self.selected_data_source = values["-data_source-"]
            self.connected = False
            self.re_plot_ready = False
            # restarting window
            self.window.close()
            self.update_layout()

        elif event == sg.WIN_CLOSED or event is None:
            return "closed"

        elif event == "Connect":
            if not self.connected:
                self.connected = True
                self.create_plots()

        elif event == "Import":
            self.refresh_plots()

        # plots refresh routine
        if self.re_plot_ready and self.connected:
            self.re_plot_ready = False
            self.refresh_plots()

        return None

    # =====================================================================================================================================
    # methods for plotting
    # =====================================================================================================================================
    # needed to integrate matplotlib and tkinter
    def draw_figure(self, canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    def create_plots(self):
        self.figs.clear()
        self.axs.clear()
        self.lines.clear()
        self.fig_aggs.clear()

        dim = self.selected_plot_layout.split("x")
        px = 1/plt.rcParams['figure.dpi']
        x_size, y_size = self.window["-plot_0-"].get_size()

        for i in range(int(dim[0]) * int(dim[1])):
            # creating figures and axis
            self.figs.append(Figure(figsize=(x_size*px, y_size*px)))
            self.axs.append(self.figs[i].add_subplot())
            # axis formating
            self.axs[i].grid()
            self.axs[i].set_ylim([-20.05, 20.05])
            # creating aggregator
            canvas = self.window[f"-plot_{i}-"].TKCanvas
            self.fig_aggs.append(self.draw_figure(canvas, self.figs[i]))
            # default plot
            line, = self.axs[i].plot(self.plot_x, self.plot_y)
            self.lines.append(line)

        for fig_agg in self.fig_aggs:
            fig_agg.draw()

    def refresh_plots(self):
        for ax in self.axs:
            ax.set_xlim([self.plot_x[0], self.plot_x[-1]])

        for line in self.lines:
            # resize to fit new data
            # y_min = 1.05 * np.min(self.sine_y)
            # y_max = 1.05 * np.max(self.sine_y)
            # self.axs[i].set_ylim([y_min, y_max])
            line.set_ydata(self.plot_y)
            line.set_xdata(self.plot_x)

        for fig in self.figs:
            fig.canvas.draw()
            fig.canvas.flush_events()

    def update_data(self, data):
        self.plot_y.pop(0)
        self.plot_y.append(data[1])
        self.plot_x.pop(0)
        self.plot_x.append(data[0])
        self.re_plot_ready = True
