# Proiect Laborator Metode Avansate de Programare
# Arnăutu Alexandrina + Bădîngă Alexandru-Nicolae
# Sursa CSV Locații: https://simplemaps.com/data/world-cities

import random
import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel, ttk
import sqlite3
import webbrowser
import csv

# Funcții pentru baza de date
def init_db():
    conn = sqlite3.connect('locations.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            csv_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_location(user_name, csv_name, lat, lon):
    conn = sqlite3.connect('locations.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO locations (user_name, csv_name, latitude, longitude)
        VALUES (?, ?, ?, ?)
    ''', (user_name, csv_name, lat, lon))
    conn.commit()
    conn.close()

def get_saved_locations():
    conn = sqlite3.connect('locations.db')
    c = conn.cursor()
    c.execute('SELECT id, user_name, csv_name, latitude, longitude FROM locations')
    locations = c.fetchall()
    conn.close()
    return locations

def delete_location(location_id):
    conn = sqlite3.connect('locations.db')
    c = conn.cursor()
    c.execute('DELETE FROM locations WHERE id = ?', (location_id,))
    conn.commit()
    conn.close()

def open_map(lat, lon):
    url = f'https://www.google.com/maps?q={lat},{lon}'
    webbrowser.open(url)

def get_random_city(cities, min_population, country):
    #facem o lista cu orasele care corespund criteriilor de selectie, astfel: parcurgem lista cities (care contine doar datele relevante noua, preluate din csv)
    #city[3] este populatia, si verificam sa fie mai mare decat criteriul, ciry[4] este tara si verificam astfel:
    #facem or logic intre (NOT country) care reprezinta cazul in care utilizatorul a selectat "Oricare" si city[4] == country caz in care utilizatorul a selectat o tara din lista
    #print(not None)  # Output: True
    filtered_cities = [city for city in cities if city[3] >= min_population and (not country or city[4].lower() == country.lower())]
    if not filtered_cities:
        return None
    return random.choice(filtered_cities)

# cities va avea date sub forma (city_name, lat, lon, population, country)
def load_worldcities_with_population(file_path="worldcities.csv"):
    cities = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = row['city']
            lat = float(row['lat'])
            lon = float(row['lng'])
            population = int(float(row['population'])) if row['population'] else 0
            country = row['country']
            cities.append((city, lat, lon, population, country))
    return cities

# functia apelata la apasarea butonului
def generate_location(entry_population, combobox_country, cities):
    try:
        min_population = int(entry_population.get())
    except ValueError:
        messagebox.showerror("Eroare", "Introduceți un număr valid pentru minimul de locuitori.")
        return None, None, None

    country = combobox_country.get()
    if country == "Oricare":
        country = None

    result = get_random_city(cities, min_population, country)
    if not result:
        messagebox.showinfo("Fără rezultate", "Nu există orașe care să îndeplinească criteriile selectate.")
        return None, None, None

    # In locations.db nu mai salvam populatia si tara, pentru nu sunt relevante _ _
    current_city, current_lat, current_lon, _, _ = result
    messagebox.showinfo("Locație generată", f"Locație: {current_city}\nLatitudine: {current_lat}\nLongitudine: {current_lon}")
    open_map(current_lat, current_lon)
    return current_city, current_lat, current_lon

#butonul save location
def save_location_popup(current_city, current_lat, current_lon):
    if current_lat is None or current_lon is None:
        messagebox.showwarning("Atenție", "Nu s-a generat nici o locație încă.")
        return

    def on_save():
        user_name = entry_name.get()
        if user_name:
            save_location(user_name, current_city, current_lat, current_lon)
            messagebox.showinfo("Succes", f"Locația \"{user_name}\" a fost salvată cu succes!")
            popup.destroy()
        else:
            messagebox.showwarning("Atenție", "Introduceți un mesaj legat de locație.")

    popup = Toplevel(root)
    popup.title("Salvează locația")
    popup.geometry("300x150")
    popup.configure(bg="#f7f7f7")

    label_name = tk.Label(popup, text="Introduceți un mesaj legat de locație:", bg="#f7f7f7", font=("Arial", 10))
    label_name.pack(pady=10)

    entry_name = tk.Entry(popup, font=("Arial", 10))
    entry_name.pack(pady=5)

    button_save = tk.Button(popup, text="Salvează", command=on_save, bg="#4caf50", fg="white", font=("Arial", 10), width=15)
    button_save.pack(pady=10)

#butonul locatii salvate
def show_saved_locations():
    locations = get_saved_locations()
    if not locations:
        messagebox.showinfo("Nicio locație", "Nu există locații salvate.")
        return

    list_popup = Toplevel(root)
    list_popup.title("Lista locațiilor salvate")
    list_popup.geometry("700x500")
    list_popup.configure(bg="#f7f7f7")

    label_list = tk.Label(list_popup, text="Locații salvate:", font=("Arial", 14, "bold"), bg="#f7f7f7", fg="#333333")
    label_list.pack(pady=10)

    listbox = tk.Listbox(list_popup, width=80, height=15, font=("Arial", 11), bg="#ffffff", fg="#333333", selectmode=tk.SINGLE)

    display_locations = []
    for location in locations:
        display_text = (f"{location[1]}\n"
                        f" (Oras: {location[2]}\n"
                        f" Lat: {location[3]:.5f}, Lon: {location[4]:.5f})")
        display_locations.append(location[0])
        listbox.insert(tk.END, display_text)

    def on_select(event):
        selected_index = listbox.curselection()
        if selected_index:
            location_id = display_locations[selected_index[0]]
            selected_location = next(loc for loc in locations if loc[0] == location_id)
            open_map(selected_location[3], selected_location[4])

    #la dublu click pe o locatie din lista afisata, deschidem locatia pe maps (daca vrem sa o revedem de exemplu)
    listbox.bind('<Double-1>', on_select)

    def delete_selected_location():
        selected_index = listbox.curselection()
        if selected_index:
            location_id = display_locations[selected_index[0]]
            delete_location(location_id)
            messagebox.showinfo("Succes", "Locația a fost ștearsă cu succes!")
            list_popup.destroy()
            show_saved_locations()

    button_delete = tk.Button(list_popup, text="Șterge locația selectată", command=delete_selected_location, bg="#f44336", fg="white", font=("Arial", 12), width=20)
    button_delete.pack(pady=10)

    listbox.pack(pady=10)

    scrollbar = tk.Scrollbar(list_popup)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    button_close = tk.Button(list_popup, text="Închide", command=list_popup.destroy, bg="#f44336", fg="white", font=("Arial", 12), width=20)
    button_close.pack(pady=10)

if __name__ == "__main__":
    init_db()

    root = tk.Tk()
    root.title("Locații noi de vizitat")
    root.geometry("400x550")
    root.configure(bg="#f7f7f7")

    cities = load_worldcities_with_population()
    countries = sorted({city[4] for city in cities})

    label_title = tk.Label(root, text="Bine ai venit!", font=("Arial", 16, "bold"), bg="#f7f7f7")
    label_title.pack(pady=10)

    label_population = tk.Label(root, text="Minim locuitori:", bg="#f7f7f7", font=("Arial", 10))
    label_population.pack(pady=5)

    entry_population = tk.Entry(root, font=("Arial", 10))
    entry_population.insert(0, "1000")
    entry_population.pack(pady=5)

    label_country = tk.Label(root, text="Țara:", bg="#f7f7f7", font=("Arial", 10))
    label_country.pack(pady=5)

    combobox_country = ttk.Combobox(root, values=["Oricare"] + countries, font=("Arial", 10))
    combobox_country.current(0)  # Selectează "Oricare" implicit
    combobox_country.pack(pady=5)

    current_city = None
    current_lat = None
    current_lon = None

    button_generate = tk.Button(root, text="Generează o locație", command=lambda: (
        globals().update(zip(["current_city", "current_lat", "current_lon"], 
                              generate_location(entry_population, combobox_country, cities)))),
        bg="#4caf50", fg="white", font=("Arial", 12), width=20)
    button_generate.pack(pady=10)

    button_save = tk.Button(root, text="Salvează locația", command=lambda: save_location_popup(current_city, current_lat, current_lon),
                            bg="#2196f3", fg="white", font=("Arial", 12), width=20)
    button_save.pack(pady=10)

    button_list = tk.Button(root, text="Afișează locațiile salvate", command=show_saved_locations, bg="#f44336", fg="white", font=("Arial", 12), width=20)
    button_list.pack(pady=10)

    root.mainloop()
