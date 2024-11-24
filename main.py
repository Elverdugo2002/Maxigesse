import re
import sqlite3
import webbrowser
import bcrypt
import fitz
from kivy.config import Config
Config.set('graphics', "width","400")
Config.set('graphics', "height","620")
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.graphics import Rectangle
from kivy.input.providers.mouse import Color
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from datetime import datetime, timedelta
from kivymd.uix.textfield import MDTextField





#========================Reset password====================================
class Reset_password(MDScreen):
    # Fonction pour vérifier un mot de passe
    def validate_user(self):
        phone = self.ids.phone.text
        if not phone:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir ce champ", buttons=[ok],
                                   size_hint_y=(.5))
            self.ids.phone.text = ''
            self.erreur.open()
        else:
            # Créer une base de données et une table si elles ne existent pas déjà
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            try:
                # Insérer le nom dans la base de données
                self.cursor.execute('select nom_client from Client where telephone_client = ?',
                                    (phone,))
                self.nom = self.cursor.fetchone()[0]
                self.conn.commit()
                self.ids.nom_client.opacity = 1
                self.ids.nom_client.text = self.nom
                self.ids.phone.readonly = True

                self.ids.passe.opacity = 1
                self.ids.repasse.opacity = 1
                self.ids.connexion.opacity = 0
                self.ids.connexions.opacity = 1
                self.ids.connexions.disabled = False
                self.ids.connexions.pos_hint = {"center_x": .5, "center_y": .10}
            except Exception as e:
                valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur",
                                       text="Le numéro du téléphone est introuvable!!!", buttons=[valider],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.conn.rollback()
                self.conn.close()
                self.ids.phone.text = ''
                self.ids.passe.text = ''

    def change_passe(self):
        passe = self.ids.passe.text
        repasse = self.ids.repasse.text

        if not passe or not repasse:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))
            self.erreur.open()
        else:
            if passe != repasse:
                ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur lors du remplissage",
                                       text="Les deux mot de passe ne correspond pas", buttons=[ok],
                                       size_hint_y=(.5))
                self.ids.passe.text = ''
                self.ids.repasse.text = ''
                self.erreur.open()
            else:
                passe = self.hacher(passe)
                try:
                    # Créer une base de données et une table si elles ne existent pas déjà
                    self.conn = sqlite3.connect('donner.db')
                    self.cursor = self.conn.cursor()
                    # Insérer le nom dans la base de données
                    self.cursor.execute('Select id_Client from client where nom_client = ?',
                                        (self.nom,))
                    id = self.cursor.fetchone()[0]
                    self.cursor.execute('update Client set mot_de_passe_client = ? where id_client = ?',
                                        (passe, id,))

                    valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                    self.erreur = MDDialog(title="Félicitation",
                                           text="Mot de passe changer avec succes!!!", buttons=[valider],
                                           size_hint_y=(.5))

                    self.erreur.open()
                    self.manager.transition.direction = 'up'

                    user_id = id  # On récupère l'ID du client ici
                    UserManager().user_id = user_id
                    self.manager.current = 'accueil_user'
                    self.conn.commit()
                except Exception as e:
                    valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                    self.erreur = MDDialog(title="Erreur",
                                           text=f"{e}!!!", buttons=[valider],
                                           size_hint_y=(.5))

                    self.erreur.open()
                    self.conn.rollback()
                    self.conn.close()
                    self.ids.repasse.text = ''
                    self.ids.passe.text = ''
                    self.conn.rollback()
                    self.conn.close()

    def hacher(self, x):
        salt = bcrypt.gensalt()
        self.hashed = bcrypt.hashpw(x.encode('utf-8'), salt)
        return self.hashed

    def close_dailog(self, obj):
        self.erreur.dismiss()
#========================Login====================================
class Login(MDScreen):
    def filter_input(self, instance):
        # Ne garde que les chiffres dans le champ de texte
        filtered_text = ''.join(filter(str.isdigit, instance.text))
       # if len(filtered_text) > 9:
       #     filtered_text = filtered_text[:9]  # Ne garde que les 9 premiers chiffres


        instance.text = filtered_text  # Met à jour le texte du champ
    def validate_user(self):
        phone = self.ids.phone.text
        passe = self.ids.passe.text
        status = 'Actifs'

        if not phone or not passe:
            self.show_error_dialog("Erreur lors du remplissage", "Veuillez remplir tous les champs")
            self.clear_fields()
            return

        self.conn = sqlite3.connect('donner.db')
        self.cursor = self.conn.cursor()
        try:
            if self.is_client(phone, passe, status):
                self.show_success_dialog("Félicitation", "Identification réussie!!!")
                self.manager.transition.direction = "up"
                self.manager.current = 'accueil_user'
            elif self.is_admin(phone, passe):
                self.show_success_dialog("Félicitation", "Identification réussie!!!")
                self.manager.transition.direction = "up"
                self.manager.current = 'accueil admin'
            else:
                self.show_error_dialog("Erreur", "Nom d'utilisateur ou mot de passe incorrect!!!")
            self.clear_fields()
        except Exception as e:
            self.show_error_dialog("Erreur", f"{e}!!!")
        finally:
            self.conn.close()

    def is_client(self, phone, passe, status):
        self.cursor.execute('SELECT mot_de_passe_client FROM Client WHERE telephone_client = ?', (phone,))
        result = self.cursor.fetchone()
        if result and self.verifier_mot_de_passe(passe, result[0]):
            self.cursor.execute(
                'SELECT id_client, nom_client FROM Client WHERE telephone_client = ? AND mot_de_passe_client = ? AND status = ?',
                (phone, result[0], status,))

            client_data = self.cursor.fetchone()
            if client_data:
                user_id = client_data[0]  # On récupère l'ID du client ici
                UserManager().user_id = user_id
                return True
        return False

    def is_admin(self, phone, passe):
        self.cursor.execute('SELECT id_admin FROM administrateur WHERE telephone_admin = ? AND mot_passe = ?',
                            (phone, passe,))
        admin_data = self.cursor.fetchone()
        if admin_data:
            user_id = admin_data[0]  # On récupère l'ID de l'administrateur ici
            UserManager().user_id = user_id
            return True
        return False

    def verifier_mot_de_passe(self, x, y):
        return bcrypt.checkpw(x.encode('utf-8'), y)

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def show_error_dialog(self, title, text):
        ok_button = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
        self.erreur = MDDialog(title=title, text=text, buttons=[ok_button], size_hint_y=(.5))
        self.erreur.open()

    def show_success_dialog(self, title, text):
        ok_button = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
        self.erreur = MDDialog(title=title, text=text, buttons=[ok_button], size_hint_y=(.5))
        self.erreur.open()

    def clear_fields(self):
        self.ids.phone.text = ''
        self.ids.passe.text = ''

class UserManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
            cls._instance.user_id = None  # ID utilisateur initialisé à None
        return cls._instance
####============================== Dans votre classe `ChangeProfile ===========:
class ChangeProfile(MDScreen):
    def on_enter(self):
        self.user_id = UserManager().user_id
        self.profile_client()

    def profile_client(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'SELECT nom_client, email_client, telephone_client, adresse_client, sexe_client FROM client WHERE id_client = ?',
                (self.user_id,))
            profile = self.cursor.fetchone()
            self.conn.commit()
            if profile:
                self.ids.noms.text = profile[0]
                self.ids.phones.text = str(profile[2])

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()


    def close_dailog(self, obj):
        self.erreur.dismiss()


    def deconnexion(self):
        oui = MDRaisedButton(text="oui", size_hint=(1,1), on_release=self.oui)
        non = MDRaisedButton(text="non", size_hint=(1, 1), on_release=self.non)
        self.erreur = MDDialog(
            title="Erreur !!!!!!!!!!!!!!",
            text="Voulez-vous vraiment vous Déconnecter ?????",
            buttons=[oui, non],
            size_hint_y=(.5)
        )
        self.erreur.open()

    def oui(self, a):
        self.manager.current = "connexion"
        self.erreur.dismiss()

    def non(self, b):
        self.erreur.dismiss()
class ChangeProfile_admin(MDScreen):
    def on_enter(self):
        self.user_id = UserManager().user_id
        self.profile_client()

    def profile_client(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'SELECT nom_admin, email_admin, telephone_admin, adresse_admin, sexe_admin FROM administrateur WHERE id_admin = ?',
                (self.user_id,))
            profile = self.cursor.fetchone()
            self.conn.commit()
            if profile:
                self.ids.noms.text = profile[0]
                self.ids.phones.text = str(profile[2])

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()


    def close_dailog(self, obj):
        self.erreur.dismiss()


    def deconnexion(self):
        oui = MDRaisedButton(text="oui", size_hint=(1,1), on_release=self.oui)
        non = MDRaisedButton(text="non", size_hint=(1, 1), on_release=self.non)
        self.erreur = MDDialog(
            title="Erreur !!!!!!!!!!!!!!",
            text="Voulez-vous vraiment vous Déconnecter ?????",
            buttons=[oui, non],
            size_hint_y=(.5)
        )
        self.erreur.open()

    def oui(self, a):
        self.manager.current = "connexion"
        self.erreur.dismiss()

    def non(self, b):
        self.erreur.dismiss()

class Compte(MDScreen):
    def profile_client(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'SELECT nom_client, email_client, telephone_client, adresse_client, sexe_client FROM client WHERE id_client = ?',
                (self.user_id,))
            profile = self.cursor.fetchone()
            self.conn.commit()
            if profile:
                self.ids.nom.text = profile[0]
                self.ids.email.text = profile[1]
                self.ids.phone.text = str(profile[2])
                self.ids.adresse.text = profile[3]
                self.ids.sexe.text = profile[4]
        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def menu_callbacks(self, text_item):
        self.ids.sexe.text = text_item
        self.menu_paiement.dismiss()

    def show_menu_genre(self):
        # Simuler les données de votre base de données
        self.genre = [
            "Masculin",
            "Feminin",
            "Autre"
        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem",
             "on_release": lambda x=societe: self.menu_callbacks(x)}
            for societe in self.genre
        ]

        # Créer le menu déroulant
        self.menu_paiement = MDDropdownMenu(
            caller=self.ids.sexe,
            items=menu_items,
            width_mult=4,
        )

        self.menu_paiement.open()

    def change_profile_user(self):
        self.valide_change(self.user_id)

    def on_enter(self):
        self.user_id = UserManager().user_id # Récupérer l'ID de l'utilisateur
        self.profile_client()
    def valide_change(self, id_client):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'UPDATE Client SET nom_client=?, email_client=?, telephone_client=?, adresse_client=?, sexe_client=? WHERE id_client=?',
                (
                    self.ids.nom.text, self.ids.email.text, self.ids.phone.text, self.ids.adresse.text,
                    self.ids.sexe.text,
                    id_client,))
            self.conn.commit()
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Félicitation",
                                   text="Changement effectué avec succès!", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def close_dailog(self, obj):
        self.erreur.dismiss()
class Compte_admin(MDScreen):
    def profile_client(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'SELECT nom_admin, email_admin, telephone_admin, adresse_admin, sexe_admin'
                ' FROM ADMINISTRATEUR WHERE id_admin = ?',
                (self.user_id,))
            profile = self.cursor.fetchone()
            self.conn.commit()
            if profile:
                self.ids.nom.text = profile[0]
                self.ids.email.text = profile[1]
                self.ids.phone.text = str(profile[2])
                self.ids.adresse.text = profile[3]
                self.ids.sexe.text = profile[4]
        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def menu_callbacks(self, text_item):
        self.ids.sexe.text = text_item
        self.menu_paiement.dismiss()

    def show_menu_genre(self):
        # Simuler les données de votre base de données
        self.genre = [
            "Masculin",
            "Feminin",
            "Autre"
        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem",
             "on_release": lambda x=societe: self.menu_callbacks(x)}
            for societe in self.genre
        ]

        # Créer le menu déroulant
        self.menu_paiement = MDDropdownMenu(
            caller=self.ids.sexe,
            items=menu_items,
            width_mult=4,
        )

        self.menu_paiement.open()

    def change_profile_user(self):
        self.valide_change(self.user_id)

    def on_enter(self):
        self.user_id = UserManager().user_id # Récupérer l'ID de l'utilisateur
        self.profile_client()
    def valide_change(self, id_client):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'UPDATE administrateur SET nom_admin=?, email_admin=?, telephone_admin=?, adresse_admin=?, sexe_admin=? WHERE id_admin=?',
                (
                    self.ids.nom.text, self.ids.email.text, self.ids.phone.text, self.ids.adresse.text,
                    self.ids.sexe.text,
                    id_client,))
            self.conn.commit()
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Félicitation",
                                   text="Changement effectué avec succès!", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def close_dailog(self, obj):
        self.erreur.dismiss()


