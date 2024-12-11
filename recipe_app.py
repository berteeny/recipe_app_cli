# dotenv variable for database connection
import os
from dotenv import load_dotenv
load_dotenv()
credentials = os.getenv("credentials")

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import sessionmaker

# ignores deprecation warning in console
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

line = ("-"*35)

# creating engine to connect to database
engine = create_engine(credentials)

# stores declarative base
Base = declarative_base()

# creating session to modify data
Session = sessionmaker(bind=engine)
session = Session()

class Recipe(Base):
    __tablename__ = "final_recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    ingredients = Column(String(255))
    cooking_time = Column(Integer)
    difficulty = Column(String(20))

# quick representation of recipe
    def __repr__(self):
        return f"<Recipe ID: {self.id}- {self.name}, {self.difficulty}>"
    
    

# well formatted version of recipe
    def __str__(self):
        return (
            f"{line}\n"
            f"Recipe ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Ingredients: {self.ingredients}\n"
            f"Cooking time: {self.cooking_time} minutes\n"
            f"Difficulty: {self.difficulty}\n"
            f"{line}"
            )
    
# calculate difficulty based on cooking time and number of ingredients 
    def calculate_difficulty(self):
        num_ingredients = len(self.return_ingredients_as_list())
        if int(self.cooking_time) < 10 and num_ingredients < 4:
            self.difficulty = "Easy"
        if int(self.cooking_time) < 10 and num_ingredients >= 4:
            self.difficulty = "Medium"
        if int(self.cooking_time) >= 10 and num_ingredients < 4:
            self.difficulty = "Intermediate"
        if int(self.cooking_time) >= 10 and num_ingredients >= 4:
            self.difficulty = "Hard"
        
# returns list of ingredients if there are ingredients, and an empty list if no ingredients 
    def return_ingredients_as_list(self):
        if not self.ingredients:
            return []
        else:
            return self.ingredients.split(", ")
        
# create table on database
Base.metadata.create_all(engine)


# main operation functions

# create a new recipe
def create_recipe():
    print(line)
    name = input("Enter the name of your recipe: ").capitalize()
    print(line)
    if len(name) > 50:
        print("Please enter a name that is less than 50 characters.")
        return
    elif not all(char.isalpha() or char.isspace() for char in name):
        print("Name can only include letters and spaces, please try again.")
        return
    
    ingredients = []
    print(line)
    n = int(input("How many ingredients would you like to enter? "))
    print(line)
    for i in range(n):
        ingredient = input("Enter new ingredient: ")
        ingredients.append(ingredient)
        ingredients_str = ", ".join(ingredients)
    
    print(line)
    cooking_time = (input("Enter the cooking time for your recipe in minutes: "))
    print(line)
    if not cooking_time.isnumeric():
        print("Cooking time must be a number.")
        return

# adding recipe to table
    recipe_entry = Recipe(
        name = name,
        ingredients = ingredients_str,
        cooking_time = cooking_time
    )

# caluclating + setting difficulty
    recipe_entry.calculate_difficulty()

# adding recipe_entry and committing changes
    session.add(recipe_entry)
    session.commit()

    print(line)
    print("Recipe has been added to the database!")


# view all recipes
def view_all_recipes():
    result = session.query(Recipe).all()
    if not result:
        print("There are currently no recipes in the database.")
        return
    else:
        print(line)
        print("All available recipes:")
        print(line)
        for recipe in result:
            print(recipe)

# search recipe by ingrdient
def search_by_ingredients():
    ing_list = session.query(Recipe).count()
    if ing_list == 0:
        print("There are currently no recipes in the database.")
        return
    else: 
        result = session.query(Recipe.ingredients).all()
        all_ingredients = []
        for r in result:
            temp_list = r[0].split(", ")
            for t in temp_list:
                if not t in all_ingredients:
                    all_ingredients.append(t)

        print(line)
        for i, ingredient in enumerate(all_ingredients, 1):
            print(f"{i}. {ingredient}")
        print(line)
        n = input("Please type the numbers of ingredients you would like to search for, seperated by spaces: ").split()
        print(line)
        for i in n:
            if not int(i.isnumeric()):
                print("Only numbers are allowed.")
            elif int(i) < 1 or int(i) > len(all_ingredients):
                print("Invalid number entered, please try again.")
            else:
                search_ingredients = []
                search_ingredients.append(all_ingredients[int(i) - 1])
        conditions = []
        for i in search_ingredients:
            like_term = f"%{i}%"
            conditions.append(Recipe.ingredients.like(like_term))

        matching_ingredients = session.query(Recipe).filter(*conditions).all()
        if not matching_ingredients:
            print("No recipes found with these ingredients.")
        else:
            for i in matching_ingredients:
                print(i)

