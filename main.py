# This Python file uses the following encoding: utf-8

"""
Fichier principal à lancer pour faire tourner le logiciel

Usage:
  main.py [options]

Options:

  -h   --help              Affiche le présent message
  --entrees <chemin>       Chemin des fichiers d'entrée
  --sansgraphiques         Pas d'interface graphique
"""

import sys
from docopt import docopt

from importes import (Client,
                      Acces,
                      CoefMachine,
                      CoefPrest,
                      Compte,
                      Livraison,
                      Machine,
                      Prestation,
                      Reservation,
                      Couts,
                      User,
                      DossierSource,
                      DossierDestination)
from outils import Outils
from parametres import (Edition,
                        Suppression,
                        Generaux)
from traitement import (Annexes,
                        BilanMensuel,
                        BilanComptes,
                        Facture,
                        Sommes,
                        Verification,
                        Detail,
                        Resumes,
                        Recapitulatifs)
from prod2qual import Prod2Qual
from latex import Latex

arguments = docopt(__doc__)

plateforme = sys.platform

if arguments["--sansgraphiques"]:
    Outils.interface_graphique(False)

if arguments["--entrees"]:
    dossier_data = arguments["--entrees"]
else:
    dossier_data = Outils.choisir_dossier(plateforme)
dossier_source = DossierSource(dossier_data)

pg_present = Outils.existe([dossier_data, Generaux.nom_fichier], plateforme)
sup_present = Outils.existe([dossier_data, Suppression.nom_fichier], plateforme)

