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
                        Generaux)
from traitement import (Annexes,
                        BilanMensuel,
                        Facture,
                        Sommes,
                        Verification,
                        Detail,
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

edition = Edition(dossier_source)

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

generaux = Generaux(dossier_source)

verification = Verification()

if verification.verification_date(edition, acces, clients, coefmachines, coefprests, comptes, livraisons, machines,
                                  prestations, reservations, couts, users) > 0:
    sys.exit("Erreur dans les dates")

if verification.verification_cohérence(generaux, edition, acces, clients, coefmachines, coefprests, comptes, livraisons,
                                       machines, prestations, reservations, couts, users) > 0:
    sys.exit("Erreur dans la cohérence")

dossier_enregistrement = Outils.chemin_dossier([generaux.chemin, edition.annee,
                                                Outils.mois_string(edition.mois)], plateforme, generaux)
dossier_lien = Outils.lien_dossier([generaux.lien, edition.annee, Outils.mois_string(edition.mois)],
                                   plateforme, generaux)
livraisons.calcul_montants(prestations, coefprests, clients, verification, comptes)
reservations.calcul_montants(machines, coefmachines, clients, verification)
acces.calcul_montants(machines, coefmachines, clients, verification, couts, comptes)

sommes = Sommes(verification, generaux)
sommes.calculer_toutes(livraisons, reservations, acces, clients, machines)

if edition.version == '0':
    dossier_csv = Outils.chemin_dossier([dossier_enregistrement, "csv_0"], plateforme, generaux)
else:
    dossier_csv = Outils.chemin_dossier([dossier_enregistrement, "csv_" + edition.version + "_" +
                                         edition.client_unique], plateforme, generaux)
dossier_destination = DossierDestination(dossier_csv)

annexes = "annexes"
dossier_annexes = Outils.chemin_dossier([dossier_enregistrement, annexes], plateforme, generaux)
lien_annexes = Outils.lien_dossier([dossier_lien, annexes], plateforme, generaux)
annexes_techniques = "annexes_techniques"
dossier_annexes_techniques = Outils.chemin_dossier([dossier_enregistrement, annexes_techniques], plateforme, generaux)
lien_annexes_techniques = Outils.lien_dossier([dossier_lien, annexes_techniques], plateforme, generaux)

facture_prod = Facture()
facture_prod.factures(sommes, dossier_destination, edition, generaux, clients, comptes, lien_annexes,
                      lien_annexes_techniques, annexes, annexes_techniques)

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

BilanMensuel.bilan(dossier_destination, edition, sommes, clients, generaux, acces, livraisons, comptes, reservations)
Detail.detail(dossier_destination, edition, sommes, clients, generaux, acces, livraisons, comptes, couts)

Recapitulatifs.cae(dossier_destination, edition, acces, comptes, clients, users, machines)
Recapitulatifs.lvr(dossier_destination, edition, livraisons, comptes, clients, users, prestations)
Recapitulatifs.res(dossier_destination, edition, reservations, clients, users, machines)

for fichier in [acces.nom_fichier, clients.nom_fichier, coefmachines.nom_fichier, coefprests.nom_fichier,
                comptes.nom_fichier, livraisons.nom_fichier, machines.nom_fichier, prestations.nom_fichier,
                reservations.nom_fichier, couts.nom_fichier, users.nom_fichier, generaux.nom_fichier,
                edition.nom_fichier]:
    dossier_destination.ecrire(fichier, dossier_source.lire(fichier))

Outils.affiche_message("OK !!!")
