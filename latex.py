import re
import os
import shutil
import sys
import subprocess
from outils import Outils
from PyPDF2 import PdfFileMerger


class Latex(object):

    @classmethod
    def possibles(cls):
        return bool(shutil.which("pdflatex"))

    @staticmethod
    def echappe_caracteres(texte):
        """
        échappement des caractères qui peuvent poser problème dans les tableaux latex
        :param texte: texte à échapper
        :return: texte échappé
        """

        p = re.compile("[^ a-zA-Z0-9_'Éèéêëâàäïûùüçöô.:,;\-%#&@\\\\$/|()\[\]\{\}]")
        texte = p.sub('', texte)

        texte = texte.replace('\\', '\\textbackslash')
        caracteres = ['%', '$', '_', '&', '#', '{', '}']
        latex_c = ['\%', '\$', '\_', '\&', '\#', '\{', '\}']
        for pos in range(0, len(caracteres)):
            texte = texte.replace(caracteres[pos], latex_c[pos])

        return texte

    @staticmethod
    def creer_latex_pdf(nom_fichier, contenu, annexes, nom_dossier=""):
        """
        création d'un pdf à partir d'un contenu latex
        :param nom_fichier: nom du pdf final
        :param contenu: contenu latex
        :param annexes: pages à concaténer à la fin
        :param nom_dossier: nom du dossier dans lequel enregistrer le pdf
        """
        nom_temporaire = "temporaire"
        with open(nom_temporaire + ".tex", 'w') as f:
            f.write(contenu)

        proc = subprocess.Popen(['pdflatex', nom_temporaire + ".tex"])
        proc.communicate()

        # 2 fois pour que les longtable soient réguliers (courant de relancer latex)

        proc = subprocess.Popen(['pdflatex', nom_temporaire + ".tex"])
        proc.communicate()

        try:
            os.unlink(nom_temporaire + '.tex')
            os.unlink(nom_temporaire + '.log')
            os.unlink(nom_temporaire + '.aux')

            fichier_temp = nom_temporaire + ".pdf"
            fichier_fin = nom_fichier + ".pdf"
            if annexes is not None and len(annexes) > 0:
                pdfs = [fichier_temp]
                for pos, chemins in sorted(annexes.items()):
                    for chemin in chemins:
                        pdfs.append(chemin)
                merger = PdfFileMerger()

                for pdf in pdfs:
                    merger.append(pdf)

                merger.write('concatene.pdf')
                shutil.copy('concatene.pdf', fichier_fin)
                os.unlink('concatene.pdf')
            else:
                shutil.copy(fichier_temp, fichier_fin)

            if nom_dossier != '':
                shutil.copy(fichier_fin, nom_dossier)
                shutil.copy(fichier_fin, fichier_temp)
                os.unlink(fichier_fin)
                os.unlink(fichier_temp)
        except OSError as err:
            Outils.affiche_message("OSError: {0}".format(err))
        except IOError as err:
            Outils.affiche_message("IOError: {0}".format(err))

    @staticmethod
    def long_tableau(contenu, structure, legende):
        """
        création d'un long tableau latex (peut s'étendre sur plusieurs pages)
        :param contenu: contenu du tableau
        :param structure: structure du tableau
        :param legende: légende du tabéeau
        :return: long tableau latex
        """
        return r'''
            {\tiny
            \begin{longtable}[c]
            ''' + structure + contenu + r'''
            \caption*{''' + legende + r'''}
            \end{longtable}}
            '''

    @staticmethod
    def tableau(contenu, structure, legende):
        """
        création d'un tableau latex
        :param contenu: contenu du tableau
        :param structure: structure du tableau
        :param legende: légende du tableau
        :return: tableau latex
        """
        return r'''
            \begin{table}[H]
            \tiny
            \centering
            \begin{tabular}''' + structure + contenu + r'''\end{tabular}
            \caption*{''' + legende + r'''}
            \end{table}
            '''

    @staticmethod
    def tableau_vide(legende):
        """
        création d'un tableau vide, juste pour avoir la légende formatée
        :param legende: légende du tableau vide
        :return: tableau avec juste la légende
        """
        return r'''
            \begin{table}[H]
            \tiny
            \centering
            \caption*{''' + legende + r'''}
            \end{table}
            '''

    @staticmethod
    def entete():
        """
        création de l'entête de fichier latex en fonction de l'OS
        :return: le contenu de l'entête
        """
        debut = r'''\documentclass[a4paper,10pt]{article}
            \usepackage[T1]{fontenc}
            \usepackage{lmodern}
            \usepackage[french]{babel}
            \usepackage{microtype}
            \DisableLigatures{encoding = *, family = * }
            '''
        if sys.platform == "win32":
            debut += r'''
                \usepackage[cp1252]{inputenc}
                '''
        elif sys.platform == "darwin":
            debut += r'''\usepackage[appelmac]{inputenc}'''
        else:
            debut += r'''\usepackage[utf8]{inputenc}'''
        return debut