class Histoirique_facture(MDScreen):

    def load_factures(self, id_societe):
        self.id_societe = id_societe
        self.show_historique_facture()  #
        self.reference()
    def reference(self):
        try:
            # Connexion à la base de données
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor3 = self.conn.cursor()
            self.cursor2 = self.conn.cursor()
            # Charger les factures du client
            self.cursor.execute(
                "SELECT count(id_facture) from facture where id_client =? and id_societe = ?",
                (UserManager().user_id,self.id_societe,))
            self.nbre = self.cursor.fetchone()
            if self.nbre != 0:
                self.ids.nbre_facture.text = str(self.nbre[0])

            self.cursor2.execute(
                "SELECT count(id_facture) from facture where id_client =? and status = ?and id_societe = ?",
                (UserManager().user_id,"Payée",self.id_societe,))
            self.nbre_payer = self.cursor2.fetchone()
            if self.nbre_payer != 0:
                self.ids.nbre_facture_payer.text = str(self.nbre_payer[0])

            self.cursor3.execute(
                "SELECT nom_client ,telephone_client from client where id_client =?",
                (UserManager().user_id,))
            self.ref = self.cursor3.fetchone()
            if self.ref != 0:
                self.ids.nom_client.text = (self.ref[0])
                self.ids.num_telephone.text = str(self.ref[1])
            self.conn.close()

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 12 !!!!!!!!!!!",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def show_historique_facture(self):
        try:
            # Connexion à la base de données
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()


            self.cursor.execute(
                "SELECT ID_FACTURE, MONTANT_FACTURE, STATUS,numero_abonne,mois FROM FACTURE WHERE id_client = ? AND id_societe = ?",
                (UserManager().user_id, self.id_societe,))
            factures = self.cursor.fetchall()

            # Ajouter des widgets pour chaque facture dans le ScrollView
            facture_container = self.ids.facture_container
            facture_container.clear_widgets()  # Clear existing widgets

            for facture in factures:
                id_facture, self.montant, status,numero,self.mois = facture

                facture_layout = MDFloatLayout(
                    size_hint=(1, None), height=dp(80), md_bg_color='white', radius=[10],elevation=5)
                if self.id_societe == 3:
                    facture_layout.add_widget(
                        MDLabel(
                            text=str(numero),
                            pos_hint={"center_x": .3, 'center_y': .8},
                            font_size="28sp",
                            font_name='Verdana',
                            size_hint=(.6, .1),
                        )
                    )
                else:
                    facture_layout.add_widget(
                        MDLabel(
                            text=str(id_facture),
                            pos_hint={"center_x": .3, 'center_y': .8},
                            font_size="28sp",
                            font_name='Regular',
                            size_hint=(.6, .1),
                        )
                    )
                facture_layout.add_widget(
                    MDLabel(
                        text=str(self.mois),
                        pos_hint={"center_x": .3, 'center_y': .5},
                        font_size="28sp",
                        font_name='Verdana',
                        size_hint=(.6, .1),
                    )
                )
                facture_layout.add_widget(
                    MDLabel(
                        text=str(self.montant),
                        pos_hint={"center_x": .86, 'center_y': .5},
                        font_size="18sp",
                        font_name='Time',
                        size_hint=(.6, .1),
                        color="green",
                        bold=True,
                    )
                )
                facture_layout.add_widget(
                    MDLabel(
                        text="FCFA",
                        pos_hint={"center_x": .98, 'center_y': .5},
                        font_size="18sp",
                        font_name='Time',
                        size_hint=(.3, .1),
                        color="green",
                    )
                )

                # Bouton pour visualiser la facture

                if status !="Payée":
                    """facture_layout.add_widget(
                        MDRaisedButton(
                            text="Payer",
                            pos_hint={"center_x":.2, 'center_y': .3},
                            size_hint=(.3, .1),
                            font_name='Regular',
                            #on_release=lambda x, id_facture=self.id_societe: self.open_pdf(id_facture)
                            #on_release=lambda x,id_factures=id_facture, montant=self.montant: self.mobile_money_1(id_factures, montant),
                        )
                    )"""
                    facture_layout.md_bg_color=('red')
                    facture_layout.add_widget(
                        MDIconButton(
                            icon='',
                            pos_hint={"center_x": .9, 'center_y': .12},
                            size_hint=(.2, .3),
                            on_release=lambda x, id_factures=id_facture, id_societe=self.id_societe,mois=self.mois, montant=self.montant: self.bouton_impayer(
                                id_factures,id_societe, montant,mois),

                        )

                    )
                    facture_layout.add_widget(
                        Image(
                            source='image/images.png',
                            pos_hint={"center_x": .9, 'center_y': .2},
                            size_hint=(.8, .4),
                            color='red',

                        )
                    )
                else:
                    facture_layout.add_widget(
                        MDLabel(
                            text=status,
                            pos_hint={"center_x": .3, 'center_y': .1},
                            font_size="22sp",
                            size_hint=(.4, .1),
                            color='green',
                            font_name='Time',
                        )
                    )
                    facture_layout.add_widget(
                        MDIconButton(
                            icon='',
                            pos_hint={"center_x":.9, 'center_y': .15},
                            size_hint=(.2, .3),
                            on_release=lambda x, id_factures=id_facture, montant=self.montant: self.bouton_payer(
                                id_factures, montant),

                        )

                    )
                    facture_layout.add_widget(
                    Image(
                        source='image/images.png',
                        pos_hint={"center_x": .9, 'center_y': .2},
                        size_hint=(.8, .4),

                         )
                    )
                if self.id_societe == 1:
                    self.ids.image.source="image/logo.png"
                    self.ids.image.size=("150dp", "100dp")

                elif self.id_societe == 2:
                    self.ids.image.source="image/logo lcde.png"
                    self.ids.image.size=("100dp", "100dp")
                elif self.id_societe ==3:
                    self.ids.image.source = "image/logo congo.jpg"
                    self.ids.image.size=("100dp", "100dp")
                facture_container.add_widget(facture_layout)
            self.conn.close()

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 13 !!!!!!!!!!!",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()


    def close_dailog(self, obj):
        self.erreur.dismiss()

    def open_pdf(self, id_facture):
        # Construire le chemin vers le fichier PDF
        pdf_path = f"file:///C:/Users/EL%20VERDUGO/Desktop/avancer/image/{id_facture}.pdf"
        # Ouvrir le fichier PDF
        webbrowser.open(pdf_path)
    def modify_pdf_SNE(self, pdf_path, output_path, name,montant,id_facture):
        # Ouvrir le PDF existant
        pdf_document = fitz.open(pdf_path)
        #time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

        # Choisir la première page
        page = pdf_document[0]
        #times_new_roman = fitz.Font("MPoppins.ttf")
        date_paiement = datetime.now().strftime("Le %d/%m/%Y à %H:%M:%S")
        try:
            self.conn = sqlite3.connect("donner.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("select mois from paiement where id_facture =?",(id_facture,))
            mois = self.cursor.fetchone()[0]
        except Exception as e:
            print(e)
            self.conn.rollback()
            self.conn.close()

        # Ajouter le nom à la position souhaitée
        page.insert_text((100, 275), name, fontsize=14, color=(0, 0, 0))  # Nom client
        page.insert_text((99, 130), date_paiement, fontsize=14, color=(0, 0, 0))  # Numéro de branchement
        page.insert_text((80, 315), date_paiement, fontsize=14, color=(0, 0, 0))  # Numéro de branchement
        page.insert_text((300, 430), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        page.insert_text((300, 452), str(montant), fontsize=14, color=(0, 0, 0))  # Montant l
        page.insert_text((300, 473), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        page.insert_text((150, 223), str(id_facture), fontsize=14, color=(0, 0, 0))  # Numero facture
        page.insert_text((100, 400), mois, fontsize=14, color=(0, 0, 0))  # Numero facture


        # Enregistrer le PDF modifié
        pdf_document.save(output_path)
        pdf_document.close()
    def modify_pdf_LCDE(self, pdf_path, output_path, name,montant,id_facture):
        # Ouvrir le PDF existant
        pdf_document = fitz.open(pdf_path)
        #time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

        # Choisir la première page
        page = pdf_document[0]
        #times_new_roman = fitz.Font("MPoppins.ttf")
        try:
            self.conn = sqlite3.connect("donner.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("select date_paiement,mETHODE_paiement from paiement where id_facture = ?",
                                (id_facture,))
            date = self.cursor.fetchall()
            date = [i[0] for i in date]
            self.cursor1 = self.conn.cursor()
            self.cursor1.execute("select methode_paiement from paiement where id_facture = ?",
                                (id_facture,))
            methode = self.cursor1.fetchone()[0]
        except Exception as e:
            print(e)
            self.conn.rollback()
            self.conn.close()

        # Ajouter le nom à la position souhaitée
        page.insert_text((300, 275), name, fontsize=14, color=(0, 0, 0))  # Nom client
        page.insert_text((210, 465), str(id_facture), fontsize=14, color=(0, 0, 0))  # id_facture
        page.insert_text((220, 200), date, fontsize=14, color=(0, 0, 0))  # date de la facture
        page.insert_text((180, 715), methode, fontsize=16, color=(0, 0, 0))  # methode de branchement
        #page.insert_text((300, 430), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        #page.insert_text((300, 452), str(montant), fontsize=14, color=(0, 0, 0))  # Montant l
        #page.insert_text((300, 473), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        #page.insert_text((150, 223), str(id_facture), fontsize=14, color=(0, 0, 0))  # Numero facture

        # Enregistrer le PDF modifié
        pdf_document.save(output_path)
        pdf_document.close()

    def modify_pdfs(self, pdf_path, output_path, name,montant,id_facture,mois):
        if self.id_societe == 1:
            pdf_document = fitz.open(pdf_path)
            # time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

            # Choisir la première page
            page = pdf_document[0]
            # times_new_roman = fitz.Font("MPoppins.ttf")
            date_paiement = datetime.now().strftime("Le %d/%m/%Y à %H:%M:%S")

            # Ajouter le nom à la position souhaitée
            page.insert_text((400, 115), name, fontsize=14, color=(0, 0, 0))  # Nom client HAUT PAGE
            page.insert_text((255, 115), str(id_facture), fontsize=14, color=(0, 0, 0))  # Nom client HAUT PAGE
            page.insert_text((380, 86), mois, fontsize=14, color=(0, 0, 0))  # Mois client HAUT PAGE

            page.insert_text((520, 420), str(montant), fontsize=14, color=(0, 0, 0))  # MONTANT client HAUT PAGE
            page.insert_text((450, 795), str(montant), fontsize=16, color=(0, 0, 0))  # MONTANT client BAS PAGE

            page.insert_text((300, 765), name, fontsize=16, color=(0, 0, 0))  # Nom client BAS PAGE
            page.insert_text((450, 765), mois, fontsize=16, color=(0, 0, 0))  # MOIS client BAS PAGE

            # Enregistrer le PDF modifié
            pdf_document.save(output_path)
            pdf_document.close()
        else:
            # Ouvrir le PDF existant
            pdf_document = fitz.open(pdf_path)
            #time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

            # Choisir la première page
            page = pdf_document[0]
            #times_new_roman = fitz.Font("MPoppins.ttf")
            date_paiement = datetime.now().strftime("Le %d/%m/%Y à %H:%M:%S")

            # Ajouter le nom à la position souhaitée
            #page.insert_text((100, 400), name, fontsize=14, color=(1, 0, 1))  # Nom client
           # page.insert_text((99, 130), date_paiement, fontsize=14, color=(0, 0, 1))  # Numéro de branchement
           # page.insert_text((80, 315), date_paiement, fontsize=14, color=(0, 0, 1))  # Numéro de branchement
           # page.insert_text((300, 430), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
           # page.insert_text((300, 452), str(montant), fontsize=14, color=(0, 0, 0))  # Montant l
            #page.insert_text((300, 473), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
            #page.insert_text((150, 223), str(id_facture), fontsize=14, color=(0, 0, 0))  # Numero facture

            # Enregistrer le PDF modifié
            pdf_document.save(output_path)
            pdf_document.close()

    def bouton_impayer(self,id_facture,id_societe,montant,mois):

        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))

            nom = self.cursor.fetchone()
            self.nom = nom[0]
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
        # Exemple d'utilisation de la méthode modify_pdf
        if id_societe == 1:
            pdf_path = 'image/FACTURE E²C.pdf'  # Chemin vers le PDF original
        else:
            pdf_path = 'image/facture LCDE.pdf'

        output_path = 'image/facture modifier.pdf'  # Chemin vers le PDF modifié
        name = self.nom  # Nom à ajouter
        montant=montant
        id_facture=id_facture
        mois = mois

        self.modify_pdfs(pdf_path, output_path, name,montant,id_facture,mois)
        self.open_pdf("facture modifier")

    def bouton_payer(self,id_facture,montant):

        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))

            nom = self.cursor.fetchone()
            self.nom = nom[0]
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
        # Exemple d'utilisation de la méthode modify_pdf
        if self.id_societe == 1:
            pdf_path = 'image/Reçus SNE.pdf'  # Chemin vers le PDF original
            output_path = 'image/facture modifier.pdf'  # Chemin vers le PDF modifié
            name = self.nom  # Nom à ajouter
            montant = montant
            id_facture = id_facture

            self.modify_pdf_SNE(pdf_path, output_path, name, montant, id_facture)
            self.open_pdf("facture modifier")
        else:
            pdf_path = "image/Reçu LCDE SA.pdf"
            output_path = 'image/facture modifier.pdf'  # Chemin vers le PDF modifié
            name = self.nom  # Nom à ajouter
            montant=montant
            id_facture=id_facture

            self.modify_pdf_LCDE(pdf_path, output_path, name,montant,id_facture)
            self.open_pdf("facture modifier")


    def mobile_money(self,montant):

        # Afficher une boîte de dialogue de succès
        oui = MDRaisedButton(text="Oui", on_release=lambda x:self.trans())
        non = MDRaisedButton(text="Non", on_release=lambda x:self.mob.dismiss())
        self.mob = MDDialog(title="Message Maxigesse",
                               text=f"Voulez-vous approuver {montant} FCFA pour Maxigesse Corporation",
                            buttons=[oui,non])

        self.mob.open()
    def trans(self):
        self.mob.dismiss()
        self.mobile_money_2()

    def mobile_money_2(self,montant):

        # Création d'un dialogue avec MDTextField pour entrer le mot de passe
        self.mob2 = MDDialog(
            title=f"Le point agrée 242064980498 a initie un retrait d'argent de votre compte,Montant {montant}.\n"
                        f"Veuillez entrez votre code pin pour confirmer:",
            type="custom",
            content_cls=MDTextField(
                hint_text=""),
            buttons=[
                MDRaisedButton(text="Envoyer", on_release=lambda x: self.mobile_money_1()),
                MDRaisedButton(text="Annuler", on_release=lambda x: self.mob2.dismiss())]
        )
        self.mob2.open()


    def mobile_money_1(self,montant):
        self.mob2.dismiss()
        date_paiement = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.da = date_paiement
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute(
                "INSERT INTO PAIEMENT (ID_FACTURE, MONTANT,type_abonne, DATE_PAIEMENT, METHODE_PAIEMENT) "
                "VALUES (?, ?,?, ?, ?)"
                , (self.num_facture, montant, "", self.da, self.me))

            self.cursor.execute("UPDATE FACTURE SET STATUS = 'Payée' WHERE ID_FACTURE = ?",
                                (self.num_facture,))
            self.conn.commit()
            success_dialog = MDDialog(
                title="Message Maxigesse ",
                text=f"Vous avez confirmer le retrait de {montant} FCFA initier par le point agrée - 242064980498 \n"
                     f"Numero de la transaction 202412345.",

                buttons=[MDRaisedButton(text="OK", on_release=lambda x: success_dialog.dismiss())]

            )
            success_dialog.open()
            self.show_success_dialog("Paiement effectué avec succès.")
           # self.on_button_click()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.show_error_dialog(f"Erreur lors du paiement:{e}")


    def NomUser(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))
            nom = self.cursor.fetchone()
            self.nom = nom[0]

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.show_error_dialog(f"Erreur lors :{e}")


