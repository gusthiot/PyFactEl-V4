from outils import Outils
from latex import Latex
import math


class Annexes(object):
    """
    Classe pour la création des annexes
    """
    @staticmethod
    def annexes(sommes, clients, edition, livraisons, acces, machines, reservations, comptes, dossier_annexe,
                plateforme, generaux, users, couts):
        """
        création des annexes de facture
        :param sommes: sommes calculées
        :param clients: clients importés
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param acces: accès importés
        :param machines: machines importées
        :param reservations: réservations importées
        :param comptes: comptes importés
        :param dossier_annexe: nom du dossier dans lequel enregistrer le dossier des annexes
        :param plateforme: OS utilisé
        :param generaux: paramètres généraux
        :param users: users importés
        :param couts: catégories coûts importées
        """
        prefixe = "annexe_"
        garde = r'''Annexes factures \newline Billing Appendices'''

        Annexes.creation_annexes(sommes, clients, edition, livraisons, acces, machines, reservations, comptes,
                                 dossier_annexe, plateforme, prefixe, generaux, garde, users, couts)

    @staticmethod
    def annexes_techniques(sommes, clients, edition, livraisons, acces, machines, reservations, comptes, dossier_annexe,
                           plateforme, generaux, users, couts):
        """
        création des annexes techniques
        :param sommes: sommes calculées
        :param clients: clients importés
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param acces: accès importés
        :param machines: machines importées
        :param reservations: réservations importées
        :param comptes: comptes importés
        :param dossier_annexe: nom du dossier dans lequel enregistrer le dossier des annexes
        :param plateforme: OS utilisé
        :param generaux: paramètres généraux
        :param users: users importés
        :param couts: catégories coûts importées
        """
        prefixe = "annexeT_"
        garde = r'''Annexes techniques \newline Technical Appendices'''

        Annexes.creation_annexes(sommes, clients, edition, livraisons, acces, machines, reservations,  comptes,
                                 dossier_annexe, plateforme, prefixe, generaux, garde, users, couts)

    @staticmethod
    def creation_annexes(sommes, clients, edition, livraisons, acces, machines, reservations, comptes, dossier_annexe,
                         plateforme, prefixe, generaux, garde, users, couts):
        """
        création des annexes techniques
        :param sommes: sommes calculées
        :param clients: clients importés
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param acces: accès importés
        :param machines: machines importées
        :param reservations: réservations importées
        :param comptes: comptes importés
        :param dossier_annexe: nom du dossier dans lequel enregistrer les annexes
        :param plateforme: OS utilisé
        :param prefixe: prefixe de nom des annexes
        :param generaux: paramètres généraux
        :param garde: titre page de garde
        :param users: users importés
        :param couts: catégories coûts importées
        """

        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer les annexes"
            print(info)
            Outils.affiche_message(info)
            return

        for code_client, scl in sommes.sommes_clients.items():
            code_client = Latex.echappe_caracteres(code_client)

            if scl['somme_t'] == 0 and prefixe == "annexe_":
                continue

            contenu = Latex.entete(plateforme)
            contenu += r'''
                \usepackage[margin=10mm, includehead]{geometry}
                \usepackage{multirow}
                \usepackage{graphicx}
                \usepackage{longtable}
                \usepackage{dcolumn}
                \usepackage{changepage}
                \usepackage[scriptsize]{caption}
                \usepackage{fancyhdr}
                '''

            if edition.filigrane != "":
                contenu += r'''
                    \usepackage{draftwatermark}
                    \SetWatermarkLightness{0.8}
                    \SetWatermarkAngle{45}
                    \SetWatermarkScale{2}
                    \SetWatermarkFontSize{2cm}
                    \SetWatermarkText{''' + edition.filigrane[:15] + r'''}
                    '''

            contenu += r'''
                \pagestyle{fancy}

                \fancyhead{}
                \fancyfoot{}

                \renewcommand{\headrulewidth}{0pt}
                \renewcommand{\footrulewidth}{0pt}

                \fancyhead[L]{\leftmark \\ \rightmark}
                \fancyhead[R]{\thepage}

                \newcommand{\fakesection}[2]{
                    \markboth{#1}{#2}
                }

                \begin{document}
                \renewcommand{\arraystretch}{1.5}
                '''
            client = clients.donnees[code_client]
            nature = generaux.nature_client_par_code_n(client['type_labo'])
            reference = nature + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
            if edition.version != "0":
                reference += "-" + edition.version

            contenu += r'''
                \begin{titlepage}
                \vspace*{8cm}
                \begin{adjustwidth}{5cm}{}
                \Large\textsc{''' + garde + r'''}\newline
                \Large\textsc{''' + reference + r'''}\newline\newline\newline
                '''

            dic_entete = {'code': code_client, 'code_sap': Latex.echappe_caracteres(client['code_sap']),
                          'nom': Latex.echappe_caracteres(client['abrev_labo']),
                          'date': edition.mois_txt + " " + str(edition.annee)}

            contenu += r'''Client %(code)s -  %(code_sap)s -  %(nom)s \newline
                 %(date)s
                \end{adjustwidth}
                \end{titlepage}''' % dic_entete
            contenu += Annexes.contenu_client(sommes, clients, code_client, edition, livraisons, acces, machines,
                                              reservations, comptes, generaux, users, couts)
            contenu += r'''\end{document}'''

            nom = prefixe + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_"
            nom += str(edition.version) + "_" + code_client

            Latex.creer_latex_pdf(nom, contenu, dossier_annexe)

    @staticmethod
    def contenu_client(sommes, clients, code_client, edition, livraisons, acces, machines, reservations, comptes,
                       generaux, users, couts):
        """
        création du contenu de l'annexe pour un client
        :param sommes: sommes calculées
        :param clients: clients importés
        :param code_client: code du client pour l'annexe
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param acces: accès importés
        :param machines: machines importées
        :param reservations: réservations importées
        :param comptes: comptes importés
        :param generaux: paramètres généraux
        :param users: users importés
        :param couts: catégories coûts importées
        :return: contenu de l'annexe du client
        """

        contenu = ""

        scl = sommes.sommes_clients[code_client]
        client = clients.donnees[code_client]
        nature = Latex.echappe_caracteres(generaux.nature_client_par_code_n(client['type_labo']))
        av_ds = Latex.echappe_caracteres(generaux.avantage_ds_par_code_n(client['type_labo']))
        av_hc = Latex.echappe_caracteres(generaux.avantage_hc_par_code_n(client['type_labo']))
        an_couts = Latex.echappe_caracteres(generaux.annexe_cout_par_code_n(client['type_labo']))
        reference = nature + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
        if edition.version != "0":
            reference += "-" + edition.version

        filtre = generaux.filtrer_article_nul_par_code_n(client['type_labo'])

        contenu_bonus_compte = ""
        contenu_procedes_compte = ""
        contenu_recap_compte = ""
        contenu_fact_compte = ""
        inc_fact = 1

        contenu_prestations_client_tab = {}
        for article in generaux.articles_d3:
            contenu_prestations_client_tab[article.code_d] = ""

        titre_5 = "Justificatif des coûts d'utilisation par compte"
        nombre_5 = "V"
        titre_4 = "Annexe détaillée par compte"
        nombre_4 = "IV"
        titre_2 = "Récapitulatifs par compte"
        nombre_2 = "II"
        contenu_compte_annexe2 = ""
        contenu_compte_annexe4 = ""
        contenu_compte_annexe5 = ""

        if code_client in sommes.sommes_comptes:
            comptes_utilises = Outils.comptes_in_somme(sommes.sommes_comptes[code_client], comptes)

            for num_compte, id_compte in sorted(comptes_utilises.items()):
                num_compte = Latex.echappe_caracteres(num_compte)
                id_compte = Latex.echappe_caracteres(id_compte)

                # ## COMPTE

                sco = sommes.sommes_comptes[code_client][id_compte]
                compte = comptes.donnees[id_compte]
                intitule_compte = Latex.echappe_caracteres(compte['numero'] + " - " + compte['intitule'])

                titre2 = "Récapitulatif du compte : " + intitule_compte
                contenu_compte_annexe2 += Annexes.section(code_client, client, edition, reference, titre2, nombre_2)

                titre4 = "Annexe détaillée du compte : " + intitule_compte
                contenu_compte_annexe4 += Annexes.section(code_client, client, edition, reference, titre4, nombre_4)

                titre5 = "Justificatif des coûts d'utilisation du compte : " + intitule_compte
                contenu_compte_annexe5 += Annexes.section(code_client, client, edition, reference, titre5, nombre_5)

                # ## ligne 1.1

                if sco['c1'] > 0 and not (filtre == "OUI" and sco['c2'] == 0):
                    poste = inc_fact * 10
                    intitule = Latex.echappe_caracteres(intitule_compte + " - " + generaux.articles[2].intitule_long)

                    if sco['somme_j_mm'] > 0 and not (filtre == "OUI" and sco['mj'] == 0):
                        dico_fact_compte = {'intitule': intitule, 'poste': str(poste),
                                            'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                            'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                            'mj': Outils.format_2_dec(sco['mj'])}
                        contenu_fact_compte += r'''
                            %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                            \hline
                            ''' % dico_fact_compte
                        poste += 1

                    for article in generaux.articles_d3:
                        categorie = article.code_d
                        if sco['sommes_cat_m'][categorie] > 0 and not (filtre == "OUI"
                                                                       and sco['tot_cat'][article.code_d] == 0):
                            intitule = Latex.echappe_caracteres(intitule_compte + " - " + article.intitule_long)
                            dico_fact_compte = {'intitule': intitule, 'poste': str(poste),
                                                'mm': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                                'mr': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                                'mj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                            contenu_fact_compte += r'''
                                %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                                \hline
                                ''' % dico_fact_compte
                            poste += 1

                    inc_fact += 1

                # ## ligne 1.5

                total = sco['mj']
                dico_recap_compte = {'compte': intitule_compte, 'procede': Outils.format_2_dec(sco['mj'])}

                ligne = r'''%(compte)s & %(procede)s ''' % dico_recap_compte

                for categorie in generaux.codes_d3():
                    total += sco['tot_cat'][categorie]
                    ligne += r''' & ''' + Outils.format_2_dec(sco['tot_cat'][categorie])

                if total > 0:
                    dico_recap_compte['total'] = Outils.format_2_dec(total)
                    ligne += r'''& %(total)s \\
                        \hline
                        ''' % dico_recap_compte
                    contenu_recap_compte += ligne

                # ## 1.6

                rsj = client['rs'] * sco['somme_j_dsi']
                rhj = client['rh'] * sco['somme_j_dhi']
                dico_procedes_compte = {'intitule': intitule_compte, 'maij': Outils.format_2_dec(sco['somme_j_mai']),
                                        'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                        'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                        'rsj': Outils.format_2_dec(rsj), 'rhj': Outils.format_2_dec(rhj),
                                        'moij': Outils.format_2_dec(sco['somme_j_moi']),
                                        'mj': Outils.format_2_dec(sco['mj'])}
                contenu_procedes_compte += r'''
                    %(intitule)s & %(maij)s & %(moij)s & %(rsj)s & %(rhj)s & %(mm)s & %(mr)s & %(mj)s \\
                    \hline
                    ''' % dico_procedes_compte

                # ## ligne 1.7

                if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                    for article in generaux.articles_d3:
                        if article.code_d in livraisons.sommes[code_client][id_compte]:
                            if contenu_prestations_client_tab[article.code_d] == "":
                                contenu_prestations_client_tab[article.code_d] = r'''
                                    \cline{2-4}
                                    \multicolumn{1}{c}{} & \multicolumn{3}{|c|}{
                                    ''' + Latex.echappe_caracteres(article.intitule_long) + r'''} \\
                                    \hline
                                    Compte & Montant & Rabais & Montant net \\
                                    \hline
                                    '''
                            dico_prestations_client = {'intitule': intitule_compte,
                                                       'cmj': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                                       'crj': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                                       'cj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                            contenu_prestations_client_tab[article.code_d] += r'''
                            %(intitule)s & %(cmj)s & %(crj)s & %(cj)s \\
                            \hline
                            ''' % dico_prestations_client

                # ## ligne 1.8

                if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:
                    bsj = client['bs'] * sco['somme_j_dsi']
                    bhj = client['bh'] * sco['somme_j_dhi']
                    dico_bonus_compte = {'compte': intitule_compte, 'bsj': Outils.format_2_dec(bsj),
                                         'bhj': Outils.format_2_dec(bhj), 'tot': Outils.format_2_dec(sco['somme_j_mb'])}
                    contenu_bonus_compte += r'''
                        %(compte)s & %(bsj)s & %(bhj)s & %(tot)s \\
                        \hline
                        ''' % dico_bonus_compte

                # ## 2.1

                structure_recap_poste = r'''{|l|r|r|r|}'''
                legende_recap_poste = r'''Table II.1 - Récapitulatif du compte'''

                dico_recap_poste = {'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                    'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                    'maij': Outils.format_2_dec(sco['somme_j_mai']),
                                    'dsij': Outils.format_2_dec(sco['somme_j_dsi']),
                                    'dhij': Outils.format_2_dec(sco['somme_j_dhi']),
                                    'mj': Outils.format_2_dec(sco['mj']),
                                    'nmij': Outils.format_2_dec((sco['somme_j_mai']-sco['somme_j_mr'])),
                                    'moij': Outils.format_2_dec(sco['somme_j_moi']),
                                    'int_proc': Latex.echappe_caracteres(generaux.articles[2].intitule_long)}

                contenu_recap_poste = r'''
                    \cline{2-4}
                    \multicolumn{1}{r|}{} & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
                    & \multicolumn{1}{c|}{Net} \\
                    \hline
                    %(int_proc)s & %(mm)s & %(mr)s & %(mj)s \\
                    \hline
                    \hspace{5mm} \textit{Machine} & \textit{%(maij)s} \hspace{5mm} & \textit{%(mr)s} \hspace{5mm}
                    & \textit{%(nmij)s} \hspace{5mm} \\
                    \hline
                    \hspace{5mm} \textit{Main d'oeuvre opérateur} & \textit{%(moij)s} \hspace{5mm} &
                    & \textit{%(moij)s} \hspace{5mm} \\
                    \hline
                    ''' % dico_recap_poste

                total = sco['mj']
                for article in generaux.articles_d3:
                    total += sco['tot_cat'][article.code_d]
                    dico_recap_poste = {'intitule': Latex.echappe_caracteres(article.intitule_long),
                                        'cmj': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                        'crj': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                        'cj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                    contenu_recap_poste += r'''
                    %(intitule)s & %(cmj)s & %(crj)s & %(cj)s \\
                    \hline
                    ''' % dico_recap_poste

                contenu_recap_poste += r'''\multicolumn{3}{|r|}{Total} & ''' + Outils.format_2_dec(total) + r'''\\
                    \hline
                    '''

                contenu_compte_annexe2 += Latex.tableau(contenu_recap_poste, structure_recap_poste, legende_recap_poste)

                # ## 2.2

                if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:
                    structure_utilise_compte = r'''{|l|c|c|c|r|r|r|r|r|r|}'''
                    legende_utilise_compte = r'''Table II.2 - Procédés (machine + main d'oeuvre)'''

                    contenu_utilise_compte = r'''
                        \cline{3-10}
                        \multicolumn{2}{c}{} & \multicolumn{2}{|c|}{Machine} & \multicolumn{2}{c|}{PU [CHF/h]}
                        & \multicolumn{2}{c|}{Montant [CHF]} & \multicolumn{1}{c|}{Déduc. Sp.}
                        & \multicolumn{1}{c|}{Déduc. HC} \\
                        \hline
                        \multicolumn{2}{|l|}{\textbf{''' + intitule_compte + r'''}} & Mach. & Oper.
                        & \multicolumn{1}{c|}{Mach.} & \multicolumn{1}{c|}{Oper.} & \multicolumn{1}{c|}{Mach.}
                        & \multicolumn{1}{c|}{Oper.} & \multicolumn{1}{c|}{''' + av_ds + r'''}
                        & \multicolumn{1}{c|}{''' + av_hc + r'''} \\
                        \hline
                        '''

                    somme = acces.sommes[code_client]['comptes'][id_compte]

                    machines_utilisees = Outils.machines_in_somme(somme, machines)

                    for id_cout, mics in sorted(machines_utilisees.items()):
                        for nom, id_machine in sorted(mics.items()):
                            dico_machine = {'machine': Latex.echappe_caracteres(nom),
                                            'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                            'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                            'mo_hp': Outils.format_heure(somme[id_machine]['mo_hp']),
                                            'mo_hc': Outils.format_heure(somme[id_machine]['mo_hc']),
                                            'pu_m': Outils.format_2_dec(somme[id_machine]['pum']),
                                            'puo_hp': Outils.format_2_dec(somme[id_machine]['puo_hp']),
                                            'puo_hc': Outils.format_2_dec(somme[id_machine]['puo_hc']),
                                            'mai_hp': Outils.format_2_dec(somme[id_machine]['mai_hp']),
                                            'mai_hc': Outils.format_2_dec(somme[id_machine]['mai_hc']),
                                            'moi_hp': Outils.format_2_dec(somme[id_machine]['moi_hp']),
                                            'moi_hc': Outils.format_2_dec(somme[id_machine]['moi_hc']),
                                            'dsi_hp': Outils.format_2_dec(somme[id_machine]['dsi_hp']),
                                            'dsi_hc': Outils.format_2_dec(somme[id_machine]['dsi_hc']),
                                            'dhi': Outils.format_2_dec(somme[id_machine]['dhi'])}

                            if somme[id_machine]['duree_hp'] > 0 or somme[id_machine]['mo_hp'] > 0:
                                contenu_utilise_compte += r'''
                                    %(machine)s & HP & %(hp)s & %(mo_hp)s & %(pu_m)s & %(puo_hp)s & %(mai_hp)s
                                    & %(moi_hp)s & %(dsi_hp)s & \\
                                    \hline
                                    ''' % dico_machine

                            if somme[id_machine]['duree_hc'] > 0 or somme[id_machine]['mo_hc'] > 0:
                                contenu_utilise_compte += r'''
                                    %(machine)s & HC & %(hc)s & %(mo_hc)s & %(pu_m)s & %(puo_hc)s & %(mai_hc)s
                                    & %(moi_hc)s & %(dsi_hc)s & %(dhi)s \\
                                    \hline
                                    ''' % dico_machine

                    dico_tot = {'maij_d': Outils.format_2_dec(sco['somme_j_mai_d']),
                                'moij_d': Outils.format_2_dec(sco['somme_j_moi_d']),
                                'dsij_d': Outils.format_2_dec(sco['somme_j_dsi_d']),
                                'dhij_d': Outils.format_2_dec(sco['somme_j_dhi_d']),
                                'maij': Outils.format_2_dec(sco['somme_j_mai']),
                                'moij': Outils.format_2_dec(sco['somme_j_moi']),
                                'dsij': Outils.format_2_dec(sco['somme_j_dsi']),
                                'dhij': Outils.format_2_dec(sco['somme_j_dhi']),
                                'rabais': Outils.format_2_dec(sco['somme_j_mr']),
                                'bonus': Outils.format_2_dec(sco['somme_j_mb'])}
                    contenu_utilise_compte += r'''
                        \multicolumn{6}{|r|}{Arrondi} & %(maij_d)s & %(moij_d)s & %(dsij_d)s & %(dhij_d)s \\
                        \hline
                        \multicolumn{6}{|r|}{Total} & %(maij)s & %(moij)s & %(dsij)s & %(dhij)s \\
                        \hline
                        ''' % dico_tot
                    if av_ds == "RABAIS" or av_hc == "RABAIS":
                        contenu_utilise_compte += r'''
                            \multicolumn{6}{r}{} & \multicolumn{2}{|r|}{Rabais total}
                            & \multicolumn{2}{r|}{%(rabais)s} \\
                            \cline{7-10}
                            ''' % dico_tot
                    if av_ds == "BONUS" or av_hc == "BONUS":
                        contenu_utilise_compte += r'''
                            \multicolumn{6}{r}{} & \multicolumn{2}{|r|}{Bonus total} & \multicolumn{2}{r|}{%(bonus)s} \\
                            \cline{7-10}
                            ''' % dico_tot

                    contenu_compte_annexe2 += Latex.tableau(contenu_utilise_compte, structure_utilise_compte,
                                                            legende_utilise_compte)
                else:
                    contenu_compte_annexe2 += Latex.tableau_vide(r'''Table II.2 - Procédés (machine + main d'oeuvre) :
                        table vide (pas d’utilisation machines)''')

                # ## 2.3

                if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                    somme = livraisons.sommes[code_client][id_compte]
                    structure_prests_compte = r'''{|l|r|c|r|r|r|}'''
                    legende_prests_compte = r'''Table II.3 - Prestations livrées'''
                    contenu_prests_compte = ""
                    for article in generaux.articles_d3:
                        if article.code_d in somme:
                            if contenu_prests_compte != "":
                                contenu_prests_compte += r'''
                                    \multicolumn{6}{c}{} \\
                                    '''

                            contenu_prests_compte += r'''
                                \hline
                                \multicolumn{1}{|l|}{
                                \textbf{''' + intitule_compte + " - " + \
                                                     Latex.echappe_caracteres(article.intitule_long) + r'''
                                }} & \multicolumn{1}{c|}{Quantité} & Unité & \multicolumn{1}{c|}{P.U.}
                                & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais} \\
                                \hline
                                '''
                            for no_prestation, sip in sorted(somme[article.code_d].items()):
                                dico_prestations = {'nom': Latex.echappe_caracteres(sip['nom']),
                                                    'num': no_prestation,
                                                    'quantite': "%.1f" % sip['quantite'],
                                                    'unite': Latex.echappe_caracteres(sip['unite']),
                                                    'pu': Outils.format_2_dec(sip['pu']),
                                                    'montant': Outils.format_2_dec(sip['montant']),
                                                    'rabais': Outils.format_2_dec(sip['rabais'])}
                                contenu_prests_compte += r'''
                                    %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s & %(pu)s & %(montant)s
                                    & %(rabais)s  \\
                                    \hline
                                    ''' % dico_prestations
                            dico_prestations = {'montant_d': Outils.format_2_dec(sco['sommes_cat_m_d'][article.code_d]),
                                                'rabais_d': Outils.format_2_dec(sco['sommes_cat_r_d'][article.code_d]),
                                                'montant': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                                'rabais': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d])}
                            contenu_prests_compte += r'''
                                \multicolumn{4}{|r|}{Arrondi} & %(montant_d)s & %(rabais_d)s  \\
                                \hline
                                \multicolumn{4}{|r|}{Total} & %(montant)s & %(rabais)s  \\
                                \hline
                                ''' % dico_prestations
                    contenu_compte_annexe2 += Latex.tableau(contenu_prests_compte, structure_prests_compte,
                                                            legende_prests_compte)
                else:
                    contenu_compte_annexe2 += Latex.tableau_vide(r'''Table II.3 - Prestations livrées :
                        table vide (pas de prestations livrées)''')

                # ## 4.1

                if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:

                    structure_machuts_compte = r'''{|l|l|l|c|c|c|c|}'''
                    legende_machuts_compte = r'''Table IV.1 - Détails des utilisations machines'''

                    contenu_machuts_compte = r'''
                        \hline
                        \multicolumn{3}{|l|}{\multirow{2}{*}{\scriptsize{\textbf{''' + intitule_compte + r'''}}}}
                        & \multicolumn{2}{c|}{Machine} & \multicolumn{2}{c|}{Main d'oeuvre} \\
                        \cline{4-7}
                        \multicolumn{3}{|l|}{} & HP & HC & HP & HC \\
                        \hline
                        '''

                    somme = acces.sommes[code_client]['comptes'][id_compte]

                    machines_utilisees = Outils.machines_in_somme(somme, machines)

                    for id_cout, mics in sorted(machines_utilisees.items()):
                        for nom_machine, id_machine in sorted(mics.items()):

                            dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                            'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                            'hc': Outils.format_heure(somme[id_machine]['duree_hc']),
                                            'mo_hp': Outils.format_heure(somme[id_machine]['mo_hp']),
                                            'mo_hc': Outils.format_heure(somme[id_machine]['mo_hc'])}
                            contenu_machuts_compte += r'''
                                \multicolumn{3}{|l|}{\textbf{%(machine)s}} & \hspace{5mm} %(hp)s & \hspace{5mm} %(hc)s &
                                 \hspace{5mm} %(mo_hp)s & \hspace{5mm} %(mo_hc)s \\
                                \hline
                                ''' % dico_machine

                            utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                            for nom, upi in sorted(utilisateurs.items()):
                                for prenom, ids in sorted(upi.items()):
                                    for id_user in sorted(ids):
                                        smu = somme[id_machine]['users'][id_user]
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hp': Outils.format_heure(smu['duree_hp']),
                                                     'hc': Outils.format_heure(smu['duree_hc']),
                                                     'mo_hp': Outils.format_heure(smu['mo_hp']),
                                                     'mo_hc': Outils.format_heure(smu['mo_hc'])}
                                        contenu_machuts_compte += r'''
                                            \multicolumn{3}{|l|}{\hspace{5mm} %(user)s} & %(hp)s & %(hc)s & %(mo_hp)s
                                            & %(mo_hc)s \\
                                            \hline
                                        ''' % dico_user
                                        for p1 in smu['data']:
                                            cae = acces.donnees[p1]
                                            login = Latex.echappe_caracteres(cae['date_login']).split()
                                            temps = login[0].split('-')
                                            date = temps[0]
                                            for p2 in range(1, len(temps)):
                                                date = temps[p2] + '.' + date
                                            if len(login) > 1:
                                                heure = login[1]
                                            else:
                                                heure = ""

                                            rem = ""
                                            if id_user != cae['id_op']:
                                                rem += "op : " + cae['nom_op']
                                            if cae['remarque_op'] != "":
                                                if rem != "":
                                                    rem += "; "
                                                rem += "rem op : " + cae['remarque_op']
                                            if cae['remarque_staff'] != "":
                                                if rem != "":
                                                    rem += "; "
                                                rem += "rem CMi : " + cae['remarque_staff']

                                            dico_pos = {'date': date, 'heure': heure,
                                                        'rem': Latex.echappe_caracteres(rem),
                                                        'hp': Outils.format_heure(cae['duree_machine_hp']),
                                                        'hc': Outils.format_heure(cae['duree_machine_hc']),
                                                        'mo_hp': Outils.format_heure(cae['duree_operateur_hp']),
                                                        'mo_hc': Outils.format_heure(cae['duree_operateur_hc'])}
                                            contenu_machuts_compte += r'''
                                                \hspace{10mm} %(date)s & %(heure)s & \parbox{5cm}{%(rem)s}
                                                & %(hp)s \hspace{5mm} & %(hc)s \hspace{5mm} & %(mo_hp)s \hspace{5mm}
                                                & %(mo_hc)s \hspace{5mm} \\
                                                \hline
                                            ''' % dico_pos

                    contenu_compte_annexe4 += Latex.long_tableau(contenu_machuts_compte, structure_machuts_compte,
                                                                 legende_machuts_compte)
                else:
                    contenu_compte_annexe4 += Latex.tableau_vide(r'''Table IV.1 - Détails des utilisations machines :
                        table vide (pas d’utilisation machines)''')

                # ## 4.2

                if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                    somme = livraisons.sommes[code_client][id_compte]

                    structure_prestations_compte = r'''{|l|c|c|c|}'''
                    legende_prestations_compte = r'''Table IV.2 - Détails des prestations livrées'''

                    contenu_prestations_compte = r'''
                        '''

                    i = 0
                    for article in generaux.articles_d3:
                        if article.code_d in somme:
                            if i == 0:
                                i += 1
                            else:
                                contenu_prestations_compte += r'''\multicolumn{4}{c}{} \\
                                    '''
                            contenu_prestations_compte += r'''
                                \hline
                                \multicolumn{1}{|l|}{
                                \textbf{''' + intitule_compte + " - " + \
                                                          Latex.echappe_caracteres(article.intitule_long) + r'''
                                }} & Quantité & Unité & Rabais \\
                                \hline
                                '''
                            for no_prestation, sip in sorted(somme[article.code_d].items()):
                                dico_prestations = {'nom': Latex.echappe_caracteres(sip['nom']),
                                                    'num': no_prestation,
                                                    'quantite': "%.1f" % sip['quantite'],
                                                    'unite': Latex.echappe_caracteres(sip['unite']),
                                                    'rabais': Outils.format_2_dec(sip['rabais'])}
                                contenu_prestations_compte += r'''
                                    %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s
                                    & \hspace{5mm} %(rabais)s \\
                                    \hline
                                    ''' % dico_prestations

                                utilisateurs = Outils.utilisateurs_in_somme(sip['users'], users)

                                for nom, upi in sorted(utilisateurs.items()):
                                    for prenom, ids in sorted(upi.items()):
                                        for id_user in sorted(ids):
                                            spu = sip['users'][id_user]
                                            dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                         'quantite': "%.1f" % spu['quantite'],
                                                         'unite': Latex.echappe_caracteres(sip['unite']),
                                                         'rabais': Outils.format_2_dec(spu['rabais'])}
                                            contenu_prestations_compte += r'''
                                                \hspace{5mm} %(user)s & %(quantite)s & %(unite)s & %(rabais)s \\
                                                \hline
                                            ''' % dico_user

                                            for pos in spu['data']:
                                                liv = livraisons.donnees[pos]
                                                rem = ""
                                                dl = ""
                                                if liv['remarque'] != "":
                                                    rem = "; Remarque : " + liv['remarque']
                                                if liv['date_livraison'] != "":
                                                    dl = "Dt livraison: " + liv['date_livraison'] + ";"
                                                dico_pos = {'date_liv': Latex.echappe_caracteres(dl),
                                                            'quantite': "%.1f" % liv['quantite'],
                                                            'rabais': Outils.format_2_dec(liv['rabais_r']),
                                                            'id': Latex.echappe_caracteres(liv['id_livraison']),
                                                            'unite': Latex.echappe_caracteres(sip['unite']),
                                                            'responsable': Latex.echappe_caracteres(liv['responsable']),
                                                            'commande': Latex.echappe_caracteres(liv['date_commande']),
                                                            'remarque': Latex.echappe_caracteres(rem)}
                                                contenu_prestations_compte += r'''
                                                    \hspace{10mm} %(date_liv)s N. livraison: %(id)s
                                                    & %(quantite)s \hspace{5mm} & %(unite)s & %(rabais)s \hspace{5mm} \\

                                                    \hspace{10mm} \scalebox{.8}{Commande: %(commande)s;
                                                    Resp: %(responsable)s%(remarque)s} & & & \\
                                                    \hline
                                                ''' % dico_pos

                    contenu_compte_annexe4 += Latex.long_tableau(contenu_prestations_compte,
                                                                 structure_prestations_compte,
                                                                 legende_prestations_compte)

                # ## 5.1

                structure_eligibles_compte = r'''{|l|r|r|r|}'''
                legende_eligibles_compte = r'''Table V.1 - Coûts d'utilisation '''

                dico_eligibles = {'mu1': Outils.format_2_dec(sco['mu1']),
                                  'mu2': Outils.format_2_dec(sco['mu2']),
                                  'mu3': Outils.format_2_dec(sco['mu3']),
                                  'mmo': Outils.format_2_dec(sco['mmo'])}
                tot1 = sco['mu1'] + sco['mmo']
                tot2 = sco['mu2'] + sco['mmo']
                tot3 = sco['mu3'] + sco['mmo']

                contenu_eligibles_compte = r'''
                    \cline{2-4}
                    \multicolumn{1}{l|}{} & \multicolumn{1}{c|}{1} & \multicolumn{1}{c|}{2} & \multicolumn{1}{c|}{3} \\
                    \hline
                    Coûts d'utilisation machine & %(mu1)s & %(mu2)s & %(mu3)s \\
                    \hline
                    Coûts main d'oeuvre opérateur & %(mmo)s & %(mmo)s & %(mmo)s \\
                    \hline
                    ''' % dico_eligibles

                if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                    somme = livraisons.sommes[code_client][id_compte]
                    for article in generaux.articles_d3:
                        if article.code_d in somme:
                            elu1 = article.eligible_U1
                            elu2 = article.eligible_U2
                            elu3 = article.eligible_U3
                            if elu1 == "NON" and elu2 == "NON" and elu3 == "NON":
                                continue
                            netx = sco['tot_cat_x'][article.code_d]
                            u1 = 0
                            u2 = 0
                            u3 = 0
                            if elu1 == "OUI":
                                u1 = netx
                            if elu2 == "OUI":
                                u2 = netx
                            if elu3 == "OUI":
                                u3 = netx
                            tot1 += u1
                            tot2 += u2
                            tot3 += u3
                            dico_article = {'intitule': Latex.echappe_caracteres(article.intitule_long),
                                            'u1': Outils.format_2_dec(u1),
                                            'u2': Outils.format_2_dec(u2), 'u3': Outils.format_2_dec(u3)}
                            contenu_eligibles_compte += r'''
                                %(intitule)s & %(u1)s & %(u2)s & %(u3)s \\
                                \hline
                                ''' % dico_article

                dico_tot = {'tot1': Outils.format_2_dec(tot1), 'tot2': Outils.format_2_dec(tot2),
                            'tot3': Outils.format_2_dec(tot3)}
                contenu_eligibles_compte += r'''
                    \multicolumn{1}{|r|}{Total} & %(tot1)s & %(tot2)s & %(tot3)s \\
                    \hline
                    ''' % dico_tot

                contenu_compte_annexe5 += Latex.tableau(contenu_eligibles_compte, structure_eligibles_compte,
                                                        legende_eligibles_compte)

                # ## 5.2

                if code_client in acces.sommes and id_compte in acces.sommes[code_client]['categories']:
                    structure_coutmachines_compte = r'''{|l|r|r|r|r|}'''
                    legende_coutmachines_compte = r'''Table V.2 - Coûts d'utilisation des machines et main d'oeuvre'''
                    contenu_coutmachines_compte = r'''
                            \hline
                            \multirow{2}{*}{\textbf{''' + intitule_compte + r'''}}
                            & \multicolumn{4}{c|}{Montant [CHF]} \\
                            \cline{2-5}
                             & \multicolumn{1}{c|}{U1} & \multicolumn{1}{c|}{U2} & \multicolumn{1}{c|}{U3}
                             & \multicolumn{1}{c|}{M.O. Oper.} \\
                            \hline
                            '''

                    som_cats = acces.sommes[code_client]['categories'][id_compte]

                    for id_cout, som_cat in sorted(som_cats.items()):

                        dico_cat = {'intitule': Latex.echappe_caracteres(couts.donnees[id_cout]['intitule']),
                                    'mu1': Outils.format_2_dec(som_cat['mu1']),
                                    'mu2': Outils.format_2_dec(som_cat['mu2']),
                                    'mu3': Outils.format_2_dec(som_cat['mu3']),
                                    'mmo': Outils.format_2_dec(som_cat['mmo'])}

                        contenu_coutmachines_compte += r'''
                            %(intitule)s & %(mu1)s & %(mu2)s & %(mu3)s & %(mmo)s \\
                            \hline
                            ''' % dico_cat

                    dico_compte = {'mu1_d': Outils.format_2_dec(sco['mu1_d']),
                                   'mu2_d': Outils.format_2_dec(sco['mu2_d']),
                                   'mu3_d': Outils.format_2_dec(sco['mu3_d']),
                                   'mmo_d': Outils.format_2_dec(sco['mmo_d']),
                                   'mu1': Outils.format_2_dec(sco['mu1']),
                                   'mu2': Outils.format_2_dec(sco['mu2']),
                                   'mu3': Outils.format_2_dec(sco['mu3']),
                                   'mmo': Outils.format_2_dec(sco['mmo'])}

                    contenu_coutmachines_compte += r'''
                        \multicolumn{1}{|r|}{Arrondi} & %(mu1_d)s & %(mu2_d)s & %(mu3_d)s & %(mmo_d)s \\
                        \hline
                        \multicolumn{1}{|r|}{Total} & %(mu1)s & %(mu2)s & %(mu3)s & %(mmo)s \\
                        \hline
                        ''' % dico_compte

                    contenu_compte_annexe5 += Latex.tableau(contenu_coutmachines_compte, structure_coutmachines_compte,
                                                            legende_coutmachines_compte)

                else:
                    contenu_compte_annexe5 += Latex.tableau_vide(r'''Table V.2 - Coûts d'utilisation des machines et
                        main d'oeuvre : table vide (pas d’utilisation machines)''')

                # ## 5.3

                if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:
                    structure_coutcats_compte = r'''{|l|c|c|r|r|r|r|r|r|r|r|}'''
                    legende_coutcats_compte = r'''Table V.3 - Coûts d'utilisation des machines et main d'oeuvre par
                        catégorie'''
                    contenu_coutcats_compte = ""

                    somme = acces.sommes[code_client]['comptes'][id_compte]
                    som_cat = acces.sommes[code_client]['categories'][id_compte]
                    machines_utilisees = Outils.machines_in_somme(somme, machines)

                    for id_cout, mics in sorted(machines_utilisees.items()):

                        if contenu_coutcats_compte != "":
                            contenu_coutcats_compte += r'''
                                \multicolumn{7}{c}{} \\
                                '''

                        contenu_coutcats_compte += r'''
                            \hline
                            \textbf{''' + intitule_compte + r'''} & \multicolumn{2}{c|}{Durée}
                            & \multicolumn{4}{c|}{PU [CHF/h]} & \multicolumn{4}{c|}{Montant [CHF]} \\
                            \hline
                            \textbf{''' + Latex.echappe_caracteres(couts.donnees[id_cout]['intitule']) + r'''}
                            & Mach. & Oper. & \multicolumn{1}{c|}{U1} & \multicolumn{1}{c|}{U2}
                            & \multicolumn{1}{c|}{U3} & \multicolumn{1}{c|}{Oper.} & \multicolumn{1}{c|}{U1}
                            & \multicolumn{1}{c|}{U2} & \multicolumn{1}{c|}{U3} & \multicolumn{1}{c|}{Oper.} \\
                            \hline
                            '''

                        for nom_machine, id_machine in sorted(mics.items()):
                            duree = somme[id_machine]['duree_hp'] + somme[id_machine]['duree_hc']
                            mo = somme[id_machine]['mo_hp'] + somme[id_machine]['mo_hc']

                            dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                            'duree': Outils.format_heure(duree), 'mo': Outils.format_heure(mo),
                                            'cu1': Outils.format_2_dec(couts.donnees[id_cout]['u1']),
                                            'cu2': Outils.format_2_dec(couts.donnees[id_cout]['u2']),
                                            'cu3': Outils.format_2_dec(couts.donnees[id_cout]['u3']),
                                            'cmo': Outils.format_2_dec(couts.donnees[id_cout]['mo']),
                                            'mu1': Outils.format_2_dec(somme[id_machine]['mu1']),
                                            'mu2': Outils.format_2_dec(somme[id_machine]['mu2']),
                                            'mu3': Outils.format_2_dec(somme[id_machine]['mu3']),
                                            'mmo': Outils.format_2_dec(somme[id_machine]['mmo'])}
                            contenu_coutcats_compte += r'''
                                %(machine)s & %(duree)s & %(mo)s & %(cu1)s & %(cu2)s & %(cu3)s & %(cmo)s & %(mu1)s
                                & %(mu2)s & %(mu3)s & %(mmo)s \\
                                \hline
                                ''' % dico_machine

                        dico_cat = {'mu1': Outils.format_2_dec(som_cat[id_cout]['mu1']),
                                    'mu2': Outils.format_2_dec(som_cat[id_cout]['mu2']),
                                    'mu3': Outils.format_2_dec(som_cat[id_cout]['mu3']),
                                    'mmo': Outils.format_2_dec(som_cat[id_cout]['mmo'])}

                        contenu_coutcats_compte += r'''
                            \multicolumn{7}{|r|}{Total} & %(mu1)s & %(mu2)s & %(mu3)s & %(mmo)s \\
                            \hline
                            ''' % dico_cat

                    contenu_compte_annexe5 += Latex.long_tableau(contenu_coutcats_compte, structure_coutcats_compte,
                                                                 legende_coutcats_compte)

                else:
                    contenu_compte_annexe5 += Latex.tableau_vide(r'''Table V.3 - Coûts d'utilisation des machines et
                        main d'oeuvre par catégorie : table vide (pas d’utilisation machines)''')

                # ## 5.4

                contenu_coutprests_compte = ""
                structure_coutprests_compte = r'''{|l|r|c|r|r|r|r|}'''
                legende_coutprests_compte = r'''Table V.4 - Coûts des prestations livrées'''
                if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                    somme = livraisons.sommes[code_client][id_compte]
                    for article in generaux.articles_d3:
                        if article.code_d in somme:
                            elu1 = article.eligible_U1
                            elu2 = article.eligible_U2
                            elu3 = article.eligible_U3
                            if elu1 == "NON" and elu2 == "NON" and elu3 == "NON":
                                continue

                            if contenu_coutprests_compte != "":
                                contenu_coutprests_compte += r'''
                                    \multicolumn{7}{c}{} \\
                                    '''

                            contenu_coutprests_compte += r'''
                                \hline
                                \multicolumn{1}{|l|}{
                                \textbf{''' + intitule_compte + " - " + \
                                                         Latex.echappe_caracteres(article.intitule_long) + r'''
                                }} & \multicolumn{1}{c|}{Quantité} & Unité & \multicolumn{1}{c|}{P.U.}
                                & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
                                & \multicolumn{1}{c|}{Net} \\
                                \hline
                                '''
                            for no_prestation, sip in sorted(somme[article.code_d].items()):
                                dico_prestations = {'nom': Latex.echappe_caracteres(sip['nom']),
                                                    'num': no_prestation,
                                                    'quantite': "%.1f" % sip['quantite'],
                                                    'unite': Latex.echappe_caracteres(sip['unite']),
                                                    'pux': Outils.format_2_dec(sip['pux']),
                                                    'montantx': Outils.format_2_dec(sip['montantx']),
                                                    'rabais': Outils.format_2_dec(sip['rabais']),
                                                    'netx': Outils.format_2_dec((sip['montantx'] - sip['rabais']))}
                                contenu_coutprests_compte += r'''
                                    %(num)s - %(nom)s & \hspace{5mm} %(quantite)s & %(unite)s & %(pux)s & %(montantx)s
                                    & %(rabais)s & %(netx)s \\
                                    \hline
                                    ''' % dico_prestations
                            dico_prestations = {
                                'montantx_d': Outils.format_2_dec(sco['sommes_cat_m_x_d'][article.code_d]),
                                'rabais_d': Outils.format_2_dec(sco['sommes_cat_r_d'][article.code_d]),
                                'montantx': Outils.format_2_dec(sco['sommes_cat_m_x'][article.code_d]),
                                'rabais': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                'netx': Outils.format_2_dec(sco['tot_cat_x'][article.code_d])}

                            contenu_coutprests_compte += r'''
                                \multicolumn{4}{|r|}{Arrondi} & %(montantx_d)s & %(rabais_d)s & \\
                                \hline
                                \multicolumn{4}{|r|}{Total} & %(montantx)s & %(rabais)s & %(netx)s \\
                                \hline
                                ''' % dico_prestations
                if contenu_coutprests_compte != "":
                    contenu_compte_annexe5 += Latex.tableau(contenu_coutprests_compte, structure_coutprests_compte,
                                                            legende_coutprests_compte)
                else:
                    contenu_compte_annexe5 += Latex.tableau_vide(r'''Table V.4 - Coûts des prestations livrées :
                        table vide (pas de prestations livrées)''')

                contenu_compte_annexe2 += r'''\clearpage'''
                contenu_compte_annexe4 += r'''\clearpage'''
                contenu_compte_annexe5 += r'''\clearpage'''
                # ## compte

        # ## Début des tableaux

        # ## Annexe 1

        contenu += Annexes.titre_annexe(code_client, client, edition, reference, "Récapitulatif", "I")
        contenu += Annexes.section(code_client, client, edition, reference, "Récapitulatif", "I")

        # ## 1.1

        brut = scl['rm'] + scl['somme_t_mm'] + scl['em']
        for cat, tt in scl['sommes_cat_m'].items():
            brut += tt
        if scl['somme_t'] > 0 or (filtre == "NON" and brut > 0):
            structure_recap_fact = r'''{|c|l|r|r|r|}'''
            legende_recap_fact = r'''Table I.1 - Récapitulatif des postes de la facture'''

            dico_recap_fact = {'emom': Outils.format_2_dec(scl['em']), 'emor': Outils.format_2_dec(scl['er']),
                               'emo': Outils.format_2_dec(scl['e']), 'resm': Outils.format_2_dec(scl['rm']),
                               'resr': Outils.format_2_dec(scl['rr']), 'res': Outils.format_2_dec(scl['r']),
                               'int_emo': Latex.echappe_caracteres(generaux.articles[0].intitule_long),
                               'int_res': Latex.echappe_caracteres(generaux.articles[1].intitule_long),
                               'p_emo': generaux.poste_emolument, 'p_res': generaux.poste_reservation}

            contenu_recap_fact = r'''
                \hline
                N. Poste & Poste & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
                & \multicolumn{1}{c|}{Total} \\
                \hline'''
            if scl['em'] > 0 and not (filtre == "OUI" and scl['e'] == 0):
                contenu_recap_fact += r'''
                    %(p_emo)s & %(int_emo)s & %(emom)s & %(emor)s & %(emo)s \\
                    \hline''' % dico_recap_fact
            if scl['rm'] > 0 and not (filtre == "OUI" and scl['r'] == 0):
                contenu_recap_fact += r'''
                    %(p_res)s & %(int_res)s & %(resm)s & %(resr)s & %(res)s \\
                    \hline
                    ''' % dico_recap_fact

            contenu_recap_fact += contenu_fact_compte

            contenu_recap_fact += r'''\multicolumn{4}{|r|}{Total}
                & ''' + Outils.format_2_dec(scl['somme_t']) + r'''\\
                \hline
                '''
            contenu += Latex.tableau(contenu_recap_fact, structure_recap_fact, legende_recap_fact)
        else:
            contenu += Latex.tableau_vide(r'''Table I.1 - Récapitulatif des postes de la facture :
                table vide (aucun article facturable)''')

        # ## 1.2

        structure_recap_poste_cl = r'''{|l|r|r|r|}'''
        legende_recap_poste_cl = r'''Table I.2 - Récapitulatif des postes'''

        dico_recap_poste_cl = {'emom': Outils.format_2_dec(scl['em']), 'emor': Outils.format_2_dec(scl['er']),
                               'emo': Outils.format_2_dec(scl['e']), 'resm': Outils.format_2_dec(scl['rm']),
                               'resr': Outils.format_2_dec(scl['rr']), 'res': Outils.format_2_dec(scl['r']),
                               'int_emo': Latex.echappe_caracteres(generaux.articles[0].intitule_long),
                               'int_res': Latex.echappe_caracteres(generaux.articles[1].intitule_long),
                               'int_proc': Latex.echappe_caracteres(generaux.articles[2].intitule_long),
                               'mm': Outils.format_2_dec(scl['somme_t_mm']),
                               'mr': Outils.format_2_dec(scl['somme_t_mr']), 'mt': Outils.format_2_dec(scl['mt'])}

        contenu_recap_poste_cl = r'''
            \cline{2-4}
            \multicolumn{1}{l|}{} & \multicolumn{1}{c|}{Montant} & \multicolumn{1}{c|}{Rabais}
            & \multicolumn{1}{c|}{Total} \\
            \hline
            %(int_emo)s & %(emom)s & %(emor)s & %(emo)s \\
            \hline
            %(int_res)s & %(resm)s & %(resr)s & %(res)s \\
            \hline
            %(int_proc)s & %(mm)s & %(mr)s & %(mt)s \\
            \hline
            ''' % dico_recap_poste_cl

        for article in generaux.articles_d3:
            dico_recap_poste_cl = {'intitule': Latex.echappe_caracteres(article.intitule_long),
                                   'mm': Outils.format_2_dec(scl['sommes_cat_m'][article.code_d]),
                                   'mr': Outils.format_2_dec(scl['sommes_cat_r'][article.code_d]),
                                   'mj': Outils.format_2_dec(scl['tot_cat'][article.code_d])}
            contenu_recap_poste_cl += r'''
                %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                \hline
                ''' % dico_recap_poste_cl

        contenu_recap_poste_cl += r'''\multicolumn{3}{|r|}{Total}
            & ''' + Outils.format_2_dec(scl['somme_t']) + r'''\\
            \hline
            '''

        contenu += Latex.tableau(contenu_recap_poste_cl, structure_recap_poste_cl, legende_recap_poste_cl)

        # ## 1.3

        structure_emolument = r'''{|r|r|l|r|r|r|r|r|}'''
        legende_emolument = r'''Table I.3 - Emolument mensuel'''

        dico_emolument = {'emb':  Outils.format_2_dec(client['emol_base_mens']),
                          'ef':  Outils.format_2_dec(client['emol_fixe']),
                          'pente': client['coef'], 'tot_eq_r': Outils.format_2_dec(scl['r']),
                          'tot_eq_m': Outils.format_2_dec(scl['mat']), 'tot_eq': Outils.format_2_dec(scl['somme_eq']),
                          'rabais': Outils.format_2_dec(scl['er']), 'emo': scl['e']}

        contenu_emolument = r'''
            \hline
            \multicolumn{1}{|l|}{Emolument de base} & \multicolumn{1}{l|}{Emolument fixe} & Pente
            & \multicolumn{1}{l|}{Total EQ R} & \multicolumn{1}{l|}{Total EQ M} & \multicolumn{1}{l|}{Total EQ} &
            \multicolumn{1}{l|}{Rabais émolument} & \multicolumn{1}{l|}{Emolument} \\
            \hline
            %(emb)s & %(ef)s & %(pente)s & %(tot_eq_r)s & %(tot_eq_m)s & %(tot_eq)s & %(rabais)s & %(emo)s \\
            \hline
            ''' % dico_emolument

        contenu += Latex.tableau(contenu_emolument, structure_emolument, legende_emolument)

        # ## 1.4

        if code_client in reservations.sommes:
            structure_frais_client = r'''{|l|c|c|r|r|}'''
            legende_frais_client = r'''Table I.4 - Pénalités de réservation'''

            contenu_frais_client = r'''
                \cline{3-5}
                \multicolumn{2}{c|}{} & Pénalités & \multicolumn{1}{c|}{PU} & \multicolumn{1}{c|}{Montant} \\
                \cline{3-5}
                \multicolumn{2}{c|}{} & Durée & \multicolumn{1}{c|}{CHF/h} & \multicolumn{1}{c|}{CHF} \\
                \hline
                '''

            machines_utilisees = Outils.machines_in_somme(scl['res'], machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    re_somme = reservations.sommes[code_client][id_machine]

                    tot_hp = scl['res'][id_machine]['tot_hp']
                    tot_hc = scl['res'][id_machine]['tot_hc']

                    dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                    'pu_hp': Outils.format_2_dec(re_somme['pu_hp']),
                                    'pu_hc': Outils.format_2_dec(re_somme['pu_hc']),
                                    'mont_hp': Outils.format_2_dec(scl['res'][id_machine]['mont_hp']),
                                    'mont_hc': Outils.format_2_dec(scl['res'][id_machine]['mont_hc']),
                                    'tot_hp': Outils.format_heure(tot_hp), 'tot_hc': Outils.format_heure(tot_hc)}

                    if tot_hp > 0:
                        contenu_frais_client += r'''%(machine)s & HP & %(tot_hp)s & %(pu_hp)s & %(mont_hp)s \\
                             \hline
                             ''' % dico_machine

                    if tot_hc > 0:
                        contenu_frais_client += r'''%(machine)s & HC & %(tot_hc)s & %(pu_hc)s & %(mont_hc)s \\
                             \hline
                             ''' % dico_machine

            dico_frais = {'rm': Outils.format_2_dec(scl['rm']), 'rm_d': Outils.format_2_dec(scl['rm_d']),
                          'r': Outils.format_2_dec(scl['r']), 'rr': Outils.format_2_dec(scl['rr'])}
            contenu_frais_client += r'''
                \multicolumn{4}{|r|}{Arrondi} & %(rm_d)s \\
                \hline
                \multicolumn{4}{|r|}{Total} & %(rm)s \\
                \hline
                \multicolumn{4}{|r|}{Rabais} & %(rr)s \\
                \hline
                \multicolumn{4}{|r|}{\textbf{Total à payer}} & \textbf{%(r)s} \\
                \hline
                ''' % dico_frais

            contenu += Latex.tableau(contenu_frais_client, structure_frais_client, legende_frais_client)
        else:
            contenu += Latex.tableau_vide(r'''Table I.4 - Pénalités de réservation :
                table vide (pas de pénalités de réservation)''')

        # ## 1.5

        legende_recap = r'''Table I.5 - Récapitulatif des comptes'''

        structure_recap = r'''{|l|r|r|'''
        contenu_recap = r'''
            \hline
            Compte & \multicolumn{1}{c|}{Procédés}'''

        for article in generaux.articles_d3:
            structure_recap += r'''r|'''
            contenu_recap += r''' & \multicolumn{1}{c|}{
            ''' + Latex.echappe_caracteres(article.intitule_court) + r'''}'''
        structure_recap += r'''}'''
        contenu_recap += r'''& \multicolumn{1}{c|}{Total} \\
            \hline
            '''

        contenu_recap += contenu_recap_compte

        dico_recap = {'procedes': Outils.format_2_dec(scl['mt']),
                      'total': Outils.format_2_dec((scl['somme_t']-scl['r']-scl['e']))}

        contenu_recap += r'''Total article & %(procedes)s''' % dico_recap

        for categorie in generaux.codes_d3():
            contenu_recap += r''' & ''' + Outils.format_2_dec(scl['tot_cat'][categorie])

        contenu_recap += r'''& %(total)s \\
            \hline
            ''' % dico_recap

        contenu += Latex.tableau(contenu_recap, structure_recap, legende_recap)

        # ## 1.6

        if code_client in acces.sommes:
            structure_procedes_client = r'''{|l|r|r|r|r|r|r|r|}'''
            legende_procedes_client = r'''Table I.6 - Récapitulatif des procédés'''

            contenu_procedes_client = r'''
                \cline{2-8}
                \multicolumn{1}{c}{} & \multicolumn{2}{|c|}{Procédés} & \multicolumn{2}{c|}{Rabais}
                & \multicolumn{2}{c|}{Facture} & Montant \\
                \cline{1-7}
                Compte & Machine & M.O. opér. & Déduc. Sp. & Déduc. HC & Montant & Rabais & \multicolumn{1}{c|}{net} \\
                \hline
                '''

            contenu_procedes_client += contenu_procedes_compte

            rst = client['rs'] * scl['dst']
            rht = client['rh'] * scl['dht']
            dico_procedes_client = {'mat': Outils.format_2_dec(scl['mat']),
                                    'mr': Outils.format_2_dec(scl['somme_t_mr']),
                                    'mm': Outils.format_2_dec(scl['somme_t_mm']),
                                    'mot': Outils.format_2_dec(scl['mot']),
                                    'mt': Outils.format_2_dec(scl['mt']),
                                    'rst': Outils.format_2_dec(rst), 'rht': Outils.format_2_dec(rht)}
            contenu_procedes_client += r'''
                Total & %(mat)s & %(mot)s & %(rst)s & %(rht)s & %(mm)s & %(mr)s & %(mt)s \\
                \hline
                ''' % dico_procedes_client

            contenu += Latex.tableau(contenu_procedes_client, structure_procedes_client, legende_procedes_client)
        else:
            contenu += Latex.tableau_vide(r'''Table I.6 - Récapitulatif des procédés :
                table vide (pas d'utilisations machines)''')

        # ## 1.7

        if code_client in livraisons.sommes:
            structure_prestations_client_recap = r'''{|l|r|r|r|}'''
            legende_prestations_client_recap = r'''Table I.7 - Récapitulatif des prestations livrées'''

            contenu_prestations_client_recap = ""
            i = 0
            for article in generaux.articles_d3:
                if contenu_prestations_client_tab[article.code_d] != "":
                    dico_prestations_client = {'cmt': Outils.format_2_dec(scl['sommes_cat_m'][article.code_d]),
                                               'crt': Outils.format_2_dec(scl['sommes_cat_r'][article.code_d]),
                                               'ct': Outils.format_2_dec(scl['tot_cat'][article.code_d])}
                    contenu_prestations_client_tab[article.code_d] += r'''
                    Total & %(cmt)s & %(crt)s & %(ct)s \\
                    \hline
                    ''' % dico_prestations_client
                    if i == 0:
                        i += 1
                    else:
                        contenu_prestations_client_recap += r'''\multicolumn{4}{c}{} \\'''
                    contenu_prestations_client_recap += contenu_prestations_client_tab[article.code_d]

            contenu += Latex.tableau(contenu_prestations_client_recap, structure_prestations_client_recap,
                                     legende_prestations_client_recap)

        else:
            contenu += Latex.tableau_vide(r'''Table I.7 - Récapitulatif des prestations livrées :
                table vide (pas de prestations livrées)''')

        # ## 1.8

        if av_ds == "BONUS" or av_hc == "BONUS":
            if code_client in acces.sommes:
                structure_bonus = r'''{|l|r|r|r|}'''
                legende_bonus = r'''Table I.8 - Récapitulatif des bonus'''

                contenu_bonus = r'''
                    \cline{2-4}
                    \multicolumn{1}{c}{} & \multicolumn{3}{|c|}{Bonus (Points)} \\
                    \hline
                    Compte & \multicolumn{1}{c|}{Déduc. Sp.} & \multicolumn{1}{c|}{Déduc. HC}
                    & \multicolumn{1}{c|}{Total} \\
                    \hline
                    '''
                contenu_bonus += contenu_bonus_compte

                bst = client['bs'] * scl['dst']
                bht = client['bh'] * scl['dht']
                dico_bonus = {'bst': math.ceil(bst), 'bht': math.ceil(bht),
                              'mbt': scl['somme_t_mb']}
                contenu_bonus += r'''Total & \multicolumn{1}{c|}{%(bst)s} & \multicolumn{1}{c|}{%(bht)s} & \multicolumn{1}{c|}{%(mbt)s} \\
                    \hline
                    ''' % dico_bonus

                contenu += Latex.tableau(contenu_bonus, structure_bonus, legende_bonus)
            else:
                contenu += Latex.tableau_vide(r'''Table I.8 - Récapitulatif des bonus :
                    table vide (pas d'utilisations machines)''')

        # ## Annexe 2

        if contenu_compte_annexe2 != "":
            contenu += Annexes.titre_annexe(code_client, client, edition, reference, titre_2, nombre_2)
            contenu += contenu_compte_annexe2

        # ## Annexe 3

        # ## contenu 3.2

        contenu_machuts = ""
        if code_client in acces.sommes:
            somme = acces.sommes[code_client]['machines']
            machines_utilisees = Outils.machines_in_somme(somme, machines)

            for id_cout, mics in sorted(machines_utilisees.items()):
                for nom_machine, id_machine in sorted(mics.items()):
                    if id_machine in scl['res']:
                        pur_hp = somme[id_machine]['pur_hp']
                        pur_hc = somme[id_machine]['pur_hc']
                        tx_hp = machines.donnees[id_machine]['tx_occ_eff_hp']
                        tx_hc = machines.donnees[id_machine]['tx_occ_eff_hc']
                        if (pur_hc > 0 and tx_hc > 0) or (pur_hp > 0 and tx_hp > 0):
                            dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                            'hp': Outils.format_heure(somme[id_machine]['duree_hp']),
                                            'hc': Outils.format_heure(somme[id_machine]['duree_hc'])}
                            contenu_machuts += r'''
                               \textbf{%(machine)s} & \hspace{5mm} %(hp)s & \hspace{5mm} %(hc)s \\
                                \hline
                                ''' % dico_machine

                            utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                            for nom, upi in sorted(utilisateurs.items()):
                                for prenom, ids in sorted(upi.items()):
                                    for id_user in sorted(ids):
                                        smu = somme[id_machine]['users'][id_user]
                                        dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                     'hp': Outils.format_heure(smu['duree_hp']),
                                                     'hc': Outils.format_heure(smu['duree_hc'])}
                                        contenu_machuts += r'''
                                            \hspace{5mm} %(user)s & %(hp)s & %(hc)s \\
                                            \hline
                                            ''' % dico_user

                                        comptes_utilises = Outils.comptes_in_somme(smu['comptes'], comptes)

                                        for num_compte, id_compte in sorted(comptes_utilises.items()):
                                            smuc = smu['comptes'][id_compte]
                                            compte = comptes.donnees[id_compte]
                                            intitule_compte = Latex.echappe_caracteres(compte['numero']
                                                                                       + " - " + compte['intitule'])
                                            dico_compte = {'compte': intitule_compte,
                                                           'hp': Outils.format_heure(smuc['duree_hp']),
                                                           'hc': Outils.format_heure(smuc['duree_hc'])}
                                            contenu_machuts += r'''
                                                \hspace{10mm} %(compte)s & %(hp)s \hspace{5mm} & %(hc)s \hspace{5mm} \\
                                                \hline
                                                ''' % dico_compte

        if code_client in reservations.sommes or contenu_machuts != "":
            contenu += Annexes.titre_annexe(code_client, client, edition, reference,
                                            "Annexe détaillée des pénalités de réservation", "III")
            contenu += Annexes.section(code_client, client, edition, reference,
                                       "Annexe détaillée des pénalités de réservation", "III")

            # ## 3.1

            if code_client in reservations.sommes:
                structure_stats_client = r'''{|l|c|c|c|c|c|c|}'''
                legende_stats_client = r'''Table III.1 - Statistiques des réservations et des utilisations machines'''
                contenu_stats_client = r'''
                    \cline{3-7}
                    \multicolumn{2}{c}{} & \multicolumn{3}{|c|}{Réservation} & Utilisation & Pénalités \\
                    \hline
                     & & Durée & Taux & Util. Min. & Durée & Durée \\
                    \hline'''

                ac_somme = None
                re_somme = reservations.sommes[code_client]

                if code_client in acces.sommes:
                    ac_somme = acces.sommes[code_client]['machines']

                machines_utilisees = Outils.machines_in_somme(scl['res'], machines)

                for id_cout, mics in sorted(machines_utilisees.items()):
                    for nom_machine, id_machine in sorted(mics.items()):
                        re_hp = re_somme[id_machine]['res_hp']
                        re_hc = re_somme[id_machine]['res_hc']
                        tx_hp = machines.donnees[id_machine]['tx_occ_eff_hp']
                        tx_hc = machines.donnees[id_machine]['tx_occ_eff_hc']

                        ac_hp = 0
                        ac_hc = 0
                        if ac_somme and id_machine in ac_somme:
                            ac_hp = ac_somme[id_machine]['duree_hp']
                            ac_hc = ac_somme[id_machine]['duree_hc']

                        tot_hp = scl['res'][id_machine]['tot_hp']
                        tot_hc = scl['res'][id_machine]['tot_hc']

                        dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                        'ac_hp': Outils.format_heure(ac_hp), 'ac_hc': Outils.format_heure(ac_hc),
                                        're_hp': Outils.format_heure(re_hp), 're_hc': Outils.format_heure(re_hc),
                                        'tot_hp': Outils.format_heure(tot_hp), 'tot_hc': Outils.format_heure(tot_hc)}

                        sclu = scl['res'][id_machine]['users']
                        utilisateurs = Outils.utilisateurs_in_somme(sclu, users)

                        if re_hp > 0:
                            contenu_stats_client += r'''
                                %(machine)s & HP & \hspace{5mm} %(re_hp)s & & & \hspace{5mm} %(ac_hp)s
                                & \hspace{5mm} %(tot_hp)s \\
                                 \hline
                                 ''' % dico_machine

                            for nom, upi in sorted(utilisateurs.items()):
                                for prenom, ids in sorted(upi.items()):
                                    for id_user in sorted(ids):
                                        ac = sclu[id_user]['ac_hp']
                                        re = sclu[id_user]['re_hp']
                                        mini = sclu[id_user]['mini_hp']
                                        tot = sclu[id_user]['tot_hp']
                                        if ac > 0 or re > 0:
                                            dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                         'ac': Outils.format_heure(ac),
                                                         're': Outils.format_heure(re), 'tx': tx_hp,
                                                         'mini': Outils.format_heure(mini),
                                                         'tot': Outils.format_heure(tot)}
                                            contenu_stats_client += r'''
                                                \hspace{5mm} %(user)s & HP & %(re)s & %(tx)s & %(mini)s & %(ac)s
                                                & %(tot)s \\
                                                \hline
                                                ''' % dico_user

                        if re_hc > 0:
                            contenu_stats_client += r'''
                                %(machine)s & HC & \hspace{5mm} %(re_hc)s & & & \hspace{5mm} %(ac_hc)s
                                & \hspace{5mm} %(tot_hc)s  \\
                                 \hline
                                 ''' % dico_machine

                            for nom, upi in sorted(utilisateurs.items()):
                                for prenom, ids in sorted(upi.items()):
                                    for id_user in sorted(ids):
                                        ac = sclu[id_user]['ac_hc']
                                        re = sclu[id_user]['re_hc']
                                        mini = sclu[id_user]['mini_hc']
                                        tot = sclu[id_user]['tot_hc']
                                        if ac > 0 or re > 0:
                                            dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                         'ac': Outils.format_heure(ac),
                                                         're': Outils.format_heure(re), 'tx': tx_hc,
                                                         'mini': Outils.format_heure(mini),
                                                         'tot': Outils.format_heure(tot)}
                                            contenu_stats_client += r'''
                                                \hspace{5mm} %(user)s & HC & %(re)s & %(tx)s & %(mini)s & %(ac)s
                                                & %(tot)s \\
                                                \hline
                                                ''' % dico_user

                contenu += Latex.long_tableau(contenu_stats_client, structure_stats_client, legende_stats_client)
            else:
                contenu += Latex.tableau_vide(r'''Table III.1 - Statistiques des réservations et des utilisations
                    machines : table vide (pas de pénalités de réservation)''')

            # ## 3.2

            if code_client in acces.sommes and contenu_machuts != "":
                structure_machuts_client = r'''{|l|c|c|}'''
                legende_machuts_client = r'''Table III.2 - Récapitulatif des utilisations machines par utilisateur'''
                contenu_machuts_client = r'''
                    \cline{2-3}
                    \multicolumn{1}{c|}{} & HP & HC \\
                    \hline'''

                contenu_machuts_client += contenu_machuts

                contenu += Latex.long_tableau(contenu_machuts_client, structure_machuts_client, legende_machuts_client)
            else:
                contenu += Latex.tableau_vide(r'''Table III.2 - Récapitulatif des utilisations machines par
                    utilisateur : table vide (pas d’utilisation machines)''')

            # ## 3.3

            if code_client in reservations.sommes:
                structure_reserve_client = r'''{|c|c|c|c|c|}'''
                legende_reserve_client = r'''Table III.3 - Détail des réservations machines par utilisateur'''

                contenu_reserve_client = r'''
                    \cline{4-5}
                    \multicolumn{3}{c}{} & \multicolumn{2}{|c|}{Durée réservée} \\
                    \cline{4-5}
                    \multicolumn{3}{c|}{} & HP & HC \\
                    \hline
                    '''

                somme = reservations.sommes[code_client]

                machines_reservees = Outils.machines_in_somme(somme, machines)

                for id_cout, mics in sorted(machines_reservees.items()):
                    for nom_machine, id_machine in sorted(mics.items()):

                        dico_machine = {'machine': Latex.echappe_caracteres(nom_machine),
                                        'hp': Outils.format_heure(somme[id_machine]['res_hp']),
                                        'hc': Outils.format_heure(somme[id_machine]['res_hc'])}
                        contenu_reserve_client += r'''
                                    \multicolumn{3}{|l|}{\textbf{%(machine)s}} & \hspace{5mm} %(hp)s &
                                    \hspace{5mm} %(hc)s \\
                                    \hline
                                    ''' % dico_machine

                        utilisateurs = Outils.utilisateurs_in_somme(somme[id_machine]['users'], users)

                        for nom, upi in sorted(utilisateurs.items()):
                            for prenom, ids in sorted(upi.items()):
                                for id_user in sorted(ids):
                                    smu = somme[id_machine]['users'][id_user]
                                    dico_user = {'user': Latex.echappe_caracteres(nom + " " + prenom),
                                                 'hp': Outils.format_heure(smu['res_hp']),
                                                 'hc': Outils.format_heure(smu['res_hc'])}
                                    contenu_reserve_client += r'''
                                                \multicolumn{3}{|l|}{\hspace{5mm} %(user)s} & %(hp)s & %(hc)s \\
                                                \hline
                                            ''' % dico_user
                                    for p1 in smu['data']:
                                        res = reservations.donnees[p1]
                                        login = Latex.echappe_caracteres(res['date_debut']).split()
                                        temps = login[0].split('-')
                                        date = temps[0]
                                        for p2 in range(1, len(temps)):
                                            date = temps[p2] + '.' + date
                                        if len(login) > 1:
                                            heure = login[1]
                                        else:
                                            heure = ""

                                        sup = ""
                                        if res['si_supprime'] == "OUI":
                                            sup = "Supprimé le : " + res['date_suppression']
                                        dico_pos = {'date': date, 'heure': heure, 'sup': Latex.echappe_caracteres(sup),
                                                    'hp': Outils.format_heure(res['duree_fact_hp']),
                                                    'hc': Outils.format_heure(res['duree_fact_hc'])}
                                        contenu_reserve_client += r'''
                                                    \hspace{10mm} %(date)s & %(heure)s & %(sup)s & %(hp)s \hspace{5mm} &
                                                     %(hc)s \hspace{5mm} \\
                                                    \hline
                                                ''' % dico_pos

                contenu += Latex.long_tableau(contenu_reserve_client, structure_reserve_client, legende_reserve_client)
            else:
                contenu += Latex.tableau_vide(r'''Table III.3 - Détail des réservations machines par utilisateur :
                    table vide (pas de réservation machines)''')

        else:
            contenu += Annexes.titre_annexe(code_client, client, edition, reference,
                                            r'''Annexe détaillée des pénalités de réservation} \newline\newline
                                             \textit{Annexe vide : pas de pénalités de réservation  ''', "III")

        # ## Annexe 4

        if contenu_compte_annexe4 != "":
            contenu += Annexes.titre_annexe(code_client, client, edition, reference, titre_4, nombre_4)
            contenu += contenu_compte_annexe4

        # ## Annexe 5

        if an_couts == "OUI" and contenu_compte_annexe5 != "":
            contenu += Annexes.titre_annexe(code_client, client, edition, reference, titre_5, nombre_5)
            contenu += contenu_compte_annexe5

        return contenu

    @staticmethod
    def titre_annexe(code_client, client, edition, reference, titre, nombre):
        """
        création d'un titre d'annexe
        :param code_client: code du client concerné
        :param client: données du client concerné
        :param edition: paramètres d'édition
        :param reference: référence de la facture
        :param titre: titre de l'annexe
        :param nombre: numéro de l'annexe
        :return: page de titre latex de l'annexe
        """
        dic_titre = {'code': code_client, 'code_sap': Latex.echappe_caracteres(client['code_sap']),
                     'nom': Latex.echappe_caracteres(client['abrev_labo']),
                     'date': edition.mois_txt + " " + str(edition.annee),
                     'ref': reference, 'titre': titre, 'nombre': nombre}

        contenu = r'''
            \clearpage
            \begin{titlepage}
            %(ref)s \hspace*{4cm} Client %(code)s - %(code_sap)s - %(nom)s - %(date)s
            \vspace*{8cm}
            \begin{adjustwidth}{5cm}{}
            \Large\textsc{Annexe %(nombre)s} \newline\newline
            \Large\textsc{%(titre)s} \newpage
            \end{adjustwidth}
            \end{titlepage}
            ''' % dic_titre

        return contenu

    @staticmethod
    def section(code_client, client, edition, reference, titre, nombre):
        """
        création d'un début de section non-visible
        :param code_client: code du client concerné
        :param client: données du client concerné
        :param edition: paramètres d'édition
        :param reference: référence de la facture
        :param titre: titre de la section
        :param nombre: numéro d'annexe de la section
        :return: section latex
        """
        dic_section = {'code': code_client, 'code_sap': Latex.echappe_caracteres(client['code_sap']),
                       'nom': Latex.echappe_caracteres(client['abrev_labo']),
                       'date': edition.mois_txt + " " + str(edition.annee),
                       'ref': reference, 'titre': titre, 'nombre': nombre}

        section = r'''
            \fakesection{%(ref)s \hspace*{4cm} Client %(code)s - %(code_sap)s - %(nom)s - %(date)s}{Annexe %(nombre)s
            - %(titre)s}
            ''' % dic_section

        return section
