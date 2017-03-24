from importes import Fichier
from outils import Outils


class CoefMachine(Fichier):
    """
    Classe pour l'importation des données de Coefficients Machines
    """

    nom_fichier = "coeffmachine.csv"
    cles = ['annee', 'mois', 'id_classe_tarif', 'intitule', 'categorie', 'coef_a', 'coef_b', 'coef_c', 'coef_d',
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

    def contient_categorie(self, categorie):
        """
        vérifie si la catégorie est présente
        :param categorie: la catégorie à vérifier
        :return: 1 si présente, 0 sinon
        """
        if self.verifie_coherence == 1:
            for cle, coefmachine in self.donnees.items():
                if coefmachine['categorie'] == categorie:
                    return 1
        else:
            for coefmachine in self.donnees:
                if coefmachine['categorie'] == categorie:
                    return 1
        return 0

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
        categories = []
        couples = []
        donnees_dict = {}

        for donnee in self.donnees:
            if donnee['categorie'] == "":
                msg += "la catégorie de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['categorie'] not in categories:
                categories.append(donnee['categorie'])

            if donnee['id_classe_tarif'] == "":
                msg += "la classe de tarif de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_classe_tarif'] not in self.classes:
                self.classes.append(donnee['id_classe_tarif'])

            if (donnee['categorie'] != "") and (donnee['id_classe_tarif'] != ""):
                couple = [donnee['categorie'], donnee['id_classe_tarif']]
                if couple not in couples:
                    couples.append(couple)
                else:
                    msg += "Couple categorie '" + donnee['categorie'] + "' et classe de tarif '" + \
                           donnee['id_classe_tarif'] + "' de la ligne " + str(ligne) + " pas unique\n"

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
            donnees_dict[donnee['id_classe_tarif'] + donnee['categorie']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        for categorie in categories:
            for classe in self.classes:
                couple = [categorie, classe]
                if couple not in couples:
                    msg += "Couple categorie '" + categorie + "' et classe de tarif '" + \
                           classe + "' n'existe pas\n"

        if msg != "":
            msg = self.libelle + "\n" + msg
            print("msg : " + msg)
            Outils.affiche_message(msg)
            return 1
        return 0
