from latex import Latex
from outils import Outils


class Facture(object):
    """
    Classe contenant les méthodes nécessaires à la génération des factures
    """

    def __init__(self, prod2qual=None):
        """
        Constructeur

        :param prod2qual: Une instance de la classe Prod2Qual
        """

        self.prod2qual = prod2qual

    def factures(self, sommes, destination, edition, generaux, clients, comptes,
                 lien_annexes, lien_annexes_techniques, annexes, annexes_techniques):
        """
        génère la facture sous forme de csv
        :param sommes: sommes calculées
        :param destination: Une instance de la classe dossier.DossierDestination
        :param edition: paramètres d'édition
        :param generaux: paramètres généraux
        :param clients: clients importés
        :param comptes: comptes importés
        :param lien_annexes: lien au dossier contenant les annexes
        :param lien_annexes_techniques: lien au dossier contenant les annexes techniques
        :param annexes: dossier contenant les annexes
        :param annexes_techniques: dossier contenant les annexes techniques
        """

        if sommes.calculees == 0:
            info = "Vous devez d'abord faire toutes les sommes avant de pouvoir créer la facture"
            print(info)
            Outils.affiche_message(info)
            return

        if self.prod2qual:
            suffixe = "_qualite.csv"
        else:
            suffixe = ".csv"
        nom = "facture_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + "_" + \
              str(edition.version) + suffixe
        with destination.writer(nom) as fichier_writer:
            fichier_writer.writerow(["Poste", "Système d'origine", "Type de document de vente",
                                     "Organisation commerciale", "Canal de distribution", "Secteur d'activité", "", "",
                                     "Client", "Nom 2 du client", "Nom 3 du client", "Adresse e-mail du client",
                                     "Client", "Client", "Client", "Devise", "Mode d'envoi",
                                     "Référence de la facture", "", "", "Texte d'entête",
                                     "Lien réseau vers l'annexe facture *.pdf", "Document interne",
                                     "Lien réseau vers l'annexe technique *.pdf", "Document interne", "", "", "", "",
                                     "", "", "Article", "", "Quantité", "Unité de quantité", "Type de prix",
                                     "Prix net du poste", "Type de rabais", "Valeur rabais du poste",
                                     "Date de livraison", "Centre financier", "", "Fonds à créditer", "", "",
                                     "Code opération", "", "", "", "Texte libre du poste", "Nom"])

            contenu = ""
            combo_list = []

            for code_client in sorted(sommes.sommes_clients.keys()):
                poste = 0
                scl = sommes.sommes_clients[code_client]
                client = clients.donnees[code_client]

                if scl['somme_t'] == 0:
                    continue
    
                code_sap = client['code_sap']
                if self.prod2qual and not (self.prod2qual.code_client_existe(code_sap)):
                    continue
    
                if client['type_labo'] == "I":
                    genre = generaux.code_int
                else:
                    genre = generaux.code_ext
                nature = generaux.nature_client_par_code_n(client['type_labo'])
                reference = nature + str(edition.annee)[2:] + Outils.mois_string(edition.mois) + "." + code_client
                if edition.version != "0":
                    reference += "-" + edition.version

                filtre = generaux.filtrer_article_nul_par_code_n(client['type_labo'])
    
                nom_annexe = "annexe_" + str(edition.annee) + "_" + Outils.mois_string(edition.mois) + \
                             "_" + str(edition.version) + "_" + code_client + ".pdf"
                lien_annexe = lien_annexes + nom_annexe
                dossier_annexe = "../" + annexes + "/" + nom_annexe
    
                nom_annexe_technique = "annexeT_" + str(edition.annee) + "_" + \
                                       Outils.mois_string(edition.mois) + "_" + str(edition.version) + "_" + \
                                       code_client + ".pdf"
                lien_annexe_technique = lien_annexes_techniques + nom_annexe_technique
                dossier_annexe_technique = "../" + annexes_techniques + "/" + nom_annexe_technique
    
                if self.prod2qual:
                    code_sap_traduit = self.prod2qual.traduire_code_client(code_sap)
                else:
                    code_sap_traduit = code_sap

                combo_list.append(code_client + " " + client['abrev_labo'])
                dico_contenu = {'code': code_client, 'abrev': client['abrev_labo'],
                                'nom': client['nom_labo'], 'dest': client['dest'], 'ref': client['ref'],
                                'ref_fact': reference, 'texte': generaux.entete}
                contenu_client = r'''<section><div id="entete"> %(code)s <br />
                    %(abrev)s <br />
                    %(nom)s <br />
                    %(dest)s <br />
                    %(ref)s <br />
                    </div><br />
                    %(ref_fact)s <br /><br />
                    %(texte)s <br />
                    ''' % dico_contenu
    
                contenu_client += r'''<table id="tableau">
                    <tr>
                    <td>Item </td><td> Date </td><td> Name </td><td> Description </td><td> Unit </td><td> Quantity </td>
                    <td> Unit Price <br /> [CHF] </td><td> Discount </td><td> Net amount <br /> [CHF] </td>
                    </tr>
                    '''
    
                fichier_writer.writerow([poste, generaux.origine, genre, generaux.commerciale,
                                         generaux.canal, generaux.secteur, "", "",
                                         code_sap_traduit, client['dest'], client['ref'], client['email'],
                                         code_sap_traduit, code_sap_traduit,
                                         code_sap_traduit, generaux.devise, client['mode'], reference, "", "",
                                         generaux.entete, lien_annexe, "", lien_annexe_technique, "X"])
    
                op_centre = client['type_labo'] + str(edition.annee)[2:] + Outils.mois_string(edition.mois)

                if scl['em'] > 0 and not (filtre == "OUI" and scl['e'] == 0):
                    poste = generaux.poste_emolument
                    fichier_writer.writerow(self.ligne_facture(generaux, generaux.articles[0], poste, scl['em'],
                                                               scl['er'], op_centre, "", edition))
                    contenu_client += self.ligne_tableau(generaux.articles[0], poste, scl['em'], scl['er'], "", edition)

                if scl['rm'] > 0 and not (filtre == "OUI" and scl['r'] == 0):
                    poste = generaux.poste_reservation
                    fichier_writer.writerow(self.ligne_facture(generaux, generaux.articles[1], poste, scl['rm'],
                                                               scl['rr'], op_centre, "", edition))
                    contenu_client += self.ligne_tableau(generaux.articles[1], poste, scl['rm'], scl['rr'], "",
                                                         edition)
    
                inc = 1

                comptes_utilises = Outils.comptes_in_somme(sommes.sommes_comptes[code_client], comptes)

                for num_compte, id_compte in sorted(comptes_utilises.items()):
                    sco = sommes.sommes_comptes[code_client][id_compte]
                    compte = comptes.donnees[id_compte]
                    if sco['c1'] > 0 and not (filtre == "OUI" and sco['c2'] == 0):
                        poste = inc*10
                        if sco['somme_j_mm'] > 0 and not (filtre == "OUI" and sco['mj'] == 0):
                            fichier_writer.writerow(self.ligne_facture(generaux, generaux.articles[2], poste,
                                                                       sco['somme_j_mm'], sco['somme_j_mr'], op_centre,
                                                                       compte['numero'] + " - " + compte['intitule'],
                                                                       edition))
                            contenu_client += self.ligne_tableau(generaux.articles[2], poste, sco['somme_j_mm'],
                                                                 sco['somme_j_mr'],
                                                                 compte['numero'] + " - " + compte['intitule'], edition)
                            poste += 1

                        for article in generaux.articles_d3:
                            categorie = article.code_d
                            if sco['sommes_cat_m'][categorie] > 0 and not (filtre == "OUI"
                                                                           and sco['tot_cat'][article.code_d] == 0):
                                fichier_writer.writerow(self.ligne_facture(generaux, article, poste,
                                                                           sco['sommes_cat_m'][categorie],
                                                                           sco['sommes_cat_r'][categorie], op_centre,
                                                                           compte['numero'] + " - " +
                                                                           compte['intitule'], edition))
                                contenu_client += self.ligne_tableau(article, poste, sco['sommes_cat_m'][categorie],
                                                                     sco['sommes_cat_r'][categorie],
                                                                     compte['numero'] + " - " + compte['intitule'],
                                                                     edition)
                                poste += 1
                        inc += 1
                contenu_client += r'''
                    <tr><td colspan="8" id="toright">Net amount [CHF] : </td><td id="toright">
                    ''' + "%.2f" % scl['somme_t'] + r'''</td></tr>
                    </table>
                    '''
                contenu_client += r'''<a href="''' + dossier_annexe + r'''" target="new">''' + nom_annexe + r'''
                    </a>&nbsp;&nbsp;&nbsp;'''
                contenu_client += r'''<a href="''' + dossier_annexe_technique + r'''" target="new">
                    ''' + nom_annexe_technique + r'''</a>'''
                contenu_client += "</section>"
                contenu += contenu_client
        self.creer_html(contenu, destination, combo_list)

    @staticmethod
    def ligne_tableau(article, poste, net, rabais, consommateur, edition):
        """
        retourne une ligne de tableau html

        :param article: Une instance de la classe generaux.Article
        :param poste: indice de poste
        :param net: montant net
        :param rabais: rabais sur le montant
        :param consommateur: consommateur
        :param edition: paramètres d'édition
        :return: ligne de tableau html
        """
        montant = net - rabais
        date_livraison = str(edition.dernier_jour) + "." + Outils.mois_string(edition.mois) + "." + str(edition.annee)
        description = article.code_d + " : " + article.code_sap
        dico_tab = {'poste': poste, 'date': date_livraison, 'descr': description,
                    'texte': article.texte_sap, 'nom': Latex.echappe_caracteres(consommateur),
                    'unit': article.unite, 'quantity': article.quantite,
                    'unit_p': "%.2f" % net, 'discount': "%.2f" % rabais, 'net': "%.2f" % montant}
        ligne = r'''<tr>
            <td> %(poste)s </td><td> %(date)s </td><td> %(nom)s </td><td> %(descr)s <br /> %(texte)s </td>
            <td> %(unit)s </td><td id="toright"> %(quantity)s </td><td id="toright"> %(unit_p)s </td>
            <td id="toright"> %(discount)s </td><td id="toright"> %(net)s </td>
            </tr>
            ''' % dico_tab
        return ligne

    @staticmethod
    def ligne_facture(generaux, article, poste, net, rabais, op_centre, consommateur, edition):
        """
        retourne une ligne de facturation formatée

        :param generaux: paramètres généraux
        :param article: Une instance de la classe generaux.Article
        :param poste: indice de poste
        :param net: montant net
        :param rabais: rabais sur le montant
        :param op_centre: centre d'opération
        :param consommateur: consommateur
        :param edition: paramètres d'édition
        :return: ligne de facturation formatée
        """
        net = "%.2f" % net
        rabais = "%.2f" % rabais
        if rabais == 0:
            rabais = ""
        code_op = generaux.code_t + op_centre + article.code_d
        date_livraison = str(edition.annee) + Outils.mois_string(edition.mois) + str(edition.dernier_jour)

        return [poste, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", "", article.code_sap, "", article.quantite,
                article.unite, article.type_prix, net,
                article.type_rabais, rabais, date_livraison, generaux.centre_financier, "",
                generaux.fonds, "", "", code_op, "", "", "", article.texte_sap,
                Latex.echappe_caracteres(consommateur)]

    def creer_html(self, contenu, destination, combo_list):
        if self.prod2qual:
            suffixe = "_qualite.html"
        else:
            suffixe = ".html"

        Outils.copier_dossier("./reveal.js/", "js", destination.chemin)
        Outils.copier_dossier("./reveal.js/", "css", destination.chemin)
        with destination.open("ticket" + suffixe) as fichier:

            html = r'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                <meta content="text/html; charset=cp1252" http-equiv="content-type" />
                <meta content="CMi" name="author" />
                <style>
                #entete {
                    margin-left: 600px;
                    text-align:left;
                }
                #tableau {
                    border-collapse: collapse;
                    margin: 20px;
                }
                #tableau tr, #tableau td {
                    border: 1px solid black;
                    vertical-align:middle;
                }
                #tableau td {
                    padding: 3px;
                }
                #toright {
                    text-align:right;
                }
                #combo {
                    margin-top: 10px;
                    margin-left: 50px;
                }
                </style>
                <link rel="stylesheet" href="css/reveal.css">
                <link rel="stylesheet" href="css/white.css">
                </head>
                <body>
                <div id="combo">
                <select name="client" onchange="changeClient(this)">
                '''

            for i in range(len(combo_list)):
                html += r'''<option value="''' + str(i) + r'''">''' + str(combo_list[i]) + r'''</option>'''
            html += r'''
                </select>
                </div>
                <div class="reveal">
                <div class="slides">
                '''
            html += contenu
            html += r'''</div></div>
                    <script src="js/reveal.js"></script>
                    <script>
                        Reveal.initialize();
                    </script>
                    <script>
                    function changeClient(sel) {
                        Reveal.slide(sel.value, 0);
                    }
                    </script>
                    </body>
                </html>'''
            fichier.write(html)
