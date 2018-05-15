from outils import Outils
from latex import Latex
from .tables_annexes import TablesAnnexes


class Annexes(object):
    """
    Classe pour la création des annexes
    """
    @staticmethod
    def annexes(sommes, clients, edition, livraisons, acces, machines, reservations, comptes, dossier_annexe_fact,
                dossier_annexe_tech, generaux, users, couts, docpdf):
        """
        création des annexes
        :param sommes: sommes calculées
        :param clients: clients importés
        :param edition: paramètres d'édition
        :param livraisons: livraisons importées
        :param acces: accès importés
        :param machines: machines importées
        :param reservations: réservations importées
        :param comptes: comptes importés
        :param dossier_annexe_fact: nom du dossier dans lequel enregistrer le dossier des annexes factures
        :param dossier_annexe_tech: nom du dossier dans lequel enregistrer le dossier des annexes techniques
        :param generaux: paramètres généraux
        :param users: users importés
        :param couts: catégories coûts importées
        :param docpdf: paramètres d'ajout de document pdf
        """

        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer les annexes"
            Outils.affiche_message(info)
            return

        for code_client, scl in sommes.sommes_clients.items():
            code_client = Latex.echappe_caracteres(code_client)
            client = clients.donnees[code_client]
            nature = Latex.echappe_caracteres(generaux.nature_client_par_code_n(client['nature']))
            av_hc = Latex.echappe_caracteres(generaux.avantage_hc_par_code_n(client['nature']))
            an_couts = Latex.echappe_caracteres(generaux.annexe_cout_par_code_n(client['nature']))
            reference = nature + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
            if edition.version > 0:
                reference += "-" + str(edition.version)

            filtre = generaux.filtrer_article_nul_par_code_n(client['nature'])

            contenu_prix_bonus_xj = ""
            contenu_prix_cae_xj = ""
            contenu_prix_xaj = ""
            contenu_prix_xf = ""
            inc_fact = 1

            contenu_prix_lvr_xdj_tab = {}
            for article in generaux.articles_d3:
                contenu_prix_lvr_xdj_tab[article.code_d] = ""

            titre_3 = "Annexe détaillée par compte"
            nombre_3 = "III"
            titre_2 = "Récapitulatifs par compte"
            nombre_2 = "II"
            contenu_annexe2_fact = ""
            contenu_annexe2_tech = ""
            contenu_annexe3 = ""

            if code_client in sommes.sommes_comptes:
                comptes_utilises = Outils.comptes_in_somme(sommes.sommes_comptes[code_client], comptes)

                for num_compte, id_compte in sorted(comptes_utilises.items()):
                    id_compte = Latex.echappe_caracteres(id_compte)

                    # ## COMPTE

                    sco = sommes.sommes_comptes[code_client][id_compte]
                    compte = comptes.donnees[id_compte]
                    intitule_compte = Latex.echappe_caracteres(compte['numero'] + " - " + compte['intitule'])

                    # ## ligne Prix XF - Table Client Récap Postes de la facture

                    if sco['c1'] > 0 and not (filtre == "OUI" and sco['c2'] == 0):
                        poste = inc_fact * 10
                        intitule = Latex.echappe_caracteres(intitule_compte + " - " +
                                                            generaux.articles[2].intitule_long)

                        if sco['somme_j_mm'] > 0 and not (filtre == "OUI" and sco['mj'] == 0):
                            dico_prix_xf = {'intitule': intitule, 'poste': str(poste),
                                            'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                            'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                            'mj': Outils.format_2_dec(sco['mj'])}
                            contenu_prix_xf += r'''
                                %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                                \hline
                                ''' % dico_prix_xf
                            poste += 1

                        for article in generaux.articles_d3:
                            categorie = article.code_d
                            if sco['sommes_cat_m'][categorie] > 0 and not (filtre == "OUI"
                                                                           and sco['tot_cat'][article.code_d] == 0):
                                intitule = Latex.echappe_caracteres(intitule_compte + " - " + article.intitule_long)
                                dico_prix_xf = {'intitule': intitule, 'poste': str(poste),
                                                'mm': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                                'mr': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                                'mj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                                contenu_prix_xf += r'''
                                    %(poste)s & %(intitule)s & %(mm)s  & %(mr)s & %(mj)s \\
                                    \hline
                                    ''' % dico_prix_xf
                                poste += 1

                        inc_fact += 1

                    # ## ligne Prix XA/J - Table Client Récap Articles/Compte

                    total = sco['mj']
                    dico_prix_xaj = {'compte': intitule_compte, 'type': compte['type'],
                                     'procede': Outils.format_2_dec(sco['mj'])}

                    ligne = r'''%(compte)s & %(type)s & %(procede)s ''' % dico_prix_xaj

                    for categorie in generaux.codes_d3():
                        total += sco['tot_cat'][categorie]
                        ligne += r''' & ''' + Outils.format_2_dec(sco['tot_cat'][categorie])

                    if total > 0:
                        dico_prix_xaj['total'] = Outils.format_2_dec(total)
                        ligne += r'''& %(total)s \\
                            \hline
                            ''' % dico_prix_xaj
                        contenu_prix_xaj += ligne

                    # ## ligne Prix CAE X/J - Table Client Récap Procédés/Compte

                    rhj = client['rh'] * sco['somme_j_dhi']
                    dico_prix_cae_xj = {'intitule': intitule_compte, 'type': compte['type'],
                                        'maij': Outils.format_2_dec(sco['somme_j_mai']),
                                        'mm': Outils.format_2_dec(sco['somme_j_mm']),
                                        'mr': Outils.format_2_dec(sco['somme_j_mr']),
                                        'rhj': Outils.format_2_dec(rhj),
                                        'moij': Outils.format_2_dec(sco['somme_j_moi']),
                                        'mj': Outils.format_2_dec(sco['mj'])}
                    contenu_prix_cae_xj += r'''
                        %(intitule)s & %(type)s & %(maij)s & %(moij)s & %(rhj)s & %(mm)s & %(mr)s & %(mj)s \\
                        \hline
                        ''' % dico_prix_cae_xj

                    # ## ligne Prix LVR X/D/J - Table Client Récap Prestations livr./code D/Compte

                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        for article in generaux.articles_d3:
                            if article.code_d in livraisons.sommes[code_client][id_compte]:
                                if contenu_prix_lvr_xdj_tab[article.code_d] == "":
                                    contenu_prix_lvr_xdj_tab[article.code_d] = r'''
                                        \cline{2-4}
                                        \multicolumn{1}{c}{} & \multicolumn{3}{|c|}{
                                        ''' + Latex.echappe_caracteres(article.intitule_long) + r'''} \\
                                        \hline
                                        Compte & Montant & Rabais & Montant net \\
                                        \hline
                                        '''
                                dico_prest_client = {'intitule': intitule_compte,
                                                     'cmj': Outils.format_2_dec(sco['sommes_cat_m'][article.code_d]),
                                                     'crj': Outils.format_2_dec(sco['sommes_cat_r'][article.code_d]),
                                                     'cj': Outils.format_2_dec(sco['tot_cat'][article.code_d])}
                                contenu_prix_lvr_xdj_tab[article.code_d] += r'''
                                %(intitule)s & %(cmj)s & %(crj)s & %(cj)s \\
                                \hline
                                ''' % dico_prest_client

                    # ## ligne Prix Bonus X/J - Table Client Récap Bonus/Compte

                    if code_client in acces.sommes and id_compte in acces.sommes[code_client]['comptes']:
                        bhj = client['bh'] * sco['somme_j_dhi']
                        dico_prix_bonus_xj = {'compte': intitule_compte, 'bhj': Outils.format_2_dec(bhj)}
                        contenu_prix_bonus_xj += r'''
                            %(compte)s & %(bhj)s \\
                            \hline
                            ''' % dico_prix_bonus_xj

                    # ## Annexe 2 du compte

                    titre2 = "Récapitulatif du compte : " + intitule_compte
                    section2 = Annexes.section(code_client, client, edition, generaux, reference, titre2, nombre_2)
                    contenu_annexe2_fact += section2
                    contenu_annexe2_tech += section2

                    contenu_annexe2_fact += TablesAnnexes.table_prix_ja("Table II.1", sco, generaux)
                    contenu_annexe2_fact += TablesAnnexes.table_prix_cae_jk("Table II.2", code_client, id_compte,
                                                                            intitule_compte, sco, acces.sommes, couts)
                    contenu_annexe2_fact += TablesAnnexes.table_prix_lvr_jd("Table II.3", code_client, id_compte,
                                                                            intitule_compte, sco, livraisons.sommes,
                                                                            generaux)
                    contenu_annexe2_fact += TablesAnnexes.table_prix_avtg_jm("Table II.4", code_client, id_compte,
                                                                             intitule_compte, sco, acces.sommes,
                                                                             machines, av_hc)
                    if an_couts == "OUI":
                        contenu_annexe2_fact += TablesAnnexes.table_cout_cae_jk("Table II.5", code_client,
                                                                                id_compte, intitule_compte, sco,
                                                                                acces.sommes, couts)
                    contenu_annexe2_tech += TablesAnnexes.table_prix_cae_jm("Table II.6", code_client, id_compte,
                                                                            intitule_compte, sco, acces.sommes,
                                                                            machines, av_hc)
                    if an_couts == "OUI":
                        contenu_annexe2_tech += TablesAnnexes.table_cout_ja("Table II.7", code_client, id_compte,
                                                                            generaux, sco, livraisons.sommes)
                        contenu_annexe2_tech += TablesAnnexes.table_cout_cae_jkm("Table II.8", code_client, id_compte,
                                                                                 intitule_compte, couts, machines,
                                                                                 acces.sommes)
                        contenu_annexe2_tech += TablesAnnexes.table_cout_lvr_jd("Table II.9", code_client, id_compte,
                                                                                intitule_compte, sco, generaux,
                                                                                livraisons.sommes)
                    contenu_annexe2_fact += r'''\clearpage'''
                    contenu_annexe2_tech += r'''\clearpage'''

                    # ## Annexe 3 du compte

                    titre3 = "Annexe détaillée du compte : " + intitule_compte
                    contenu_annexe3 += Annexes.section(code_client, client, edition, generaux, reference, titre3,
                                                       nombre_3)
                    contenu_annexe3 += TablesAnnexes.table_tps_cae_jkmu("Table III.1", code_client, id_compte,
                                                                        intitule_compte, users, machines, couts, acces)
                    if code_client in livraisons.sommes and id_compte in livraisons.sommes[code_client]:
                        contenu_annexe3 += TablesAnnexes.table_qte_lvr_jdu("Table III.2", code_client, id_compte,
                                                                           intitule_compte, generaux, livraisons, users)
                    contenu_annexe3 += r'''\clearpage'''

                    # ## compte

            # ## Début des tableaux

            entete = Annexes.entete(edition, client, code_client, generaux.centre, reference)
            contenu_tech = entete
            contenu_fact = entete

            # ## Annexe 1

            annexe1 = Annexes.titre_annexe(code_client, client, edition, generaux, reference, "Récapitulatif", "I")
            section1 = Annexes.section(code_client, client, edition, generaux, reference, "Récapitulatif", "I")
            contenu_tech += annexe1 + section1
            contenu_fact += annexe1 + section1

            contenu_fact += TablesAnnexes.table_prix_xf("Table I.1", scl, generaux, filtre, contenu_prix_xf)
            contenu_fact += TablesAnnexes.table_prix_xaj("Table I.2", scl, generaux, contenu_prix_xaj)
            if av_hc == "BONUS":
                contenu_fact += TablesAnnexes.table_prix_bonus_xj("Table I.3", code_client, scl, acces.sommes, client,
                                                                  contenu_prix_bonus_xj)
            contenu_tech += TablesAnnexes.table_prix_xa("Table I.4", scl, generaux)
            contenu_tech += TablesAnnexes.table_prix_xe("Table I.5", scl, client)
            contenu_tech += TablesAnnexes.table_prix_cae_xj("Table I.6", code_client, scl, acces.sommes, client,
                                                            contenu_prix_cae_xj)
            contenu_tech += TablesAnnexes.table_prix_lvr_xdj("Table I.7", code_client, scl, livraisons.sommes, generaux,
                                                             contenu_prix_lvr_xdj_tab)

            # ## Annexe 2

            if contenu_annexe2_fact != "":
                contenu_fact += Annexes.titre_annexe(code_client, client, edition, generaux, reference, titre_2,
                                                     nombre_2)
                contenu_fact += contenu_annexe2_fact

            if contenu_annexe2_tech != "":
                contenu_tech += Annexes.titre_annexe(code_client, client, edition, generaux, reference, titre_2,
                                                     nombre_2)
                contenu_tech += contenu_annexe2_tech

            # ## Annexe 3

            if contenu_annexe3 != "":
                contenu_fact += Annexes.titre_annexe(code_client, client, edition, generaux, reference, titre_3,
                                                     nombre_3)
                contenu_fact += contenu_annexe3

            # ## Annexe 4

            contenu_cae_xmu = TablesAnnexes.contenu_tps_m_cae_xmu(code_client, scl, acces.sommes, machines, users,
                                                                  comptes)

            if code_client in reservations.sommes or contenu_cae_xmu != "":
                contenu_fact += Annexes.titre_annexe(code_client, client, edition, generaux, reference,
                                                     "Annexe détaillée des pénalités de réservation", "IV")
                contenu_fact += Annexes.section(code_client, client, edition, generaux, reference,
                                                "Annexe détaillée des pénalités de réservation", "IV")
                contenu_fact += TablesAnnexes.table_prix_xr("Table IV.1", code_client, scl, reservations.sommes,
                                                            machines)
                contenu_fact += TablesAnnexes.table_tps_penares_xmu("Table IV.2", code_client, scl, acces.sommes,
                                                                    reservations.sommes, machines, users)
                contenu_fact += TablesAnnexes.table_tps_m_cae_xmu("Table IV.3", code_client, acces, contenu_cae_xmu)
                contenu_fact += TablesAnnexes.table_tps_res_xmu("Table IV.4", code_client, reservations, machines,
                                                                users)
            else:
                contenu_fact += Annexes.titre_annexe(code_client, client, edition, generaux, reference,
                                                     r'''Annexe détaillée des pénalités de réservation} \newline\newline
                                                      \textit{Annexe vide : pas de pénalités de réservation  ''', "IV")

            # ## Annexe 5

            annexe_5 = Annexes.titre_annexe(code_client, client, edition, generaux, reference,
                                            "Documents contractuels et informatifs", "V")
            annexe_5 += Annexes.section(code_client, client, edition, generaux, reference,
                                        "Documents contractuels et informatifs", "V")

            # ## Finale

            if scl['somme_t'] != 0:
                if docpdf is not None:
                    pdfs = docpdf.pdfs_pour_client(client, 'annexe_fact')
                else:
                    pdfs = None
                if pdfs is not None and len(pdfs) > 0:
                    contenu_fact += annexe_5
                nom_fact = "annexe_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_"
                nom_fact += str(edition.version) + "_" + code_client
                contenu_fact += r'''\end{document}'''
                Latex.creer_latex_pdf(nom_fact, contenu_fact, pdfs, dossier_annexe_fact)

            if docpdf is not None:
                pdfs = docpdf.pdfs_pour_client(client, 'annexe_tech')
            else:
                pdfs = None
            if pdfs is not None and len(pdfs) > 0:
                contenu_tech += annexe_5
            nom_tech = "annexeT_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_"
            nom_tech += str(edition.version) + "_" + code_client
            contenu_tech += r'''\end{document}'''
            Latex.creer_latex_pdf(nom_tech, contenu_tech, pdfs, dossier_annexe_tech)

    @staticmethod
    def titre_annexe(code_client, client, edition, generaux, reference, titre, nombre):
        """
        création d'un titre d'annexe
        :param code_client: code du client concerné
        :param client: données du client concerné
        :param edition: paramètres d'édition
        :param generaux: paramètres généraux
        :param reference: référence de la facture
        :param titre: titre de l'annexe
        :param nombre: numéro de l'annexe
        :return: page de titre latex de l'annexe
        """
        dic_titre = {'code': code_client, 'code_sap': Latex.echappe_caracteres(client['code_sap']),
                     'nom': Latex.echappe_caracteres(client['abrev_labo']),
                     'date': edition.mois_txt + " " + str(edition.annee), 'ref': reference, 'titre': titre,
                     'nombre': nombre, 'centre': Latex.echappe_caracteres(generaux.centre)}

        contenu = r'''
            \clearpage
            \begin{titlepage}
            \begin{adjustwidth}{0cm}{}
            %(centre)s \newline
            %(ref)s \hspace*{4cm} Client %(code)s - %(code_sap)s - %(nom)s - %(date)s
            \end{adjustwidth}
            \vspace*{8cm}
            \begin{adjustwidth}{5cm}{}
            \Large\textsc{Annexe %(nombre)s} \newline\newline
            \Large\textsc{%(titre)s} \newpage
            \end{adjustwidth}
            \end{titlepage}
            ''' % dic_titre

        return contenu

    @staticmethod
    def section(code_client, client, edition, generaux, reference, titre, nombre):
        """
        création d'un début de section non-visible
        :param code_client: code du client concerné
        :param client: données du client concerné
        :param edition: paramètres d'édition
        :param generaux: paramètres généraux
        :param reference: référence de la facture
        :param titre: titre de la section
        :param nombre: numéro d'annexe de la section
        :return: section latex
        """
        dic_section = {'code': code_client, 'code_sap': Latex.echappe_caracteres(client['code_sap']),
                       'nom': Latex.echappe_caracteres(client['abrev_labo']),
                       'date': edition.mois_txt + " " + str(edition.annee), 'ref': reference,
                       'titre': titre, 'nombre': nombre, 'centre': Latex.echappe_caracteres(generaux.centre)}

        section = r'''
            \fakesection{%(centre)s \newline %(ref)s \hspace*{4cm} Client %(code)s - %(code_sap)s - %(nom)s - 
            %(date)s}{Annexe %(nombre)s - %(titre)s}
            ''' % dic_section

        return section

    @staticmethod
    def entete(edition, client, code_client, centre, reference):
        entete = Latex.entete()
        entete += r'''
            \usepackage[margin=10mm, includehead]{geometry}
            \usepackage{multirow}
            \usepackage{graphicx}
            \usepackage{longtable}
            \usepackage{dcolumn}
            \usepackage{changepage}
            \usepackage[scriptsize]{caption}
            \usepackage{fancyhdr}\usepackage{float}
            \restylefloat{table}

            '''

        if edition.filigrane != "":
            entete += r'''
                \usepackage{draftwatermark}
                \SetWatermarkLightness{0.8}
                \SetWatermarkAngle{45}
                \SetWatermarkScale{2}
                \SetWatermarkFontSize{2cm}
                \SetWatermarkText{''' + edition.filigrane[:15] + r'''}
                '''

        entete += r'''
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

        entete += r'''
            \begin{titlepage}
            \textsc{''' + Latex.echappe_caracteres(centre) + r'''}
            \vspace*{8cm}
            \begin{adjustwidth}{5cm}{}
            \Large\textsc{Annexes Factures \newline Billing Appendices}\newline
            \Large\textsc{''' + reference + r'''}\newline\newline\newline
            '''

        dic_entete = {'code': code_client, 'code_sap': Latex.echappe_caracteres(client['code_sap']),
                      'nom': Latex.echappe_caracteres(client['abrev_labo']),
                      'date': edition.mois_txt + " " + str(edition.annee)}

        entete += r'''Client %(code)s -  %(code_sap)s -  %(nom)s \newline
             %(date)s
            \end{adjustwidth}
            \end{titlepage}''' % dic_entete
        return entete