class Histoirique_paiement(MDScreen):

    def load_factures(self, id_societe):
        self.id_societe = id_societe
        self.show_historique_facture()  #
        self.reference()
    def reference(self):
        try:
            # Connexion à la base de données
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor3 = self.conn.cursor()
            # Charger les factures du client
            self.cursor.execute(
                "SELECT count(id_facture) from paiement where id_client =? and id_societe = ?",
                (UserManager().user_id,self.id_societe,))
            self.nbre = self.cursor.fetchone()
            if self.nbre != 0:
                self.ids.nbre_facture_payer.text = str(self.nbre[0])

            self.cursor3.execute(
                "SELECT nom_client ,telephone_client from client where id_client =?",
                (UserManager().user_id,))
            self.ref = self.cursor3.fetchone()
            if self.ref != 0:
                self.ids.nom_client.text = (self.ref[0])
                self.ids.num_telephone.text = str(self.ref[1])
            self.conn.close()

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 12 !!!!!!!!!!!",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def show_historique_facture(self):
        try:
            # Connexion à la base de données
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()


            self.cursor.execute(
                "SELECT ID_FACTURE, MONTANT,numero_abonne,mois FROM paiement WHERE id_client = ? and id_societe = ?",
                (UserManager().user_id,self.id_societe,))
            factures = self.cursor.fetchall()

            # Ajouter des widgets pour chaque facture dans le ScrollView
            facture_container = self.ids.facture_container
            facture_container.clear_widgets()  # Clear existing widgets

            for facture in factures:
                id_facture, self.montant,numero,mois = facture

                facture_layout = MDFloatLayout(
                    size_hint=(1, None), height=dp(80), md_bg_color='white', radius=[10],elevation=5)
                if self.id_societe == 3:
                    facture_layout.add_widget(
                        MDLabel(
                            text=str(numero),
                            pos_hint={"center_x": .3, 'center_y': .8},
                            font_size="28sp",
                            font_name='Verdana',
                            size_hint=(.6, .1),
                        )
                    )
                else:
                    facture_layout.add_widget(
                        MDLabel(
                            text=str(id_facture),
                            pos_hint={"center_x": .3, 'center_y': .8},
                            font_size="28sp",
                            font_name='Regular',
                            size_hint=(.6, .1),
                        )
                    )
                facture_layout.add_widget(
                    MDLabel(
                        text=str(mois),
                        pos_hint={"center_x": .3, 'center_y': .5},
                        font_size="28sp",
                        font_name='Verdana',
                        size_hint=(.6, .1),
                    )
                )
                facture_layout.add_widget(
                    MDLabel(
                        text=str(self.montant),
                        pos_hint={"center_x": .86, 'center_y': .5},
                        font_size="18sp",
                        font_name='Time',
                        size_hint=(.6, .1),
                        color="green",
                        bold=True,
                    )
                )
                facture_layout.add_widget(
                    MDLabel(
                        text="FCFA",
                        pos_hint={"center_x": .98, 'center_y': .5},
                        font_size="18sp",
                        font_name='Time',
                        size_hint=(.3, .1),
                        color="green",
                    )
                )

                # Bouton pour visualiser la facture
                status = "Payée"
                facture_layout.add_widget(
                    MDLabel(
                        text=status,
                        pos_hint={"center_x": .3, 'center_y': .1},
                        font_size="22sp",
                        size_hint=(.4, .1),
                        color='green',
                        font_name='Time',
                    )
                )
                facture_layout.add_widget(
                    MDIconButton(
                        icon='',
                        pos_hint={"center_x": .9, 'center_y': .15},
                        size_hint=(.2, .3),
                        on_release=lambda x, id_factures=id_facture, montant=self.montant: self.bouton_payer(
                            id_factures, montant),

                    )

                )
                facture_layout.add_widget(
                    Image(
                        source='image/images.png',
                        pos_hint={"center_x": .9, 'center_y': .2},
                        size_hint=(.8, .4),

                    )
                )


                if self.id_societe == 1:
                    self.ids.image.source="image/logo.png"
                    self.ids.image.size=("150dp", "100dp")
                elif self.id_societe == 2:
                    self.ids.image.source="image/logo lcde.png"
                    self.ids.image.size=("100dp", "100dp")
                elif self.id_societe ==3:
                    self.ids.image.source = "image/logo congo.jpg"
                    self.ids.image.size=("100dp", "100dp")
                facture_container.add_widget(facture_layout)
            self.conn.close()

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 13 !!!!!!!!!!!",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()


    def close_dailog(self, obj):
        self.erreur.dismiss()

    def open_pdf(self, id_facture):
        # Construire le chemin vers le fichier PDF
        pdf_path = f"file:///C:/Users/EL%20VERDUGO/Desktop/avancer/image/{id_facture}.pdf"
        # Ouvrir le fichier PDF
        webbrowser.open(pdf_path)
    def modify_pdf_SNE(self, pdf_path, output_path, name,montant,id_facture):
        # Ouvrir le PDF existant
        pdf_document = fitz.open(pdf_path)
        #time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

        # Choisir la première page
        page = pdf_document[0]
        #times_new_roman = fitz.Font("MPoppins.ttf")
        date_paiement = datetime.now().strftime("Le %d/%m/%Y à %H:%M:%S")
        try:
            self.conn = sqlite3.connect("donner.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("select mois from paiement where id_facture =?",(id_facture,))
            mois = self.cursor.fetchone()[0]
        except Exception as e:
            print(e)
            self.conn.rollback()
            self.conn.close()

        # Ajouter le nom à la position souhaitée
        page.insert_text((100, 275), name, fontsize=14, color=(0, 0, 0))  # Nom client
        page.insert_text((99, 130), date_paiement, fontsize=14, color=(0, 0, 0))  # Numéro de branchement
        page.insert_text((80, 315), date_paiement, fontsize=14, color=(0, 0, 0))  # Numéro de branchement
        page.insert_text((300, 430), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        page.insert_text((300, 452), str(montant), fontsize=14, color=(0, 0, 0))  # Montant l
        page.insert_text((300, 473), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        page.insert_text((150, 223), str(id_facture), fontsize=14, color=(0, 0, 0))  # Numero facture
        page.insert_text((100, 400), mois, fontsize=14, color=(0, 0, 0))  # Numero facture


        # Enregistrer le PDF modifié
        pdf_document.save(output_path)
        pdf_document.close()
    def modify_pdf_LCDE(self, pdf_path, output_path, name,montant,id_facture):
        # Ouvrir le PDF existant
        pdf_document = fitz.open(pdf_path)
        #time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

        # Choisir la première page
        page = pdf_document[0]
        #times_new_roman = fitz.Font("MPoppins.ttf")
        try:
            self.conn = sqlite3.connect("donner.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("select date_paiement,mETHODE_paiement from paiement where id_facture = ?",
                                (id_facture,))
            date = self.cursor.fetchall()
            date = [i[0] for i in date]
            self.cursor1 = self.conn.cursor()
            self.cursor1.execute("select mETHODE_paiement from paiement where id_facture = ?",
                                (id_facture,))
            methode = self.cursor1.fetchone()[0]
        except Exception as e:
            print(e)
            self.conn.rollback()
            self.conn.close()

        # Ajouter le nom à la position souhaitée
        page.insert_text((300, 275), name, fontsize=14, color=(0, 0, 0))  # Nom client
        page.insert_text((210, 465), str(id_facture), fontsize=14, color=(0, 0, 0))  # id_facture
        page.insert_text((220, 200), date, fontsize=14, color=(0, 0, 0))  # date de la facture
        page.insert_text((180, 715), methode, fontsize=16, color=(0, 0, 0))  # methode de branchement
        #page.insert_text((300, 430), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        #page.insert_text((300, 452), str(montant), fontsize=14, color=(0, 0, 0))  # Montant l
        #page.insert_text((300, 473), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
        #page.insert_text((150, 223), str(id_facture), fontsize=14, color=(0, 0, 0))  # Numero facture

        # Enregistrer le PDF modifié
        pdf_document.save(output_path)
        pdf_document.close()

    def modify_pdfs(self, pdf_path, output_path, name,montant,id_facture,mois):
        if self.id_societe == 1:
            pdf_document = fitz.open(pdf_path)
            # time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

            # Choisir la première page
            page = pdf_document[0]
            # times_new_roman = fitz.Font("MPoppins.ttf")
            date_paiement = datetime.now().strftime("Le %d/%m/%Y à %H:%M:%S")

            # Ajouter le nom à la position souhaitée
            page.insert_text((400, 115), name, fontsize=14, color=(0, 0, 0))  # Nom client HAUT PAGE
            page.insert_text((255, 115), str(id_facture), fontsize=14, color=(0, 0, 0))  # Nom client HAUT PAGE
            page.insert_text((380, 86), mois, fontsize=14, color=(0, 0, 0))  # Mois client HAUT PAGE

            page.insert_text((520, 420), str(montant), fontsize=14, color=(0, 0, 0))  # MONTANT client HAUT PAGE
            page.insert_text((450, 795), str(montant), fontsize=16, color=(0, 0, 0))  # MONTANT client BAS PAGE

            page.insert_text((300, 765), name, fontsize=16, color=(0, 0, 0))  # Nom client BAS PAGE
            page.insert_text((450, 765), mois, fontsize=16, color=(0, 0, 0))  # MOIS client BAS PAGE

            # Enregistrer le PDF modifié
            pdf_document.save(output_path)
            pdf_document.close()
        else:
            # Ouvrir le PDF existant
            pdf_document = fitz.open(pdf_path)
            #time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

            # Choisir la première page
            page = pdf_document[0]
            #times_new_roman = fitz.Font("MPoppins.ttf")
            date_paiement = datetime.now().strftime("Le %d/%m/%Y à %H:%M:%S")

            # Ajouter le nom à la position souhaitée
            #page.insert_text((100, 400), name, fontsize=14, color=(1, 0, 1))  # Nom client
           # page.insert_text((99, 130), date_paiement, fontsize=14, color=(0, 0, 1))  # Numéro de branchement
           # page.insert_text((80, 315), date_paiement, fontsize=14, color=(0, 0, 1))  # Numéro de branchement
           # page.insert_text((300, 430), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
           # page.insert_text((300, 452), str(montant), fontsize=14, color=(0, 0, 0))  # Montant l
            #page.insert_text((300, 473), str(montant), fontsize=14, color=(0, 0, 0))  # Montant
            #page.insert_text((150, 223), str(id_facture), fontsize=14, color=(0, 0, 0))  # Numero facture

            # Enregistrer le PDF modifié
            pdf_document.save(output_path)
            pdf_document.close()


    def bouton_payer(self,id_facture,montant):

        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))

            nom = self.cursor.fetchone()
            self.nom = nom[0]
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
        # Exemple d'utilisation de la méthode modify_pdf
        if self.id_societe == 1:
            pdf_path = 'image/Reçus SNE.pdf'  # Chemin vers le PDF original
            output_path = 'image/facture modifier.pdf'  # Chemin vers le PDF modifié
            name = self.nom  # Nom à ajouter
            montant = montant
            id_facture = id_facture

            self.modify_pdf_SNE(pdf_path, output_path, name, montant, id_facture)
            self.open_pdf("facture modifier")
        else:
            pdf_path = "image/Reçu LCDE SA.pdf"
            output_path = 'image/facture modifier.pdf'  # Chemin vers le PDF modifié
            name = self.nom  # Nom à ajouter
            montant=montant
            id_facture=id_facture

            self.modify_pdf_LCDE(pdf_path, output_path, name,montant,id_facture)
            self.open_pdf("facture modifier")


    def mobile_money(self,montant):

        # Afficher une boîte de dialogue de succès
        oui = MDRaisedButton(text="Oui", on_release=lambda x:self.trans())
        non = MDRaisedButton(text="Non", on_release=lambda x:self.mob.dismiss())
        self.mob = MDDialog(title="Message Maxigesse",
                               text=f"Voulez-vous approuver {montant} FCFA pour Maxigesse Corporation",
                            buttons=[oui,non])

        self.mob.open()
    def trans(self):
        self.mob.dismiss()
        self.mobile_money_2()

    def mobile_money_2(self,montant):

        # Création d'un dialogue avec MDTextField pour entrer le mot de passe
        self.mob2 = MDDialog(
            title=f"Le point agrée 242064980498 a initie un retrait d'argent de votre compte,Montant {montant}.\n"
                        f"Veuillez entrez votre code pin pour confirmer:",
            type="custom",
            content_cls=MDTextField(
                hint_text=""),
            buttons=[
                MDRaisedButton(text="Envoyer", on_release=lambda x: self.mobile_money_1()),
                MDRaisedButton(text="Annuler", on_release=lambda x: self.mob2.dismiss())]
        )
        self.mob2.open()


    def mobile_money_1(self,montant):
        self.mob2.dismiss()
        date_paiement = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.da = date_paiement
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute(
                "INSERT INTO PAIEMENT (ID_FACTURE, MONTANT,type_abonne, DATE_PAIEMENT, METHODE_PAIEMENT) "
                "VALUES (?, ?,?, ?, ?)"
                , (self.num_facture, montant, "", self.da, self.me))

            self.cursor.execute("UPDATE FACTURE SET STATUS = 'Payée' WHERE ID_FACTURE = ?",
                                (self.num_facture,))
            self.conn.commit()
            success_dialog = MDDialog(
                title="Message Maxigesse ",
                text=f"Vous avez confirmer le retrait de {montant} FCFA initier par le point agrée - 242064980498 \n"
                     f"Numero de la transaction 202412345.",

                buttons=[MDRaisedButton(text="OK", on_release=lambda x: success_dialog.dismiss())]

            )
            success_dialog.open()
            self.show_success_dialog("Paiement effectué avec succès.")
           # self.on_button_click()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.show_error_dialog(f"Erreur lors du paiement:{e}")


    def NomUser(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))
            nom = self.cursor.fetchone()
            self.nom = nom[0]

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.show_error_dialog(f"Erreur lors :{e}")

