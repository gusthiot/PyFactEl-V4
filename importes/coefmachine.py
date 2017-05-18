from importes import Fichier
from outils import Outils


class CoefMachine(Fichier):
    """
    Classe pour l'importation des données de Coefficients Machines
    """

    nom_fichier = "coeffmachine.csv"
    cles = ['annee', 'mois', 'nature', 'emolument', 'tarif_u', 'coef_a', 'coef_mo']
    libelle = "Coefficients Machines"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def est_coherent(self, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes (si couple catégorie - classe de tarif est unique),
        et efface les colonnes mois et année
        :param generaux: paramètres généraux
        :return: 1 s'il y a une erreur, 0 sinon
        """
        if self.verifie_date == 0:
            info = self.libelle + ". vous devez vérifier la date avant de vérifier la cohérence"
            Outils.affiche_message(info)
            return 1

        if self.verifie_coherence == 1:
            print(self.libelle + ": cohérence déjà vérifiée")
            return 0

        msg = ""
        ligne = 1
        donnees_dict = {}
        natures = []

        for donnee in self.donnees:
            if donnee['nature'] == "":
                msg += "la nature client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['nature'] not in generaux.obtenir_code_n():
                msg += "la nature client de la ligne " + str(ligne) + " n'existe pas dans les codes N\n"
            elif donnee['nature'] not in natures:
                if donnee['nature'] not in natures:
                    natures.append(donnee['nature'])
                else:
                    msg += "la nature '" + donnee['nature'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            if donnee['tarif_u'] == "":
                msg += "le tarif U de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['tarif_u'] not in ['U1', 'U2', 'U3']:
                msg += "le tarif U de la ligne " + str(ligne) + " n'est pas parmi [U1, U2, U3]\n"

            donnee['emolument'], info = Outils.est_un_nombre(donnee['emolument'], "l'émolument", ligne)
            msg += info
            donnee['coef_a'], info = Outils.est_un_nombre(donnee['coef_a'], "le coefficient A", ligne)
            msg += info
            donnee['coef_mo'], info = Outils.est_un_nombre(donnee['coef_mo'], "le coefficient MO", ligne)
            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['nature']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            Outils.affiche_message(msg)
            return 1
        return 0
