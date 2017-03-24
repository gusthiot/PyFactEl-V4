from outils import Outils


class Recapitulatifs(object):

    @staticmethod
    def cae(dossier_destination, edition, acces, comptes, clients, users, machines):

        nom = "cae_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version != '0':
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = [edition.annee, edition.mois, "Id-Compte", "Numéro de compte", "Intitulé compte", "Code Client CMi",
                     "Abrev. Labo", "Id-User", "Nom User", "Prénom User", "Id-Machine", "Nom Machine",
                     "Date et Heure login", "Durée machine HP", "Durée machine HC", "Durée opérateur HP",
                     "Durée opérateur HC", "Id-Opérateur", "Prénom Nom opérateur", "Remarque opérateur",
                     "Remarque staff"]
            fichier_writer.writerow(ligne)

            for donnee in acces.donnees:
                compte = comptes.donnees[donnee['id_compte']]
                client = clients.donnees[compte['code_client']]
                user = users.donnees[donnee['id_user']]
                machine = machines.donnees[donnee['id_machine']]
                ligne = [edition.annee, edition.mois, donnee['id_compte'], compte['numero'], compte['intitule'],
                         compte['code_client'], client['abrev_labo'], donnee['id_user'], user['nom'], user['prenom'],
                         donnee['id_machine'], machine['nom'], donnee['date_login'], donnee['duree_machine_hp'],
                         donnee['duree_machine_hc'], donnee['duree_operateur_hp'], donnee['duree_operateur_hc'],
                         donnee['id_op'], donnee['nom_op'], donnee['remarque_op'], donnee['remarque_staff']]
                fichier_writer.writerow(ligne)

    @staticmethod
    def lvr(dossier_destination, edition, livraisons, comptes, clients, users, prestations):
        nom = "lvr_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version != '0':
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = [edition.annee, edition.mois, "Id-Compte", "Numéro de compte", "Intitulé compte", "Code Client CMi",
                     "Abrev. Labo", "Id-User", "Nom User", "Prénom User", "Id-Prestation", "Numéro de prestation",
                     "Désignation prestation", "Date de livraison", "Quantité livrée", "Unité de livraison",
                     "Rabais [CHF]", "Responsable", "ID-Livraison", "Date et Heure de la commande",
                     "Date et Heure de la prise en charge", "Remarque"]
            fichier_writer.writerow(ligne)

            for donnee in livraisons.donnees:
                compte = comptes.donnees[donnee['id_compte']]
                client = clients.donnees[compte['code_client']]
                user = users.donnees[donnee['id_user']]
                prestation = prestations.donnees[donnee['id_prestation']]
                ligne = [edition.annee, edition.mois, donnee['id_compte'], compte['numero'], compte['intitule'],
                         compte['code_client'], client['abrev_labo'], donnee['id_user'], user['nom'], user['prenom'],
                         donnee['id_prestation'], prestation['no_prestation'], prestation['designation'],
                         donnee['date_livraison'], donnee['quantite'], prestation['unite_prest'], donnee['rabais'],
                         donnee['responsable'], donnee['id_livraison'], donnee['date_commande'], donnee['date_prise'],
                         donnee['remarque']]
                fichier_writer.writerow(ligne)

    @staticmethod
    def res(dossier_destination, edition, reservations, clients, users, machines):
        nom = "res_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + str(edition.version)
        if edition.version != '0':
            nom += "_" + str(edition.client_unique)
        nom += ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = [edition.annee, edition.mois, "Code Client CMi", "Abrev. Labo", "Id-User", "Nom User",
                     "Prénom User", "Id-Machine", "Nom Machine", "Date et Heure début de slot",
                     "Durée du slot réservé HP", "Durée du slot réservé HC", "Slot supprimé", "Durée ouvrée",
                     "Date et Heure de réservation", "Date et Heure de suppression"]
            fichier_writer.writerow(ligne)

            for donnee in reservations.donnees:
                client = clients.donnees[donnee['code_client']]
                user = users.donnees[donnee['id_user']]
                machine = machines.donnees[donnee['id_machine']]
                ligne = [edition.annee, edition.mois, donnee['code_client'], client['abrev_labo'],
                         donnee['id_user'], user['nom'], user['prenom'], donnee['id_machine'], machine['nom'],
                         donnee['date_debut'], donnee['duree_hp'], donnee['duree_hc'], donnee['si_supprime'],
                         donnee['duree_ouvree'], donnee['date_reservation'], donnee['date_suppression']]
                fichier_writer.writerow(ligne)
