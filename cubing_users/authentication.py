# cubing_users/authentication.py
import hashlib
import random
from .models import Cuber


def hash_color_code(color_code):
    """
    Hash un color_code avec SHA256.

    Args:
        color_code: liste ou string (ex: ['Rouge','Bleu','Vert'] ou "Rouge,Bleu,Vert")

    Returns:
        String hexadécimal SHA256
    """
    if isinstance(color_code, list):
        color_code = ','.join(color_code)
    return hashlib.sha256(color_code.encode()).hexdigest()


def verify_color_code(color_code, hashed):
    """
    Vérifie si un color_code correspond au hash stocké.

    Args:
        color_code: liste ou string
        hashed:     le hash SHA256 stocké en DB

    Returns:
        Boolean
    """
    return hash_color_code(color_code) == hashed


def generate_color_code():
    """
    Génère un color_code aléatoire de 3 couleurs (répétitions permises).

    Returns:
        Liste de 3 couleurs
    """
    colors = ['Rouge', 'Bleu', 'Vert', 'Jaune', 'Orange', 'Blanc']
    return [random.choice(colors) for _ in range(3)]


class CuberAuthenticationBackend:
    """
    Backend d'authentification custom pour les cubeurs.
    Authentifie avec: animal + cube_color + quality_1 + quality_2 + color_code (3 couleurs)
    """

    def authenticate(self, request, animal=None, cube_color=None,
                     quality_1=None, quality_2=None, color_code=None, **kwargs):
        """
        Authentifie un cubeur avec son identité visuelle et son code couleur.

        Args:
            animal:     clé de l'animal   (ex: 'hibou')
            cube_color: clé de la couleur  (ex: 'bleu')
            quality_1:  clé 1re qualité    (ex: 'curieux')
            quality_2:  clé 2e qualité     (ex: 'courageux')
            color_code: string 3 couleurs séparées par virgule (ex: 'Rouge,Bleu,Rouge')

        Returns:
            Cuber si authentification réussie, None sinon
        """
        if not all([animal, cube_color, quality_1, quality_2, color_code]):
            return None

        try:
            cuber = Cuber.objects.get(
                animal=animal,
                cube_color=cube_color,
                quality_1=quality_1,
                quality_2=quality_2,
            )

            if verify_color_code(color_code, cuber.color_code_hash):
                return cuber

        except Cuber.DoesNotExist:
            # Hash dummy pour éviter les timing attacks
            hash_color_code(color_code)

        return None

    def get_user(self, cuber_id):
        """Récupère un cubeur par son ID — utilisé par Django pour la session."""
        try:
            return Cuber.objects.get(cuber_id=cuber_id)
        except Cuber.DoesNotExist:
            return None