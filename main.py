import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import json
import os
from datetime import datetime, timedelta
import io
import traceback

# Application Setup, initialize the application window
app = tk.Tk()
app.title("Portable Paleo Encyclopedia")
app.geometry("500x900")

# Set the window icon using a PNG file
logo_image = tk.PhotoImage(file='logo.png')  # Replace 'logo.png' with the path to your image file
app.iconphoto(True, logo_image)

# Cache file setup
cache_file = "animal_profiles.json"

# Define the color schemes
sepia = {
    'bg': '#f4ecd8',
    'fg': '#4f4b40',
    'button': '#c0a080',
    'text': '#4f4b40',
}

dark_mode = {
    'bg': '#2d2d2d',
    'fg': '#cccccc',
    'button': '#5c5c5c',
    'text': '#cccccc',
}

# Function to apply a color scheme
def apply_theme(theme):
    app.configure(bg=theme['bg'])
    profile_text_widget.configure(bg=theme['bg'], fg=theme['fg'])
    image_label.configure(background=theme['bg'])
    style = ttk.Style(app)
    style.configure('TButton', background=theme['button'], foreground=theme['fg'])
    style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])

# Toggle function to switch between sepia and dark mode
def toggle_theme():
    current_theme = toggle_theme_button.cget('text')
    new_theme = dark_mode if current_theme == 'Dark Mode' else sepia
    toggle_theme_button.config(text='Sepia Mode' if current_theme == 'Dark Mode' else 'Dark Mode')
    apply_theme(new_theme)

# Function to open an "About" dialog
def show_about():
    about_text = "Portable Paleo Encyclopedia\nVersion 1.0\n© 2024 Rebel Doomer @ Gitlab"
    profile_text_widget.delete(1.0, tk.END)
    profile_text_widget.insert(tk.END, about_text)

    # Open the image file
    logo_image = Image.open('logo.png')  # Replace 'logo.png' with the path to your image file

    # Resize the logo
    logo_image = logo_image.resize((300, 300),
                                   Image.Resampling.LANCZOS)  # Use Image.Resampling.LANCZOS instead of Image.ANTIALIAS

    # Convert the image to a PhotoImage
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Update the image label
    image_label.config(image=logo_photo)
    image_label.image = logo_photo  # Keep a reference!


def show_animal_profile(animal_name):
    summary, image_url = fetch_wikipedia_summary(animal_name)
    page_views = fetch_page_views(animal_name)
    profile_text_widget.delete(1.0, tk.END)  # Clear existing text
    profile_text_widget.insert(tk.END, f"{summary}\nPage Views: {page_views}")  # Insert new text
    if image_url:
        display_image_from_url(image_url)

# Load cache function with datetime check
def load_cache():
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            data = json.load(file)
            return data
    return {'data': {}, 'last_updated': str(datetime.now().date())}

# Save cache function
def save_cache(cache):
    with open(cache_file, "w") as file:
        json.dump(cache, file)

# Function to fetch page views data
def fetch_page_views(title):
    now = datetime.now()
    start_date = (now - timedelta(days=30)).strftime("%Y%m%d")
    end_date = now.strftime("%Y%m%d")
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{title}/daily/{start_date}/{end_date}"

    headers = {
        'User-Agent': 'Portable Paleo Encyclopedia/1.0 @ GitLab. Contact: email@swisscows.email'
    }

    try:
        response = requests.get(url, headers=headers)  # Add headers parameter here
        response.raise_for_status()
        data = response.json()
        views = sum(item['views'] for item in data['items']) if 'items' in data else 0
        return views
    except requests.exceptions.HTTPError as http_err:
        log_error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        log_error(f"Other error occurred: {err}")
    except json.decoder.JSONDecodeError:
        log_error("JSON decoding failed")
    return 0


# Function to display fetched image from URL with error handling
def display_image_from_url(image_url):
    headers = {
        'User-Agent': 'Portable Paleo Encyclopedia/1.0 @ GitLab. Contact: email@swisscows.email'
    }

    try:
        response = requests.get(image_url, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        if 'image' in response.headers.get('Content-Type', ''):
            img_data = response.content
            img = Image.open(io.BytesIO(img_data)).resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            image_label.config(image=photo)
            image_label.image = photo  # Keep a reference, this is important!
        else:
            raise IOError("Content-Type not recognized as an image.")
    except Exception as e:
        log_error(f"Error loading image: {e}")
        messagebox.showerror("Error", "Failed to load image.")
def log_error(message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

# Function to fetch Wikipedia summary and image URL
def fetch_wikipedia_summary(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

    headers = {
        'User-Agent': 'Portable Paleo Encyclopedia/1.0 @ GitLab. Contact: email@swisscows.email'
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    summary = data.get('extract', "Summary not available.")
    image_url = data.get('originalimage', {}).get('source', "")
    return summary, image_url

# UI Elements - Modified for scrollbar
profile_text_widget = tk.Text(app, wrap="word", height=10, width=50)
profile_text_widget.pack(side="top", fill="both", expand=True)

scrollbar = tk.Scrollbar(app, command=profile_text_widget.yview)
scrollbar.pack(side="right", fill="y")

# List of dinosaurs
animals = sorted([
	'Jeholopterus', 'Hatzegopteryx', 'Cryodrakon', 'Tarbosaurus', 'Oviraptor',
	'Megalosaurus', 'Therizinosaurus', 'Quetzalcoatlus', 'Parasaurolophus', 'Carnotaurus',
	'Ankylosaurus', 'Dilophosaurus', 'Allosaurus', 'Giganotosaurus', 'Archaeopteryx',
	'Mosasaurus', 'Stegosaurus', 'Nigersaurus', 'Velociraptor', 'Spinosaurus', 'Tyrannosaurus',
	'Microraptor'
])
# Create a dropdown menu
animal_combobox = ttk.Combobox(app, values=animals)
animal_combobox.pack(side="top", pady=10)

# Function to handle selection
def on_animal_selected(event):
    selected_animal = animal_combobox.get()
    show_animal_profile(selected_animal)

# Bind the selection event
animal_combobox.bind('<<ComboboxSelected>>', on_animal_selected)


profile_text_widget.config(yscrollcommand=scrollbar.set)

image_label = ttk.Label(app)
image_label.pack(side="top", fill='both', expand=True)

toggle_theme_button = ttk.Button(app, text='Dark Mode', command=toggle_theme)
toggle_theme_button.pack(side="top")

about_button = ttk.Button(app, text="About", command=show_about)
about_button.pack(side="top", pady=10)

# Apply the initial sepia theme
apply_theme(sepia)

# Start the application loop
app.mainloop()
