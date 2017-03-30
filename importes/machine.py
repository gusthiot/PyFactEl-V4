from importes import Fichier
from outils import Outils


class Machine(Fichier):
    """
    Classe pour l'importation des données de Machines Cmi
    """

    cles = ['annee', 'mois', 'id_machine', 'nom', 'id_cout', 'rabais_hc', 'tx_occ_eff_hp',
            'penalite_hp', 'tx_occ_eff_hc', 'penalite_hc', 'delai_sans_frais']
    nom_fichier = "machine.csv"
    libelle = "Machines"

    def contient_id(self, id_machine):
        """
        vérifie si une machine contient l'id donné
        :param id_machine: id à vérifier
        :return: 1 si id contenu, 0 sinon
        """
        ligne = 1
        if self.verifie_coherence == 1:
            for cle, machine in self.donnees.items():
                if machine['id_machine'] == id_machine:
                    return ligne
                ligne += 1
        else:
            for machine in self.donnees:
                if machine['id_machine'] == id_machine:
                    return ligne
                ligne += 1
        return 0

    def est_coherent(self, couts):
        """
        vérifie que les données du fichier importé sont cohérentes (id machine unique, id catégorie cout référencé,
        catégorie machine référencé dans les coefficients machines), et efface les colonnes mois et année
        :param couts: catégories couts importés
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
        ids = []
        donnees_dict = {}

        for donnee in self.donnees:
            if donnee['id_machine'] == "":
                msg += "le machine id de la ligne " + str(ligne) + " ne peut être vide\n"
            elif donnee['id_machine'] not in ids:
                ids.append(donnee['id_machine'])
            else:
                msg += "l'id machine '" + donnee['id_machine'] + "' de la ligne " + str(ligne) +\
                       " n'est pas unique\n"

            if donnee['id_cout'] == "":
                msg += "l'id catégorie cout de la ligne " + str(ligne) + " ne peut être vide\n"
            elif couts.contient_id(donnee['id_cout']) == 0:
                msg += "l'id catégorie cout '" + donnee['id_cout'] + "' de la ligne " + str(ligne) \
                       + " n'est pas référencé\n"

            donnee['rabais_hc'], info = Outils.est_un_nombre(donnee['rabais_hc'],
                                                             "le rabais heures creuses", ligne)
            msg += info
            donnee['tx_occ_eff_hp'], info = Outils.est_un_nombre(donnee['tx_occ_eff_hp'],
                                                                 "le taux effectif d'occupation HP", ligne)
            msg += info
            donnee['penalite_hp'], info = Outils.est_un_nombre(donnee['penalite_hp'],
                                                               "la pénalité HP", ligne)
            msg += info
            donnee['tx_occ_eff_hc'], info = Outils.est_un_nombre(donnee['tx_occ_eff_hc'],
                                                                 "le taux effectif d'occupation HC", ligne)
            msg += info
            donnee['penalite_hc'], info = Outils.est_un_nombre(donnee['penalite_hc'],
                                                               "la pénalité HC", ligne)
            msg += info
            donnee['delai_sans_frais'], info = Outils.est_un_nombre(donnee['delai_sans_frais'], "le délai sans frais",
                                                                    ligne)
            msg += info

            del donnee['annee']
            del donnee['mois']
            donnees_dict[donnee['id_machine']] = donnee
            ligne += 1

        self.donnees = donnees_dict
        self.verifie_coherence = 1

        if msg != "":
            msg = self.libelle + "\n" + msg
            print("msg : " + msg)
            Outils.affiche_message(msg)
            return 1
        return 0
