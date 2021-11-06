from Telemetry import main_window
from Telemetry.data_generator import generate

main_window.create_window()

while True:
    event = main_window.read_window()
    if event == "closed":
        break
    main_window.update_data(generate())
