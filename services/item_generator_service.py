import random
import logging
import re
import uuid
import time
import hashlib
import json
import base64
from cryptography.fernet import Fernet
import os

logger = logging.getLogger(__name__)

# Generamos una clave secreta para la encriptación
# Esta clave debe ser guardada de forma segura y no debe ser compartida
SECRET_KEY = os.environ.get('ITEM_ENCRYPTION_KEY') or Fernet.generate_key()
cipher_suite = Fernet(SECRET_KEY)

def generate_unique_id(item_info):
    # Añadimos un timestamp para mayor unicidad
    item_info["timestamp"] = int(time.time())
    
    # Convertimos toda la información del objeto a JSON
    item_json = json.dumps(item_info)
    
    # Encriptamos la información
    encrypted_info = cipher_suite.encrypt(item_json.encode())
    
    # Codificamos la información encriptada en base64
    encrypted_info_encoded = base64.urlsafe_b64encode(encrypted_info).decode()
    
    # Generamos un hash SHA-256 de la información encriptada
    hash_object = hashlib.sha256(encrypted_info)
    hash_digest = hash_object.hexdigest()
    
    # Combinamos la información encriptada, el hash y un UUID para mayor unicidad
    unique_id = f"{encrypted_info_encoded}.{hash_digest[:16]}.{str(uuid.uuid4())}"
    
    return unique_id