# edit existing recipe
def edit_recipe():
    result = session.query(Recipe).count()
    if result == 0:
        print("There are currently no recipes in the database.")
        return
    else:
        results = session.query(Recipe.id, Recipe.name).all()
        print("\nAvailable recipes:")
        print(line)
        for i in results:
            print(f"{i.id}. {i.name}")
        print(line)
        selected_id = input("Enter the number of the recipe you wish to edit: ").strip()
        if not int(selected_id.isnumeric()) or int(selected_id) not in [r.id for r in results]:
            print("\nInvalid entry, please try again")

        else:
            recipe_to_edit = session.query(Recipe).filter(Recipe.id == selected_id).one()
            print(line)
            print(f"1. Name: {recipe_to_edit.name}")
            print(f"2. Ingredients: {recipe_to_edit.ingredients}")
            print(f"3. Cooking time in minutes: {recipe_to_edit.cooking_time}")
            print(line)
            n = input("Enter the number of the value you wish to edit (one at a time): ").strip()
            if n not in ["1", "2", "3"]:
                print("Invalid choice, please enter 1, 2 or 3.")
            elif n == "1":
                print(line)
                new_value = input("Enter the new name for this recipe: ")
                print(line)
                if len(new_value) > 50 or not all(char.isalpha() or char.isspace() for char in new_value):
                    print("Name must only contain letters, and must be less than 50 characters.")
                else:
                    recipe_to_edit.name = new_value.capitalize()
                    print("Recipe has been updated!")

            elif n == "2":
                print(line)
                new_value_list = input("Enter all ingredients, seperated by commas: ").split()
                print(line)
                if len(new_value_list) > 255:
                    print("Ingredients must be less than 255 characters.")
                else:    
                    new_value = " ".join(new_value_list)
                    recipe_to_edit.ingredients = new_value
                    print("Recipe has been updated!")

            elif n == "3":
                print(line)
                new_value = input("Enter a new cooking time in minutes: ").strip()
                print(line)
                if not int(new_value.isnumeric()):
                    print("Only numbers are allowed.")
                else: 
                    recipe_to_edit.cooking_time = int(new_value)
                    print("Recipe has been updated!")
            recipe_to_edit.calculate_difficulty()

            session.commit()        
                

# delete recipe
def delete_recipe():
    result = session.query(Recipe).count()
    
    if result == 0:
        print(line)
        print("There are currently no recipes in the database.")
        return
    else:
        all_recipes = session.query(Recipe.id, Recipe.name).all()
        print("All available recipes:")
        print(line)
        for recipe in all_recipes:
            print(f"{recipe.id}. {recipe.name}")
        print(line)
        n = input("Please enter the number of the recipe you wish to delete: ").strip()
        print(line)
        if not int(n.isnumeric()) or int(n) not in [r.id for r in all_recipes]:
            print("Invalid entry, please try again.")

        else:
            recipe_to_delete = session.query(Recipe).filter(Recipe.id == int(n)).one()
            if not recipe_to_delete:
                print("That number is not assigned to a recipe, please try again.")
            else:
                print("Are you sure you wish to delete this recipe? This action cannot be undone.")
                verification = input("Continue? (y/n)").lower().strip()
                print(line)
                if verification == "n":
                    print("Deletion cancelled.")
                elif verification == "y":
                    session.delete(recipe_to_delete)
                    session.commit()
                    print("Recipe deleted.") 
                else:
                    print("Invalid entry, please type either y or n")

            
# main menu
def main_menu():
    while True:
        print(line)
        print("Welcome to Recipes!")
        print("What would you like to do?")
        print(line)
        print("1. Create a new recipe")
        print("2. View all recipes")
        print("3. Search for a recipe by ingredient")
        print("4. Edit an existing recipe")
        print("5. Delete an existing recipe")
        print("6. Exit")
        print(line)
        action = input("Please type a number to select an action: ").strip()
          
          
        if action == "1":   
            create_recipe()
        elif action == "2":
            view_all_recipes()
        elif action == "3":
            search_by_ingredients()
        elif action == "4":
            edit_recipe()
        elif action == "5":
            delete_recipe()
        elif action == "6":   
            print("\nExiting Recipes.")
            session.close()
            engine.dispose()
            break
        else:
            print("\nInvalid entry, please type a number between 1 and 6.\n")
            

# start main menu on init
main_menu()