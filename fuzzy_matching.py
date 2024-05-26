from fuzzywuzzy import fuzz, process
import re

# Database of car names
car_db = [
    "ford_aspire", "ford_ecosport", "ford_endeavour", "ford_figo", 
    "honda_amaze", "honda_city", "honda_wr_v", "hyundai_aura", 
    "hyundai_grand_i10", "hyundai_i10", "jeep_compass", "jeep_meridian", 
    "kia_carens", "kia_seltos", "kia_sonet", "land_rover_defender", 
    "mahindra_scorpio", "mahindra_thar", "mahindra_xuv300", "mahindra_xuv400", 
    "mahindra_xuv700", "maruti_celerio", "maruti_suzuki_brezza", 
    "maruti_suzuki_s_presso", "maruti_suzuki_swift", "maruti_suzuki_wagonr", 
    "maruti_suzuki_xl6", "mg_astor", "mg_gloster", "mg_hector", "mg_zs_ev", 
    "renault_kiger", "renault_triber", "skoda_kushaq", "skoda_slavia", 
    "tata_harrier", "tata_punch", "tata_tiago", "toyota_camry", "toyota_fortuner", 
    "toyota_fortuner_legender", "toyota_glanza", "toyota_innova_crysta", 
    "nissan_magnite", "volkswagen_tiguan"
]

# Normalize the text by converting to lowercase and removing certain words
def normalize(text):
    text = text.lower()
    text = re.sub(r'\b(india|pvt|ltd|motor|cars)\b', '', text)
    text = re.sub(r'\W+', ' ', text).strip()
    return text if text else "unknown"

# Extract the model name from user input based on the given word count
def extract_model(user_input, word_count):
    match = re.search(r'-\s*([^\s-]+(?:\s+[^\s-]+)*)', user_input)
    if match:
        model = match.group(1)
        return ' '.join(model.split()[:word_count])
    return user_input.strip()

# Extract the brand name from user input
def extract_brand(user_input, known_brands):
    norm_input = normalize(user_input)
    for brand in known_brands:
        if brand in norm_input:
            return brand
    return ""

# Remove the brand name from the model name
def remove_brand(model_name, brand_name):
    pattern = re.compile(re.escape(brand_name), re.IGNORECASE)
    return pattern.sub('', model_name).strip()

# Find the best match for the user input from the car database
def best_match(user_input, car_db, known_brands):
    user_brand = extract_brand(user_input, known_brands)
    norm_user_brand = normalize(user_brand)
    db_brands = {name.split('_')[0] for name in car_db}

    if norm_user_brand != "unknown":
        best_brand = (norm_user_brand if norm_user_brand in db_brands 
                      else process.extractOne(norm_user_brand, db_brands, scorer=fuzz.token_set_ratio)[0])
        brand_matches = [name for name in car_db if name.startswith(best_brand)]
        model_name = extract_model(user_input, 2)
        refined_model = remove_brand(normalize(model_name), best_brand)
        best_name, best_score = process.extractOne(refined_model, brand_matches, scorer=fuzz.token_set_ratio)
    else:
        norm_input_1 = normalize(extract_model(user_input, 1))
        norm_input_2 = normalize(extract_model(user_input, 2))
        best_name_1, best_score_1 = process.extractOne(norm_input_1, car_db, scorer=fuzz.token_set_ratio)
        best_name_2, best_score_2 = process.extractOne(norm_input_2, car_db, scorer=fuzz.token_set_ratio)
        if best_score_1 >= best_score_2:
            best_name, best_score = best_name_1, best_score_1
        else:
            best_name, best_score = best_name_2, best_score_2
    
    return best_name, best_score

# Unique brands from the car database
unique_brands = {name.split('_')[0] for name in car_db}

# Main loop to take user input and find best match
if __name__ == "__main__":
    while True:
        user_input = input("Enter vehicle  (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            break
        
        # Check for invalid inputs
        if not re.search(r'[a-zA-Z0-9]', user_input):
            print("Invalid input. Please enter a valid vehicle .\n")
            continue
        
        match_name, match_score = best_match(user_input, car_db, unique_brands)
        print(f"{match_name} - {match_score}%\n")