def decode_unique_id(unique_id):
    try:
        # Separamos las partes del ID
        encrypted_info_encoded, hash_part, uuid_part = unique_id.split('.')
        
        # Decodificamos la información encriptada de base64
        encrypted_info = base64.urlsafe_b64decode(encrypted_info_encoded)
        
        # Desencriptamos la información
        decrypted_info = cipher_suite.decrypt(encrypted_info)
        
        # Convertimos la información desencriptada a un diccionario
        item_info = json.loads(decrypted_info)
        
        # Convertimos el timestamp a un formato legible
        item_info["creation_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item_info["timestamp"]))
        
        # Añadimos las partes del hash y UUID al diccionario de información
        item_info["hash_part"] = hash_part
        item_info["uuid_part"] = uuid_part
        
        return item_info
    except Exception as e:
        return {"error": f"No se pudo decodificar el ID: {str(e)}"}

class ItemGenerator:
    def __init__(self):
        self.colors = [
            "silver", "iron", "steel", "bronze", "copper", "brass", "gold", 
            "black", "gray", "brown", "red", "blue", "green", "white", 
            "yellow", "orange", "purple", "crimson", "navy", "forest green", 
            "tan", "beige", "maroon", "olive", "ivory", "ebony"
        ]

        self.item_types = [
            # Armor - Head
            "helmet", "crown",
            # Armor - Torso
            "chestplate", "breastplate",
            # Armor - Arms
            "bracer", "glove",
            # Armor - Legs
            "greaves", "pant",
            # Armor - Feet
            "boot", "shoe",
            # Shields
            "shield",
            # Melee weapons
            "sword", "axe", "mace", "spear", "dagger", "warhammer",
            # Ranged weapons
            "bow", "crossbow"
        ]
        
        self.materials = [
            "iron", "steel", "bronze", "copper", "brass", "silver", "gold", 
            "leather", "wood", "oak", "pine", "maple", "elm", "ash",
            "cloth", "linen", "wool", "silk", "cotton", 
            "stone", "granite", "marble", "obsidian", "flint",
            "bone", "ivory", "horn", "scale",
            "hardened leather", "studded leather", "boiled leather",
            "reinforced wood", "treated wood", "lacquered wood",
            "tempered steel", "folded steel", "damascus steel",
            "mithril", "adamantium", "orichalcum"  # Algunos materiales fantásticos comunes
        ]
        
        self.effects = [
            "glowing", "shimmering", "pulsating", "humming", "floating", "whispering", "crackling", "swirling", 
            "radiating", "resonating", "flickering", "sparking", "smoking", "rippling", "hovering", "vibrating", 
            "echoing", "shining", "blazing", "freezing", "melting", "phasing", "warping", "distorting", "singing", 
            "chiming", "thundering", "lightning", "raining", "snowing", "steaming", "bubbling", "dripping", "oozing", 
            "crystallizing", "disintegrating", "reforming", "multiplying", "shrinking", "growing", "teleporting", 
            "vanishing", "reappearing", "levitating", "orbiting", "spiraling", "cascading", "erupting", "imploding"
        ]
        
        self.powers = [
            "arcane", "divine", "elemental", "psychic", "nature", "cosmic", "demonic", "celestial", "temporal", "void", 
            "necromantic", "illusion", "transmutation", "enchantment", "abjuration", "evocation", "conjuration", 
            "divination", "shadow", "light", "chaos", "order", "life", "death", "dream", "nightmare", "gravity", 
            "dimensional", "planar", "astral", "ethereal", "fae", "draconic", "eldritch", "primordial", "runic", 
            "blood", "soul", "mind", "body", "spirit", "quantum", "alchemical", "technological", "psionic", "kinetic", 
            "thermal", "sonic", "magnetic", "radioactive", "crystalline"
        ]
        
        self.details = [
            "intricate engravings", "gemstones", "runes", "symbols", "ethereal patterns", "living vines", 
            "shifting constellations", "ancient scriptures", "pulsing veins", "spectral wisps", "fractal patterns", 
            "holographic images", "swirling mists", "floating sigils", "pulsing auras", "shimmering forcefield", 
            "orbiting particles", "cascading energy", "flickering shadows", "prismatic reflections", "morphing shapes", 
            "hypnotic spirals", "ghostly apparitions", "burning embers", "crackling electricity", "frozen crystals", 
            "bubbling liquids", "swirling vortexes", "ticking gears", "pulsing heartbeat", "whispering voices", 
            "echoing footsteps", "rustling leaves", "howling winds", "crashing waves", "rumbling earth", "twinkling stars", 
            "phases of the moon", "solar eclipses", "auroral lights", "cosmic nebulae", "black holes", "quantum fluctuations", 
            "time distortions", "reality ripples", "dimensional rifts", "astral projections", "spirit manifestations"
        ]
        
        self.abilities = [
            "enhance focus", "boost strength", "improve agility", "increase wisdom", "amplify magic", "manipulate time", 
            "control elements", "summon spirits", "drain life", "grant invisibility", "teleport", "shapeshift", 
            "mind control", "foresee the future", "resurrect the dead", "create illusions", "manipulate gravity", 
            "phase through matter", "absorb energy", "reflect attacks", "heal wounds", "curse enemies", "bless allies", 
            "control weather", "communicate with nature", "open portals", "manipulate emotions", "grant wishes", 
            "control probability", "manipulate dreams", "bend reality", "nullify magic", "create force fields", 
            "manipulate size", "control magnetism", "generate electricity", "manipulate light", "control sound", 
            "manipulate plants", "control animals", "manipulate metal", "generate force", "control temperature", 
            "manipulate memories", "grant flight", "breathe underwater", "see in darkness", "understand all languages"
        ]
        
        self.origins = [
            "forged by ancient dwarves", "blessed by elven priests", "crafted by a mad wizard", "found in a dragon's hoard", 
            "gifted by the gods", "created from a fallen star", "emerged from the Void", "stolen from a demon lord", 
            "unearthed from a forgotten tomb", "assembled by a time traveler", "woven by cosmic spiders", "sung into existence by sirens", 
            "crystallized from a phoenix's tear", "forged in the heart of a dying star", "carved from the World Tree", 
            "born from the dreams of a sleeping titan", "crafted from the essence of a dead god", "formed in the depths of the abyss", 
            "created by a wish from a djinn", "pulled from a parallel universe", "grown in an alchemist's garden", 
            "built by an ancient automaton", "shaped by the collective will of a hive mind", "retrieved from the astral plane", 
            "won in a bet with Fate itself", "found in the wreckage of a sky castle", "formed from solidified moonlight", 
            "created by a child's imagination", "born from the clash of opposing elements", "discovered in the ruins of Atlantis", 
            "retrieved from the far future", "summoned from the realm of nightmares", "created by a reality-warping paradox", 
            "formed from the last breath of a dying universe", "crafted by the Fae in their twilight realm", 
            "discovered in the belly of a world-serpent", "created from the shattered shards of a magic mirror", 
            "born from the fusion of matter and antimatter", "woven from the threads of destiny", "shaped by the echoes of creation", 
            "found in the space between dimensions", "crafted from the bones of an elder dragon", "born from a supernova explosion", 
            "created by the dance of chaos and order", "retrieved from the edge of reality", "formed in the crucible of creation"
        ]

    def generate_item_description(self, keyword):
        logger.info(f"Generando descripción para palabra clave: {keyword}")
        
        color = random.choice(self.colors)
        item_type = random.choice(self.item_types)
        material = random.choice(self.materials)
        effect = random.choice(self.effects)
        power = random.choice(self.powers)
        detail = random.choice(self.details)
        ability = random.choice(self.abilities)
        origin = random.choice(self.origins)

        description = f"The {keyword.capitalize()} {item_type} is a legendary artifact. "
        description += f"It is {color} and crafted from {material}, {effect} with {power} energy. "
        description += f"The item features {detail} that symbolize its ability to {ability}. "
        description += f"This extraordinary object was {origin} and incorporates elements of {keyword} in its design. "
        description += f"The influence of {keyword} is evident in its overall appearance and magical properties."

        logger.info(f"Descripción generada: {description}")
        return description

    def extract_item_info(self, description):
        logger.info("Extrayendo información del objeto")
        
        # Patrones regex actualizados para extraer información
        keyword_pattern = r"The (\w+) (\w+) is a legendary artifact"
        color_material_pattern = r"It is (\w+) and crafted from ([\w\s]+),"
        effect_power_pattern = r"(\w+) with (\w+) energy"
        detail_pattern = r"features ([\w\s]+) that symbolize"
        ability_pattern = r"ability to ([\w\s]+)\."
        origin_pattern = r"This extraordinary object was ([\w\s]+) and"
        
        # Extraer información usando regex
        keyword_match = re.search(keyword_pattern, description)
        color_material_match = re.search(color_material_pattern, description)
        effect_power_match = re.search(effect_power_pattern, description)
        detail_match = re.search(detail_pattern, description)
        ability_match = re.search(ability_pattern, description)
        origin_match = re.search(origin_pattern, description)
        
        keyword = keyword_match.group(1) if keyword_match else ""
        item_type = keyword_match.group(2) if keyword_match else ""
        color = color_material_match.group(1) if color_material_match else ""
        material = color_material_match.group(2) if color_material_match else ""
        effect = effect_power_match.group(1) if effect_power_match else ""
        power = effect_power_match.group(2) if effect_power_match else ""
        detail = detail_match.group(1) if detail_match else ""
        ability = ability_match.group(1) if ability_match else ""
        origin = origin_match.group(1) if origin_match else ""
        
        item_info = {
            "keyword": keyword,
            "name": f"The {keyword.capitalize()} {item_type.capitalize()}",
            "description": description,
            "item_type": item_type,
            "strength_bonus": random.randint(0, 10),
            "defense_bonus": random.randint(0, 10),
            "health_bonus": random.randint(0, 50),
            "dodge_bonus": round(random.uniform(0, 0.1), 2),
            "critical_chance_bonus": round(random.uniform(0, 0.1), 2),
            "agility_bonus": random.randint(0, 10),
            "aura": power,  # Usamos el "power" como aura
            "color": color,
            "material": material,
            "effect": effect,
            "detail": detail,
            "ability": ability,
            "origin": origin
        }
        
        # Generamos el unique_id después de tener toda la información del objeto
        item_info["id"] = uuid.uuid4().hex
        item_info["unique_id"] = generate_unique_id(item_info)
        
        logger.info(f"Información del objeto extraída: {item_info}")
        return item_info

generator = ItemGenerator()

def generar_descripcion_objeto(keyword):
    return generator.generate_item_description(keyword)

def extraer_informacion_objeto(description):
    return generator.extract_item_info(description)
