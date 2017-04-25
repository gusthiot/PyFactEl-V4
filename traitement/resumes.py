from outils import Outils


class Resumes(object):
    """
    Classe pour la création et la modification des résumés statistiques mensuels
    """

    fichiers = ["bilan", "bilan-comptes", "detail", "cae", "lvr", "res"]
    positions = [3, 3, 2, 5, 5, 2]

    @staticmethod
    def base(edition, dossier_source, dossier_destination):
        """
        création des résumés statistiques mensuels
        :param edition: paramètres d'édition
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        """
        for fichier in Resumes.fichiers:
            fichier_complet = fichier + "_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois)
            dossier_destination.ecrire(fichier_complet + ".csv", dossier_source.lire(fichier_complet + "_0.csv"))
        ticket_complet = "ticket_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois)
        ticket_texte = dossier_source.string_lire(ticket_complet + "_0.html")
        ticket_texte = ticket_texte.replace("..", ".")
        dossier_destination.string_ecrire(ticket_complet + ".html", ticket_texte)

    @staticmethod
    def mise_a_jour(edition, dossier_source, dossier_destination, maj, html_sections):
        """
        modification des résumés mensuels au niveau du client dont la facture est modifiée 
        :param edition: paramètres d'édition
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param maj: données modifiées pour le client pour les différents fichiers
        :param html_sections: section html modifiée pour le client
        """
        if len(maj) != len(Resumes.fichiers):
            info = "Résumés : erreur taille tableau"
            print(info)
            Outils.affiche_message(info)
            return

        for i in range(len(Resumes.fichiers)):
            fichier_complet = Resumes.fichiers[i] + "_" + str(edition.annee) + "_" + \
                              Outils.mois_string(edition.mois) + ".csv"
            print("modification " + Resumes.fichiers[i] + " : " + edition.client_unique)
            donnees_csv = Resumes.ouvrir_csv_sans_client(
                dossier_source, fichier_complet, edition.client_unique, Resumes.positions[i])
            with dossier_destination.writer(fichier_complet) as fichier_writer:
                for ligne in donnees_csv:
                    fichier_writer.writerow(ligne)
                for ligne in maj[i]:
                    fichier_writer.writerow(ligne)

        ticket_complet = "ticket_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + ".html"
        ticket_texte = dossier_source.string_lire(ticket_complet)
        index = ticket_texte.find('<section id="' + edition.client_unique + '">')
        if index > -1:
            index2 = ticket_texte.find('</section>', index)
            if index2 > -1:
                texte = ticket_texte[:index] + html_sections + ticket_texte[(index2+10):]
                texte = texte.replace("..", ".")
                dossier_destination.string_ecrire(ticket_complet, texte)
            else:
                info = "Fin de section non trouvée"
                print(info)
                Outils.affiche_message(info)
        else:
            info = "Section attendue non trouvée"
            print(info)
            Outils.affiche_message(info)

    @staticmethod
    def ouvrir_csv_sans_client(dossier_source, fichier, code_client, position_code):
        """
        ouverture d'un csv comme string sans les données d'un client donné
        :param dossier_source: Une instance de la classe dossier.DossierSource
        :param fichier: nom du fichier csv
        :param code_client: code du client à ignorer
        :param position_code: position colonne du code client dans le csv
        :return: donnees du csv modifiées en tant que string
        """
        donnees_csv = []
        try:
            fichier_reader = dossier_source.reader(fichier)
            for ligne in fichier_reader:
                if ligne == -1:
                    continue
                if ligne[position_code] != code_client:
                    donnees_csv.append(ligne)
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : " + fichier)
        return donnees_csv
