from importes import Fichier
from outils import Outils
import re


class Client(Fichier):
    """
    Classe pour l'importation des données de Clients Cmi
    """

    cles = ['annee', 'mois', 'code', 'code_sap', 'abrev_labo', 'nom_labo', 'ref', 'dest', 'email', 'mode',
            'type_labo', 'emol_sans_activite', 'emol_base_mens', 'emol_fixe', 'coef', 'id_classe_tarif',
            'classe_tarif']
    nom_fichier = "client.csv"
    libelle = "Clients"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.codes = []

    def obtenir_codes(self):
        """
        retourne les codes de tous les clients
        :return: codes de tous les clients
        """
        if self.verifie_coherence == 0:
            info = self.libelle + ". vous devez vérifier la cohérence avant de pouvoir obtenir les codes"
            print(info)
            Outils.affiche_message(info)
            return []
        return self.codes

    def est_coherent(self, coefmachines, coefprests, generaux):
        """
        vérifie que les données du fichier importé sont cohérentes (code client unique,
        classe tarif présente dans coefficients, type de labo dans paramètres), et efface les colonnes mois et année
        :param coefmachines: coefficients machines importés
        :param coefprests: coefficients prestations importés
        :param generaux: paramètres généraux
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
        classes = []
        donnees_dict = {}

        for donnee in self.donnees:
            if donnee['id_classe_tarif'] == "":
                msg += "la classe de tarif de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_classe_tarif'] not in classes:
                classes.append(donnee['id_classe_tarif'])

            if donnee['code_sap'] == "":
                msg += "le code sap de la ligne " + str(ligne) + " ne peut être vide\n"

            if donnee['code'] == "":
                msg += "le code client de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['code'] not in self.codes:
                self.codes.append(donnee['code'])
            else:
                msg += "le code client '" + donnee['code'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            if donnee['type_labo'] == "":
                msg += "le type de labo de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['type_labo'] not in generaux.obtenir_code_n():
                msg += "le type de labo '" + donnee['type_labo'] + "' de la ligne " + str(ligne) +\
                    " n'existe pas dans les types N\n"

            if (donnee['mode'] != "") and (donnee['mode'] not in generaux.obtenir_modes_envoi()):
                msg += "le mode d'envoi '" + donnee['mode'] + "' de la ligne " + str(ligne) +\
                    " n'existe pas dans les modes d'envoi généraux\n"

            if (donnee['email'] != "") and (not re.match("[^@]+@[^@]+\.[^@]+", donnee['email'])):
                msg += "le format de l'e-mail '" + donnee['email'] + "' de la ligne " + str(ligne) +\
                    " n'est pas correct\n"

            if not((donnee['emol_sans_activite'] == "NON") or (donnee['emol_sans_activite'] == "ZERO") or
                    (donnee['emol_sans_activite'] == "OUI")):
                msg += "l'émolument à payer même sans activité de la ligne " + str(ligne) \
                       + " doit valoir ZERO, NON ou OUI\n"

            donnee['emol_base_mens'], info = Outils.est_un_nombre(donnee['emol_base_mens'], "l'émolument de base",
                                                                  ligne)
            msg += info
            donnee['emol_fixe'], info = Outils.est_un_nombre(donnee['emol_fixe'], "l'émolument fixe", ligne)
            msg += info
            donnee['coef'], info = Outils.est_un_nombre(donnee['coef'], "le coefficient a", ligne)
            msg += info

            av_ds = generaux.avantage_ds_par_code_n(donnee['type_labo'])
            av_hc = generaux.avantage_hc_par_code_n(donnee['type_labo'])

            donnee['rs'] = 1
            donnee['bs'] = 0
            donnee['rh'] = 1
            donnee['bh'] = 0
            if av_ds == 'BONUS':
                donnee['bs'] = 1
                donnee['rs'] = 0
            if av_hc == 'BONUS':
                donnee['bh'] = 1
                donnee['rh'] = 0

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['code']] = donnee

            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        for classe in classes:
            if classe not in coefmachines.obtenir_classes():
                msg += "la classe de tarif '" + classe + "' n'est pas présente dans les coefficients machines\n"
            if classe not in coefprests.obtenir_classes():
                msg += "la classe de tarif '" + classe + "' n'est pas présente dans les coefficients prestations\n"

        if msg != "":
            msg = self.libelle + "\n" + msg
            print("msg : " + msg)
            Outils.affiche_message(msg)
            return 1
        return 0
