from yoyo import step

__depends__ = {
    "0003_seed_series"
}

species_data = [
    ("Vicia faba", "Broad bean"),
    ("Allium cepa", "Bulb onion"),
    ("Galium aparine", "Common cleavers"),
    ("Corylus avellana", "Common hazel"),
    ("Hedera helix", "Common ivy"),
    ("Xanthoria parietina", "Common orange lichen"),
    ("Gossyplum sp.", "Cotton"),
    ("Hypnum cupressiforme", "Cypress-leaved plait-moss"),
    ("Taraxacum officinale", "Dandelion"),
    ("Polypodiopsida sp.", "Fern"),
    ("Ligustrum lucidum", "Glossy privet"),
    ("Musca domestica", "House Fly"),
    ("Hydra sp.", "Hydra"),
    ("Pittosporum tobira", "Japanese pittosporum"),
    ("Jasminum nudiflorum", "Jasmine"),
    ("Lilium sp.", "Lily"),
    ("Tilia sp.", "Lime"),
    ("Zea sp.", "Maize"),
    ("Hirudo sp.", "Medicinal leech"),
    (None, "Mushroom"),
    ("Brassica napus", "Oilseed rape"),
    ("Nerium indicum", "Oleander"),
    ("Capsicum sp.", "Pepper"),
    ("Pinus sp.", "Pine"),
    ("Cucurbita sp.", "Pumpkin"),
    ("Salix caprea", "Pussy willow"),
    ("Taenia pisiformis", "Rabbit tapeworm"),
    ("Raphanus sativus", "Radish"),
    ("Oryza sativa", "Rice"),
    ("Cycas revoluta", "Sago palm"),
    ("Capsella bursa-pastoris", "Shepherd’s purse"),
    ("Tradescantia reflexa", "Spiderwort"),
    ("Nostoc commune", "Star jelly"),
    ("Helianthus annuus", "Sunflower"),
    ("Gossyplum hirsutum", "Upland cotton"),
    ("Volvox sp.", "Volvox"),
    ("Triticum aestivum", "Wheat"),
    (None, "Worm"),
]


def insert_sql(sci, common):
    sci_val = f"'{sci}'" if sci is not None else "NULL"
    common_val = f"'{common}'" if common is not None else "NULL"

    return f"""
        INSERT OR IGNORE INTO SPECIES (Scientific_Name, Common_Name)
        VALUES ({sci_val}, {common_val})
    """


def delete_sql(sci, common):
    if sci is None:
        return f"DELETE FROM SPECIES WHERE Scientific_Name IS NULL AND Common_Name = '{common}'"
    return f"DELETE FROM SPECIES WHERE Scientific_Name = '{sci}'"


steps = [
    step(insert_sql(sci, common), delete_sql(sci, common))
    for sci, common in species_data
]