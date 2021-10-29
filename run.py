from Telemetry import main_window, container
from Telemetry.data_generator import Generator

main_window.create_window()
generator = Generator(2)

while True:
    event = main_window.read_window()
    if event == "closed":
        break
    container.update(generator.get())
    main_window.update_data(container.read_last())