class Histoirique_paiement_priver(MDScreen):

    def load_factures(self, id_societe):
        self.id_societe = id_societe
        self.show_historique_facture()  #
        self.reference()
    def reference(self):
        try:
            # Connexion à la base de données
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor3 = self.conn.cursor()
            # Charger les factures du client
            self.cursor.execute(
                "SELECT count(id_facture) from paiement where id_client =? and id_societe = ?",
                (UserManager().user_id,self.id_societe,))
            self.nbre = self.cursor.fetchone()
            if self.nbre != 0:
                self.ids.nbre_facture.text = str(self.nbre[0])
            self.cursor3.execute(
                "SELECT nom_client ,telephone_client from client where id_client =?",
                (UserManager().user_id,))
            self.ref = self.cursor3.fetchone()
            if self.ref != 0:
                self.ids.nom_client.text = (self.ref[0])
                self.ids.num_telephone.text = str(self.ref[1])
            self.conn.close()

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 12 !!!!!!!!!!!",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def show_historique_facture(self):
        try:
            # Connexion à la base de données
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()


            self.cursor.execute(
                "SELECT ID_FACTURE,Id_client, montant,numero_abonne,mois,type_abonne,date_paiement FROM Paiement WHERE id_client = ? and id_societe = ? ",
                (UserManager().user_id,self.id_societe,))
            factures = self.cursor.fetchall()

            # Ajouter des widgets pour chaque facture dans le ScrollView
            facture_container = self.ids.facture_container
            facture_container.clear_widgets()  # Clear existing widgets

            for facture in factures:
                id_facture,id_client, self.montant,numero,self.mois,self.type_abonne,self.date_paiement = facture

                facture_layout = MDFloatLayout(
                    size_hint=(1, None), height=dp(80), md_bg_color='white', radius=[10],elevation=5)
                facture_layout.add_widget(
                    MDLabel(
                        text=str(numero),
                        pos_hint={"center_x": .3, 'center_y': .8},
                        font_size="28sp",
                        font_name='Verdana',
                        size_hint=(.6, .1),
                    )
                )
                facture_layout.add_widget(
                    MDLabel(
                        text=str(self.mois),
                        pos_hint={"center_x": .3, 'center_y': .5},
                        font_size="28sp",
                        font_name='Verdana',
                        size_hint=(.6, .1),
                    )
                )
                facture_layout.add_widget(
                    MDLabel(
                        text=str(self.montant),
                        pos_hint={"center_x": .86, 'center_y': .5},
                        font_size="18sp",
                        font_name='Time',
                        size_hint=(.6, .1),
                        color="green",
                        bold=True,
                    )
                )
                facture_layout.add_widget(
                    MDLabel(
                        text="FCFA",
                        pos_hint={"center_x": .98, 'center_y': .5},
                        font_size="18sp",
                        font_name='Time',
                        size_hint=(.3, .1),
                        color="green",
                    )
                )

                # Bouton pour visualiser la facture
                status = 'Payée'
                facture_layout.add_widget(
                    MDLabel(
                        text=status,
                        pos_hint={"center_x": .3, 'center_y': .1},
                        font_size="22sp",
                        size_hint=(.4, .1),
                        color='green',
                        font_name='Time',
                    )
                )
                facture_layout.add_widget(
                    MDIconButton(
                        icon='',
                        pos_hint={"center_x": .9, 'center_y': .15},
                        size_hint=(.2, .3),
                        on_release=lambda x, id_factures=id_facture, mois=self.mois, type_abonne=self.type_abonne,
                                          date_paiement=self.date_paiement
                                          , montant=self.montant: self.on_button_click(
                            id_factures, montant, mois, type_abonne, date_paiement),

                    )

                )
                facture_layout.add_widget(
                    Image(
                        source='image/images.png',
                        pos_hint={"center_x": .9, 'center_y': .2},
                        size_hint=(.8, .4),

                    )
                )
                if self.id_societe == 1:
                    self.ids.image.source="image/logo.png"
                    self.ids.image.size=("150dp", "100dp")


                elif self.id_societe == 2:
                    self.ids.image.source="image/logo lcde.png"
                    self.ids.image.size=("100dp", "100dp")
                elif self.id_societe ==3:
                    self.ids.image.source = "image/logo congo.jpg"
                    self.ids.image.size=("100dp", "100dp")
                facture_container.add_widget(facture_layout)
            self.conn.close()

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 13 !!!!!!!!!!!",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()


    def close_dailog(self, obj):
        self.erreur.dismiss()

    def open_pdf(self, id_facture):
        # Construire le chemin vers le fichier PDF
        pdf_path = f"file:///C:/Users/EL%20VERDUGO/Desktop/avancer/image/{id_facture}.pdf"
        # Ouvrir le fichier PDF
        webbrowser.open(pdf_path)
    def modify_pdf(self, pdf_path, output_path, name,montant,id_facture,mois,type,date):
        # Ouvrir le PDF existant
        pdf_document = fitz.open(pdf_path)
        #time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

        # Choisir la première page
        page = pdf_document[0]
        #times_new_roman = fitz.Font("MPoppins.ttf")
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute("select mois,type_abonne,date_paiement,numero_abonne from paiement where id_facture = ?",(id_facture,))
            tous = self.cursor.fetchone()
            numero_abonne = (tous[3])
        except Exception as e :
            print(e)
            self.conn.rollback()
            self.conn.close()

        # Ajouter le nom à la position souhaitée
        page.insert_text((130, 259), name, fontsize=16, color=(0, 0, 0))  # Nom client
        page.insert_text((330, 259), date, fontsize=16, color=(0, 0, 0))  # Nom client

        page.insert_text((30, 335), str(id_facture), fontsize=14, color=(0, 0, 0))  # Numero facture
        page.insert_text((220, 335), str(mois), fontsize=14, color=(0, 0, 0))  # mois de branchement
        page.insert_text((300, 335), type, fontsize=14, color=(0, 0, 0))  # Numéro de branchement
        page.insert_text((403, 335), str(numero_abonne), fontsize=14, color=(0, 0, 0))  # Numéro de branchement


        page.insert_text((460, 424), str(montant), fontsize=16, color=(0, 0, 0))  # Montant


        # Enregistrer le PDF modifié
        pdf_document.save(output_path)
        pdf_document.close()
    def on_button_click(self,id_facture,montant,mois,type,date):

        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))

            nom = self.cursor.fetchone()
            self.nom = nom[0]
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
        # Exemple d'utilisation de la méthode modify_pdf
        #if id_facture == 1:
        pdf_path = 'image/reçu telecom.pdf'  # Chemin vers le PDF original

        output_path = 'image/facture modifier.pdf'  # Chemin vers le PDF modifié
        name = self.nom  # Nom à ajouter
        montant=montant
        id_facture=id_facture
        mois=mois
        type=type
        date=date


        self.modify_pdf(pdf_path, output_path, name,montant,id_facture,mois,type,date)
        self.open_pdf("facture modifier")




#==================================Accueil ======================

class Accueil(MDScreen):
    def on_enter(self):
        self.user_id = UserManager().user_id  # Récupérer l'ID de l'utilisateur
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'SELECT nom_client, email_client, telephone_client, adresse_client, sexe_client FROM client WHERE id_client = ?',
                (self.user_id,))
            profile = self.cursor.fetchone()
            self.conn.commit()
            if profile:
                self.ids.nom.text = profile[0]

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 1",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

        Clock.schedule_interval(self.switch_next_slide, 20)

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def switch_next_slide(self, dt):
        carousel = self.ids.carousel
        if carousel.index == len(carousel.slides) - 1:
            carousel.index = 0  # Réinitialiser à la première diapositive si à la dernière
        else:
            carousel.load_next(mode='next')

class Accueil_admin(MDScreen):
    def on_enter(self):
        self.user_id = UserManager().user_id  # Récupérer l'ID de l'utilisateur
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                'SELECT nom_admin, email_admin, telephone_admin, adresse_admin, sexe_admin FROM administrateur WHERE id_admin = ?',
                (self.user_id,))
            profile = self.cursor.fetchone()
            self.conn.commit()
            if profile:
                self.ids.nom.text = profile[0]

        except Exception as e:
            valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur 1",
                                   text=f"{e}", buttons=[valider],
                                   size_hint_y=(.5))
            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

        Clock.schedule_interval(self.switch_next_slide, 20)

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def switch_next_slide(self, dt):
        carousel = self.ids.carousel
        if carousel.index == len(carousel.slides) - 1:
            carousel.index = 0  # Réinitialiser à la première diapositive si à la dernière
        else:
            carousel.load_next(mode='next')

#========================Inscription====================================
class Inscription(MDScreen):
    def validate_email(self, instance):
        # Expression régulière pour valider le format de l'email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        email_text = instance.text

        if re.match(email_pattern, email_text):
            instance.line_color_normal = (0.8, 1, 0.8, 1)  # Vert clair pour un email valide
        else:
            instance.line_color_normal = (1, 0.8, 0.8, 1)  # Rouge clair pour un email invalide
    # Fonction pour hacher un mot de passe
    def menu_callbacks(self, text_item):
        self.ids.sexe.text = text_item
        self.menu_paiement.dismiss()
    def show_menu_genre(self):
        # Simuler les données de votre base de données
        self.genre = [
            "Masculin",
            "Feminin",
            "Autre"
        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem",
             "on_release": lambda x=societe: self.menu_callbacks(x)}
            for societe in self.genre
        ]

        # Créer le menu déroulant
        self.menu_paiement = MDDropdownMenu(
            caller=self.ids.sexe,
            items=menu_items,
            width_mult=4,
        )

        self.menu_paiement.open()

    def hacher(self, x):
        salt = bcrypt.gensalt()
        self.hashed = bcrypt.hashpw(x.encode('utf-8'), salt)
        return self.hashed

    def inscription(self):
        if self.ids.checkbox.active:
            nom = self.ids.nom.text
            email = self.ids.email.text
            passe = self.ids.passe.text
            con_passe = self.ids.con_passe.text
            phone = self.ids.phone.text
            adresse = self.ids.adresse.text
            sexe = self.ids.sexe.text
            today = datetime.now()
            jour = (today.strftime('%d/%m/%Y'))
            status = "Actifs"
            if not nom or not email or not phone or not passe or not con_passe or not adresse or not sexe:
                ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur lors du remplissage",
                                       text="Veuillez remplir tous les champs", buttons=[ok],
                                       size_hint_y=(.5))
                self.ids.nom.text = ''
                self.ids.email.text = ''
                self.ids.phone.text = ''
                self.ids.passe.text = ''
                self.ids.con_passe.text = ''
                self.ids.adresse.text = ''
                self.ids.sexe.text = ''
                self.erreur.open()
            elif passe != con_passe:
                ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur lors du remplissage",
                                       text="Les deux mot de passe ne correspond pas", buttons=[ok],
                                       size_hint_y=(.5))
                self.ids.passe.text = ''
                self.ids.con_passe.text = ''
                self.erreur.open()
            else:
                # Créer une base de données et une table si elles ne existent pas déjà
                self.conn = sqlite3.connect('donner.db')
                self.cursor = self.conn.cursor()
                passe = self.hacher(passe)

                try:
                    self.cursor.execute("select telephone_client from client where 1")
                    tel = self.cursor.fetchall()
                    tel = [i[0] for i in tel]
                    self.cursor.execute("select email_client from client where 1")
                    email_existe = self.cursor.fetchall()
                    email_existe = [i[0] for i in email_existe]

                    if phone in tel:
                        ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                        self.erreur = MDDialog(title="Erreur de saisie",
                                               text=f"Le {phone} existe déjà.\nVeuillez changer de numéro.", buttons=[ok],
                                               size_hint_y=(.5))
                        self.erreur.open()
                    elif email in email_existe:
                        ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                        self.erreur = MDDialog(title="Erreur de saisie",
                                               text=f"{email} existe déjà.\nVeuillez changer d'email.",
                                               buttons=[ok],
                                               size_hint_y=(.5))
                        self.erreur.open()
                    else:
                        self.cursor.execute("INSERT INTO CLIENT (ID_ADMIN,NOM_CLIENT,EMAIL_CLIENT"
                                        ",MOT_DE_PASSE_CLIENT,TELEPHONE_CLIENT,DATE_D_INSCRIPTION,ADRESSE_CLIENT,SEXE_CLIENT,status)"
                                           " VALUES (?,?,?,?,?,?,?,?,?)",
                                        ("2", nom, email, passe, phone, jour, adresse, sexe, status,))

                        ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                        self.erreur = MDDialog(title="Félicitation !!!!",
                                               text="Inscription effectué avec succès", buttons=[ok],
                                               size_hint_y=(.5))
                        self.erreur.open()
                        self.cursor.execute("select id_client from client where nom_client = ?", (nom,))
                        id = self.cursor.fetchone()
                        self.conn.commit()
                        UserManager().user_id = id[0]
                        self.erreur.open()
                        self.ids.nom.text = ''
                        self.ids.email.text = ''
                        self.ids.con_passe.text = ''
                        self.ids.phone.text = ''
                        self.ids.passe.text = ''
                        self.ids.adresse.text = ''
                        self.ids.sexe.text = ''
                        self.manager.current = 'accueil_user'
                except Exception as e:
                    Fermer = MDRaisedButton(text="Fermer", size_hint=(1, 1), on_release=self.close_dailog)
                    self.erreur = MDDialog(title="Erreur!!!!!!!!!!!!!!",
                                           text=f"{e}", buttons=[Fermer],
                                           size_hint_y=(.5))
                    self.erreur.open()
                    self.conn.rollback()
                    self.conn.close()
        else:
            ok = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez accepter les termes et conditions pour vous inscrires", buttons=[ok],
                                   size_hint_y=(.5))
            self.erreur.open()


    def close_dailog(self, obj):
        self.erreur.dismiss()


#========================Client====================================

