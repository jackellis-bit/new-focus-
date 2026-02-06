"""
VFX Target Companies
====================

STRICT target account list - 208 VFX houses.
Only leads from these companies will be processed by the pipeline.
Any leads from companies not in this list will be REJECTED.

Source: VFX Target Accounts spreadsheet (Feb 2026)

Markets: USA, UK, Canada, India, France
"""

COMPANIES = [
    # ==========================================
    # USA
    # ==========================================
    {
        'name': 'a52',
        'parent': 'MakeMake',
        'market': 'usa',
        'location': 'Santa Monica, CA, USA',
        'notable_projects': 'Honda, FS1, Nike, Skims',
    },
    {
        'name': 'Alt.vfx',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA',
        'notable_projects': 'Christy, Alice in Borderland, Nine Perfect Strangers',
    },
    {
        'name': 'Artjail',
        'parent': None,
        'market': 'usa',
        'location': 'New York, NY',
        'notable_projects': 'Hubspot, Dominos, Nerdwallet, Mercedes Benz',
    },
    {
        'name': 'Afterparty VFX',
        'parent': None,
        'market': 'usa',
        'location': 'New York, NY',
        'notable_projects': 'Dead Ringers, Separation, Captain Fantastic',
    },
    {
        'name': 'Barnstorm VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Boulder, CO, USA',
        'notable_projects': '',
    },
    {
        'name': 'Big Block',
        'parent': None,
        'market': 'usa',
        'location': 'El Segundo, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Blur Studio',
        'parent': None,
        'market': 'usa',
        'location': 'Culver City, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'BOT VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Alpharetta, GA, CA',
        'notable_projects': 'Avatar: Fire and Ash, Stranger Things S5, Black Panther, The Mandalorian, Avengers: Endgame',
    },
    {
        'name': 'Brainstorm Digital',
        'parent': None,
        'market': 'usa',
        'location': 'New York, NY',
        'notable_projects': '',
    },
    {
        'name': 'Brickyard VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Boston, MA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Cadence Effects',
        'parent': None,
        'market': 'usa',
        'location': 'New Lebanon, NY',
        'notable_projects': '',
    },
    {
        'name': 'Cantina Creative',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Carbon VFX',
        'parent': None,
        'market': 'usa',
        'location': 'New York, NY',
        'notable_projects': '',
    },
    {
        'name': 'Cavalry VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Chicken Bone VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Cineverse VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Company 3',
        'parent': 'Framestore',
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Cosa VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': 'The Boys, True Detective, Westworld',
    },
    {
        'name': 'Crafty Apes',
        'parent': None,
        'market': 'usa',
        'location': 'New York, NY, USA',
        'notable_projects': 'Black Panther, The Mandalorian, Watchmen',
    },
    {
        'name': 'Day for Nite',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Deluxe',
        'parent': None,
        'market': 'usa',
        'location': 'Burbank, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Digital Domain',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': 'Titanic, The Curious Case of Benjamin Button, Avengers',
    },
    {
        'name': 'Digital Frontier FX',
        'parent': None,
        'market': 'usa',
        'location': 'Marina del Rey, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Distant Objects',
        'parent': None,
        'market': 'usa',
        'location': 'San Francisco, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'DreamWorks Animation',
        'parent': 'NBCUniversal (Comcast)',
        'market': 'usa',
        'location': 'Glendale, CA, USA',
        'notable_projects': 'Shrek, How to Train Your Dragon',
    },
    {
        'name': 'Encore VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Burbank, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Fin Design + Effects',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'FuseFX',
        'parent': 'FuseFX (independent)',
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': "Agents of S.H.I.E.L.D., American Horror Story, The Boys",
    },
    {
        'name': 'Gentle Giant Studios',
        'parent': 'Netflix',
        'market': 'usa',
        'location': 'Burbank, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Industrial Light & Magic (ILM)',
        'parent': 'Lucasfilm (The Walt Disney Company)',
        'market': 'usa',
        'location': 'San Francisco, CA, USA',
        'notable_projects': "Star Wars, Jurassic Park, Avengers: Endgame",
        'existing_contacts': [
            {'name': 'Jeff White', 'title': 'Creative Director / VFX Supervisor', 'email': 'jeffw@ilm.com'},
            {'name': 'Peter Kyme', 'title': 'CG Technology Supervisor', 'email': 'pkyme@ilm.com'},
        ],
        'notes': 'Daniel Pinar met with them on 9/10/25. Conversation seems to have stalled out after that.',
    },
    {
        'name': 'Ingenuity Studios',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': 'Westworld, Mr. Robot',
    },
    {
        'name': 'Legend 3D',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Method Studios',
        'parent': 'Framestore',
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'PCO / Post Collective',
        'parent': 'Independent',
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Pixar Animation Studios',
        'parent': 'The Walt Disney Company',
        'market': 'usa',
        'location': 'Emeryville, CA, USA',
        'notable_projects': 'Toy Story, Inside Out, Finding Nemo',
    },
    {
        'name': 'Pixar RenderMan/Tech (VFX tools)',
        'parent': 'The Walt Disney Company',
        'market': 'usa',
        'location': 'Emeryville, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Prologue',
        'parent': None,
        'market': 'usa',
        'location': 'Venice, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Proof Inc.',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Riot Games VFX',
        'parent': 'Riot Games',
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Shade VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Stargate Studios',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Tau Films',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': '',
    },
    {
        'name': 'Taylor James',
        'parent': None,
        'market': 'usa',
        'location': 'New York, NY, USA',
        'notable_projects': '',
    },
    {
        'name': 'The Molecule',
        'parent': None,
        'market': 'usa',
        'location': 'New York, NY, USA',
        'notable_projects': '',
    },
    {
        'name': 'Tippett Studio',
        'parent': None,
        'market': 'usa',
        'location': 'Berkeley, CA, USA',
        'notable_projects': 'Alien: Romulus, The Witcher, The Mandalorian, Dark Winds',
    },
    {
        'name': 'VFX Legion',
        'parent': None,
        'market': 'usa',
        'location': 'Burbank, CA, USA',
        'notable_projects': 'Black Phone, Tulsa King, Wednesday, Suits',
    },
    {
        'name': 'VisualCreatures',
        'parent': None,
        'market': 'usa',
        'location': 'Los Angeles, CA, USA',
        'notable_projects': 'Cherry, Citadel, The Gray Man',
    },
    {
        'name': 'Whiskytree',
        'parent': None,
        'market': 'usa',
        'location': 'San Rafael, CA, USA',
        'notable_projects': 'Andor, Obi-Wan Kenobi, Masters of the Air, Wakanda Forever',
    },
    {
        'name': 'XYZ Graphics',
        'parent': None,
        'market': 'usa',
        'location': 'San Francisco, CA, USA',
        'notable_projects': 'Google, Old Navy, Method',
    },
    {
        'name': 'ZERO VFX',
        'parent': None,
        'market': 'usa',
        'location': 'Boston, MA, USA',
        'notable_projects': 'The Smashing Machine, Challengers, 1923',
    },
    {
        'name': 'Zoic Studios',
        'parent': None,
        'market': 'usa',
        'location': 'Culver City, CA, USA',
        'notable_projects': 'Game of Thrones, Fargo, 1923, Alien: Earth',
    },

    # ==========================================
    # UK
    # ==========================================
    {
        'name': 'Absolute Post',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Adolescence, The Buccaneers, MobLand',
    },
    {
        'name': 'Atomic Arts',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Outlander, The Rings of Power, Lilo & Stitch, The Batman',
    },
    {
        'name': 'Automatik VFX',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Kinds of Kindness, Back to Black',
    },
    {
        'name': 'BlueBolt',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'Caviar VFX',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'Cinesite',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'No Time to Die, The Mandalorian, Aquaman',
    },
    {
        'name': 'DNEG',
        'parent': 'Prime Focus',
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Dune, Tenet, Interstellar, Inception, Ex Machina',
        'existing_contacts': [
            {'name': 'Pranav Pujara', 'title': 'Global Head of Pipeline', 'email': 'pranav.pujara@dneg.com'},
        ],
    },
    {
        'name': 'Dupe VFX',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'Framestore',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Gravity, Blade Runner 2049, Guardians of the Galaxy',
        'existing_contacts': [
            {'name': 'Tim Webber', 'title': 'Chief Creative Officer', 'email': ''},
            {'name': 'Tom Partridge', 'title': 'Head of Editorial, Pre Production Services', 'email': 'tom.partridge@framestore.com'},
        ],
    },
    {
        'name': 'Goodbye Kansas Visual Effects',
        'parent': 'Goodbye Kansas Group',
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'Jellyfish Pictures',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Star Wars: The Last Jedi',
    },
    {
        'name': 'Milk VFX',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Sherlock, Doctor Who',
    },
    {
        'name': 'Nvizible',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'One of Us',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Ex Machina, The Crown',
    },
    {
        'name': 'Outpost VFX',
        'parent': None,
        'market': 'uk',
        'location': 'Bournemouth, UK',
        'notable_projects': '',
    },
    {
        'name': 'Proof of Concept (POC)',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'RealtimeUK',
        'parent': None,
        'market': 'uk',
        'location': 'Manchester, UK',
        'notable_projects': '',
    },
    {
        'name': 'Recom Farmhouse',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'Straight To The Biscuits',
        'parent': None,
        'market': 'uk',
        'location': 'Lincoln, ENG, UK',
        'notable_projects': '',
    },
    {
        'name': 'Territory Studio',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': 'Blade Runner 2049, Avengers',
    },
    {
        'name': 'The Brewery VFX and Animation',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '',
    },
    {
        'name': 'Union VFX',
        'parent': None,
        'market': 'uk',
        'location': 'London, UK',
        'notable_projects': '28 Years Later, Poor Things, Slow Horses, Black Mirror',
    },

    # ==========================================
    # CANADA
    # ==========================================
    {
        'name': 'AA Studios',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': 'Geant Beaupre, Vil & Miserable, French Girl, Portrait Robot',
    },
    {
        'name': 'AB VFX Inc.',
        'parent': None,
        'market': 'canada',
        'location': 'Abbotsford, BC, Canada',
        'notable_projects': 'The Boys, Dark Winds, RRR',
    },
    {
        'name': 'Acme FX',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, Canada',
        'notable_projects': 'It, Black Mirror, The Shape of Water',
    },
    {
        'name': 'Alchemy24',
        'parent': 'Rodeo FX',
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': 'IT: Welcome to Derry, Smile 2, Mission: Impossible - Dead Reckoning Part One',
    },
    {
        'name': 'Allegiance Studios',
        'parent': None,
        'market': 'canada',
        'location': 'Kelowna, BC, Canada',
        'notable_projects': 'The Purge: Election Year, Hardcore Henry',
    },
    {
        'name': 'Alter Ego Post',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, Canada',
        'notable_projects': 'Furiosa, The Lego Movie 2, Mad Max: Fury Road',
    },
    {
        'name': 'Animism Studios',
        'parent': None,
        'market': 'canada',
        'location': 'Vancouver, BC, Canada',
        'notable_projects': "The Morning Show, Grey's Anatomy, Stranger Things",
    },
    {
        'name': 'Bardel Entertainment',
        'parent': None,
        'market': 'canada',
        'location': 'Vancouver, BC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'beloFX',
        'parent': None,
        'market': 'canada',
        'location': 'Vancouver, BC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Cause and FX',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Cinetism Inc.',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Distillery VFX',
        'parent': None,
        'market': 'canada',
        'location': 'Vancouver, BC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Folks VFX',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': 'The Expanse, Motherland: Fort Salem',
    },
    {
        'name': 'Hybride',
        'parent': 'Ubisoft (Hybride Technologies)',
        'market': 'canada',
        'location': 'Piedmont, QC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Image Engine',
        'parent': 'Cinesite',
        'market': 'canada',
        'location': 'Vancouver, BC, Canada',
        'notable_projects': 'The Mandalorian, Jurassic World, District 9',
    },
    {
        'name': 'MELS Studios',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'MR. X',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, Canada',
        'notable_projects': 'Star Trek: Discovery, The Boys, Vikings',
    },
    {
        'name': 'Raynault VFX',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Real by Fake',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'ReDefine',
        'parent': 'DNEG',
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Rocket Science VFX',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Rodeo FX',
        'parent': None,
        'market': 'canada',
        'location': 'Montreal, QC, Canada',
        'notable_projects': 'Dune, Game of Thrones, Stranger Things',
    },
    {
        'name': 'Eyeline',
        'parent': 'Netflix',
        'market': 'canada',
        'location': 'Vancouver, BC, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Soho VFX',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, CA',
        'notable_projects': '',
    },
    {
        'name': 'Sony Pictures Imageworks',
        'parent': 'Sony Pictures Entertainment (Sony Group)',
        'market': 'canada',
        'location': 'Vancouver, BC, Canada',
        'notable_projects': 'Spider-Man: Across the Spider-Verse, No Way Home, Hotel Transylvania',
    },
    {
        'name': 'Spin VFX',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, Canada',
        'notable_projects': 'The Boys, Star Trek, The Expanse',
    },
    {
        'name': 'Squeeze Studio',
        'parent': None,
        'market': 'canada',
        'location': 'Quebec City, Canada',
        'notable_projects': '',
    },
    {
        'name': 'Stormborn Studios Inc.',
        'parent': None,
        'market': 'canada',
        'location': 'Vancouver, BC, CA',
        'notable_projects': '',
    },
    {
        'name': 'FEATHER',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, CA',
        'notable_projects': '',
    },
    {
        'name': 'Switch VFX and Animation',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, CA',
        'notable_projects': '',
    },
    {
        'name': 'Tantrum',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, CA',
        'notable_projects': '',
    },
    {
        'name': 'The Embassy',
        'parent': None,
        'market': 'canada',
        'location': 'Vancouver, BC, CA',
        'notable_projects': '',
    },
    {
        'name': 'WeFX',
        'parent': None,
        'market': 'canada',
        'location': 'Toronto, ON, CA',
        'notable_projects': 'Wednesday, 1923, Reacher, John Wick: Chapter 4',
    },

    # ==========================================
    # INDIA
    # ==========================================
    {
        'name': 'Astra Studios',
        'parent': None,
        'market': 'india',
        'location': 'Bengaluru, India',
        'notable_projects': '',
    },
    {
        'name': 'Basilic Fly',
        'parent': None,
        'market': 'india',
        'location': 'Chennai, India',
        'notable_projects': '',
    },
    {
        'name': 'Makuta VFX',
        'parent': None,
        'market': 'india',
        'location': 'Hyderabad, India',
        'notable_projects': '',
    },
    {
        'name': 'PhantomFX',
        'parent': None,
        'market': 'india',
        'location': 'Chennai, India',
        'notable_projects': '',
    },
    {
        'name': 'redchillies.vfx',
        'parent': 'Red Chillies Entertainment',
        'market': 'india',
        'location': 'Mumbai, India',
        'notable_projects': 'Ra.One, Pathaan, Jawan',
    },
    {
        'name': 'SDFX Studios',
        'parent': None,
        'market': 'india',
        'location': 'Mumbai, India',
        'notable_projects': '',
    },

    # ==========================================
    # FRANCE
    # ==========================================
    {
        'name': 'Moving Picture Company (MPC)',
        'parent': 'TransPerfect',
        'market': 'france',
        'location': 'Paris, France',
        'notable_projects': 'The Jungle Book (2016), The Lion King (2019), Godzilla vs. Kong',
    },
    {
        'name': 'The Mill',
        'parent': 'TransPerfect',
        'market': 'france',
        'location': 'Paris, France',
        'notable_projects': 'Adidas, Google, NFL, Starbucks, Netflix, EA Sports',
    },

    # ==========================================
    # LOCATION UNKNOWN / NOT SPECIFIED
    # These companies were in the target list without location data.
    # Market will be set to 'unknown' until enriched.
    # ==========================================
    {'name': 'East of LA VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'East Side Effects', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'EFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Eggplant Picture & Sound', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Ekstasy', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Electric Theatre Collective', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Entity FX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Evil Eye Pictures', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Filament Post', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Flavor TV', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Fort York', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Fox VFX Lab', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Frame 48', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Freefolk', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'FRENDER', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'FRIMA', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Furious FX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'FUSE Animation', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Ghost Ship VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Ghost VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Glassworks', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Glimpse VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'GloriaFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Goldtooth', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Gradient Effects', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Halon Entertainment', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Haymaker', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Herne Hill', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'HiFi 3D', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'HMX Media', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Hootenanny', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Hula Hoop VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Hydraulx VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Ice VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Imaginarium Studios', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Imaginary Forces', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Incessant Rain Studios', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Indigo Studios', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Infusion Studios', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Intelligent Creatures', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Ixor VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'JAMM VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Kalos Studios', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Kerosene Visual Effects', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Kevin VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Koala FX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Kreaturz', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Krow VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Lacus Post', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Latch & Key Film Co.', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Lerfilm Inc.', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Lipsync Post', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Lobo', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Lola VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Luma Pictures', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mackevision', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Magnopus', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mammal Studios', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'ManvsMachine', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Marks', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'MARZ', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mathematic Studio', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mavericks VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'MELS', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Meptik', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mercury Visual Solutions', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mirada Studios', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mist VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Molinare', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Moment Factory', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Moonraker VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'MOOV Studio', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Mousetrappe', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Muse VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Neymarc Visuals', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Nice Shoes', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'nineteentwenty', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Nomad', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'nVizage', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Oblique FX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'One Tree Forest Films', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Original Force', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Outpost', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Passion Pictures', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Peerless', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Phosphene', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Picture Shop', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Piranha NYC', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Pixlhut', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Pixomondo', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'PixRock VFX', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Playfight', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Possible Productions', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
    {'name': 'Potion Pictures', 'parent': None, 'market': 'unknown', 'location': '', 'notable_projects': ''},
]


# ============================================================================
# COMPANY NAME MATCHING
# ============================================================================

# Normalized name -> original name mapping (built at import time)
_COMPANY_NAMES = {c['name'].lower().strip(): c['name'] for c in COMPANIES}

# Also add common variations
_COMPANY_ALIASES = {
    'ilm': 'Industrial Light & Magic (ILM)',
    'industrial light and magic': 'Industrial Light & Magic (ILM)',
    'industrial light & magic': 'Industrial Light & Magic (ILM)',
    'mpc': 'Moving Picture Company (MPC)',
    'moving picture company': 'Moving Picture Company (MPC)',
    'spi': 'Sony Pictures Imageworks',
    'imageworks': 'Sony Pictures Imageworks',
    'poc': 'Proof of Concept (POC)',
    'dd': 'Digital Domain',
    'the mill': 'The Mill',
    'mr x': 'MR. X',
    'mr. x': 'MR. X',
}


def is_target_company(company_name: str) -> bool:
    """
    Check if a company is in our strict target list.
    
    Args:
        company_name: Company name to check
        
    Returns:
        True if the company is a target account
    """
    if not company_name:
        return False
    
    name_lower = company_name.lower().strip()
    
    # Exact match
    if name_lower in _COMPANY_NAMES:
        return True
    
    # Alias match
    if name_lower in _COMPANY_ALIASES:
        return True
    
    # Fuzzy match: check if target name is contained in the input or vice versa
    for target_name in _COMPANY_NAMES:
        if target_name in name_lower or name_lower in target_name:
            return True
    
    return False


def normalize_company_name(company_name: str) -> str:
    """
    Normalize a company name to match our target list.
    
    Args:
        company_name: Raw company name from lead data
        
    Returns:
        Normalized name matching our list, or original if no match
    """
    if not company_name:
        return ''
    
    name_lower = company_name.lower().strip()
    
    # Exact match
    if name_lower in _COMPANY_NAMES:
        return _COMPANY_NAMES[name_lower]
    
    # Alias match
    if name_lower in _COMPANY_ALIASES:
        return _COMPANY_ALIASES[name_lower]
    
    # Fuzzy: check if target is contained in input
    for target_lower, target_original in _COMPANY_NAMES.items():
        if target_lower in name_lower or name_lower in target_lower:
            return target_original
    
    return company_name


def get_company(company_name: str) -> dict:
    """
    Get company data by name.
    
    Args:
        company_name: Company name (exact or alias)
        
    Returns:
        Company dict or None
    """
    normalized = normalize_company_name(company_name)
    for c in COMPANIES:
        if c['name'] == normalized:
            return c
    return None


def get_companies_by_market(market: str) -> list:
    """Get all companies for a specific market."""
    return [c for c in COMPANIES if c['market'] == market]


def get_all_company_names() -> list:
    """Get sorted list of all target company names."""
    return sorted([c['name'] for c in COMPANIES])


def get_all_companies() -> list:
    """Get all companies."""
    return COMPANIES


def get_summary() -> dict:
    """Get summary counts."""
    summary = {
        'total': len(COMPANIES),
        'by_market': {},
        'with_location': len([c for c in COMPANIES if c.get('location')]),
        'with_projects': len([c for c in COMPANIES if c.get('notable_projects')]),
        'with_contacts': len([c for c in COMPANIES if c.get('existing_contacts')]),
    }
    for c in COMPANIES:
        m = c['market']
        summary['by_market'][m] = summary['by_market'].get(m, 0) + 1
    return summary


if __name__ == '__main__':
    s = get_summary()
    print(f"Total target companies: {s['total']}")
    print(f"With known location: {s['with_location']}")
    print(f"With notable projects: {s['with_projects']}")
    print(f"With existing contacts: {s['with_contacts']}")
    print(f"\nBy market:")
    for market, count in sorted(s['by_market'].items(), key=lambda x: -x[1]):
        print(f"  {market}: {count}")
