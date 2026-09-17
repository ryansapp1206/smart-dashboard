# vocabulary.py

replacements = {
    "six tee": "sixty", "sick stee": "sixty", "six d": "sixty", "six tea": "sixty",
    "fifth tee": "fifty", "fif d": "fifty", 
    "four d": "forty", "four tee": "forty", "for d": "forty",
    "third e": "thirty", "thir d": "thirty", "dirty": "thirty",
    "seven d": "seventy", "eight d": "eighty", "ate e": "eighty", "nine d": "ninety",
    "twen e": "twenty", "a hundred": "one hundred"
}

word_to_num = {
    "zero": 0, "one": 1, "won": 1, "two": 2, "three": 3, "tree": 3, 
    "four": 4, "for": 4, "five": 5, "six": 6, "sex": 6, "seven": 7, 
    "eight": 8, "ate": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100
}

chord_map = {
    # MINOR CHORDS
    " a minor ": "Am", " ay minor ": "Am", " aim in her ": "Am", " a miner ": "Am",
    " eight minor ": "Am", " ate minor ": "Am", " a minner ": "Am", " a myner ": "Am",
    " amen or ": "Am", " a might ": "Am", " aiming her ": "Am", " a liner ": "Am",
    " a my nor ": "Am", " a diner ": "Am", " a finer ": "Am", " pay minor ": "Am",
    " day minor ": "Am", " a meaner ": "Am", " hey minor ": "Am",

    " b minor ": "Bm", " be minor ": "Bm", " bee minor ": "Bm", " me minor ": "Bm", 
    " vee minor ": "Bm", " v minor ": "Bm", " bean miner ": "Bm",

    " c minor ": "Cm", " see minor ": "Cm", " sea minor ": "Cm", " z minor ": "Cm",

    " d minor ": "Dm", " dee minor ": "Dm", " the minor ": "Dm", " the miner ": "Dm",
    " demon or ": "Dm", " de minor ": "Dm", " team in her ": "Dm", " the higher ": "Dm",
    " d higher ": "Dm", " dee higher ": "Dm", " deep minor ": "Dm", " dean minor ": "Dm",
    " jimmy dean minor ": "Dm", " tea minor ": "Dm", " t minor ": "Dm", " diminish ": "Dm",
    " dominor ": "Dm", " the myner ": "Dm",

    " e minor ": "Em", " ee minor ": "Em", " he minor ": "Em", " he miner ": "Em",
    " e miner ": "Em", " meaner ": "Em", " eat minor ": "Em", " e higher ": "Em",
    " he higher ": "Em", " ee higher ": "Em", " you minor ": "Em", " yi minor ": "Em",
    " even or ": "Em",

    # MAJOR CHORDS
    " a chord ": "A", " a cord ": "A", " a board ": "A", " a court ": "A", " a core ": "A",
    " hey chord ": "A", " eight chord ": "A", " ay chord ": "A", " a cool ": "A",
    " hey cool ": "A", " a for ": "A", " hey for ": "A", " a card ": "A", " ate chord ": "A",
    " ape chord ": "A",

    " c chord ": "C", " see chord ": "C", " sea chord ": "C", " c cord ": "C",
    " see cord ": "C", " sea cord ": "C", " record ": "C", " secord ": "C",
    " z chord ": "C", " see board ": "C", " see core ": "C", " c cool ": "C",
    " see cool ": "C", " c card ": "C", " see card ": "C", " seat chord ": "C",
    " seed chord ": "C", " seek chord ": "C", " secret ": "C", " zee chord ": "C",
    " si chord ": "C", " she chord ": "C", " seem to ": "C", " seem ": "C",

    " d chord ": "D", " dee chord ": "D", " d cord ": "D", " dee cord ": "D",
    " decor ": "D", " decord ": "D", " beat chord ": "D", " d cool ": "D",
    " dee cool ": "D", " d for ": "D", " d card ": "D", " the chord ": "D",
    " the cord ": "D", " the board ": "D", " the core ": "D", " the cool ": "D",
    " the for ": "D", " the card ": "D", " tea chord ": "D", " t chord ": "D",
    " deep chord ": "D", " dean chord ": "D", " these chord ": "D", " jimmy dean ": "D",
    " de chord ": "D",

    " e chord ": "E", " ee chord ": "E", " he chord ": "E", " he cord ": "E",
    " e cord ": "E", " eat chord ": "E", " ee cord ": "E", " e cool ": "E",
    " ee cool ": "E", " he cool ": "E", " e for ": "E", " he for ": "E",
    " e card ": "E", " key chord ": "E", " be chord ": "E", " me chord ": "E",
    " each chord ": "E",

    " g chord ": "G", " gee chord ": "G", " g cord ": "G", " gee cord ": "G",
    " g cool ": "G", " gee cool ": "G", " g core ": "G", " g court ": "G",
    " jig cord ": "G", " cheese chord ": "G", " g for ": "G", " gee for ": "G",
    " g card ": "G", " gee card ": "G", " jeep chord ": "G", " chief chord ": "G",
    " cheap chord ": "G", " g board ": "G", " jean chord ": "G", " jee chord ": "G",
    " chi chord ": "G", " cheap board ": "G",

    # SINGLE LETTERS
    " a ": "A", " ay ": "A", " hey ": "A", " aye ": "A", " eight ": "A", " ate ": "A", " ape ": "A",
    " c ": "C", " see ": "C", " sea ": "C", " z ": "C", " si ": "C", " zee ": "C", " seat ": "C", " seed ": "C",
    " d ": "D", " dee ": "D", " de ": "D", " tee ": "D", " tea ": "D", " dean ": "D",
    " e ": "E", " ee ": "E", " he ": "E", " yi ": "E", " eat ": "E", " each ": "E",
    " g ": "G", " gee ": "G", " jee ": "G", " chi ": "G", " cheese ": "G", " jig ": "G", " jean ": "G"
}