class gestion_client(MDScreen):

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def on_pre_enter(self):
        self.creer_tableau()

    def get_row_data(self, factures):
        return [(facture_id, montant, status) for facture_id, montant, status in factures]

    def filter_data(self):
        # Récupérer le texte du champ de filtrage
        filter_text = self.ids.recherche.text.lower()
        # Filtrer les données
        self.filtered_row_data = [
            facture for facture in self.factures_initiales
            if facture[0].lower().startswith(filter_text) or # Filtrer par nom de société
             facture[1].lower().startswith(filter_text)  # Filtrer par nom de société
        ]

        # Mettre à jour le DataTable avec les données filtrées
        self.tableau.row_data = [
            (nom, email, phone, adresse, sexe,status)
            for nom, email, phone, adresse, sexe,status in self.filtered_row_data
        ]
    def creer_tableau(self):
        try:
            connection = sqlite3.connect("donner.db")
            cursor = connection.cursor()
            cursor.execute("SELECT nom_client,email_client,telephone_client,adresse_client,sexe_client,status FROM client")
            client = cursor.fetchall()
            connection.commit()

            self.factures_initiales = [
                (nom, email, phone, adresse, sexe, status)
                for nom, email, phone, adresse, sexe, status in client

            ]
            self.filtered_row_data = self.factures_initiales  # Initialement, tout est visible


            tableau_paiement = MDDataTable(
                size_hint=(.9, .5),
                pos_hint={'center_x': 0.5, 'center_y': .53},
                use_pagination=True,
                rows_num=4,
                column_data=[
                    ("Nom du Client", dp(45)),
                    ("Email du Client", dp(45)),
                    ("N°Téléphone du Client", dp(45)),
                    ("Adresse du Client", dp(45)),
                    ("Sexe du Client", dp(45)),
                    ("Status du Client", dp(45)),

                ],
                row_data=[
                    (nom, email, phone, adresse, sexe, status)
                    for nom, email, phone, adresse, sexe, status in self.filtered_row_data
                ]
            )
            self.tableau = tableau_paiement
            self.add_widget(tableau_paiement)
            self.ids.recherche.on_text_validate = self.filter_data

        except Exception as e:
            Fermer = MDRaisedButton(text="Fermer", size_hint=(.8, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur!!!!!!!!!!!!!!",
                                   text=f"{e}", buttons=[Fermer],
                                   size_hint_y=(.5))
            self.erreur.open()
            connection.rollback()
            connection.close()

class bloque_client(MDScreen):

    def blocage_client(self):
        nom_client = self.ids.nom_client.text
        status = 'Inactifs'
        if not nom_client:
            ok = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.nom_client.text = ""
            self.erreur.open()
        else:

            # Créer une base de données et une table si elles ne existent pas déjà
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            try:
                # Insérer le nom dans la base de données
                self.cursor.execute("update client set status = ? where nom_client = ?",
                                    (status, nom_client,))
                self.conn.commit()
                self.valide = MDRaisedButton(text="OK", size_hint=(1,1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Félicitation",
                                       text=f"Mr {nom_client} a été Bloqué avec succès!!!", buttons=[self.valide],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.ids.nom_client.text = ""
                self.manager.current = 'bloquez client'
            except Exception as e:
                self.valide = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur !!!!!!!!",
                                       text=f"Erreur au niveau de {e}!!!",
                                       buttons=[self.valide],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.conn.rollback()
                self.conn.close()

    def deblocage_client(self):
        nom_client = self.ids.nom_client.text
        status = 'Actifs'
        if not nom_client:
            ok = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.nom_client.text = ""
            self.erreur.open()
        else:

            # Créer une base de données et une table si elles ne existent pas déjà
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            try:
                # Insérer le nom dans la base de données
                self.cursor.execute("update client set status = ? where nom_client = ?",
                                    (status, nom_client,))
                self.conn.commit()
                self.valide = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Félicitation",
                                       text=f"Mr {nom_client} a été débloqué avec succès!!!", buttons=[self.valide],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.ids.nom_client.text = ""
                self.manager.current = 'debloquez client'
            except Exception as e:
                self.valide = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur !!!!!!!!",
                                       text=f"Erreur au niveau de {e}!!!",
                                       buttons=[self.valide],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.conn.rollback()
                self.conn.close()

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def show_menu(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Insérer le nom dans la base de données
            national = 'National'
            self.cursor.execute(
                "select nom_client,email_client,telephone_client,adresse_client,sexe_client,status from client where status =?",
                ("Actifs",))
            self.client = self.cursor.fetchall()
            self.client = [i[0] for i in self.client]
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()

        menu_items = [
            {"text": client, "viewclass": "OneLineListItem", "on_release": lambda x=client: self.menu_callback(x)}
            for client in self.client
        ]

        # Créer le menu déroulant
        self.menu_client = MDDropdownMenu(
            caller=self.ids.nom_client,
            items=menu_items,
            width_mult=4,
        )
        self.menu_client.open()
    def show_menu_bloquer(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Insérer le nom dans la base de données
            national = 'National'
            self.cursor.execute(
                "select nom_client,email_client,telephone_client,adresse_client,sexe_client,status from client where status =?"
                ,("Inactifs",))
            self.client = self.cursor.fetchall()
            if self.client !=None:
                self.client_bloquer = [i[0] for i in self.client]
                self.conn.commit()

            menu_items = [
                {"text": client, "viewclass": "OneLineListItem", "on_release": lambda x=client: self.menu_callback(x)}
                for client in self.client_bloquer
            ]

            # Créer le menu déroulant
            self.menu_client = MDDropdownMenu(
                caller=self.ids.nom_client,
                items=menu_items,
                width_mult=4,
            )
            self.menu_client.open()
        except Exception as e:
            ok = MDRaisedButton(text="OK", size_hint=(.6, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text=f"Erreur au niveau {e}", buttons=[ok],
                                   size_hint_y=(.5))


            self.erreur.open()
            self.conn.rollback()
            self.conn.close()

    def menu_callback(self, text_item):
        self.ids.nom_client.text = text_item
        self.menu_client.dismiss()


#========================gestion_societer====================================
class Ajouter_societer(MDScreen):
    nom_societe = ObjectProperty(None)
    type_societe = ObjectProperty(None)
    dialog = None

    def ajouter_societe(self):
        societe = self.ids.nom_societe.text
        type = self.ids.type_societe.text

        if not societe or not type:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.nom_societe.text = ""
            self.ids.type_societe.text = ""
            self.erreur.open()
        else:

            # Créer une base de données et une table si elles ne existent pas déjà
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            try:
                # Insérer le nom dans la base de données
                self.cursor.execute("INSERT INTO societe (id_admin,nom_societe,type_societe) VALUES (?,?,?)",
                                    ("Popa", societe, type,))
                self.conn.commit()
                valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Félicitation",
                                       text=f"{societe} Ajouter avec succès!!!", buttons=[valider],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.ids.nom_societe.text = ""
                self.ids.type_societe.text = ""

            except Exception as e:
                Fermer = MDRaisedButton(text="Fermer", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur!!!!!!!!!!!!!!",
                                       text=f"{e}", buttons=[Fermer],
                                       size_hint_y=(.5))
                self.erreur.open()
                self.conn.rollback()
                self.conn.close()

    def close_dailog(self, obj):
        self.erreur.dismiss()


class gestion_societe(MDScreen):
    def close_dailog(self, obj):
        self.erreur.dismiss()

    def on_pre_enter(self):
        self.creer_tableau()

    def get_row_data(self, factures):
        return [(facture_id, montant, status) for facture_id, montant, status in factures]

    def filter_data(self):
        # Récupérer le texte du champ de filtrage
        filter_text = self.ids.recherche.text.lower()
        # Filtrer les données
        self.filtered_row_data = [
            facture for facture in self.factures_initiales
            if facture[1].lower().startswith(filter_text)  # Filtrer par nom de société
        ]

        # Mettre à jour le DataTable avec les données filtrées
        self.tableau.row_data = [
            (nom, type_societe)
            for societe_id, nom, type_societe in self.filtered_row_data
        ]

    def creer_tableau(self):
        try:
            connection = sqlite3.connect("donner.db")
            cursor = connection.cursor()
            cursor.execute("SELECT id_societe, nom_societe, type_societe FROM societe")
            self.societe_donnees = cursor.fetchall()
            connection.commit()

            self.factures_initiales = [
                (societe_id, nom, type_societe)
                for societe_id, nom, type_societe in self.societe_donnees
            ]
            self.filtered_row_data = self.factures_initiales  # Initialement, tout est visible

            tableau = MDDataTable(
                size_hint=(.9, .5),
                pos_hint={'center_x': 0.5, 'center_y': .43},
                use_pagination=True,

                rows_num=4,
                column_data=[
                    ("Nom de la société", dp(45)),
                    ("Type de société", dp(30))

                ],
                row_data=[
                    (nom, type_societe)
                    for societe_id, nom, type_societe in self.filtered_row_data
                ]
            )

            tableau.bind(on_row_press=self.on_row_press)

            self.tableau = tableau
            self.add_widget(tableau)
            self.ids.recherche.on_text_validate = self.filter_data
        except Exception as e:
            Fermer = MDRaisedButton(text="Fermer", size_hint=(.8, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur",
                                   text=f"{e}", buttons=[Fermer],
                                   size_hint_y=(.5))
            self.erreur.open()
            connection.rollback()
        finally:
            connection.close()

    def on_row_press(self, instance_table, instance_row):
        # Récupérer les informations de la ligne sélectionnée
        row_data = instance_row.text.split()
        societe_id = row_data[0]
        # Déterminer l'action en fonction de la colonne sélectionnée
        col_index = instance_table.ids
        if col_index == 2:  # Colonne "Modifier"
            self.confirmer_action(societe_id)
        elif col_index == 3:  # Colonne "Supprimer"
            self.confirmer_action(societe_id)

    def confirmer_action(self, societe_id):

        # Ajout du canvas pour la couleur de fond
        #self.modifier(societe_id)
        self.ids.label_societe.opacity=1
        self.ids.recherche.opacity=1
        self.ids.valider_societe.opacity=1
        self.ids.icone.opacity=1
        self.ids.card.opacity=1

        connection = sqlite3.connect("donner.db")
        cursor = connection.cursor()
        cursor.execute('select nom_societe,type_societe from societe WHERE nom_societe like "%?%"',
                       (societe_id,))
        nom = cursor.fetchall()
        # type = cursor.fetchone()[1]

        connection.commit()
        connection.close()


        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 1)  # Couleur primaire de l'application
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        # Création de la MDCard
        card = MDCard(
            size_hint=(0.9, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.82},
            md_bg_color="yellow",
            radius=[2],
        )

        # Ajout de la label au card
        label = MDLabel(
            text="Modifier une Société",
            pos_hint={"center_y": 0.5},
            halign="center",
            font_style="H4",
            italic=True,
            bold=True,
            color='blue',

        )
        card.add_widget(label)

        # Ajout de la carte au layout principal
        self.add_widget(card)

        # Création d'un second MDFloatLayout pour les champs de texte
        fields_layout = MDFloatLayout(
            size_hint=(0.92, 0.56),
            pos_hint={'center_x': 0.5, 'center_y': 0.44},
            md_bg_color='white',
            radius=[2]
        )

        # Champ pour le nom de la société
        self.nom_societe = MDTextField(
            size_hint=(None, None),
            width=50,
            pos_hint={'center_x': 0.5, 'center_y': .9},
            hint_text="Nom de la société",
            icon_right="home-outline",
            mode="rectangle",
            size_hint_x=0.9,
            required=True,
            line_color_focus='yellow',
            line_color_normal="blue",
            text= nom[0]
        )
        fields_layout.add_widget(self.nom_societe)

        # Champ pour le type de la société
        self.type_societe = MDTextField(
            hint_text="Type de société",
            pos_hint={'center_x': 0.5, 'center_y': .7},
            icon_right="file-document-outline",
            mode="rectangle",
            size_hint_x=0.9,
            required=True,
            line_color_focus='yellow',
            line_color_normal="blue"
        )
        fields_layout.add_widget(self.type_societe)

        # Bouton de validation
        validate_button = MDRaisedButton(
            text="Valider",
            size_hint=(.9, .1),
            pos_hint={'center_x': 0.5, 'center_y': .07},
            height="40dp",
            font_size="22sp",
            md_bg_color=self.theme_cls.accent_color,
            on_release=self.modifier
        )
        fields_layout.add_widget(validate_button)

        # Ajout du layout de champs au layout principal
        self.add_widget(fields_layout)

        # Bouton de retour
        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={ "center_y": 0.96},
            md_bg_color="white",
            color= "white",
            on_release=lambda x:self.go_back()
        )
        self.add_widget(back_button)

    def fermer_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()

    def executer_action(self, action, societe_id):
        self.fermer_dialog(None)
        if action == "supprimer":
            self.supprimer_societe(societe_id)
        elif action == "modifier":
            self.modifier_societe(societe_id)

    def supprimer_societe(self, societe_id):
        connection = sqlite3.connect("donner.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM societe WHERE id_societe=?", (societe_id,))
        connection.commit()
        connection.close()
        self.creer_tableau()

    def modifier_societe(self, societe_id):
        # Logique pour modifier la société, par exemple ouvrir un autre écran pour éditer les informations
        pass


#========================gestion_paiement====================================
class Ajouter_paiement(MDScreen):
    nom_societe = ObjectProperty(None)
    type_societe = ObjectProperty(None)
    dialog = None

    def ajouter_paiement(self):
        paiement = self.ids.nom_paiement.text

        if not paiement or not type:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.nom_paiement.text = ""
            self.erreur.open()
        else:

            # Créer une base de données et une table si elles ne existent pas déjà
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            try:
                # Insérer le nom dans la base de données
                self.cursor.execute("INSERT INTO paiement(ID_FACTURE,MONTANT,DATE_PAIEMENT,METHODE_PAIEMENT)"
                                    " VALUES (?,?,?,?)",
                                    ('', '', '', paiement,))
                self.conn.commit()
                valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Félicitation",
                                       text=f"{paiement} Ajouter avec succès!!!", buttons=[valider],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.ids.nom_paiement.text = ""


            except Exception as e:
                self.conn.rollback()
                self.conn.close()

    def close_dailog(self, obj):
        self.erreur.dismiss()


class gestion_paiement(MDScreen):
    def close_dailog(self, obj):
        self.erreur.dismiss()

    def on_pre_enter(self):
        self.creer_tableau()

    def get_row_data(self, factures):
        return [(facture_id, montant) for facture_id, montant in factures]

    def filter_data(self):
        # Récupérer le texte du champ de filtrage
        filter_text = self.ids.recherche.text.lower()
        # Filtrer les données
        self.filtered_row_data = [
            facture for facture in self.factures_initiales
            if facture[0].lower().startswith(filter_text)  # Filtrer par nom de société
        ]

        # Mettre à jour le DataTable avec les données filtrées
        self.tableau.row_data = [
            (nom,)
            for nom in self.filtered_row_data
        ]

    def creer_tableau(self):
        try:
            connection = sqlite3.connect("donner.db")
            cursor = connection.cursor()
            cursor.execute("SELECT methode_paiement FROM paiement")
            self.paiement = cursor.fetchall()
            self.paiement = [i[0] for i in self.paiement]
            connection.commit()

            self.factures_initiales = [
                (nom)
                for nom in self.paiement
            ]
            self.filtered_row_data = self.factures_initiales  # Initialement, tout est visible

            tableau_paiement = MDDataTable(
                size_hint=(.9, .5),
                pos_hint={'center_x': 0.5, 'center_y': .43},
                use_pagination=True,
                rows_num=4,
                column_data=[
                    ("Nom du paiement", dp(45))
                ],
                row_data=[
                    (nom,)
                    for nom in self.filtered_row_data
                ]
            )
            self.add_widget(tableau_paiement)
            self.tableau = tableau_paiement
            #self.add_widget(tableau_paiement)
            self.ids.recherche.on_text_validate = self.filter_data
        except Exception as e:
            Fermer = MDRaisedButton(text="Fermer", size_hint=(.8, .6), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur!!!!!!!!!!!!!!",
                                   text=f"{e}", buttons=[Fermer],
                                   size_hint_y=(.5))
            self.erreur.open()
            connection.rollback()
            connection.close()

    def on_row_press(self, instance_table, instance_row):
        # Récupérer les informations de la ligne sélectionnée
        row_data = instance_row.text.split()
        societe_id = row_data[0]
        if societe_id == '[font=Icons]󰏫[/font]':
            self.confirmer_action(societe_id)
        elif societe_id == "Energie":
            self.confirmer_action(societe_id)
        elif societe_id == "La":
            self.confirmer_action(societe_id)

    def confirmer_action(self, societe_id):

        # Ajout du canvas pour la couleur de fond
        # self.modifier(societe_id)
        self.ids.label_societe.opacity = 0
        self.ids.recherche.opacity = 0
        self.ids.valider_societe.opacity = 0
        self.ids.icone.opacity = 0
        self.ids.card.opacity = 0

        connection = sqlite3.connect("donner.db")
        cursor = connection.cursor()
        cursor.execute('select nom_societe,type_societe from societe WHERE nom_societe like "%?%"',
                       (societe_id,))
        nom = cursor.fetchall()
        # type = cursor.fetchone()[1]

        connection.commit()
        connection.close()

        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 1)  # Couleur primaire de l'application
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        # Création de la MDCard
        card = MDCard(
            size_hint=(0.9, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.82},
            md_bg_color="yellow",
            radius=[2],
        )

        # Ajout de la label au card
        label = MDLabel(
            text="Modifier une Société",
            pos_hint={"center_y": 0.5},
            halign="center",
            font_style="H4",
            italic=True,
            bold=True,
            color='blue',

        )
        card.add_widget(label)

        # Ajout de la carte au layout principal
        self.add_widget(card)

        # Création d'un second MDFloatLayout pour les champs de texte
        fields_layout = MDFloatLayout(
            size_hint=(0.92, 0.56),
            pos_hint={'center_x': 0.5, 'center_y': 0.44},
            md_bg_color='white',
            radius=[2]
        )

        # Champ pour le nom de la société
        self.nom_societe = MDTextField(
            size_hint=(None, None),
            width=50,
            pos_hint={'center_x': 0.5, 'center_y': .9},
            hint_text="Nom de la société",
            icon_right="home-outline",
            mode="rectangle",
            size_hint_x=0.9,
            required=True,
            line_color_focus='yellow',
            line_color_normal="blue"
        )
        fields_layout.add_widget(self.nom_societe)

        # Champ pour le type de la société
        self.type_societe = MDTextField(
            hint_text="Type de société",
            pos_hint={'center_x': 0.5, 'center_y': .7},
            icon_right="file-document-outline",
            mode="rectangle",
            size_hint_x=0.9,
            required=True,
            line_color_focus='yellow',
            line_color_normal="blue"
        )
        fields_layout.add_widget(self.type_societe)

        # Bouton de validation
        validate_button = MDRaisedButton(
            text="Valider",
            size_hint=(.9, .1),
            pos_hint={'center_x': 0.5, 'center_y': .07},
            height="40dp",
            font_size="22sp",
            md_bg_color=self.theme_cls.accent_color,
            on_release=self.modifier
        )
        fields_layout.add_widget(validate_button)

        # Ajout du layout de champs au layout principal
        self.add_widget(fields_layout)

        # Bouton de retour
        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={"center_y": 0.96},
            md_bg_color="white",
            color="white",
            on_release=lambda x: self.go_back()
        )
        self.add_widget(back_button)

    def _update_rect(self, *args):
        # Met à jour la taille du rectangle lorsque la taille change
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "gestion paiement"

    def modifier(self, societe_id):
        nom = self.nom_societe.text
        type_societe = self.type_societe.text
        try:
            connection = sqlite3.connect("donner.db")
            cursor = connection.cursor()
            cursor.execute("update societe set nom_societe =?,type_societe = ? WHERE id_societe=?",
                           (nom, type_societe, societe_id,))
            connection.commit()
        except Exception as e:
            connection.close()

#========================gestion facture====================================
class Ajouter_facture(MDScreen):

    def ajouter_factures(self):
        today = datetime.now()
        jour = (today.strftime('%d/%m/%Y'))
        montant = self.ids.montant_facture.text
        nom_client = self.ids.nom_client.text
        nom_societe = self.ids.nom_societe.text
        mois_societe = self.ids.mois_societe.text
        date_debut = today.strptime('22/11/2024', '%d/%m/%Y')
        date_fin_str = date_debut + timedelta(days=15)
        date_fin = date_fin_str.strftime('%d/%m/%Y')
        status = 'Impayer'

        if not montant or not nom_client or not nom_societe or not mois_societe or not date_fin or not status:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.nom_societe.text = ""
            self.ids.mois_societe.text = ""
            self.ids.montant_facture.text = ""
            self.ids.nom_client.text = ""
            self.erreur.open()
        else:

            # Créer une base de données et une table si elles ne existent pas déjà
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            try:
                # Insérer le nom dans la base de données
                self.cursor.execute("select id_societe from societe where nom_societe = ?",
                                    (nom_societe,))
                id_societe = self.cursor.fetchone()[0]
                # Insérer le nom dans la base de données
                self.cursor.execute(
                    "INSERT INTO FACTURE (MONTANT_FACTURE, ID_CLIENT, ID_SOCIETE, DATE_DEBUT, DATE_FIN, STATUS, numero_abonne,mois)"
                    " VALUES (?, ?, ?, ?, ?, ?,?,?)",
                    (montant, nom_client, id_societe, jour, date_fin, status,"",mois_societe,))
                self.conn.commit()
                valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Félicitation",
                                       text=f"Facture de la societé {nom_societe} a été ajouter avec succès!!!",
                                       buttons=[valider],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.ids.nom_societe.text = ""
                self.ids.mois_societe.text = ""
                self.ids.montant_facture.text = ""
                self.ids.nom_client.text = ""
                self.manager.current = 'ajouter facture'
            except Exception as e:
                validers = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur !!!!!!!!",
                                       text=f"Erreur au niveau de {e}!!!",
                                       buttons=[validers],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.conn.rollback()
                self.conn.close()

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def show_menu(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Insérer le nom dans la base de données
            national = 'National'
            self.cursor.execute("select nom_societe from societe where type_societe = ?", (national,))
            self.societes = self.cursor.fetchall()
            self.societes = [i[0] for i in self.societes]
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()

        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem", "on_release": lambda x=societe: self.menu_callback(x)}
            for societe in self.societes
        ]

        # Créer le menu déroulant
        self.menu_societe = MDDropdownMenu(
            caller=self.ids.nom_societe,
            items=menu_items,
            width_mult=4,
        )
        self.menu_societe.open()

    def menu_callback(self, text_item):
        self.ids.nom_societe.text = text_item
        self.menu_societe.dismiss()
    def show_menu_mois(self):
        # Simuler les données de votre base de données
        self.mois = [
            "Janvier",
            "Fevrier",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Decembre",

        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items_mois = [
            {"text": mois, "viewclass": "OneLineListItem",
             "on_release": lambda x=mois: self.menu_callback_mois(x)}
            for mois in self.mois
        ]

        # Créer le menu déroulant
        self.menu_mois = MDDropdownMenu(
            caller=self.ids.mois_societe,
            items=menu_items_mois,
            width_mult=4,
        )

        self.menu_mois.open()

    def menu_callback_mois(self, text_item):
        self.ids.mois_societe.text = text_item
        self.menu_mois.dismiss()



class gestion_facture(MDScreen):
    def close_dailog(self, obj):
        self.erreur.dismiss()

    def on_pre_enter(self):
        self.creer_tableau()
    def get_row_data(self, factures):
        return [(facture_id, montant, status) for facture_id, montant, status in factures]

    def filter_data(self):
        # Récupérer le texte du champ de filtrage
        filter_text = self.ids.recherche.text.lower()
        # Filtrer les données
        self.filtered_row_data = [
            facture for facture in self.factures_initiales
            if facture[1].lower().startswith(filter_text) or  # Filtrer par nom de la facture
             facture[2].lower().startswith(filter_text)   # Filtrer par nom du client
        ]

        # Mettre à jour le DataTable avec les données filtrées
        self.tableau.row_data = [
            (facture_id,societe, client, montant, status,mois)
            for facture_id, societe, client, montant, status,mois in self.filtered_row_data
        ]

    def creer_tableau(self):
        try:
            connection = sqlite3.connect("donner.db")
            cursor = connection.cursor()
            cursor.execute(
                "SELECT ID_FACTURE,(select nom_societe from societe where societe.id_societe = facture.id_societe) as nom_facture"
                ",id_client, montant_facture,status,mois FROM facture")
            societe_donnees = cursor.fetchall()
            connection.commit()

            self.factures_initiales = [
                (facture_id, societe, client, montant, status,mois)
                for facture_id, societe, client, montant, status,mois in societe_donnees

            ]

            self.filtered_row_data = self.factures_initiales  # Initialement, tout est visible

            tableau = MDDataTable(
                size_hint=(.9, .5),
                pos_hint={'center_x': 0.5, 'center_y': .43},
                use_pagination=True,
                rows_num=4,
                column_data=[
                    ("N°Facture", dp(20)),
                    ("Nom Societe", dp(40)),
                    ("Nom Client", dp(20)),
                    ("Montant", dp(15)),
                    ("Status", dp(15)),
                    ("Mois", dp(25)),

                ],
                row_data=[
                    (facture_id,societe, client, montant, status,mois)
                    for facture_id, societe, client, montant, status,mois in self.filtered_row_data
                ]
            )

            #tableau.bind(on_row_press=self.on_row_press)

            self.tableau = tableau
            self.add_widget(tableau)
            self.ids.recherche.on_text_validate = self.filter_data
        except Exception as e:
            Fermer = MDRaisedButton(text="Fermer", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur!!!!!!!!!!!!!!",
                                   text=f"{e}", buttons=[Fermer],
                                   size_hint_y=(.5))
            self.erreur.open()
            connection.rollback()
            connection.close()

    def on_row_press(self, instance_table, instance_row):
        # Récupérer les informations de la ligne sélectionnée
        row_data = instance_row.text.split()
        societe_id = row_data[0]
        if societe_id == '[font=Icons]󰏫[/font]':
            self.confirmer_action(societe_id)
        elif societe_id == "Energie":
            self.confirmer_action(societe_id)
        elif societe_id == "La":
            self.confirmer_action(societe_id)

    def confirmer_action(self, societe_id):

        # Ajout du canvas pour la couleur de fond
        # self.modifier(societe_id)
        self.ids.label_societe.opacity = 0
        self.ids.recherche.opacity = 0
        self.ids.valider_societe.opacity = 0
        self.ids.icone.opacity = 0
        self.ids.card.opacity = 0

        connection = sqlite3.connect("donner.db")
        cursor = connection.cursor()
        cursor.execute('select nom_societe,type_societe from societe WHERE nom_societe like "%?%"',
                       (societe_id,))
        nom = cursor.fetchall()
        # type = cursor.fetchone()[1]

        connection.commit()
        connection.close()

        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 1)  # Couleur primaire de l'application
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        # Création de la MDCard
        card = MDCard(
            size_hint=(0.9, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.82},
            md_bg_color="yellow",
            radius=[2],
        )

        # Ajout de la label au card
        label = MDLabel(
            text="Modifier une Société",
            pos_hint={"center_y": 0.5},
            halign="center",
            font_style="H4",
            italic=True,
            bold=True,
            color='blue',

        )
        card.add_widget(label)

        # Ajout de la carte au layout principal
        self.add_widget(card)

        # Création d'un second MDFloatLayout pour les champs de texte
        fields_layout = MDFloatLayout(
            size_hint=(0.92, 0.56),
            pos_hint={'center_x': 0.5, 'center_y': 0.44},
            md_bg_color='white',
            radius=[2]
        )

        # Champ pour le nom de la société
        self.nom_societe = MDTextField(
            size_hint=(None, None),
            width=50,
            pos_hint={'center_x': 0.5, 'center_y': .9},
            hint_text="Nom de la société",
            icon_right="home-outline",
            mode="rectangle",
            size_hint_x=0.9,
            required=True,
            line_color_focus='yellow',
            line_color_normal="blue"
        )
        fields_layout.add_widget(self.nom_societe)

        # Champ pour le type de la société
        self.type_societe = MDTextField(
            hint_text="Type de société",
            pos_hint={'center_x': 0.5, 'center_y': .7},
            icon_right="file-document-outline",
            mode="rectangle",
            size_hint_x=0.9,
            required=True,
            line_color_focus='yellow',
            line_color_normal="blue"
        )
        fields_layout.add_widget(self.type_societe)

        # Bouton de validation
        validate_button = MDRaisedButton(
            text="Valider",
            size_hint=(.9, .1),
            pos_hint={'center_x': 0.5, 'center_y': .07},
            height="40dp",
            font_size="22sp",
            md_bg_color=self.theme_cls.accent_color,
            on_release=self.modifier
        )
        fields_layout.add_widget(validate_button)

        # Ajout du layout de champs au layout principal
        self.add_widget(fields_layout)

        # Bouton de retour
        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={"center_y": 0.96},
            md_bg_color="white",
            color="white",
            on_release=lambda x: self.go_back()
        )
        self.add_widget(back_button)

    def _update_rect(self, *args):
        # Met à jour la taille du rectangle lorsque la taille change
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "gestion facture"

    def modifier(self, societe_id):
        nom = self.nom_societe.text
        type_societe = self.type_societe.text
        try:
            connection = sqlite3.connect("donner.db")
            cursor = connection.cursor()
            cursor.execute("update societe set nom_societe =?,type_societe = ? WHERE id_societe=?",
                           (nom, type_societe, societe_id,))
            connection.commit()
        except Exception as e:
            connection.close()


#========================gestion facture priver====================================
class Ajouter_facture_priver(MDScreen):

    def ajouter_factures_priver(self):
        today = datetime.now()
        jour = (today.strftime('%d/%m/%Y'))
        num_abonne = self.ids.num_abonne.text
        nom_client = self.ids.nom_client.text
        nom_societe = self.ids.nom_societe.text
        date_debut = today.strptime('22/08/2024', '%d/%m/%Y')
        date_fin_str = date_debut + timedelta(days=15)
        date_fin = date_fin_str.strftime('%d/%m/%Y')
        status = 'Impayer'

        if not nom_client or not nom_societe or not date_fin or not status or not num_abonne:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.nom_societe.text = ""
            self.ids.nom_client.text = ""
            self.ids.num_abonne.text = ""
            self.erreur.open()
        else:
            # Créer une base de données et une table si elles ne existent pas déjà
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            try:

                # Insérer le nom dans la base de données
                self.cursor.execute("select id_societe from societe where nom_societe = ?",
                                    (nom_societe,))
                id_societe = self.cursor.fetchone()[0]
                self.cursor.execute(
                    "INSERT INTO FACTURE (numero_abonne,MONTANT_FACTURE, ID_CLIENT, ID_SOCIETE, DATE_DEBUT, DATE_FIN, STATUS)"
                    " VALUES (?,?,?, ?, ?, ?,?)",
                    (num_abonne, '', nom_client, id_societe, jour, date_fin, status,))
                self.conn.commit()
                valider = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Félicitation",
                                       text=f"Facture de la societé {nom_societe} a été ajouter avec succès!!!",
                                       buttons=[valider],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.ids.nom_societe.text = ""
                self.ids.nom_client.text = ""
                self.ids.num_abonne.text = ""
                self.manager.current = 'ajouter facture priver'
            except Exception as e:
                self.erreur = MDDialog(title="Erreur !!!!!!!!",
                                       text=f"Erreur au niveau de {e}!!!",
                                       buttons=[valider],
                                       size_hint_y=(.5))

                self.erreur.open()
                self.conn.rollback()
                self.conn.close()

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def show_menu_priver(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            priver = ("Priver")
            # Insérer le nom dans la base de données
            self.cursor.execute("select nom_societe from societe where type_societe=?", (priver,))
            self.societes = self.cursor.fetchall()
            self.societes = [i[0] for i in self.societes]
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()

        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem", "on_release": lambda x=societe: self.menu_callback(x)}
            for societe in self.societes
        ]

        # Créer le menu déroulant
        self.menu_societe = MDDropdownMenu(
            caller=self.ids.nom_societe,
            items=menu_items,
            width_mult=4,
        )
        self.menu_societe.open()

    def menu_callback(self, text_item):
        self.ids.nom_societe.text = text_item
        self.menu_societe.dismiss()


#========================gestion paiement client====================================
class paiement_client(MDScreen):
    name = ObjectProperty(None)
    id_societe = ObjectProperty(None)

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def paiement_clients(self, id_societe):
        #self.clear_widgets()
        self.id_societe = id_societe
        today = datetime.now()
        date_debut = today.strptime('22/08/2024', '%d/%m/%Y')
        date_fin_str = date_debut + timedelta(days=15)
        date_fin = date_fin_str.strftime('%d/%m/%Y')
        self.num_facture = self.ids.num_facture.text
        # self.tableaux.opacity = 0
        if not self.num_facture:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage de la facture",
                                   text="Veuillez remplir tous les champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.num_facture.text = ""
            self.erreur.open()

        else:
            self.tableau()

    def efface_tableau(self):
        if hasattr(self, 'tableaux'):
            self.remove_widget(self.tableaux)

    def tableau(self):
        try:
            # Connexion à la base de données
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()

            # Charger les factures du client
            self.cursor.execute(
                "SELECT ID_FACTURE, MONTANT_FACTURE,mois, STATUS FROM FACTURE WHERE id_facture = ? and id_societe = ?",
                (self.num_facture, self.id_societe,))
            self.factures = self.cursor.fetchall()
            self.mois = [i[2] for i in self.factures]
            if len(self.factures) != 0:
                # Supprimer l'ancien tableau s'il existe
                self.efface_tableau()

                row_data = [
                    (facture_id, montant,mois, status)
                    for facture_id, montant,mois, status in self.factures
                ]

                for facture in self.factures:
                    self.montant_fact = facture[1]
                    facture = facture[3]

                self.tableaux = MDDataTable(
                    size_hint=(.9, .3),
                    pos_hint={'center_x': .5, 'center_y': .42},
                    column_data=[
                        ("N°Facture", dp(30)),
                        ("Montant", dp(18)),
                        ("Mois", dp(31)),
                        ("Status", dp(15)),
                    ],
                    row_data=row_data
                )
                text_couleur = self.ids.rechercher.text_color
                couleur = self.ids.rechercher.md_bg_color

                if facture != 'Payée':
                    self.ids.rechercher.opacity = 0  # Masquer le bouton continuer
                    self.ids.rechercher.disabled = True  # Désactiver le bouton continuer
                    self.ids.num_facture.opacity = 0  # Masquer le champ N°Facture
                    self.ids.num_facture.disabled = True  # Masquer le champ N°Facture

                    self.payer = MDRaisedButton(
                        text="Payer la facture",
                        size_hint=(.62, .07),
                        elevation=3,
                        md_bg_color=couleur,
                        text_color=text_couleur,
                        font_style="H6",
                        pos_hint={"center_x": .5, "center_y": .08},
                        on_release=lambda x: self.payer_facture()
                    )
                    self.add_widget(self.payer)
                    '''self.show_facture = MDRaisedButton(
                        text="Voir la facture",
                        size_hint=(.62, .05),
                        elevation=3,
                        md_bg_color=couleur,
                        text_color=text_couleur,
                        font_style="H6",
                        pos_hint={"center_x": .5, "center_y": .2},
                        on_release=lambda x: self.on_button_click()
                    )
                    self.add_widget(self.show_facture)'''

                    self.remove_widget(self.tableaux)
                """                else:
                    self.show_facture = MDRaisedButton(
                        text="Voir la facture",
                        size_hint=(.62, .05),
                        elevation=3,
                        md_bg_color=couleur,
                        text_color=text_couleur,
                        font_style="H6",
                        pos_hint={"center_x": .5, "center_y": .2},
                        on_release=lambda x: self.on_button_clicks()
                    )
                    self.add_widget(self.show_facture)"""
                self.add_widget(self.tableaux)
            else:
                Fermer = MDRaisedButton(text="Fermer", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(
                    title="Erreur!!!!!!!!!!!!!!",
                    text="Le numéro de cette facture n'existe pas",
                    buttons=[Fermer],
                    size_hint_y=(.5)
                )
                self.erreur.open()
                self.ids.num_facture.text = ""

        except Exception as e:
            Fermer = MDRaisedButton(text="Fermer", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(
                title="Erreur 12!!!!!!!!!!!!!!",
                text=f"Erreur au niveau {e}",
                buttons=[Fermer],
                size_hint_y=(.5)
            )
            self.erreur.open()
            self.ids.num_facture.text = ""

    def efface(self):
       # self.montant.text = ''
        self.ids.methode_sne.text = ""
        self.ids.methode_sne.disabled = True
        self.montants.opacity=0
        self.ids.methode_sne.opacity = 0
        self.ids.num_facture.text = ""
        self.ids.num_facture.opacity = 1
        self.ids.num_facture.disabled = False
        self.ids.rechercher.disabled = False
        self.ids.rechercher.opacity = 1
        self.valider.disabled = True
        self.valider.opacity = 0
        self.payer.disabled = True
        self.payer.opacity = 0


    def reinitialiser_champs(self):
        # Réinitialiser les champs de texte
        self.ids.num_facture.text = ""
        self.ids.methode_sne.text = ""

        # Si vous avez d'autres éléments que vous souhaitez réinitialiser, ajoutez-les ici, par exemple :
        if hasattr(self, 'tableaux'):
            self.remove_widget(self.tableaux)
            # Réinitialiser les widgets de paiement
        if hasattr(self, 'montants'):
            self.remove_widget(self.montants)
            del self.montants  # Libérer la mémoire

            # Remettre les boutons à l'état initial si nécessaire
        if hasattr(self, 'valider'):
            self.remove_widget(self.valider)

            # Réactivez et affichez à nouveau les champs à l'initialisation
        self.ids.num_facture.opacity = 1
        self.ids.num_facture.disabled = False
        self.ids.methode_sne.opacity = 0
        self.ids.methode_sne.disabled = True

        # Réinitialiser l'état des boutons
        if hasattr(self, 'payer'):
            self.remove_widget(self.payer)
            self.ids.rechercher.opacity=1
            self.ids.rechercher.disabled=False


    def payer_facture(self):
        self.remove_widget(self.tableaux)
        self.ids.methode_sne.opacity = 1
        self.ids.methode_sne.disabled = False
        self.ids.num_facture.disabled = False
        self.ids.num_facture.opacity = 0

        couleur = (self.ids.rechercher.md_bg_color)
        text_couleur = (self.ids.rechercher.text_color)

        self.montants = MDTextField(
            size_hint=(None, None),
            size=(300, 300),
            font_style='H4',
            hint_text="Montant ",
            text=str(self.montant_fact),
            pos_hint={"center_x": .5, "center_y": .60},
            hint_text_color_normal= (1, 1, 1, 1 ), # Texte du hint en blanc
            text_color_normal= 'yellow',  # Texte du hint en blanc
            icon_right_color_normal= (1, 1, 1, 1),  # Couleur de l'icône en blanc
            line_color_focus= (0, 0.7, 0.8, 1) , # Même couleur de focus
            line_color_normal= (0.8, 0.8, 0.8, 1),  # Même couleur normale
            theme_text_color= "Custom",
            text_color= "white",
            icon_right="currency-usd",
            disabled = True

        )

        self.valider = MDRaisedButton(
            text="Valider",
            size_hint=(.62, .07),
            elevation=3,
            md_bg_color=couleur,
            text_color=text_couleur,
            icon="file-document",
            font_style="H6",
            pos_hint={"center_x": .5, "center_y": .080},
            on_release=lambda x: self.paiement_facture(self.montants.text, self.ids.methode_sne.text)
        )

        self.add_widget(self.montants)
        self.add_widget(self.valider)

    def paiement_facture(self, montant, methode):
        self.me = methode
        # Assurez-vous que les champs sont remplis
        if not self.montants.text or not methode:
            self.show_error_dialog("Veuillez remplir tous les champs.")
        else:

            date_paiement = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.da = date_paiement
            self.mobile_money()

    #===================================================D'autre fonction========================================================
    def menu_callback(self, text_item):
        self.ids.methode_sne.text = text_item
        self.menu.dismiss()

    def show_menu(self):
        # Simuler les données de votre base de données
        self.societes = [
            "Mobile Money",
            "Airtel Money",
            "Max Coin",
            "Max Money"
        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem",
             "on_release": lambda x=societe: self.menu_callback(x)}
            for societe in self.societes
        ]

        # Créer le menu déroulant
        self.menu = MDDropdownMenu(
            caller=self.ids.methode_sne,
            items=menu_items,
            width_mult=4,
        )

        self.menu.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()
    def close_dialog1(self):
        self.success_dialog.dismiss()


    def show_error_dialog(self, message):
        # Afficher une boîte de dialogue d'erreur
        error_dialog = MDDialog(
            title="Erreur",
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: error_dialog.dismiss()),
                     ]
        )
        error_dialog.open()

    def show_success_dialog(self, message):
        # Afficher une boîte de dialogue de succès
        success_dialog = MDDialog(
            title="Succès",
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: success_dialog.dismiss())]
        )
        success_dialog.open()

    def open_pdf(self, id_facture):
        # Construire le chemin vers le fichier PDF
        pdf_path = f"file:///C:/Users/EL%20VERDUGO/Desktop/avancer\\image\\{id_facture}.pdf"
        # Ouvrir le fichier PDF
        webbrowser.open(pdf_path)

    def modify_pdf(self, pdf_path, output_path, name):
        # Ouvrir le PDF existant
        pdf_document = fitz.open(pdf_path)
        # time = fitz.Font("C:/Users/EL VERDUGO/Desktop/avancer/Font/times.ttf")

        # Choisir la première page
        page = pdf_document[0]
        # times_new_roman = fitz.Font("MPoppins.ttf")
        for i in self.factures:
            numero=i[0]
            montant=i[1]


        # Ajouter le nom à la position souhaitée
        page.insert_text((400, 115), name, fontsize=12, color=(0, 0, 1))  # AjAustez les coordonnées
        page.insert_text((250, 115), str(numero), fontsize=12, color=(0, 0, 0))  # AjAustez les coordonnées
        page.insert_text((200, 115), str(montant), fontsize=12, color=(0, 0, 0))  # AjAustez les coordonnées

        # Enregistrer le PDF modifié
        pdf_document.save(output_path)
        pdf_document.close()

    def on_button_click(self):
        # Exemple d'utilisation de la méthode modify_pdf
        pdf_path = 'image/FACTURE SNE.pdf'  # Chemin vers le PDF original
        output_path = 'image/modified_invoice.pdf'  # Chemin vers le PDF modifié
        name = "popa"  # Nom à ajouter

        self.modify_pdf(pdf_path, output_path, name)
        self.open_pdf("modified_invoice")
    def on_button_clicks(self):
        # Exemple d'utilisation de la méthode modify_pdf
        pdf_path = 'image/Copie.pdf'  # Chemin vers le PDF original
        output_path = 'image/modified_invoice.pdf'  # Chemin vers le PDF modifié
        name = "popa"  # Nom à ajouter

        self.modify_pdf(pdf_path, output_path, name)
        self.open_pdf("modified_invoice")

    def mobile_money(self):

        # Afficher une boîte de dialogue de succès
        oui = MDRaisedButton(text="Oui", on_release=lambda x:self.trans())
        non = MDRaisedButton(text="Non", on_release=lambda x:self.mob.dismiss())
        self.mob = MDDialog(title="Message Maxigesse",
                               text=f"Voulez-vous approuver {self.montants.text} FCFA pour Maxigesse Corporation",
                            buttons=[oui,non])

        self.mob.open()
    def trans(self):
        self.mob.dismiss()
        self.mobile_money_2()

    def mobile_money_2(self):

        # Création d'un dialogue avec MDTextField pour entrer le mot de passe
        self.mob2 = MDDialog(
            title=f"Le point agrée 242064980498 a initie un retrait d'argent de votre compte,Montant {self.montants.text}.\n"
                        f"Veuillez entrez votre code pin pour confirmer:",
            type="custom",
            content_cls=MDTextField(
                hint_text=""),
            buttons=[
                MDRaisedButton(text="Envoyer", on_release=lambda x: self.mobile_money_1()),
                MDRaisedButton(text="Annuler", on_release=lambda x: self.mob2.dismiss())]
        )
        self.mob2.open()


    def mobile_money_1(self):
        self.mob2.dismiss()
        try:
            self.mois = self.mois[0]
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute(
                "INSERT INTO PAIEMENT (ID_FACTURE,ID_Client,ID_societe, MONTANT,type_abonne,DATE_PAIEMENT, METHODE_PAIEMENT,mois) "
                "VALUES (?,?,?,?,?,?,?,?)"
                , (self.num_facture,UserManager().user_id,self.id_societe, self.montants.text, "", self.da, self.me,self.mois,))

            self.cursor.execute("UPDATE FACTURE SET STATUS = 'Payée' WHERE ID_FACTURE = ?",
                                (self.num_facture,))
            self.conn.commit()
            success_dialog = MDDialog(
                title="Message Maxigesse ",
                text=f"Vous avez confirmer le retrait de {self.montants.text} FCFA initier par le point agrée - 242064980498 \n"
                     f"Numero de la transaction 202412345.",

                buttons=[MDRaisedButton(text="OK", on_release=lambda x: success_dialog.dismiss())]

            )
            success_dialog.open()
            self.show_success_dialog("Paiement effectué avec succès.")
           # self.on_button_click()
            self.efface()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.show_error_dialog(f"Erreur lors du paiement:{e}")

    def NomUser(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))
            nom = self.cursor.fetchone()
            self.nom = nom[0]

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.show_error_dialog(f"Erreur lors :{e}")


