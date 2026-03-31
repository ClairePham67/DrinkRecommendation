
import sqlite3
import random
#1. CREATE A DATABASE THAT STORES USER'S DRINKS: this contain name of the drinks and ingredients.
##User can select their favorite drinks.
def create_drink_database():
    # Connect to SQLite database 
    conn = sqlite3.connect("drinks_database.db")
    cursor = conn.cursor()

    # Drop old table if it exists (clears old structure with 'category' column)
    cursor.execute("DROP TABLE IF EXISTS favorite_drinks")
    # Create table for saving user's favorite drinks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorite_drinks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drink_name TEXT NOT NULL,
        ingredients TEXT,
        is_favorite INTEGER DEFAULT 0,
        category TEXT
    );
    """)

    sample_drinks = [
        ("Espresso", "Espresso shot"),
        ("Latte", "Espresso, Steamed milk"),
        ("Cappuccino", "Espresso, Steamed milk, Foam"),
        ("Green Tea", "Green tea leaves, Water"),
        ("Black Tea", "Black tea leaves, Water"),
        ("Chai Latte", "Black tea, Milk, Spices"),
        ("Orange Juice", "Orange"),
        ("Apple Juice", "Apple"),
        ("Smoothie", "Mixed fruits, Yogurt"),
        ("Iced Coffee", "Coffee, Ice")
    ]
    #category_pool = ["Coffee", "Uncategorized", "Tea", "Juice", "Smoothie", "Soda", "Chocolate", "Energy Drink", "Milkshake"]
    # Randomly generate the rest up to 50 drinks
    ingredients_pool = ["Milk", "Espresso", "Ice", "Tea", "Sugar", "Lemon", "Mint", "Ginger", "Orange", "Apple", "Syrup", "Water"]
    #randomly generate 50 drinks
    while len(sample_drinks) < 50:
        name = f"Drink_{len(sample_drinks)+1}"
        ingredients = ", ".join(random.sample(ingredients_pool, k=3))
        sample_drinks.append((name, ingredients))

    # Insert drinks into the table
    cursor.executemany("""INSERT INTO favorite_drinks (drink_name, ingredients) VALUES (?, ?)""", sample_drinks)
    #Commit the change and close
    print("Database and table created with 50 drinks.")
    conn.commit()
    conn.close()
    
#2. DISPLAY ALL DRINKS TO USER
def display_drinks():
    conn = sqlite3.connect("drinks_database.db")
    cursor = conn.cursor()
    # Select all rows from the table
    cursor.execute("SELECT id, drink_name, ingredients, is_favorite, category FROM favorite_drinks")
    rows = cursor.fetchall()
    #header
    print(f"{'ID':<5} {'Drink Name':<20} {'Ingredients':<40} {'Favorite':<10}{'Category':<15}")
    # Print each row
    for row in rows:
        id_, name, ingredients, is_fav, category = row
        category = category if category else "Uncategorized"
        print(f"{id_:<5} {name:<20} {ingredients:<40} {is_fav:<10}{category:<15}")
    conn.close()

#3. MARK FAVORITE DRINK AND UPDATE THE DATABASE
#User mark a drink as their favorite (Favorite = 1)
def mark_favorite(): 
    try:
        #Ask user the ID drink they want to mark as their favorite and update that from 0 to 1 (fav)
        fav_id = int(input("\nEnter the ID of the drink you want to mark as favorite: "))
        conn = sqlite3.connect("drinks_database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE favorite_drinks SET is_favorite = 1 WHERE id = ?", (fav_id,))
        conn.commit()
        print(f"Drink with ID {fav_id} marked as favorite.")

        # Re-fetch and display updated table
        cursor.execute("SELECT * FROM favorite_drinks")
        updated_rows = cursor.fetchall()

        print("\nUpdated Drink List:")
        print(f"{'ID':<5} {'Drink Name':<20} {'Ingredients':<40} {'Favorite':<10}")
        for row in updated_rows:
            id_, name, ingredients, is_fav = row
            print(f"{id_:<5} {name:<20} {ingredients:<40} {is_fav:<10}")
        conn.close()
        
    except ValueError:
        print("Invalid input. Please enter a valid drink ID.")

#4. Ask AI for a drink suggestion and its recipe to make at home based on the weather and flavor's descriptions.
###ask user if they want to add this recipe into their list of drinks and mark as favorite. (Update on database)
import openai
import os
def drink_suggestion():
    # Create OpenAI client with API key
    client = openai.OpenAI(
        api_key="APIKey" 
    )

    MODEL_NAME = "gpt-4.1"

    # Get user input about the city, flavor preferences, and available ingredients
    city = input("Enter your city for weather-based sugesstions: ")
    flavor_profile = input("What flavor preferences are you in the mood for? e.g. sweet, fruity, etc.")
    ingredients = input("List the ingredients you have available (comma-seperated): ")
    print("...AI responding...")
    #Construct user prompt
    user_prompt = (
        f"I'm in {city}. Can you recommend a drink recipe based on the current weather here?"
        f"I'm in the mood for something{flavor_profile}."
        f"I have the following ingredients at home: {ingredients}."
        f"Please give me a recipe I can make using these ingredients."
        )
    try:
        # Send request
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        # Extract and print content
        message = response.choices[0].message
        print("\n--- DRINK RECOMMENDATION FOR YOU ---")
        print(message.content)
        #Ask user to if they want to save the recipe and mark as their favorite drink
        save_recipe = input("\nWould you like to save this drink to your list? (y/n): ").strip().lower()
        if save_recipe == 'y':
            mark_favorite = input("Do you want to mark this drink as a favorite? (y/n): ").strip().lower()
            is_favorite = 1 if mark_favorite == 'y' else 0
            # Connect to SQLite database (it will create the file if it doesn't exist)
            conn = sqlite3.connect("drinks_database.db")
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorite_drinks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    drink_name TEXT,
                    ingredients TEXT,
                    is_favorite INTEGER DEFAULT 0
                )
            ''')

            # Ask for drink name
            drink_name = input("Enter a name for this drink: ").strip()

            # Insert drink into table
            cursor.execute('''
                INSERT INTO favorite_drinks (drink_name, ingredients, is_favorite)
                VALUES (?, ?, ?)
            ''', (drink_name, ingredients, is_favorite))
            print("Drink recipe is saved to your list.")
            # Save and close connection
            conn.commit()
            conn.close()

    except Exception as e: #execute if there is error running the program and print the error message
        print("\n--- ERROR OCCURRED ---")
        print(str(e))

#5. Ask AI to find the nearest coffee shop that sells a particular drink.
def find_coffee_store():
    # Create OpenAI client with API key
    client = openai.OpenAI(
        api_key="API" 
    )

    MODEL_NAME = "gpt-4.1"
    #Get user drink they want and if anything else to add on like check if the coffee shop runs promotion/seasonal specials
    drink_name = input("What drink would you like? ")
    location = input("Enter your location: ")
    more_concern = input("Do you want to look up anything else about your drink or allergies or coffee shop? (y/n)")
    if more_concern == "y":
        additional_request = input("Additional request:  ")
    else:
        additional_request = "I do not have any additional request."
    print("...AI responding...")
    #Construct user prompt
    user_prompt = (f"I want a {drink_name} and I am currently at {location}. Could you please find a coffee shop nearby that sells this drink?\t{additional_request}")
    try:
        # Send request
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        # Extract and print content
        message = response.choices[0].message
        print("\n--- COFFEE SHOPS NEAR YOU ---")
        print(message.content)
    except Exception as e: #execute if there is error running the program and print the error message
        print("\n--- ERROR OCCURRED ---")
        print(str(e))

#6. Ask AI to rate my custom recipe in a scale (1-10, respectively, lowest score to highest score) and make additional adjustment
def rating_my_recipe():
    # Create OpenAI client with API key
    client = openai.OpenAI(
        api_key="APIKEY" 
    )

    MODEL_NAME = "gpt-4.1"
    #Get user input for their make-up recipe
    print("Type your custom recipe down here:")
    your_recipe = input("My invented recipe:  ")
    print("...AI responding...")
    #Construct user prompt
    user_prompt = (f" {your_recipe}. Please rate my idea in a scale (1-10, 10 is highest score), and if I need to make any additional adjustment")
    try:
        # Send request
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        # Extract and print content
        message = response.choices[0].message
        print("\nRATING YOUR EXPERIMENTAL RECIPE")
        print(message.content)
    except Exception as e: #execute if there is error running the program and print the error message
        print("\n--- ERROR OCCURRED ---")
        print(str(e))

# 7. This feature add a drink category. Using a new DrinkCategory class that store drink's ID, name, and category
class DrinkCategory:
    def __init__(self, drink_id, drink_name, category):
        self.drink_id = drink_id
        self.drink_name = drink_name
        self.category = category

    def set_drink_id(self, drink_id):
        self.drink_id = drink_id

    def set_drink_name(self, drink_name):
        self.drink_name = drink_name

    def set_category(self, category):
        self.category = category

    def get_drink_id(self):
        return self.drink_id

    def get_drink_name(self):
        return self.drink_name

    def get_category(self):
        return self.category

#Function to allow user to modify a category to a drink in a database
def assign_drink_category():
    conn = sqlite3.connect("drinks_database.db")
    cursor = conn.cursor()

    # Add a new column 'category' since it doesn't exist yet
    cursor.execute("PRAGMA table_info(favorite_drinks)")
    columns = [info[1] for info in cursor.fetchall()]
    if "category" not in columns:
        cursor.execute("ALTER TABLE favorite_drinks ADD COLUMN category TEXT")

    # Show drinks to user first
    cursor.execute("SELECT id, drink_name, ingredients FROM favorite_drinks")
    drinks = cursor.fetchall()
    print("\nAvailable Drinks to Categorize:")
    for drink in drinks:
        print(f"ID: {drink[0]}, Name: {drink[1]}, Ingredients: {drink[2]}")

    try:
        # Get user input
        drink_id = int(input("\nEnter the ID of the drink you want to categorize: "))
        category = input("Enter the category for this drink (e.g., coffee, smoothie, soda, chocolate, etc.): ").strip()

        # Create DrinkCategory object
        cursor.execute("SELECT drink_name FROM favorite_drinks WHERE id = ?", (drink_id,))
        drink_row = cursor.fetchone()
        if drink_row:
            drink_name = drink_row[0]
            drink_obj = DrinkCategory(drink_id, drink_name, category)

            # Update database
            cursor.execute(
                "UPDATE favorite_drinks SET category = ? WHERE id = ?",
                (drink_obj.get_category(), drink_obj.get_drink_id())
            )
            conn.commit()
            print(f"\nDrink '{drink_obj.get_drink_name()}' has been categorized as '{drink_obj.get_category()}'.")
        else:
            print("No drink found with that ID.")

    except ValueError:
        print("Invalid input. Please enter a valid drink ID.")

    conn.close()

    
import tkinter as tk
from tkinter import messagebox
def handle_exit(): #this handle exit command
        exit
def handle_mark_favorite():
        display_drinks()
        mark_favorite()
def main():
    create_drink_database()  # run once at the start
    #GUI for user
    # Create main window
    root = tk.Tk()
    root.title("Favorite Drink Tracker")
    root.geometry("400x400")

    # Title Label
    title_label = tk.Label(root, text="Favorite Drink Tracker", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=20)
    #Button color and style
    button_style = {
        "width": 30,
        "height": 2,
        "bg": "#4CAF50",     #  green color
        "fg": "white",       # White text
        "activebackground": "#45a049", # Darker green when clicked
        "activeforeground": "white",
        "bd": 0,             # No border for flat style
        "font": ("Helvetica", 12)
    }

    # Buttons for each option
    btn_view = tk.Button(root, text="View All Drinks", command=display_drinks, **button_style)
    btn_view.pack(pady=5)

    btn_mark = tk.Button(root, text="Mark a Drink as Favorite", command=handle_mark_favorite, **button_style)
    btn_mark.pack(pady=5)

    btn_suggest = tk.Button(root, text="Ask AI for Drink Suggestion", command=drink_suggestion, **button_style)
    btn_suggest.pack(pady=5)

    btn_find = tk.Button(root, text="Find Nearest Coffee Shop", command= find_coffee_store, **button_style)
    btn_find.pack(pady=5)

    btn_rate = tk.Button(root, text="Rate My Custom Recipe", command=rating_my_recipe, **button_style)
    btn_rate.pack(pady=5)
    btn_assign_category = tk.Button(root, text="Assign Category to Drink", command=assign_drink_category, **button_style)
    btn_assign_category.pack(pady=5)
    
    btn_exit = tk.Button(root, text="Exit Program", command=handle_exit, **button_style)
    btn_exit.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()

