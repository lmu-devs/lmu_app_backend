from shared.src.enums import LanguageEnum


def translate_taste_profile(language: LanguageEnum) -> dict:
    """Translates the taste profile to the requested language"""
    
    def translate_text(item: dict) -> dict:
        # Create a new dict with all fields except 'text'
        new_item = {k: v for k, v in item.items() if k != 'text'}
        # Add translated text
        new_item['text'] = item['text'].get(language.value, item['text'].get('de-DE', 'not translated'))
        return new_item

    # Translate preferences presets
    translated_profile = {
        "preferences_presets": [
            translate_text(preset) for preset in taste_profile["preferences_presets"]
        ],
        "alergies_presets": [
            translate_text(preset) for preset in taste_profile["alergies_presets"]
        ],
        "sorted_labels": []
    }

    # Translate sorted labels
    for category in taste_profile["sorted_labels"]:
        translated_category = {
            "enum_category": category["enum_category"],
            "name": category["name"].get(language.value, category["name"].get('de-DE', 'not translated')),
            "items": [translate_text(item) for item in category["items"]]
        }
        translated_profile["sorted_labels"].append(translated_category)

    return translated_profile

taste_profile = {
   "preferences_presets": 
      [
         {
            "enum_name": "ALL",
            "text": {
               "de-DE": "Alles",
               "en-US": "All"
            },
            "emoji_abbreviation": "🥩",
            "exclude": []
         },
         {
            "enum_name": "PESCETARIAN",
            "text": {
               "de-DE": "Pescetarisch",
               "en-US": "Pescetarian"
            },
            "emoji_abbreviation": "🐠",
            "exclude": [
               "POULTRY",
               "BEEF",
               "VEAL",
               "PORK",
               "LAMB",
               "WILD_MEAT",
               "GELATIN"
            ]
         },
         {
            "enum_name": "VEGETARIAN",
            "text": {
               "de-DE": "Vegetarisch",
               "en-US": "Vegetarian"
            },
            "emoji_abbreviation": "🥕",
            "exclude": [
               "POULTRY",
               "BEEF",
               "VEAL",
               "PORK",
               "LAMB",
               "WILD_MEAT",
               "FISH",
               "SHELLFISH",
               "GELATIN"
            ]
         },
         {
            "enum_name": "VEGAN",
            "text": {
               "de-DE": "Vegan",
               "en-US": "Vegan"
            },
            "emoji_abbreviation": "🌱",
            "exclude": [
               "POULTRY",
               "BEEF",
               "VEAL",
               "PORK",
               "LAMB",
               "WILD_MEAT",
               "FISH",
               "SHELLFISH",
               "MILK",
               "LACTOSE",
               "CHICKEN_EGGS",
               "GELATIN"
            ]
         },
      ],
   "alergies_presets": 
      [
         {
            "enum_name": "GLUTENFREE",
            "text": {
               "de-DE": "Glutenfrei",
               "en-US": "Gluten-Free"
            },
            "emoji_abbreviation": "🌾",
            "exclude": [
               "GLUTEN",
               "WHEAT",
               "RYE",
               "CEREAL",
               "BARLEY",
               "OAT",
               "SPELT",
               "HYBRIDS"
            ]
         },
         {
            "enum_name":"LACTOSEFREE",
         "text":{
               "de-DE":"Lactosefrei",
               "en-US":"Lactose-Free"
            },
            "emoji_abbreviation":"🥛",
            "exclude":[
               "MILK",
               "LACTOSE"
            ]
         },
      # {
      #    "enum_name":"HALAL",
      #    "name":"Halal",
      #    "exclude":[
      #       "PORK",
      #       "ALCOHOL"
      #    ]
      # },
      # {
      #    "enum_name":"KOSHER",
      #    "name":"Kosher",
      #    "exclude":[
      #       "PORK",
      #       "SHELLFISH",
      #       "MOLLUSCS"
      #    ]
      # }
      ],
   "sorted_labels":[
      {
         "enum_category":"MEAT",
         "name":{
            "de-DE": "Fleisch",
            "en-US": "Meat"
         },
         "items":[
            {
               "enum_name":"BEEF",
               "text":{
                  "de-DE":"Rinderfleisch",
                  "en-US":"Beef"
               },
               "emoji_abbreviation":"🐮",
               "text_abbreviation":""
            },
            {
               "enum_name":"LAMB",
               "text":{
                  "de-DE":"Lammfleisch",
                  "en-US":"Lamb"
               },
               "emoji_abbreviation":"🐑",
               "text_abbreviation":""
            },
            {
               "enum_name":"PORK",
               "text":{
                  "de-DE":"Schweinefleisch",
                  "en-US":"Pork"
               },
               "emoji_abbreviation":"🐷",
               "text_abbreviation":""
            },
            {
               "enum_name":"POULTRY",
               "text":{
                  "de-DE":"Geflügel",
                  "en-US":"Poultry"
               },
               "emoji_abbreviation":"🐔",
               "text_abbreviation":""
            },
            {
               "enum_name":"VEAL",
               "text":{
                  "de-DE":"Kalbsfleisch",
                  "en-US":"Veal"
               },
               "emoji_abbreviation":"🐂",
               "text_abbreviation":""
            },
            {
               "enum_name":"WILD_MEAT",
               "text":{
                  "de-DE":"Wildfleisch",
                  "en-US":"Wild meat"
               },
               "emoji_abbreviation":"🐗",
               "text_abbreviation":""
            }
         ]
      },
      {
         "enum_category":"SEAFOOD",
         "name":{
            "de-DE": "Fisch",
            "en-US": "Seafood"
         },
         "items":[
            {
               "enum_name":"FISH",
               "text":{
                  "de-DE":"Fisch",
                  "en-US":"Fish"
               },
               "emoji_abbreviation":"🐠",
               "text_abbreviation":"D"
            },
            {
               "enum_name":"SHELLFISH",
               "text":{
                  "de-DE":"Krebstiere",
                  "en-US":"Shellfish"
               },
               "emoji_abbreviation":"🦀",
               "text_abbreviation":"B"
            }
         ]
      },
      {
         "enum_category":"DAIRY",
         "name":{
            "de-DE": "Milchprodukte",
            "en-US": "Dairy Products"
         },
         "items":[
            {
               "enum_name":"CHICKEN_EGGS",
               "text":{
                  "de-DE":"Eier",
                  "en-US":"Egg"
               },
               "emoji_abbreviation":"🥚",
               "text_abbreviation":"C"
            },
            {
               "enum_name":"LACTOSE",
               "text":{
                  "de-DE":"Laktose",
                  "en-US":"Lactose"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"La"
            },
            {
               "enum_name":"MILK",
               "text":{
                  "de-DE":"Milch",
                  "en-US":"Milk"
               },
               "emoji_abbreviation":"🥛",
               "text_abbreviation":"G"
            },
         ]
      },
      {
         "enum_category":"GLUTEN",
         "name":{
            "de-DE": "Gluten",
            "en-US": "Gluten"
         },
         "items":[
            {
               "enum_name":"BARLEY",
               "text":{
                  "de-DE":"Gerste",
                  "en-US":"Barley"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"GlG"
            },
            {
               "enum_name":"CEREAL",
               "text":{
                  "de-DE":"Getreide",
                  "en-US":"Cereal"
               },
               "emoji_abbreviation":"🌾",
               "text_abbreviation":""
            },
            {
               "enum_name":"GLUTEN",
               "text":{
                  "de-DE":"Gluten",
                  "en-US":"Gluten Containing Cereals"
               },
               "emoji_abbreviation":"🥖",
               "text_abbreviation":"A"
            },
            {
               "enum_name":"OAT",
               "text":{
                  "de-DE":"Hafer",
                  "en-US":"Oat"
               },
               "emoji_abbreviation":"🥣",
               "text_abbreviation":"GlH"
            },
            {
               "enum_name":"RYE",
               "text":{
                  "de-DE":"Roggen",
                  "en-US":"Rye"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"GlR"
            },
            {
               "enum_name":"SPELT",
               "text":{
                  "de-DE":"Dinkel",
                  "en-US":"Spelt"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"GlD"
            },
            {
               "enum_name":"WHEAT",
               "text":{
                  "de-DE":"Weizen",
                  "en-US":"Wheat"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"GlW"
            },
         ]
      },
      {
         "enum_category":"NUTS",
         "name":{
            "de-DE": "Nüsse",
            "en-US": "Nuts"
         },
         "items":[
            {
               "enum_name":"ALMONDS",
               "text":{
                  "de-DE":"Mandeln",
                  "en-US":"Almonds"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"ScM"
            },
            {
               "enum_name":"CASHEWS",
               "text":{
                  "de-DE":"Cashewnüsse",
                  "en-US":"Cashews"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"ScC"
            },
            {
               "enum_name":"HAZELNUTS",
               "text":{
                  "de-DE":"Haselnüsse",
                  "en-US":"Hazelnuts"
               },
               "emoji_abbreviation":"🌰",
               "text_abbreviation":"ScH"
            },
            {
               "enum_name":"MACADAMIA",
               "text":{
                  "de-DE":"Macadamianüsse",
                  "en-US":"Macadamias"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"ScMa"
            },
            {
               "enum_name":"PEANUTS",
               "text":{
                  "de-DE":"Erdnüsse",
                  "en-US":"Peanut"
               },
               "emoji_abbreviation":"🥜",
               "text_abbreviation":"E"
            },
            {
               "enum_name":"PECAN",
               "text":{
                  "de-DE":"Pekanüsse",
                  "en-US":"Pecans"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"ScP"
            },
            {
               "enum_name":"PISTACHIOES",
               "text":{
                  "de-DE":"Pistazien",
                  "en-US":"Pistachios"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"ScP"
            },
            {
               "enum_name":"SESAME",
               "text":{
                  "de-DE":"Sesam",
                  "en-US":"Sesame"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"K"
            },
            {
               "enum_name":"WALNUTS",
               "text":{
                  "de-DE":"Walnüsse",
                  "en-US":"Walnuts"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"ScW"
            },
         ]
      },
      {
         "enum_category":"ADDITIVES",
         "name":{
            "de-DE": "Zusatzstoffe",
            "en-US": "Additives"
         },
         "items":[
            {
               "enum_name":"DYESTUFF",
               "text":{
                  "de-DE":"Farbstoffe",
                  "en-US":"Dyestuff"
               },
               "emoji_abbreviation":"🎨",
               "text_abbreviation":"1"
            },
            {
               "enum_name":"SWEETENERS",
               "text":{
                  "de-DE":"Süßungsmittel",
                  "en-US":"Sweeteners"
               },
               "emoji_abbreviation":"🍬",
               "text_abbreviation":"11"
            },
            {
               "enum_name":"FLAVOR_ENHANCER",
               "text":{
                  "de-DE":"Geschmacksverstärker",
                  "en-US":"Flavor Enhancer"
               },
               "emoji_abbreviation":"🔬",
               "text_abbreviation":"4"
            },
            {
               "enum_name":"PRESERVATIVES",
               "text":{
                  "de-DE":"Preservate",
                  "en-US":"Preservatives"
               },
               "emoji_abbreviation":"🥫",
               "text_abbreviation":"2"
            },
            {
               "enum_name":"PHENYLALANINE",
               "text":{
                  "de-DE":"Phenylaline",
                  "en-US":"Phenylalanine"
               },
               "emoji_abbreviation":"💊",
               "text_abbreviation":""
            },
            {
               "enum_name":"ANTIOXIDANTS",
               "text":{
                  "de-DE":"Antioxidanten",
                  "en-US":"Antioxidants"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"3"
            }
         ]
      },
      {
         "enum_category":"MISCELLANEOUS",
         "name":{
            "de-DE": "Sonstiges",
            "en-US": "Miscellaneous"
         },
         "items":[
            {
               "enum_name":"SOY",
               "text":{
                  "de-DE":"Soja",
                  "en-US":"Soy"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"F"
            },
            {
               "enum_name":"HYBRIDS",
               "text":{
                  "de-DE":"Hybridstämme",
                  "en-US":"Hybrid Strains"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"GlHy"
            },
            {
               "enum_name":"CELERY",
               "text":{
                  "de-DE":"Sellerie",
                  "en-US":"Celery"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"I"
            },
            {
               "enum_name":"MUSTARD",
               "text":{
                  "de-DE":"Senf",
                  "en-US":"Mustard"
               },
               "emoji_abbreviation":"🌭",
               "text_abbreviation":"J"
            },
            {
               "enum_name":"SULPHURS",
               "text":{
                  "de-DE":"Schwefeldioxid",
                  "en-US":"Sulphurs"
               },
               "emoji_abbreviation":"🔻",
               "text_abbreviation":"L"
            },
            {
               "enum_name":"SULFITES",
               "text":{
                  "de-DE":"Sulfite",
                  "en-US":"Sulfites"
               },
               "emoji_abbreviation":"🔺",
               "text_abbreviation":"L"
            },
            {
               "enum_name":"LUPIN",
               "text":{
                  "de-DE":"Lupine",
                  "en-US":"Lupin"
               },
               "emoji_abbreviation":"",
               "text_abbreviation":"M"
            },
            {
               "enum_name":"MOLLUSCS",
               "text":{
                  "de-DE":"Weichtiere",
                  "en-US":"Molluscs"
               },
               "emoji_abbreviation":"🐙",
               "text_abbreviation":"N"
            },
            {
               "enum_name":"SHELL_FRUITS",
               "text":{
                  "de-DE":"Schalenfrüchte",
                  "en-US":"Shell Fruits"
               },
               "emoji_abbreviation":"🥥",
               "text_abbreviation":"H"
            },
            {
               "enum_name":"WAXED",
               "text":{
                  "de-DE":"Gewachst",
                  "en-US":"Waxed"
               },
               "emoji_abbreviation":"🐝",
               "text_abbreviation":"13"
            },
            {
               "enum_name":"PHOSPATES",
               "text":{
                  "de-DE":"Phosphate",
                  "en-US":"Phosphates"
               },
               "emoji_abbreviation":"🔷",
               "text_abbreviation":"7"
            },
            {
               "enum_name":"COCOA_CONTAINING_GREASE",
               "text":{
                  "de-DE":"Kakaohaltiges Fett",
                  "en-US":"Cocoa Containing Grease"
               },
               "emoji_abbreviation":"🍫",
               "text_abbreviation":""
            },
            {
               "enum_name":"GELATIN",
               "text":{
                  "de-DE":"Gelatine",
                  "en-US":"Gelatin"
               },
               "emoji_abbreviation":"🍮",
               "text_abbreviation":""
            },
            {
               "enum_name":"ALCOHOL",
               "text":{
                  "de-DE":"Alkohol",
                  "en-US":"Alcohol"
               },
               "emoji_abbreviation":"🍷",
               "text_abbreviation":""
            },
            {
               "enum_name":"GARLIC",
               "text":{
                  "de-DE":"Knoblauch",
                  "en-US":"Garlic"
               },
               "emoji_abbreviation":"🧄",
               "text_abbreviation":""
            },
            # {
            #    "enum_name":"BAVARIA",
            #    "text":{
            #       "de-DE":"Zertifizierte Qualität Bayern",
            #       "en-US":"Certified Quality Bavaria"
            #    },
            #    "emoji_abbreviation":"🥨",
            #    "text_abbreviation":""
            # },
            # {
            #    "enum_name":"MSC",
            #    "text":{
            #       "de-DE":"Marine Stewardship Council",
            #       "en-US":"Marine Stewardship Council"
            #    },
            #    "emoji_abbreviation":"🎣",
            #    "text_abbreviation":""
            # }
         ]
      }
   ]
}