class paiement_facture_priver_client(MDScreen):
    name = ObjectProperty(None)
    id_societe = ObjectProperty(None)

    # ===================================================D'autre fonction========================================================
    def menu_callback(self, text_item):
        self.ids.methode_sne.text = text_item
        self.menu.dismiss()

    def menu_callbacks(self, text_item):
        self.ids.method_input_priver.text = text_item
        self.menu_paiement.dismiss()

    def menu_callback_mois(self, text_item):
        self.ids.mois.text = text_item
        self.menu_mois.dismiss()

    def show_menu(self):
        # Simuler les données de votre base de données
        self.societes = [
            "Mobile Money",
            "Airtel Money",
            "Max Coin",
            "Max Money"
        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem",
             "on_release": lambda x=societe: self.menu_callback(x)}
            for societe in self.societes
        ]

        # Créer le menu déroulant
        self.menu = MDDropdownMenu(
            caller=self.ids.methode_sne,
            items=menu_items,
            width_mult=4,
        )

        self.menu.open()
    def show_menu_paiement(self):
        # Simuler les données de votre base de données
        self.societes = [
            "Mobile Money",
            "Airtel Money",
            "Max Coin",
            "Max Money"
        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items = [
            {"text": societe, "viewclass": "OneLineListItem",
             "on_release": lambda x=societe: self.menu_callbacks(x)}
            for societe in self.societes
        ]

        # Créer le menu déroulant
        self.menu_paiement = MDDropdownMenu(
            caller=self.ids.method_input_priver,
            items=menu_items,
            width_mult=4,
        )

        self.menu_paiement.open()

    def show_menu_mois(self):
        # Simuler les données de votre base de données
        self.mois = [
            "Janvier",
            "Fevrier",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Decembre",

        ]

        # Créer des éléments de menu à partir des données de la base
        menu_items_mois = [
            {"text": mois, "viewclass": "OneLineListItem",
             "on_release": lambda x=mois: self.menu_callback_mois(x)}
            for mois in self.mois
        ]

        # Créer le menu déroulant
        self.menu_mois = MDDropdownMenu(
            caller=self.ids.mois,
            items=menu_items_mois,
            width_mult=4,
        )

        self.menu_mois.open()

    def show_menu_montant(self):
        menu_items = [
            {"text": "15000", "viewclass": "OneLineListItem", "on_release": lambda x="15000": self.set_price(x)},
            {"text": "25000", "viewclass": "OneLineListItem", "on_release": lambda x="25000": self.set_price(x)},
            {"text": "35000", "viewclass": "OneLineListItem", "on_release": lambda x="35000": self.set_price(x)},
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.montant_priver,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def set_price(self, price):
        self.ids.montant_priver.text = price
        description = {
            "15000": "Ménage",
            "25000": "Particulié",
            "35000": "Entreprise"
        }
        self.ids.type_abn.text = description[price]
        self.menu.dismiss()

    def close_dialog(self, instance):
        self.dialog.dismiss()
    def close_dialog1(self):
        self.success_dialog.dismiss()


    def show_error_dialog(self, message):
        # Afficher une boîte de dialogue d'erreur
        error_dialog = MDDialog(
            title="Erreur",
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: error_dialog.dismiss()),
                     ]
        )
        error_dialog.open()

    def show_success_dialog(self, message):
        # Afficher une boîte de dialogue de succès
        success_dialog = MDDialog(
            title="Succès",
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: success_dialog.dismiss())]
        )
        success_dialog.open()

    def close_dailog(self, obj):
        self.erreur.dismiss()

    def societe_priver(self, id_societe):
        self.id_societe = id_societe
        today = datetime.now()
        date_debut = today.strptime('22/08/2024', '%d/%m/%Y')
        date_fin_str = date_debut + timedelta(days=31)
        date_fin = date_fin_str.strftime('%d/%m/%Y')
        self.num_abn = self.ids.num_abn_priver.text
        self.conn = sqlite3.connect('donner.db')
        self.cursor = self.conn.cursor()
        # Charger les factures du client

        if not self.num_abn:
            ok = MDRaisedButton(text="OK", size_hint=(1, 1), on_release=self.close_dailog)
            self.erreur = MDDialog(title="Erreur lors du remplissage de l'abonnement",
                                   text="Veuillez remplir ce champs", buttons=[ok],
                                   size_hint_y=(.5))

            self.ids.num_abn_priver.text = ""
            self.erreur.open()

        else:
            try:
                self.conn = sqlite3.connect('donner.db')
                self.cursor = self.conn.cursor()
                # Charger les factures du client
                self.cursor.execute(
                    "SELECT ID_FACTURE,montant_facture FROM FACTURE WHERE numero_abonne = ? and id_societe = ?",
                    (self.num_abn, self.id_societe,))

                self.factures = self.cursor.fetchall()
                self.conn.commit()
                if len(self.factures) != 0:
                    self.ids.num_abn_priver.disabled = True
                    self.ids.num_abn_priver.opacity = 1
                    self.ids.rechercher.disabled = True
                    self.ids.rechercher.opacity = 0
                    self.ids.mois.disabled = False
                    self.ids.mois.opacity = 1
                    self.ids.mois.size_hint_x = 1
                    self.ids.num_abn_priver.size_hint_x = 1
                    self.ids.montant_priver.pos_hint = {'center_x': 0.5, 'center_y': .65}
                    self.ids.montant_priver.size_hint_x = 1
                    self.ids.montant_priver.disabled = False
                    self.ids.montant_priver.opacity = 1
                    self.ids.type_abn.size_hint_x = 1
                    self.ids.type_abn.opacity = 1
                    self.ids.method_input_priver.opacity = 1
                    self.ids.method_input_priver.size_hint_x = 1
                    self.ids.method_input_priver.disabled = False
                    couleur = (self.ids.rechercher.md_bg_color)
                    text_couleur = (self.ids.rechercher.text_color)
                    self.payer = MDRaisedButton(
                        text="Payer",
                        size_hint=(.62, .05),
                        elevation=3,
                        md_bg_color=couleur,
                        text_color=text_couleur,
                        font_style="H6",
                        pos_hint={"center_x": .5, "center_y": .080},
                        on_release=lambda x: (
                            self.paiement_facture_priver(self.ids.montant_priver.text, self.ids.method_input_priver.text))
                    )
                    self.add_widget(self.payer)

                else:
                    Fermer = MDRaisedButton(text="Fermer", size_hint=(1, 1), on_release=self.close_dailog)
                    self.erreur = MDDialog(title="Erreur!!!!!!!!!!!!!!",
                                           text="Ce numéro d'abonnement n'existe pas", buttons=[Fermer],
                                           size_hint_y=(.5))
                    self.erreur.open()
                    self.ids.num_abn_priver.text = ""

            except Exception as e:

                Fermer = MDRaisedButton(text="Fermer", size_hint=(1, 1), on_release=self.close_dailog)
                self.erreur = MDDialog(title="Erreur!!!!!!!!!!!!!!",
                                       text=f"Erreur au niveau {e}", buttons=[Fermer],
                                       size_hint_y=(.5))
                self.erreur.open()
                self.ids.num_abn_priver.text = ""

    def paiement_facture_priver(self, montant, methode):
        # Assurez-vous que les champs sont remplis
        if not montant or not methode or not self.ids.mois.text:
            self.show_error_dialog("Veuillez remplir tous les champs de l'abonnenement.")
        else:

            date_paiement = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.da = date_paiement
            self.mo = montant
            self.me = methode
            try:
                self.conn = sqlite3.connect('donner.db')
                self.cursor = self.conn.cursor()
                self.cursor.execute(
                    "SELECT ID_FACTURE FROM FACTURE WHERE numero_abonne = ? and id_societe = ?",
                    (self.num_abn, self.id_societe,))

                self.num_facture = self.cursor.fetchone()[0]
                self.conn.commit()

                self.conn = sqlite3.connect('donner.db')
                self.cursors = self.conn.cursor()
                # Exécuter la logique de paiement et mise à jour de la facture
                val = ("select mois from paiement where id_facture = ?")
                donne = (self.num_facture)
                self.cursors.execute(val, (donne,))
                moi = self.cursors.fetchall()
                moi = [i[0] for i in moi]
                if self.ids.mois.text in moi:
                    self.show_error_dialog("Ce mois est déjà payé ")
                else:
                    self.mobile_money_priver()
            except Exception as e:
                self.conn.rollback()
                self.show_error_dialog(f"Erreur lors du paiement:{e}")

    def efface_priver(self):
        if self.ids.num_abn_priver.disabled != False:
            self.ids.num_abn_priver.disabled = False
            self.ids.rechercher.disabled = False
            self.ids.rechercher.opacity = 1
            self.ids.num_abn_priver.text = ''
            self.payer.opacity = 0
            self.payer.disabled = True
            self.ids.montant_priver.disabled = True
            self.ids.montant_priver.opacity = 0
            self.ids.montant_priver.text = ""
            self.ids.method_input_priver.opacity = 0
            self.ids.method_input_priver.disabled = True
            self.ids.method_input_priver.text = ""
            self.ids.mois.disabled = True
            self.ids.mois.opacity = 0
            self.ids.mois.text = ""
            self.ids.type_abn.opacity = 0
            self.ids.type_abn.text = ""

        else:
            self.ids.num_abn_priver.text = ''


    def mobile_money_priver(self):

        # Afficher une boîte de dialogue de succès
        oui = MDRaisedButton(text="Oui", on_release=lambda x: self.trans_priver())
        non = MDRaisedButton(text="Non", on_release=lambda x: self.mob.dismiss())
        self.mob = MDDialog(title="Message Maxigesse",
                            text=f"Voulez-vous approuver {self.ids.montant_priver.text} FCFA pour Maxigesse Corporation",
                            buttons=[oui, non])

        self.mob.open()

    def trans_priver(self):
        self.mob.dismiss()
        self.mobile_money_priver_2()

    def mobile_money_priver_2(self):

        # Création d'un dialogue avec MDTextField pour entrer le mot de passe
        self.mob2 = MDDialog(
            title=f"Le point agrée 242064980498 a initie un retrait d'argent de votre compte,Montant {self.ids.montant_priver.text}.\n"
                  f"Veuillez entrez votre code pin pour confirmer:",
            type="custom",
            content_cls=MDTextField(
                hint_text=""),
            buttons=[
                MDRaisedButton(text="Envoyer", on_release=lambda x: self.mobile_money_priver_3()),
                MDRaisedButton(text="Annuler", on_release=lambda x: self.mob2.dismiss())]
        )
        self.mob2.open()

    def mobile_money_priver_3(self):
        self.mob2.dismiss()
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                "SELECT ID_FACTURE FROM FACTURE WHERE numero_abonne = ? and id_societe = ?",
                (self.num_abn, self.id_societe,))

            self.num_facture = self.cursor.fetchone()[0]

            self.conn = sqlite3.connect('donner.db')
            self.cursors = self.conn.cursor()
            status = "Payée"
            self.cursors.execute(
                "INSERT INTO PAIEMENT (ID_FACTURE,ID_Client,id_societe, MONTANT,type_abonne,mois, DATE_PAIEMENT, METHODE_PAIEMENT,numero_abonne) "
                "VALUES (?,?,?,?,?,?,?,?,?)"
                , (self.num_facture,UserManager().user_id,self.id_societe, self.mo, self.ids.type_abn.text, self.ids.mois.text,
                   self.da, self.me,
                   self.num_abn,))

            self.cursors.execute(
                "UPDATE FACTURE SET STATUS = 'Payée',montant_facture = ?,mois = ? WHERE numero_abonne = ?",
                (self.mo, self.ids.mois.text, self.num_abn,))

            self.conn.commit()
            self.efface_priver()
            self.show_success_dialog("Paiement effectué avec succès.")
            success_dialog = MDDialog(
                title="Message Maxigesse ",
                text=f"Vous avez confirmer le retrait de {self.mo} FCFA initier par le point agrée - 242064980498 \n"
                     f"Numero de la transaction 202412345.",

                buttons=[MDRaisedButton(text="OK", on_release=lambda x: success_dialog.dismiss())]

            )
            success_dialog.open()
        except Exception as e:
            self.conn.rollback()
            self.show_error_dialog(f"Erreur lors du paiement:{e}")

    def NomUser(self):
        try:
            self.conn = sqlite3.connect('donner.db')
            self.cursor = self.conn.cursor()
            # Exécuter la logique de paiement et mise à jour de la facture
            self.cursor.execute("select nom_client from client where id_client=?",
                                (UserManager().user_id,))
            nom = self.cursor.fetchone()
            self.nom = nom[0]

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.show_error_dialog(f"Erreur lors :{e}")


