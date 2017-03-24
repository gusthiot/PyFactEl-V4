from importes import Fichier
from outils import Outils


class CoefMachine(Fichier):
    """
    Classe pour l'importation des données de Coefficients Machines
    """

    nom_fichier = "coeffmachine.csv"
    cles = ['annee', 'mois', 'id_classe_tarif', 'intitule', 'emolument', 'coef_a', 'coef_b', 'coef_c', 'coef_d',
            'coef_e', 'coef_mo', 'coef_r']
    libelle = "Coefficients Machines"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes = []

    def obtenir_classes(self):
        """
        retourne toutes les classes de tarif présentes
        :return: toutes les classes de tarif présentes
        """
        if self.verifie_coherence == 0:
            info = self.libelle + ". vous devez vérifier la cohérence avant de pouvoir obtenir les classes"
            print(info)
            Outils.affiche_message(info)
            return []
        return self.classes

    def est_coherent(self):
        """
        vérifie que les données du fichier importé sont cohérentes (si couple catégorie - classe de tarif est unique),
        et efface les colonnes mois et année
        :return: 1 s'il y a une erreur, 0 sinon
        """
        if self.verifie_date == 0:
            info = self.libelle + ". vous devez vérifier la date avant de vérifier la cohérence"
            print(info)
            Outils.affiche_message(info)
            return 1

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}

        for donnee in self.donnees:
            if donnee['id_classe_tarif'] == "":
                msg += "la classe de tarif de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_classe_tarif'] not in self.classes:
                if donnee['id_classe_tarif'] not in self.classes:
                    self.classes.append(donnee['id_classe_tarif'])
                else:
                    msg += "la classe de tarif '" + donnee['id_classe_tarif'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            donnee['emolument'], info = Outils.est_un_nombre(donnee['emolument'], "l'émolument", ligne)
            msg += info
            donnee['coef_a'], info = Outils.est_un_nombre(donnee['coef_a'], "le coefficient A", ligne)
            msg += info
            donnee['coef_b'], info = Outils.est_un_nombre(donnee['coef_b'], "le coefficient B", ligne)
            msg += info
            donnee['coef_c'], info = Outils.est_un_nombre(donnee['coef_c'], "le coefficient C", ligne)
            msg += info
            donnee['coef_d'], info = Outils.est_un_nombre(donnee['coef_d'], "le coefficient D", ligne)
            msg += info
            donnee['coef_e'], info = Outils.est_un_nombre(donnee['coef_e'], "le coefficient E", ligne)
            msg += info
            donnee['coef_mo'], info = Outils.est_un_nombre(donnee['coef_mo'], "le coefficient MO", ligne)
            msg += info
            donnee['coef_r'], info = Outils.est_un_nombre(donnee['coef_r'], "le coefficient R", ligne)
            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['id_classe_tarif']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            print("msg : " + msg)
            Outils.affiche_message(msg)
            return 1
        return 0
