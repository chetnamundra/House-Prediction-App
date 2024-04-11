from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import RoundedRectangle, Color
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
import pickle
import logging
import mysql.connector as m

con = m.connect(host='localhost', user='root', passwd='0000', database='house_prediction')
screen_manager = ScreenManager()
logging.getLogger('matplotlib.font_manager').disabled = True

Builder.load_string('''
<FDDButton@Button>:
    size_hint_y: None
    height: '50dp'
    
<FilterDD>:
    auto_dismiss: False
''')
alist=[None,None,None,None,None]

def show_login_popup(instance):
    content = BoxLayout(orientation='vertical', spacing=10, padding=(10,10,10,10))
    email_input = TextInput(hint_text='Email',padding_y=12.5)
    
    password_input = TextInput(hint_text='Password', password=True)
    login_button = Button(text='Login', on_press=lambda x: login(popup, email_input.text, password_input.text))
    content.add_widget(email_input)
    content.add_widget(password_input)

    login_button.background_color = (1, 1, 1, 0)
    login_rect = RoundedRectangle(pos=login_button.pos, size=login_button.size, radius=[10, 10, 10, 10])
    login_button.bind(pos=lambda instance, value: setattr(login_rect, 'pos', value))
    login_button.bind(size=lambda instance, value: setattr(login_rect, 'size', value))
    login_button.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
    login_button.canvas.before.add(login_rect)
    
    content.add_widget(login_button)
    
    popup = Popup(title='Login', content=content, size_hint=(None, None), size=(300, 250))
    popup.open()

def login(popup, email, password):
    
    cursor = con.cursor()
    query = "SELECT * FROM user WHERE email = %s AND password = %s"
    
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    
    cursor.close()


    if user:
        popup.dismiss()
        app = App.get_running_app()
        app.root.current = 'home'
    else:
        failed_message = Label(text='Login failed')
        popup = Popup(title='Login', content=failed_message, size_hint=(None, None), size=(300, 200))
        popup.open()
        
def show_signup_popup(instance):
    content = BoxLayout(orientation='vertical',spacing=10, padding=(10,10,10,10))
    name_input = TextInput(hint_text='Name',padding_y=12.5)
    email_input = TextInput(hint_text='Email',padding_y=12.5)
    create_password_input = TextInput(hint_text='Create Password', password=True,padding_y=12.5)
    signup_button = Button(text='Signup', on_press=lambda x: signup(popup,name_input.text, email_input.text, create_password_input.text))
    signup_button.background_color = (1, 1, 1, 0)
    signup_rect = RoundedRectangle(pos=signup_button.pos, size=signup_button.size, radius=[10, 10, 10, 10])
    signup_button.bind(pos=lambda instance, value: setattr(signup_rect, 'pos', value))
    signup_button.bind(size=lambda instance, value: setattr(signup_rect, 'size', value))
    signup_button.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
    signup_button.canvas.before.add(signup_rect)
    
    content.add_widget(name_input)
    content.add_widget(email_input)
    content.add_widget(create_password_input)
    content.add_widget(signup_button)
    
    
    popup = Popup(title='Signup', content=content, size_hint=(None, None), size=(300, 300))
    popup.open()

def signup(popup,name, email, password):
    cursor = con.cursor()
    cursor.execute("select email from user")
    result=cursor.fetchall()
    for x in result:
        if email in x:
            failed_message = Label(text='email exists! try logging in')
            popup = Popup(title='signup', content=failed_message, size_hint=(None, None), size=(300, 200))
            popup.open()
            break
    else:
        query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
        values = (name, email, password)
        cursor.execute(query, values)
        con.commit()
        cursor.close()
        popup.dismiss()
    
        app = App.get_running_app()
        app.root.current = 'home'

