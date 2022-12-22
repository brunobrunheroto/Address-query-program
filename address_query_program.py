from tkintermapview import TkinterMapView
import tkinter
import regex
import customtkinter
import requests
import pandas as pd

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-orange.json")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.pattern = regex.compile(r"^*[0-9]{0,8}$")
        vcmd = (self.register(self.entry_validation_using_regex), "%P")

        # configure window
        self.title("Address query program by brazilian zip code (CEP)")
        self.geometry(f"{710}x{520}")
        self.resizable(False, False)
        self.iconbitmap("address_query_program.ico")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="news")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Simple CEP",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Location Finder",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=1, column=0, padx=20, pady=(0, 5))

        self.CEP_Entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="CEP without '-'", validate="key",
                                                validatecommand=vcmd)
        self.CEP_Entry.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button = customtkinter.CTkButton(self.sidebar_frame, text="Search", command=self.check_cep)
        self.sidebar_button.grid(row=3, column=0, padx=20, pady=10)

        self.valid_CEP = customtkinter.CTkLabel(self.sidebar_frame, text="", font=("Roboto", 15))
        self.valid_CEP.grid(row=4, column=0, padx=20, pady=10)

        # Map options
        self.map_label = customtkinter.CTkLabel(self.sidebar_frame, text="Map Services", font=("Roboto", 15))
        self.map_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["OpenStreetMap", "Google normal",
                                                                                       "Google satellite"],
                                                           command=self.change_map)
        self.map_option_menu.grid(row=6, column=0, padx=(20, 20))

        # Theme Options
        self.theme_label = customtkinter.CTkLabel(self.sidebar_frame, text="Theme", font=("Roboto", 15))
        self.theme_label.grid(row=7, column=0, padx=10, pady=(10, 0))
        self.theme_option_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                             command=self.change_theme_event)
        self.theme_option_menu.grid(row=8, column=0, padx=20, pady=(0, 10))

        # CEP Data
        self.data_display = customtkinter.CTkFrame(self, corner_radius=0, width=360)
        self.data_display.grid(row=0, column=1, rowspan=5, sticky="news")
        self.data_display.grid_rowconfigure(5, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.data_display, text="CEP Data",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=1, padx=20, pady=(10, 0))

        self.estate = customtkinter.CTkLabel(self.data_display, text="Estate:", font=("Roboto", 15))
        self.estate.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        self.city = customtkinter.CTkLabel(self.data_display, text="City:", font=("Roboto", 15))
        self.city.grid(row=2, column=1, padx=10, pady=0, sticky="w")

        self.neighborhood = customtkinter.CTkLabel(self.data_display, text="Neighborhood:", font=("Roboto", 15))
        self.neighborhood.grid(row=3, column=1, padx=10, pady=0, sticky="w")

        self.complement = customtkinter.CTkLabel(self.data_display, text="Complement:", font=("Roboto", 15))
        self.complement.grid(row=4, column=1, padx=10, pady=0, sticky="w")

        # Map View
        self.map_widget = TkinterMapView(self.data_display, width=500, height=500, corner_radius=0)
        self.map_widget.grid(row=5, column=1, padx=10, pady=(10, 10))

        # Default Location for the Map
        self.map_widget.set_address("São Paulo, Campinas, Centro")

    def entry_validation_using_regex(self, value):
        return self.pattern.match(value) is not None

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)

    def change_theme_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def clean_fields(self):
        self.estate.configure(text=f"Estate:")
        self.city.configure(text=f"City:")
        self.neighborhood.configure(text=f"Neighborhood:")
        self.complement.configure(text=f"Complement:")
        self.valid_CEP.configure(text="Type a valid CEP!")

    def check_cep(self):
        if self.CEP_Entry.get() != "":
            # Request to the Via CEP API
            response = requests.get(f"http://viacep.com.br/ws/{self.CEP_Entry.get()}/json/")
            if response.status_code == 200:
                res_json = response.json()
                parse_json_text = [res_json]
                df = pd.DataFrame(parse_json_text)
                if 'erro' not in df.columns:
                    # Updating values
                    self.estate.configure(text=f"Estate: {df['uf'][0]}")
                    self.city.configure(text=f"City: {df['localidade'][0]}")
                    self.neighborhood.configure(text=f"Neighborhood: {df['logradouro'][0]}")
                    self.complement.configure(text=f"Complement: {df['complemento'][0]}")
                    self.map_widget.set_address(f"{df['localidade'][0]}, {df['logradouro'][0]}, {df['bairro'][0]}")
                    self.map_widget.update()
                    self.valid_CEP.configure(text="")
                    return
        self.clean_fields()


if __name__ == "__main__":
    app = App()
    app.mainloop()
