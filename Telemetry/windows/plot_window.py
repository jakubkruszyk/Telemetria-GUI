from Telemetry.globals import *
from Telemetry.windows.base_window import BaseWindow, img_to_64, min_max_popup, plot_sources_popup
from Telemetry import usb_receiver
import PySimpleGUI as sg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotWindow(BaseWindow):
    # =====================================================================================================================================
    # layouts for gui sections
    # =====================================================================================================================================
    def single_plot_layout(self, num):
        sub_layout = [[sg.Button("Lines", metadata=num)],
                      [sg.Canvas(key=f"-plot_{num}-", background_color="black")]]
        return sg.Column(layout=sub_layout, background_color="white")

    # =====================================================================================================================================
    # variables for work parameters
    # =====================================================================================================================================
    plots_sources = {0: "None"}
    selected_plot_lines = dict()

    plots_layout = []

    # variables for plotting
    figs = []
    axs = []
    lines = []
    fig_aggs = []

    # data for plotting
    plot_y = None
    plot_x = None

    data = {key: [0 for _ in range(PLOTS_POINTS)] for key in AVAILABLE_PLOTS}  # key: [val, min, max]

    # =====================================================================================================================================
    # init
    # =====================================================================================================================================
    # init values format (layout, data_source, plots_sources)
    def __init__(self, **kwargs):
        self.selected_layout = kwargs.get("layout", "1x1")
        self.selected_data_source = kwargs.get("source", DATA_SOURCES[0])
        self.plots_sources = kwargs.get("plot_sources", dict())

        self.update_layout()
        self.plot_x = [0 for _ in range(PLOTS_POINTS)]
        dim = self.selected_layout.split("x")
        self.selected_plot_lines = {key: [] for key in range(int(dim[0]) * int(dim[1]))}

    # =====================================================================================================================================
    # methods for managing window
    # =====================================================================================================================================
    def update_layout(self):
        self.plots_layout.clear()
        self.plots_sources.clear()
        dim = self.selected_layout.split("x")
        self.plot_y = [[0 for _ in range(PLOTS_POINTS)] for _ in range(int(dim[0]) * int(dim[1]))]
        self.plots_layout = [[self.single_plot_layout(int(dim[1]) * row + col) for col in range(int(dim[1]))]
                             for row in range(int(dim[0]))]
        self.plots_sources = {k: "None" for k in range(int(dim[0]) * int(dim[1]))}
        self.selected_plot_lines = {key: [] for key in range(int(dim[0]) * int(dim[1]))}

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

        self.window = sg.Window(WINDOW_TITLE, layout=whole_layout, finalize=True, resizable=True,
                                icon=img_to_64(ICON_PATH))
        self.window.maximize()

        # resize plots to fill the screen
        window_size = self.window.get_screen_size()
        dim = self.selected_layout.split("x")
        x_size = int((window_size[0] - SIDE_MENU_WIDTH) / int(dim[1]) - 2 * PLOTS_PADDING)
        y_size = int((window_size[1] - TOP_MENU_SIZE) / int(dim[0]) - 2 * PLOTS_PADDING - PLOTS_Y_OFFSET)
        for i in range(int(dim[0]) * int(dim[1])):
            self.window[f"-plot_{i}-"].set_size((x_size, y_size))

        self.create_plots()

    def read_window(self):
        event, values = self.window.read(timeout=20)
        if event == sg.WIN_CLOSED or event is None:
            return "closed"

        elif event == "Settings":
            min_max_popup()
            self.save_config(CONFIG_PATH)

        elif event == "Export":
            self.save_config(CONFIG_PATH)

        elif event == "Import":
            self.load_config()

        elif event == "Connect":
            if not self.connected:
                resp = usb_receiver.connect_to_port(self.selected_port)
                if resp is not True:
                    sg.popup_ok(resp)
                    self.connected = False
                else:
                    self.connected = True

        elif event == "-layout_type-":
            # saving parameters that may changed and cleaning flags
            self.selected_layout = values["-layout_type-"]
            self.selected_data_source = values["-data_source-"]
            self.connected = False
            # restarting window
            self.window.close()
            # check if just need to change plots layout or whole window
            temp = values[event].split("x")
            if not (temp[0].isdigit() and temp[1].isdigit()):
                return "layout"
            else:
                self.update_layout()
                self.create_window()

        elif event == "Lines":
            plot_id = values[event].metadata
            selected_lines = plot_sources_popup()
            self.selected_plot_lines[plot_id] = selected_lines

        # elif event[:-3] == "-plot_source":
        #     plot_id = int(event[-2])
        #     self.plots_sources[plot_id] = values[event]
        #     data = container.read_range()
        #     self.plot_y[plot_id] = data[self.plots_sources[plot_id]]

        elif event == "-data_source-":
            if values[event] == "USB":
                self.window["-usb_settings-"].update(visible=True)
                self.selected_port = values["-selected_com-"]
            else:
                self.window["-usb_settings-"].update(visible=False)

        # connect to com port picked from list
        elif event == "-selected_com-":
            usb_receiver.connect_to_port(values["-selected_com-"])

        # refresh com ports list
        elif event == "-refresh_com-":
            if usb_receiver.available_ports():
                if usb_receiver.ser.is_open:
                    com_port = usb_receiver.ser.name
                else:
                    com_port = None
                self.window['-selected_com-'].update(value=com_port, values=usb_receiver.available_ports(),
                                                     disabled=False)
            else:
                self.window['-selected_com-'].update(value="Unavailable", disabled=True)
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

        dim = self.selected_layout.split("x")
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
            line, = self.axs[i].plot(self.plot_x, self.plot_y[0])
            self.lines.append(line)

        for fig_agg in self.fig_aggs:
            fig_agg.draw()

    def refresh_plots(self):
        for ax in self.axs:
            ax.set_xlim([self.plot_x[0], self.plot_x[-1]])

        for line, y in zip(self.lines, self.plot_y):
            # TODO resize to fit new data
            # y_min = 1.05 * np.min(self.sine_y)
            # y_max = 1.05 * np.max(self.sine_y)
            # self.axs[i].set_ylim([y_min, y_max])
            line.set_ydata(y)
            line.set_xdata(self.plot_x)

        for fig in self.figs:
            fig.canvas.draw()
            fig.canvas.flush_events()

    def update_data(self, data: dict) -> None:
        self.plot_x.pop(0)
        self.plot_x.append(data.pop("time"))
        for key, value in data.items():
            self.data[key].pop(0)
            self.data[key].append(value)
        self.refresh_plots()
