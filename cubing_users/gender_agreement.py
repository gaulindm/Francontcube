# cubing_users/gender_agreement.py
"""
Accord grammatical pour les noms d'identité des cubeurs.

Principe: l'adjectif (qualité) s'accorde avec le genre GRAMMATICAL du nom
de l'animal, jamais avec le genre personnel du cubeur. On ne demande donc
jamais le genre du cubeur — le français fait déjà le travail pour nous.

Ex: "grenouille" est féminin -> "Grenouille Curieuse", peu importe qui
se cache derrière l'identité.
"""

# Genre grammatical de chaque animal — 'm' ou 'f'.
# Basé sur l'usage courant du nom d'espèce en français (le nom "par défaut",
# pas une forme féminine alternative comme "louve" ou "renarde").
ANIMAL_GENDER = {
    'renard':     'm',
    'hibou':      'm',
    'panda':      'm',
    'tortue':     'f',
    'grenouille': 'f',
    'lapin':      'm',
    'ours':       'm',
    'castor':     'm',
    'loup':       'm',
    'manchot':    'm',
    'ecureuil':   'm',
    'perroquet':  'm',
}

# Formes masculine/féminine de chaque qualité.
# Les adjectifs invariables (rapide, calme) ont la même forme aux deux genres.
QUALITY_FORMS = {
    'curieux':     {'m': 'Curieux',     'f': 'Curieuse'},
    'intelligent': {'m': 'Intelligent', 'f': 'Intelligente'},
    'rapide':      {'m': 'Rapide',      'f': 'Rapide'},
    'determine':   {'m': 'Déterminé',   'f': 'Déterminée'},
    'perseverant': {'m': 'Persévérant', 'f': 'Persévérante'},
    'concentre':   {'m': 'Concentré',   'f': 'Concentrée'},
    'gentil':      {'m': 'Gentil',      'f': 'Gentille'},
    'aidant':      {'m': 'Aidant',      'f': 'Aidante'},
    'creatif':     {'m': 'Créatif',     'f': 'Créative'},
    'joyeux':      {'m': 'Joyeux',      'f': 'Joyeuse'},
    'patient':     {'m': 'Patient',     'f': 'Patiente'},
    'courageux':   {'m': 'Courageux',   'f': 'Courageuse'},
    'prudent':     {'m': 'Prudent',     'f': 'Prudente'},
    'confiant':    {'m': 'Confiant',    'f': 'Confiante'},
    'calme':       {'m': 'Calme',       'f': 'Calme'},
}


def agree_quality(quality_key, animal_key):
    """
    Retourne la forme de la qualité accordée au genre grammatical de l'animal.
    Repli sur la clé brute si la qualité ou l'animal est inconnu (ne devrait
    pas arriver si les données viennent des formulaires du site).
    """
    gender = ANIMAL_GENDER.get(animal_key, 'm')
    forms = QUALITY_FORMS.get(quality_key)
    if not forms:
        return quality_key.capitalize()
    return forms[gender]
