from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from colorama import init, Fore, Style
import json
from gtts import gTTS
import os

# Setup
init(autoreset=True)
model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

VALID_PIZZAS = [
    "Margherita", "Pepperoni", "Vegetariana", "Four Cheese", "Diavola",
    "BBQ Chicken", "Hawaiian", "Paneer Tikka", "Vegan Delight"
]
VALID_SIZES = ["small", "medium", "large"]

order = {
    "pizza": None,
    "size": None,
    "toppings": [],
    "allergies": None,
    "specialRequests": None,
    "name": None,
    "address": None
}

steps = [
    ("pizza", "What pizza would you like?"),
    ("size", "What size do you want? (small, medium, large)"),
    ("toppings", "Any extra toppings?"),
    ("allergies", "Do you have any allergies or dietary restrictions?"),
    ("specialRequests", "Any special requests? (e.g. very spicy, no onions)"),
    ("name", "Can I have your name?"),
    ("address", "What's your delivery address?")
]

def ai_greeting():
    prompt = "Greet the customer politely and ask what pizza they'd like to order."
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=50)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def take_order():
    for field, question in steps:
        while True:
            print(Fore.GREEN + f"PizzaBot: {question}" + Style.RESET_ALL)
            answer = input("You: ").strip()

            if field == "toppings":
                if answer.lower() in ["no", "none", "nothing"]:
                    order["toppings"] = []
                else:
                    order["toppings"] = [t.strip() for t in answer.split(",")]
                break

            elif field == "pizza":
                matched_pizza = None
                for pizza in VALID_PIZZAS:
                    if pizza.lower() in answer.lower():
                        matched_pizza = pizza
                        break
                if matched_pizza:
                    order["pizza"] = matched_pizza
                    break
                else:
                    print(Fore.RED + f"Sorry, we don't have that. Choose from: {', '.join(VALID_PIZZAS)}" + Style.RESET_ALL)

            elif field == "size":
                detected_size = None
                for size in VALID_SIZES:
                    if size in answer.lower():
                        detected_size = size
                        break
                if detected_size:
                    order["size"] = detected_size
                    break
                else:
                    print(Fore.RED + "Please choose a size: small, medium, or large." + Style.RESET_ALL)

            else:
                order[field] = answer
                break

def show_order():
    print("\n" + Fore.YELLOW + "PizzaBot: Here's your final order:" + Style.RESET_ALL)
    print(f"Pizza: {order['pizza']}")
    print(f"Size: {order['size']}")
    print(f"Toppings: {', '.join(order['toppings']) if order['toppings'] else 'None'}")
    print(f"Allergies: {order['allergies'] or 'None'}")
    print(f"Special Requests: {order['specialRequests'] or 'None'}")
    print(f"Name: {order['name']}")
    print(f"Delivery Address: {order['address']}")

# Run bot
print(Fore.CYAN + "PizzaBot: Hello! I'm your pizza assistant. Let's build your order!" + Style.RESET_ALL)
print(Fore.CYAN + "PizzaBot: " + ai_greeting() + Style.RESET_ALL)
take_order()

# Allow corrections
while True:
    show_order()
    confirmation = input(Fore.YELLOW + "\nPizzaBot: Does everything look correct? (yes/no): " + Style.RESET_ALL).lower()

    if confirmation == "yes":
        break

    print(Fore.BLUE + "PizzaBot: What would you like to change? (pizza, size, toppings, allergies, special requests, name, address)" + Style.RESET_ALL)
    field = input("You: ").strip().lower()

    if field in order:
        print(Fore.GREEN + f"PizzaBot: Please enter the new {field}:" + Style.RESET_ALL)
        new_value = input("You: ").strip()
        if field == "toppings":
            if new_value.lower() in ["no", "none", "nothing"]:
                order["toppings"] = []
            else:
                order["toppings"] = [t.strip() for t in new_value.split(",")]
        else:
            order[field] = new_value
    else:
        print(Fore.RED + "PizzaBot: Sorry, that's not a valid field. Please try again." + Style.RESET_ALL)

# Confirm order
print(Fore.MAGENTA + "\nPizzaBot: Awesome! Your order is confirmed. We'll start preparing your delicious pizza right away!" + Style.RESET_ALL)

with open("final_order.json", "w") as f:
    json.dump(order, f, indent=4)

# Speak summary
summary = f"""
Your order summary:
Pizza: {order['size']} {order['pizza']}
Toppings: {', '.join(order['toppings']) if order['toppings'] else 'None'}
Allergies: {order['allergies'] or 'None'}
Special Requests: {order['specialRequests'] or 'None'}
Delivery Address: {order['address']}
Customer Name: {order['name']}
"""

print(Fore.YELLOW + "\nSpeaking summary..." + Style.RESET_ALL)
tts = gTTS(text=summary, lang="en")
tts.save("order.mp3")
os.system("start order.mp3")