#========================Fichier main===================================

class MainApp(MDApp):

    def build(self):
        global ecran
        ecran = ScreenManager()
        self.title= 'Accueil'

        #self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Yellow"
       # ecran.add_widget(Builder.load_file("client/Login.kv"))

        #============================Admin=================================================================

        #ecran.add_widget(Builder.load_file("admin/home.kv"))
        ecran.add_widget(Builder.load_file("client/login.kv"))
        ecran.add_widget(Builder.load_file("admin/accueil_admin.kv"))
        ecran.add_widget(Builder.load_file("admin/profile admin.kv"))
        ecran.add_widget(Builder.load_file("admin/compte admin.kv"))

        # =====================================Gestion Client===================================

        ecran.add_widget(Builder.load_file("admin/Client/Gestion client.kv"))
        ecran.add_widget(Builder.load_file("admin/Client/bloquer client.kv"))
        ecran.add_widget(Builder.load_file("admin/Client/debloquer client.kv"))
        # =====================================Gestion societe===================================
        ecran.add_widget(Builder.load_file("admin/societe/gestion societe.kv"))
        ecran.add_widget(Builder.load_file("admin/societe/ajouter societer.kv"))
        #=====================================Gestion facture===================================
        ecran.add_widget(Builder.load_file("admin/facture/gestion facture.kv"))
        ecran.add_widget(Builder.load_file("admin/facture/type facture.kv"))
        ecran.add_widget(Builder.load_file("admin/facture/ajouter facture.kv"))
        ecran.add_widget(Builder.load_file("admin/facture/ajouter facture priver.kv"))

        #=====================================Gestion paiement===================================
        ecran.add_widget(Builder.load_file("admin/paiement/gestion paiement.kv"))
        ecran.add_widget(Builder.load_file("admin/paiement/ajouter paiement.kv"))

        #=============================Client============================================================================

        #ecran.add_widget(Builder.load_file("client/home.kv"))
        ecran.add_widget(Builder.load_file("client/inscription.kv"))
        ecran.add_widget(Builder.load_file("client/Reset password.kv"))

        ecran.add_widget(Builder.load_file("client/accueil_user.kv"))

        ecran.add_widget(Builder.load_file("client/profile.kv"))
        ecran.add_widget(Builder.load_file("client/compte.kv"))
        ecran.add_widget(Builder.load_file("client/historique des facture.kv"))
        ecran.add_widget(Builder.load_file("client/historique des facture priver.kv"))
        ecran.add_widget(Builder.load_file("client/historique des paiement.kv"))
        ecran.add_widget(Builder.load_file("client/historique des paiement priver.kv"))
        ecran.add_widget(Builder.load_file("client/choix societe.kv"))
        ecran.add_widget(Builder.load_file("client/choix paiement.kv"))

        ecran.add_widget(Builder.load_file("client/lcde.kv"))
        ecran.add_widget(Builder.load_file("client/congo_telecom.kv"))
        ecran.add_widget(Builder.load_file("client/sne.kv"))

        return ecran
       

    def change_screen(self, screen_name):
        ecran.current = screen_name


if __name__ == "__main__":
    LabelBase.register(name='MPoppins',fn_regular='C:\\Users\\EL VERDUGO\\Desktop\\lestest\\Font\\Poppins-Medium.ttf')
    LabelBase.register(name='Regular',fn_regular='C:\\Users\\EL VERDUGO\\Desktop\\lestest\\Font\\Poppins-Regular.ttf')
    LabelBase.register(name='Time',fn_regular='C:\\Users\\EL VERDUGO\\Desktop\\lestest\\Font\\times.ttf')
    LabelBase.register(name='Verdana',fn_regular='C:\\Users\\EL VERDUGO\\Desktop\\lestest\\Font\\verdana.ttf')
    MainApp().run()
