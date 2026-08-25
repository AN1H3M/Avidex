from exa_py import Exa
from dotenv import load_dotenv
import os

load_dotenv(".env")

EXA_KEY = os.getenv("EXA_KEY")

exa = Exa(EXA_KEY)

sample_data = [['rarity', 'Rare'],
               ['common_name', 'Glow-throated Hummingbird'],
               ['species', 'Selasphorus ardens'],
               ['callUrl', None],
               ['wingspan', None],
               ['size', None],
               ['identifying_marks', 'Males are bronze and green with a pinkish-red gorget bordered by a white collar on the front of the neck. The Glow-throated exhibits a mostly black tail, unlike the Scintillant Hummingbird which has a rufous tail with black striping. The female Glow-throated is brighter below and has less rufous edging on the tail. Both sexes have short, black bills. (Information Sourced with AI)'], ['range', 'Restricted to west central Panama,cited at a few locations including Serranía de Tabasará and potentially the highlands of Península de Azuero. Recorded in Cerro Colorado/Cerro Flores and Santa Fé/Cerro Tute. (Information Sourced with AI)'],
               ['description', 'Unfortunately, little information exists on this small Panamanian endemic. Classified as vulnerable due to its limited range, the Glow-throated Hummingbird is restricted to west central Panama and has been cited at only a few locations including the Serranía de Tabasará and potentially in the highlands of the Península de Azuero. During the 20th century, this species was only recorded in two areas: Cerro Colorado/Cerro Flores and Santa Fé/Cerro Tute. Although not officially documented, forest fragmentation in Serranía de Tabasará and elsewhere is suspected to be contributing to a decline in the population.\n\nLittle information about the bird’s basic biology exists other than it inhabits forest borders and clearings between 750-1800 meters. Males are bronze and green with a pinkish-red gorget bordered by a white collar on the front of the neck. Both sexes could possibly be confused with the Scintillant Hummingbird (Selasphorus sctintilla) but the Glow-throated exhibits a mostly blacktail where the Scintillant Hummingbird’s is rufous with some black striping. The female Glow-throated is brighter below and has less rufous edging on the tail than does the Scintillant. Both sexes have short, black bills.'],
               ['photographUrl', None],
               ['mating_season', None]]

results = exa.search(
    query=f"{sample_data[2][1]}",
    type= "deep",
    system_prompt=f"""Lookup missing information and verify existing information about a bird given a list of info about it to prepare for a SQL PL entry. An example data entry created by a human in the SQL table is:
    rarityID, commonName, species, callUrl, wingspan, size, identifyingMarks, range, description, photographUrl, matingSeason
    'Uncommon', 'Bald Eagle', 'Haliaeetus leucocephalus', NULL, 'The average Bald Eagle wingpsan is 6.9 feet', 'The average Bald Eagle is 27.9 inches to 37.8 inches long', 'The Bald Eagle is easily identified by its white capped head and neck, in contrast to the rest of its dark brown coat', 'Found all across North America, except for the most northern regions and below Mexico', 'The Bald Eagle got its name from the Middle English word, \'Balde\', meaning white-headed (not hairless!) These eagles mainly eat fish, and can be found around bodies of water. Though more often than not, they prefer to steal fish from other fishing animals, humans included.', NULL, 'Bald Eagle nesting season typically begins in December, and lasts until July. Though their courtship behaviors may begin as early as late Fall, depending on location.
    
    The callUrl and photographUrl do not need to be looked up. Don't verify the existing information

    Check with multiple sources for validity.

    Add a tag describing the data after i.e. (verified) or (contradicted) following this legend:
    verified: reliable sources support the claim
    contradicted: reliable sources show it is false
    partially_correct: some details are right but others need correction
    disputed: credible sources disagree
    unverified: insufficient evidence
    needs_review: any result requiring a person's decision

    Prefer journals or scientific articles

    Existing info:
    {sample_data}
    """,
    output_schema= {
        "type":"object",
        "required": ["rarity","common_name","species","callUrl","wingspan","size","identifying_marks"],
        "properties": {
            "rarity": {"type":"string", "enum":["Common", "Uncommon", "Rare", "Legendary"], "description":"Same as input data. Do not change or add tag"},
            "common_name": {"type":"string", "description":"Same as input data. Do not change or add tag"},
            "species": {"type":"string", "description":"Same as input data. Do not change or add tag"},
            "wingspan": {"type":"string", "description":"The wingpspan of the bird in question if sources dispute existing information or is null"},
            "size": {"type": "string", "description": "The size of the bird if sources dispute existing information or is null"},
            "identifying_marks": {"type": "string", "description": "The identifying descriptors of the bird if sources dispute existing information or is null"},
            "range": {"type": "string", "description": "The range of the bird if sources dispute existing information or is null"},
            "description": {"type": "string", "description": "Same as input data. Do not change or add tag"},
            "mating_season": {"type": "string", "description": "The mating season and mating ranges of the bird if sources dispute existing information or is null"},
        },
    },
    contents={"highlights":True}
)

print(results.output.content if results.output else None)
print(f"\n\n")
print(results.output.grounding if results.output else None)