if pg_present:
    if sup_present:
        msg = "Deux fichiers bruts incompatibles dans le répertoire : supprfact.csv et paramedit.csv"
        print("msg : " + msg)
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")

    edition = Edition(dossier_source)
    generaux = Generaux(dossier_source)

    acces = Acces(dossier_source)
    clients = Client(dossier_source)
    coefmachines = CoefMachine(dossier_source)
    coefprests = CoefPrest(dossier_source)
    comptes = Compte(dossier_source)
    livraisons = Livraison(dossier_source)
    machines = Machine(dossier_source)
    prestations = Prestation(dossier_source)
    reservations = Reservation(dossier_source)
    couts = Couts(dossier_source)
    users = User(dossier_source)

    verification = Verification()

    if verification.verification_date(edition, acces, clients, coefmachines, coefprests, comptes, livraisons, machines,
                                      prestations, reservations, couts, users) > 0:
        sys.exit("Erreur dans les dates")

    if verification.verification_cohérence(generaux, edition, acces, clients, coefmachines, coefprests, comptes,
                                           livraisons, machines, prestations, reservations, couts, users) > 0:
        sys.exit("Erreur dans la cohérence")

    existe = Outils.existe([generaux.chemin, edition.annee, Outils.mois_string(edition.mois)], plateforme)
    dossier_enregistrement = Outils.chemin_dossier([generaux.chemin, edition.annee,
                                                    Outils.mois_string(edition.mois)], plateforme, generaux)
    dossier_lien = Outils.lien_dossier([generaux.lien, edition.annee, Outils.mois_string(edition.mois)],
                                       plateforme, generaux)

    if edition.version == '0':
        if existe:
            msg = "Le répertoire " + dossier_enregistrement + " existe déjà !"
            print("msg : " + msg)
            Outils.affiche_message(msg)
            sys.exit("Erreur sur le répértoire")
        dossier_csv = Outils.chemin_dossier([dossier_enregistrement, "csv_0"], plateforme, generaux)
    else:
        existe = Outils.existe([dossier_enregistrement, "csv_" + edition.version + "_" +
                                edition.client_unique], plateforme)
        if existe:
            msg = "La version " + edition.version + " du client " + edition.client_unique + " existe déjà !"
            print("msg : " + msg)
            Outils.affiche_message(msg)
            sys.exit("Erreur sur le répértoire")
        dossier_csv = Outils.chemin_dossier([dossier_enregistrement, "csv_" + edition.version + "_" +
                                             edition.client_unique], plateforme, generaux)
    dossier_destination = DossierDestination(dossier_csv)

    livraisons.calcul_montants(prestations, coefprests, clients, verification, comptes)
    reservations.calcul_montants(machines, coefmachines, clients, verification, couts)
    acces.calcul_montants(machines, coefmachines, clients, verification, couts, comptes)

    sommes = Sommes(verification, generaux)
    sommes.calculer_toutes(livraisons, reservations, acces, clients, machines)

    annexes = "annexes"
    dossier_annexes = Outils.chemin_dossier([dossier_enregistrement, annexes], plateforme, generaux)
    lien_annexes = Outils.lien_dossier([dossier_lien, annexes], plateforme, generaux)
    annexes_techniques = "annexes_techniques"
    dossier_annexes_techniques = Outils.chemin_dossier([dossier_enregistrement, annexes_techniques], plateforme,
                                                       generaux)
    lien_annexes_techniques = Outils.lien_dossier([dossier_lien, annexes_techniques], plateforme, generaux)

    Outils.copier_dossier("./reveal.js/", "js", dossier_enregistrement)
    Outils.copier_dossier("./reveal.js/", "css", dossier_enregistrement)
    facture_prod = Facture()
    f_html_sections = facture_prod.factures(sommes, dossier_destination, edition, generaux, clients, comptes,
                                            lien_annexes, lien_annexes_techniques, annexes, annexes_techniques)

    prod2qual = Prod2Qual(dossier_source)
    if prod2qual.actif:
        facture_qual = Facture(prod2qual)
        generaux_qual = Generaux(dossier_source, prod2qual)
        facture_qual.factures(sommes, dossier_destination, edition, generaux_qual, clients, comptes, lien_annexes,
                              lien_annexes_techniques, annexes, annexes_techniques)

    if Latex.possibles():
        Annexes.annexes_techniques(sommes, clients, edition, livraisons, acces, machines, reservations, comptes,
                                   dossier_annexes_techniques, plateforme, generaux, users, couts)
        Annexes.annexes(sommes, clients, edition, livraisons, acces, machines, reservations, comptes, dossier_annexes,
                        plateforme, generaux, users, couts)

    bm_lignes = BilanMensuel.creation_lignes(edition, sommes, clients, generaux, acces, livraisons, comptes,
                                             reservations)
    BilanMensuel.bilan(dossier_destination, edition, generaux, bm_lignes)
    bc_lignes = BilanComptes.creation_lignes(edition, sommes, clients, generaux, comptes)
    BilanComptes.bilan(dossier_destination, edition, generaux, bc_lignes)
    det_lignes = Detail.creation_lignes(edition, sommes, clients, generaux, acces, livraisons, comptes, couts)
    Detail.detail(dossier_destination, edition, det_lignes)

    cae_lignes = Recapitulatifs.cae_lignes(edition, acces, comptes, clients, users, machines)
    Recapitulatifs.cae(dossier_destination, edition, cae_lignes)
    lvr_lignes = Recapitulatifs.lvr_lignes(edition, livraisons, comptes, clients, users, prestations)
    Recapitulatifs.lvr(dossier_destination, edition, lvr_lignes)
    res_lignes = Recapitulatifs.res_lignes(edition, reservations, clients, users, machines)
    Recapitulatifs.res(dossier_destination, edition, res_lignes)

    for fichier in [acces.nom_fichier, clients.nom_fichier, coefmachines.nom_fichier, coefprests.nom_fichier,
                    comptes.nom_fichier, livraisons.nom_fichier, machines.nom_fichier, prestations.nom_fichier,
                    reservations.nom_fichier, couts.nom_fichier, users.nom_fichier, generaux.nom_fichier,
                    edition.nom_fichier]:
        dossier_destination.ecrire(fichier, dossier_source.lire(fichier))

    if edition.version == '0':
        Resumes.base(edition, DossierSource(dossier_csv), DossierDestination(dossier_enregistrement))
    elif Outils.existe([dossier_enregistrement, "csv_0"], plateforme):
        maj = [bm_lignes, bc_lignes, det_lignes, cae_lignes, lvr_lignes, res_lignes]
        Resumes.mise_a_jour(edition, DossierSource(dossier_enregistrement),
                            DossierDestination(dossier_enregistrement), maj, f_html_sections)
elif sup_present:
    suppression = Suppression(dossier_source)
    dossier_enregistrement = Outils.chemin_dossier([suppression.chemin, suppression.annee,
                                                    Outils.mois_string(suppression.mois)], plateforme, None)
    if suppression.version == '0':
        msg = "Le numéro de version doit être supérieur ou égal à 1 !"
        print("msg : " + msg)
        Outils.affiche_message(msg)
        sys.exit("Erreur sur la version")
    else:
        existe = Outils.existe([dossier_enregistrement, "csv_" + suppression.version + "_" +
                                suppression.client_unique], plateforme)
        if existe:
            msg = "La version " + suppression.version + " du client " + suppression.client_unique + " existe déjà !"
            print("msg : " + msg)
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        existe = Outils.existe([dossier_enregistrement, "csv_0"], plateforme)
        if not existe:
            msg = " La version 0 n’existe pas dans " + dossier_enregistrement + \
                  ", impossible de supprimer une facture !"
            print("msg : " + msg)
            Outils.affiche_message(msg)
            sys.exit("Erreur sur la version")

        Resumes.suppression(suppression, DossierSource(dossier_enregistrement), DossierDestination(dossier_enregistrement))
else:
    msg = "Ni supprfact.csv, ni paramedit.csv dans le répértoire, rien ne sera fait !"
    print("msg : " + msg)
    Outils.affiche_message(msg)
    sys.exit("Erreur sur les fichiers")


Outils.affiche_message("OK !!!")