def data_table(location, bhk, bath, balcony):

    data=[]

    with open(r'F:\bms\hm\kivyy\clean_data.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for i in csvreader:
            tup=[]

            if location==None or i[1]==location:
                if i[1]=='location':
                    pass
                else:
                    tup.append(i[1])
            tup.append(i[2])
            if bath==None:
                tup.append(i[3])
            elif bath.isdigit() and i[3]!='bath':
                if float(i[3])==int(bath):
                    tup.append(i[3])
            if balcony==None:
                tup.append(i[4])
            elif balcony.isdigit() and i[4]!='balcony':
                if float(i[4])==int(balcony):
                    tup.append(i[4])
            if bhk==None:
                tup.append(i[6])
            elif bhk.isdigit() and i[6]!='bhk':
                if int(i[6])==int(bhk) : 
                    tup.append(i[6])
            tup.append(i[5])
            if len(tup)==6:
                data.append(tuple(tup))
            if len(data)==20:
                return data
    return data 
                    
def home_button(layout, search_layout, pred_layout, tab_layout, chart_layout):
    def logoutt(popup):
        popup.dismiss()
        app = App.get_running_app()
        app.root.current = 'start'
        
    def update_widgets_text(instance):
        global alist
        alist=[None,None,None,None,None]

        content = BoxLayout(orientation='vertical')
        
        # Create two images
        image1 = Image(source='about.png', size=(400,700))
        
        # Create a button
        button = Button(text='Logout', size_hint=(0.8, None), on_release=lambda x: logoutt(popup),
                        height=50,background_color = (1, 1, 1, 0),pos_hint={'center_x': 0.5, 'center_y': 0.5})

        # Create a RoundedRectangle for the button background
        buttonr = RoundedRectangle(pos=button.pos, size=button.size, radius=[10, 10, 10, 10])
        
        # Bind the button's position and size to the RoundedRectangle
        button.bind(pos=lambda instance, value: setattr(buttonr, 'pos', value))
        button.bind(size=lambda instance, value: setattr(buttonr, 'size', value))
        
        # Set the button's background color and add the RoundedRectangle
        button.canvas.before.add(Color(1, 0, 0, 0.5))
        button.canvas.before.add(buttonr)

        # Add the elements to the content layout
        content.add_widget(image1)

        content.add_widget(button)

        # Create and open the popup
        popup = Popup(title='',content=content, size_hint=(None, None), size=(400, 775),background_color = (0, 0, 0, 1))
        popup.separator_height = 0
        popup.open()
        
        search(search_layout,pred_layout,tab_layout,chart_layout)
        prediction(pred_layout)
        table(tab_layout)
        chart(chart_layout, 'yes')
        

    layout1 = FloatLayout()
    
    button = Button( on_press=update_widgets_text ,background_normal='home.png',
                                    size=(150,150),pos_hint={'center_x': 0.5, 'center_y': 0.5},size_hint=(None, None))
    layout1.add_widget(button)
    layout.add_widget(layout1)

def button_update(buttons,button_to_update,var):
    
    def button_clicked(button,dropdown,button_to_update,var):
        
        global alist
        alist[var]=button.text
        dropdown.dismiss()
        button_to_update.text = button.text

    def apply_filter(wid,value,dropdown,buttons,filter1,button_to_update,var):
        dropdown.clear_widgets()
        dropdown.add_widget(filter1)

        for btn_text in buttons:
                if not value or value in btn_text:
                    button = Factory.FDDButton(text=btn_text, background_color=(0.5, 0.5, 1, 1))
                    button.bind(on_release=lambda btn: button_clicked(btn, dropdown, button_to_update,var))
                    dropdown.add_widget(button)
        
    def filterDD(buttons, button_to_update, var):
        filter1=Factory.TextInput(size_hint_y=None)
        dropdown = Factory.DropDown()
        dropdown.add_widget(filter1)
        filter1.bind(text=lambda instance, value: apply_filter(instance, value, dropdown, buttons, filter1,button_to_update,var))
        apply_filter(None, '', dropdown, buttons, filter1,button_to_update,var)
        return dropdown
    dropdown=filterDD(buttons, button_to_update,var)
    return dropdown

def search(layout,pred_layout,tab_layout,chart_layout):

    def update_widgets(popup,tot_sqft):

        if popup==None:
            pass
        else:
            popup.dismiss()
            
        global alist
        alist[4]=tot_sqft
        print(alist)
        
        prediction(pred_layout)
        table(tab_layout)
        chart(chart_layout, 'yes')
    
    loc_list=['1st Block Jayanagar', '1st Phase JP Nagar',
       '2nd Phase Judicial Layout', '2nd Stage Nagarbhavi',
       '5th Block Hbr Layout', '5th Phase JP Nagar', '6th Phase JP Nagar',
       '7th Phase JP Nagar', '8th Phase JP Nagar', '9th Phase JP Nagar',
       'AECS Layout', 'Abbigere', 'Akshaya Nagar', 'Ambalipura',
       'Ambedkar Nagar', 'Amruthahalli', 'Anandapura', 'Ananth Nagar',
       'Anekal', 'Anjanapura', 'Ardendale', 'Arekere', 'Attibele',
       'BEML Layout', 'BTM 2nd Stage', 'BTM Layout', 'Babusapalaya',
       'Badavala Nagar', 'Balagere', 'Banashankari',
       'Banashankari Stage II', 'Banashankari Stage III',
       'Banashankari Stage V', 'Banashankari Stage VI', 'Banaswadi',
       'Banjara Layout', 'Bannerghatta', 'Bannerghatta Road',
       'Basavangudi', 'Basaveshwara Nagar', 'Battarahalli', 'Begur',
       'Begur Road', 'Bellandur', 'Benson Town', 'Bharathi Nagar',
       'Bhoganhalli', 'Billekahalli', 'Binny Pete', 'Bisuvanahalli',
       'Bommanahalli', 'Bommasandra', 'Bommasandra Industrial Area',
       'Bommenahalli', 'Brookefield', 'Budigere', 'CV Raman Nagar',
       'Chamrajpet', 'Chandapura', 'Channasandra', 'Chikka Tirupathi',
       'Chikkabanavar', 'Chikkalasandra', 'Choodasandra', 'Cooke Town',
       'Cox Town', 'Cunningham Road', 'Dasanapura', 'Dasarahalli',
       'Devanahalli', 'Devarachikkanahalli', 'Dodda Nekkundi',
       'Doddaballapur', 'Doddakallasandra', 'Doddathoguru', 'Domlur',
       'Dommasandra', 'EPIP Zone', 'Electronic City',
       'Electronic City Phase II', 'Electronics City Phase 1',
       'Frazer Town', 'GM Palaya', 'Garudachar Palya', 'Giri Nagar',
       'Gollarapalya Hosahalli', 'Gottigere', 'Green Glen Layout',
       'Gubbalala', 'Gunjur', 'HAL 2nd Stage', 'HBR Layout',
       'HRBR Layout', 'HSR Layout', 'Haralur Road', 'Harlur', 'Hebbal',
       'Hebbal Kempapura', 'Hegde Nagar', 'Hennur', 'Hennur Road',
       'Hoodi', 'Horamavu Agara', 'Horamavu Banaswadi', 'Hormavu',
       'Hosa Road', 'Hosakerehalli', 'Hoskote', 'Hosur Road', 'Hulimavu',
       'ISRO Layout', 'ITPL', 'Iblur Village', 'Indira Nagar', 'JP Nagar',
       'Jakkur', 'Jalahalli', 'Jalahalli East', 'Jigani',
       'Judicial Layout', 'KR Puram', 'Kadubeesanahalli', 'Kadugodi',
       'Kaggadasapura', 'Kaggalipura', 'Kaikondrahalli',
       'Kalena Agrahara', 'Kalyan nagar', 'Kambipura', 'Kammanahalli',
       'Kammasandra', 'Kanakapura', 'Kanakpura Road', 'Kannamangala',
       'Karuna Nagar', 'Kasavanhalli', 'Kasturi Nagar', 'Kathriguppe',
       'Kaval Byrasandra', 'Kenchenahalli', 'Kengeri',
       'Kengeri Satellite Town', 'Kereguddadahalli', 'Kodichikkanahalli',
       'Kodigehaali', 'Kodigehalli', 'Kodihalli', 'Kogilu', 'Konanakunte',
       'Koramangala', 'Kothannur', 'Kothanur', 'Kudlu', 'Kudlu Gate',
       'Kumaraswami Layout', 'Kundalahalli', 'LB Shastri Nagar',
       'Laggere', 'Lakshminarayana Pura', 'Lingadheeranahalli',
       'Magadi Road', 'Mahadevpura', 'Mahalakshmi Layout', 'Mallasandra',
       'Malleshpalya', 'Malleshwaram', 'Marathahalli', 'Margondanahalli',
       'Marsur', 'Mico Layout', 'Munnekollal', 'Murugeshpalya',
       'Mysore Road', 'NGR Layout', 'NRI Layout', 'Nagarbhavi',
       'Nagasandra', 'Nagavara', 'Nagavarapalya', 'Narayanapura',
       'Neeladri Nagar', 'Nehru Nagar', 'OMBR Layout', 'Old Airport Road',
       'Old Madras Road', 'Padmanabhanagar', 'Pai Layout', 'Panathur',
       'Parappana Agrahara', 'Pattandur Agrahara', 'Poorna Pragna Layout',
       'Prithvi Layout', 'R.T. Nagar', 'Rachenahalli',
       'Raja Rajeshwari Nagar', 'Rajaji Nagar', 'Rajiv Nagar',
       'Ramagondanahalli', 'Ramamurthy Nagar', 'Rayasandra',
       'Sahakara Nagar', 'Sanjay nagar', 'Sarakki Nagar', 'Sarjapur',
       'Sarjapur  Road', 'Sarjapura - Attibele Road',
       'Sector 2 HSR Layout', 'Sector 7 HSR Layout', 'Seegehalli',
       'Shampura', 'Shivaji Nagar', 'Singasandra', 'Somasundara Palya',
       'Sompura', 'Sonnenahalli', 'Subramanyapura', 'Sultan Palaya',
       'TC Palaya', 'Talaghattapura', 'Thanisandra', 'Thigalarapalya',
       'Thubarahalli', 'Thyagaraja Nagar', 'Tindlu', 'Tumkur Road',
       'Ulsoor', 'Uttarahalli', 'Varthur', 'Varthur Road', 'Vasanthapura',
       'Vidyaranyapura', 'Vijayanagar', 'Vishveshwarya Layout',
       'Vishwapriya Layout', 'Vittasandra', 'Whitefield',
       'Yelachenahalli', 'Yelahanka', 'Yelahanka New Town', 'Yelenahalli',
       'Yeshwanthpur', 'other']
    
    bhk_list=[ '4',  '3',  '2',  '1',  '6',  '5',  '7',  '8',  '9', '10', '11', '16', '13']
    bath_list=[ '4',  '3',  '2',  '1',  '8',  '5',  '7',  '6',  '9', '12', '10', '16', '13']
    bal_list=['1', '2', '3', '0']

    def real_search_layout(value):
        if value>800:
    
            layout1 = BoxLayout(orientation='horizontal',size_hint=(1, 1))
            layout2 = BoxLayout(orientation='vertical',size_hint=(0.8, 1))
            layout3 = BoxLayout(orientation='horizontal',size_hint=(0.2, 1))
            upp=BoxLayout(orientation='horizontal',size_hint=(1, 0.5),padding=(10, 20, 10, 20))
            low=BoxLayout(orientation='horizontal',size_hint=(1, 0.5),padding=(10, 20, 10, 20))

            label1 = Label(text='Location : ',size_hint_x=0.2)
            upp.add_widget(label1)
            loc_btn = Factory.FDDButton(text="Select Location",size_hint_x=0.4, height=50)
            loc_fdd = button_update(loc_list, loc_btn, 0 )
            loc_btn.bind(on_release=lambda btn: loc_fdd.open(loc_btn))

            loc_btn.background_color = (1, 1, 1, 0)
            loc_rect = RoundedRectangle(pos=loc_btn.pos, size=loc_btn.size, radius=[10, 10, 10, 10])
            loc_btn.bind(pos=lambda instance, value: setattr(loc_rect, 'pos', value))
            loc_btn.bind(size=lambda instance, value: setattr(loc_rect, 'size', value))
            loc_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
            loc_btn.canvas.before.add(loc_rect)
            
            upp.add_widget(loc_btn)

            

            label1 = Label(text='Total Sqft : ',size_hint_x=0.2)
            upp.add_widget(label1)
            tot_sqft = TextInput(height=25,padding_y=12.5,size_hint_x=0.2)
            upp.add_widget(tot_sqft)

            layout2.add_widget(upp)

            label1 = Label(text='BHK : ')
            low.add_widget(label1)
            bhk_btn = Factory.FDDButton(text="BHK",height=50)
            bhk_fdd = button_update(bhk_list, bhk_btn, 1)
            bhk_btn.bind(on_release=lambda btn: bhk_fdd.open(bhk_btn))

            bhk_btn.background_color = (1, 1, 1, 0)
            bhk_rect = RoundedRectangle(pos=bhk_btn.pos, size=bhk_btn.size, radius=[10, 10, 10, 10])
            bhk_btn.bind(pos=lambda instance, value: setattr(bhk_rect, 'pos', value))
            bhk_btn.bind(size=lambda instance, value: setattr(bhk_rect, 'size', value))
            bhk_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
            bhk_btn.canvas.before.add(bhk_rect)
            
            low.add_widget(bhk_btn)

            label1 = Label(text='bath : ')
            low.add_widget(label1)
            bath_btn = Factory.FDDButton(text="bath",height=50)
            bath_fdd = button_update(bath_list, bath_btn, 2)
            bath_btn.bind(on_release=lambda btn: bath_fdd.open(bath_btn))
            
            bath_btn.background_color = (1, 1, 1, 0)
            bath_rect = RoundedRectangle(pos=bath_btn.pos, size=bath_btn.size, radius=[10, 10, 10, 10])
            bath_btn.bind(pos=lambda instance, value: setattr(bath_rect, 'pos', value))
            bath_btn.bind(size=lambda instance, value: setattr(bath_rect, 'size', value))
            bath_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
            bath_btn.canvas.before.add(bath_rect)
            
            low.add_widget(bath_btn)

            label1 = Label(text='Balcony : ')
            low.add_widget(label1)
            bal_btn = Factory.FDDButton(text="balcony",height=50)
            bal_fdd = button_update(bal_list, bal_btn, 3)
            bal_btn.bind(on_release=lambda btn: bal_fdd.open(bal_btn))

            bal_btn.background_color = (1, 1, 1, 0)
            bal_rect = RoundedRectangle(pos=bal_btn.pos, size=bal_btn.size, radius=[10, 10, 10, 10])
            bal_btn.bind(pos=lambda instance, value: setattr(bal_rect, 'pos', value))
            bal_btn.bind(size=lambda instance, value: setattr(bal_rect, 'size', value))
            bal_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
            bal_btn.canvas.before.add(bal_rect)
            
            low.add_widget(bal_btn)
            
            layout2.add_widget(low)

            search_button = Button( on_press=lambda x: update_widgets(None,tot_sqft.text),size_hint=(None,None),
                                    background_normal='searching.png',size=(150,150),pos_hint={'center_x': 0.5, 'center_y': 0.5})
            
            layout3.add_widget(search_button)

            layout1.add_widget(layout2)
            layout1.add_widget(layout3)

            if len(layout.children)==0:
                layout.add_widget(layout1)
            else:
                label2 = layout.children[0]
                layout.add_widget(layout1)
                layout.remove_widget(label2)

        else:
            global alist
            alist=[None,None,None,None,None]
            def searching_popup(instance):
                
                content = BoxLayout(orientation='vertical', padding=(10, 20, 10, 20),spacing=10)
                
                label1 = Label(text='Location : ')
                content.add_widget(label1)
                loc_btn = Factory.FDDButton(text="Select Location", size_hint=(None, None),width=250,height=50)
                loc_fdd = button_update(loc_list, loc_btn, 0 )
                loc_btn.bind(on_release=lambda btn: loc_fdd.open(loc_btn))
                loc_btn.background_color = (1, 1, 1, 0)
                loc_rect = RoundedRectangle(pos=loc_btn.pos, size=loc_btn.size, radius=[10, 10, 10, 10])
                loc_btn.bind(pos=lambda instance, value: setattr(loc_rect, 'pos', value))
                loc_btn.bind(size=lambda instance, value: setattr(loc_rect, 'size', value))
                loc_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
                loc_btn.canvas.before.add(loc_rect)
                content.add_widget(loc_btn)

                label1 = Label(text='Total Sqft : ')
                content.add_widget(label1)
                tot_sqft = TextInput(padding_y=12.5)
                content.add_widget(tot_sqft)

                baby=BoxLayout(orientation='horizontal')
                label1 = Label(text='BHK : ')
                baby.add_widget(label1)
                bhk_btn = Factory.FDDButton(text="BHK",  height=50)
                bhk_fdd = button_update(bhk_list, bhk_btn, 1)
                bhk_btn.bind(on_release=lambda btn: bhk_fdd.open(bhk_btn))
                bhk_btn.background_color = (1, 1, 1, 0)
                bhk_rect = RoundedRectangle(pos=bhk_btn.pos, size=bhk_btn.size, radius=[10, 10, 10, 10])
                bhk_btn.bind(pos=lambda instance, value: setattr(bhk_rect, 'pos', value))
                bhk_btn.bind(size=lambda instance, value: setattr(bhk_rect, 'size', value))
                bhk_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
                bhk_btn.canvas.before.add(bhk_rect)
                baby.add_widget(bhk_btn)
                content.add_widget(baby)
                
                baby=BoxLayout(orientation='horizontal')
                label1 = Label(text='bath : ')
                baby.add_widget(label1)
                bath_btn = Factory.FDDButton(text="bath", height=50)
                bath_fdd = button_update(bath_list, bath_btn, 2)
                bath_btn.bind(on_release=lambda btn: bath_fdd.open(bath_btn))
                bath_btn.background_color = (1, 1, 1, 0)
                bath_rect = RoundedRectangle(pos=bath_btn.pos, size=bath_btn.size, radius=[10, 10, 10, 10])
                bath_btn.bind(pos=lambda instance, value: setattr(bath_rect, 'pos', value))
                bath_btn.bind(size=lambda instance, value: setattr(bath_rect, 'size', value))
                bath_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
                bath_btn.canvas.before.add(bath_rect)
                baby.add_widget(bath_btn)
                content.add_widget(baby)

                baby=BoxLayout(orientation='horizontal')
                label1 = Label(text='Balcony : ')
                baby.add_widget(label1)
                bal_btn = Factory.FDDButton(text="balcony",  height=50)
                bal_fdd = button_update(bal_list, bal_btn, 3)
                bal_btn.bind(on_release=lambda btn: bal_fdd.open(bal_btn))
                bal_btn.background_color = (1, 1, 1, 0)
                bal_rect = RoundedRectangle(pos=bal_btn.pos, size=bal_btn.size, radius=[10, 10, 10, 10])
                bal_btn.bind(pos=lambda instance, value: setattr(bal_rect, 'pos', value))
                bal_btn.bind(size=lambda instance, value: setattr(bal_rect, 'size', value))
                bal_btn.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
                bal_btn.canvas.before.add(bal_rect)
                baby.add_widget(bal_btn)
                content.add_widget(baby)
                
                search_button = Button(text='search', on_press=lambda x: update_widgets(popup,tot_sqft.text))
                search_button.background_color = (1, 1, 1, 0)
                sea_rect = RoundedRectangle(pos=search_button.pos, size=search_button.size, radius=[10, 10, 10, 10],height=50)
                search_button.bind(pos=lambda instance, value: setattr(sea_rect, 'pos', value))
                search_button.bind(size=lambda instance, value: setattr(sea_rect, 'size', value))
                search_button.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
                search_button.canvas.before.add(sea_rect)
                content.add_widget(search_button)
        
                popup = Popup(title='search', content=content, size_hint=(None, None), size=(300,600 ))
                popup.open()

            layout1= BoxLayout(orientation='horizontal')
            search_button = Button( on_press=searching_popup,size_hint=(None,None),
                                    background_normal='searching.png',size=(150,150),pos_hint={'center_x': 0.5, 'center_y': 0.5})
            layout1.add_widget(search_button)

            if len(layout.children)==0:
                layout.add_widget(layout1)
            else:
                label2 = layout.children[0]
                layout.add_widget(layout1)
                layout.remove_widget(label2)
                
    real_search_layout(Window.width)
    def on_width_change_for_Search(instance, value):
        real_search_layout(value)

    Window.bind(width=on_width_change_for_Search)
            
def prediction(layout):
    def predict(location,bhk,bath,balcony,sqft):
        pipe = pickle.load(open(f"F://bms//hm//kivyy//LinearRegression.pkl",'rb'))
        ip = pd.DataFrame([[location,sqft,bath,bhk,balcony]],columns=['location','total_sqft','bath','bhk','balcony'])
        prediction = pipe.predict(ip)[0]

        return str(np.round(prediction,2))
    
    global alist
    if alist[0]==None or alist[4]==None or alist[4]=='':
        text1="Please enter both location and total sqft to continue with prediction results"
        s=15
        b=False
    else:
        if alist[1]==None:
            bhk=2
        else:
            bhk=float(alist[1])
        if alist[2]==None:
            bath=2
        else:
            bath=float(alist[2])
        if alist[3]==None:
            balcony=2
        else:
            balcony=float(alist[3])
        pred=predict(alist[0],bhk,bath,balcony,float(alist[4]))
        if float(pred)>100:
            t1=str(pred[0])
            t=t1+" Crores and "+str(pred[1:]) + " Lakhs"
        else:
            t=str(pred)+" Lakhs"
        text1="PREDICTION : "+t
        s=30
        b=True

    label3 = Label(text=text1,size_hint=(1, None),text_size=(0.7*Window.width, None),  halign='center', valign='top',  padding=(10, 10), font_size=s,bold=b)
    if len(layout.children)==0:
        
        layout.add_widget(label3)
    else:
        label2 = layout.children[0]
        layout.add_widget(label3)
        layout.remove_widget(label2)

    def on_width_change_for_pred(instance, value):
        label3 = Label(text=text1,size_hint=(1, None),text_size=(value, None),  halign='center', valign='top',  padding=(10, 10))
        if len(layout.children)==0:
        
            layout.add_widget(label3)
        else:
            label2 = layout.children[0]
            layout.add_widget(label3)
            layout.remove_widget(label2)

    Window.bind(width=on_width_change_for_pred)
              
def table(layout):

    global alist
    data=data_table(alist[0],alist[1],alist[2], alist[3])
    labels_text = [ 'Tot Sqft', 'bath', 'Balcony', 'BHK', 'per Sqft']

    def table_real_layout(value):
        if value>700:
            box_layout=BoxLayout(orientation='vertical',size_hint=(1, 1))
            scroll_view1 = ScrollView(size_hint=(1,1), do_scroll_x=True, do_scroll_y=True, scroll_type=['bars', 'content'])
            scroll_view2 = ScrollView(size_hint=(1,None), height=50,do_scroll_x=True, do_scroll_y=True, scroll_type=['bars', 'content'])
            
            label4 = GridLayout(cols=6, row_force_default=True, row_default_height=dp(40),size_hint=(1,1)
                                ,spacing=[0,10],padding=(10,10,10,10))

            
            label = Button( text='Location',size_hint_x=0.35,
                            background_color=(0.5,0.5,1,1))
            label4.add_widget(label)

            for text in labels_text:
                label = Button( text=text,size_hint_x=0.13,
                                background_color=(0.5,0.5,1,1))
                label4.add_widget(label)
                
            label3 = GridLayout(cols=6, row_force_default=True, row_default_height=dp(50),size_hint=(1,None),spacing=[0,10],padding=(10,10,10,10))

            for row in data:
                label = Label( text=row[0],size_hint_x=0.35, halign='center',text_size=(None, None))
                label3.add_widget(label)
                for i in range(1,6):
                    label = Label( text=row[i],size_hint_x=0.13, halign='center', text_size=(None, None))
                    label3.add_widget(label)


            label3.bind(minimum_height=label3.setter('height'), minimum_width=label3.setter('width'))
            label4.bind(minimum_width=label4.setter('width'))
            
            scroll_view1.add_widget(label3)
            scroll_view2.add_widget(label4)
            box_layout.add_widget(scroll_view2)
            box_layout.add_widget(scroll_view1)
            if len(layout.children)==0:
                layout.add_widget(box_layout)
            else:
                label2 = layout.children[0]
                layout.add_widget(box_layout)
                layout.remove_widget(label2)

        else:

            box_layout=BoxLayout(orientation='vertical',size_hint=(1, 1))
            scroll_view1 = ScrollView(size_hint=(1,1), do_scroll_x=True, do_scroll_y=True, scroll_type=['bars', 'content'])
            scroll_view2 = ScrollView(size_hint=(1,None), height=50,do_scroll_x=True, do_scroll_y=True, scroll_type=['bars', 'content'])
            
            label4 = GridLayout(cols=6, row_force_default=True, row_default_height=dp(40),size_hint=(None,None),spacing=[0,10],padding=(10,10,10,10))
            
            label = Button( text='Location',size_hint_min_x=200,width=200,
                            background_color=(0.5,0.5,1,1))
            label4.add_widget(label)

            for text in labels_text:
                label = Button( text=text,size_hint_min_x=75,width=75,
                                background_color=(0.5,0.5,1,1))
                label4.add_widget(label)
                
            label3 = GridLayout(cols=6, row_force_default=True, row_default_height=dp(50),size_hint=(None,None))

            for row in data:
                label = Label( text=row[0], size_hint_min_x=200, halign='center', width=200, text_size=(None, None))
                label3.add_widget(label)
                for i in range(1,6):
                    label = Label( text=row[i], size_hint_min_x=75, halign='center', width=75, text_size=(None, None))
                    label3.add_widget(label)


            label3.bind(minimum_height=label3.setter('height'), minimum_width=label3.setter('width'))
            label4.bind(minimum_width=label4.setter('width'))
            
            scroll_view1.add_widget(label3)
            scroll_view2.add_widget(label4)
            box_layout.add_widget(scroll_view2)
            box_layout.add_widget(scroll_view1)
            if len(layout.children)==0:
                layout.add_widget(box_layout)
            else:
                label2 = layout.children[0]
                layout.add_widget(box_layout)
                layout.remove_widget(label2)
        
                
    table_real_layout(Window.width)
    def on_width_change(instance, value):
        table_real_layout(value)
  
    Window.bind(width=on_width_change)

def chart(layout,text1):

    def chart1():
        global alist
        l = alist[0]
        if l is None:
            l = '1st Block Jayanagar'
        data = pd.read_csv(r'F:\bms\hm\kivyy\clean_data.csv')
        fig1, ax1 = plt.subplots()
        fig1.set_facecolor('#000000')

        for location, location_df in data.groupby('location'):
            if location == l:
                location_df['bhk'].hist(bins=5, label='Count', alpha=0.7, color='#5c5cbd')
        
        ax1.set_xlabel("BHK",fontsize=8)
        ax1.set_xticks(range(1,7))
        ax1.set_ylabel("Count",fontsize=8)
        ax1.set_title("BHK Distribution in " + l,color='white',fontsize=10)
        ax1.legend()

        # Set the background color to black
        ax1.set_facecolor('#000000')
        plt.subplots_adjust(left=0.2)
        # Set text colors to white
        ax1.xaxis.label.set_color('white')
        ax1.yaxis.label.set_color('white')
        ax1.tick_params(axis='x', colors='white')
        ax1.tick_params(axis='y', colors='white')
        ax1.grid(False)

        # Create a canvas
        canvas1 = FigureCanvasKivyAgg(fig1)
        return canvas1

    def chart2():
        b = alist[1]
        if b is None:
            b = 3
        else:
            b = int(b)

        x1 = []
        d = []
        z3 = []
        
        fig2, ax2 = plt.subplots()
        q = pd.read_csv(r'F:\bms\hm\kivyy\clean_data.csv')
        df = q[q.bhk == b]
        for location, location_df in df.groupby('location'):
            x1.append(location_df['price'].mean())
        x1.sort()
        Q1 = int(0.25 * len(x1))
        Q3 = int(0.75 * len(x1))
        IQR = x1[Q3] - x1[Q1]
        j = 0
        for i in x1:
            if (i < Q1 - 1.5 * IQR) or (i > Q3 + 1.5 * IQR):
                j += 1
            else:
                z3.append(i)
        d = z3
        p = np.array([0.0, 25.0, 50.0, 75.0, 100.0])
        perc = np.percentile(d, p)

        # Set background color and figure color to black
        fig2.patch.set_facecolor('#000000')
        ax2.set_facecolor('#000000')
        
        plt.subplots_adjust(left=0.2)
        # Set text color to white
        ax2.xaxis.label.set_color('white')
        ax2.yaxis.label.set_color('white')
        ax2.title.set_color('white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['top'].set_color('white')
        ax2.spines['right'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')

        # Plot the data with red points and blue line
        plt.plot(d, color='#5c5cbd', label='Line')
        plt.scatter((len(d) - 1) * p / 100., perc, color='red', label='Points')

        plt.title("Percentile Prices of {} BHK in Bangalore".format(b),fontsize=10)
        plt.xlabel("Percentile",fontsize=8)
        plt.ylabel("Mean Price",fontsize=8)
        plt.xticks((len(d) - 1) * p / 100., map(str, p))

        canvas2 = FigureCanvasKivyAgg(fig2,size_hint=(1, 1))
        return canvas2
        

    def real_chart_layout(value):
        if value>800:

            box=BoxLayout(orientation='vertical')

            canvas1 = chart1()
            
            box.add_widget(canvas1)


            
    
            #box.add_widget(canvas1)
            canvas2=chart2()
            box.add_widget(canvas2)

            if len(layout.children)==0:
                layout.add_widget(box)
            else:
                label2 = layout.children[0]
                layout.add_widget(box)
                layout.remove_widget(label2)
        else:
            def chart_popup(instance):
                box=BoxLayout(orientation='vertical',size_hint=(1, 1))

                canvas1=chart1()
                canvas2=chart2()

                box.add_widget(canvas1)
                box.add_widget(canvas2)
                popup = Popup(title='',content=box, size_hint=(None, None), size=(400, 775),background_color = (0, 0, 0, 1))
                popup.separator_height = 0
                
                popup.open()

            layout1= BoxLayout(orientation='horizontal')
            chart_button = Button( on_press=chart_popup ,background_normal='analysis.png',
                                    size=(150,150),pos_hint={'center_x': 0.5, 'center_y': 0.5},size_hint=(None, None))
            layout1.add_widget(chart_button)
            
            if len(layout.children)==0:
                layout.add_widget(layout1)
            else:
                label2 = layout.children[0]
                layout.add_widget(layout1)
                layout.remove_widget(label2)

    real_chart_layout(Window.width)
    def on_width_change_for_chart(instance, value):
        real_chart_layout(value)

    Window.bind(width=on_width_change_for_chart)

class HousePredictionApp(App):
    def build(self):
        self.start_screen()
        self.home_screen()
        return screen_manager
    
    def start_screen(self):
        start_screen = Screen(name='start')
        main_layout = BoxLayout(orientation='vertical',size_hint=(1,1))
        box=BoxLayout(orientation='horizontal',size_hint=(1,0.5))

        image=Image(source='homepage.png',pos_hint={'center_x': 0.5, 'center_y': 0.5})
        box.add_widget(image)
        main_layout.add_widget(box)

        buttons_layout = BoxLayout(orientation='horizontal',spacing=20, padding=(20, 0, 20, 0),size_hint=(1,0.5))
        
        login_button = Button(text='Login', on_press=show_login_popup, size_hint_y=0.2 ,
                              font_size=30,size_hint_x=0.2,pos_hint={'center_x': 0.5, 'center_y': 0.5})
        signup_button = Button(text='Signup', on_press=show_signup_popup,
                               size_hint_y=0.2 ,
                               size_hint_x=0.2,pos_hint={'center_x': 0.5, 'center_y': 0.5},
                               font_size=30)
        
        signup_button.background_color = (1, 1, 1, 0)
        signup_rect = RoundedRectangle(pos=signup_button.pos, size=signup_button.size, radius=[0, 20, 20, 0])
        signup_button.bind(pos=lambda instance, value: setattr(signup_rect, 'pos', value))
        signup_button.bind(size=lambda instance, value: setattr(signup_rect, 'size', value))
        signup_button.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
        signup_button.canvas.before.add(signup_rect)

        login_button.background_color = (1, 1, 1, 0)
        login_rect = RoundedRectangle(pos=login_button.pos, size=login_button.size, radius=[20, 0, 0, 20])
        login_button.bind(pos=lambda instance, value: setattr(login_rect, 'pos', value))
        login_button.bind(size=lambda instance, value: setattr(login_rect, 'size', value))
        login_button.canvas.before.add(Color(0.5, 0.5, 1, 0.5))
        login_button.canvas.before.add(login_rect)
        
        buttons_layout.add_widget(login_button)
        buttons_layout.add_widget(signup_button)
        main_layout.add_widget(buttons_layout)

        start_screen.add_widget(main_layout)
        screen_manager.add_widget(start_screen)
    
    def home_screen(self):
        home_screen = Screen(name='home')
        def main_layout(value):
            if value>800:

                layout = BoxLayout(orientation='vertical',size_hint=(1, 1))

                l1 = BoxLayout(orientation='horizontal',size_hint=(1, 0.2))
                
                home_layout = BoxLayout(orientation='horizontal',size_hint=(0.2, 1))
                
                search_layout = BoxLayout(orientation='horizontal',size_hint=(0.8, 1))
                
                
                l1.add_widget(home_layout)
                l1.add_widget(search_layout)
                layout.add_widget(l1)
                
                l2 = BoxLayout(orientation='horizontal',size_hint=(1, 0.8))
                
                l3 = BoxLayout(orientation='vertical',size_hint=(0.7, 1))

                pred_layout = BoxLayout(orientation='horizontal',size_hint=(1,0.2))
                prediction(pred_layout)

                tab_layout = BoxLayout(orientation='vertical',size_hint=(1, 0.8))
                table(tab_layout)
                
                l3.add_widget(pred_layout)
                l3.add_widget(tab_layout)
                l2.add_widget(l3)

                chart_layout = BoxLayout(orientation='vertical',size_hint=(0.3, 1))
                chart(chart_layout, 'chart')
                
                l2.add_widget(chart_layout)
                layout.add_widget(l2)
                search(search_layout, pred_layout,tab_layout,chart_layout)
                home_button(home_layout, search_layout, pred_layout, tab_layout, chart_layout)
            
                return layout
            else:
                layout = BoxLayout(orientation='vertical',size_hint=(1, 1))

                l1 = BoxLayout(orientation='horizontal',size_hint=(1, 0.2))
                
                home_layout = BoxLayout(orientation='horizontal',size_hint=(0.33, 1))
                
                search_layout = BoxLayout(orientation='horizontal',size_hint=(0.34, 1))

                chart_layout = BoxLayout(orientation='vertical',size_hint=(0.33, 1))
                chart(chart_layout, 'chart')
                
                l1.add_widget(home_layout)
                l1.add_widget(search_layout)
                l1.add_widget(chart_layout)
                layout.add_widget(l1)
                
                l3 = BoxLayout(orientation='vertical',size_hint=(1, 0.8))

                pred_layout = BoxLayout(orientation='horizontal',size_hint=(1,0.2))
                prediction(pred_layout)

                tab_layout = BoxLayout(orientation='vertical',size_hint=(1, 0.8))
                table(tab_layout)
                
                l3.add_widget(pred_layout)
                l3.add_widget(tab_layout)
                layout.add_widget(l3)
        
                search(search_layout, pred_layout,tab_layout,chart_layout)
                home_button(home_layout, search_layout, pred_layout, tab_layout, chart_layout)
            
                return layout

        
        
        layout=main_layout(Window.width)
        home_screen.add_widget(layout)
        screen_manager.add_widget(home_screen)
        def on_width_change_for_main(instance, value):
            new_layout = main_layout(value)
            home_screen.clear_widgets()
            home_screen.add_widget(new_layout)
              
        Window.bind(width=on_width_change_for_main)
        
if __name__ == '__main__':
    Window.size = (825, 700)
    HousePredictionApp().run()








