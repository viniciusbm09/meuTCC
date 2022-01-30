#Importando bibliotecas
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from typing import Counter
import PIL.Image, PIL.ImageTk
from PIL import Image
import cv2
from matplotlib import image
from mtcnn.mtcnn import MTCNN
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import sched
import time, threading

from numpy import True_
import deep_faces_detec
import statistics

 

#Classe principal
class Application:

    #variavéis para cálculo e de controle
    var_mediana = int(0)
    var_leituras = int(0)
    var_acumulado = []
    var_maior_valor = int(0)
    var_control_frame = 1
    var_count_frame = 0


    

    def __init__(self, window, window_title):
        
        self.s = sched.scheduler(time.time, time.sleep)
        #configurações da interface
        background = 'light blue1'
        self.window = window
        self.window.title(window_title)

        #CONTAINERES
        left_frame = Frame(self.window, width="750", height="700", bg=background)
        left_frame.pack(side=LEFT)

        left_frame_top = Frame(left_frame, width="740", height="100", bg=background)
        left_frame_top.pack(side=TOP)

        left_frame_bottom = Frame(left_frame, width="740", height="200",  bg=background)
        left_frame_bottom.pack(side=BOTTOM)

        right_frame = Frame(self.window, width="650", height="700", bg="orange")
        right_frame.pack(side=LEFT)

        display = Frame(right_frame, width="645", height="565", padx=5, pady=5, bg="orange")
        display.pack(side=TOP)

        display_file = Frame(right_frame, padx=15, pady=15,bg="orange")
        display_file.pack(fill=BOTH)

        tool_bar = Frame(display, bd=8, bg="orange")
        tool_bar.pack(side=BOTTOM)
        
        #DISPLAYS
        self.canvas = Canvas(display, bg="black", width="640", height="360")
        self.canvas.pack()

        self.canvas_frame1 = Canvas(display_file, bg="black", width="218", height="123")
        self.canvas_frame1.pack(side=LEFT)

        self.canvas_frame2 = Canvas(display_file, bg="black", width="218", height="123")
        self.canvas_frame2.pack(side=RIGHT)
    

        #BARRA DE MENUS
        mnBar = Menu(self.window)
        mnArquivo = Menu(mnBar)
        mnArquivo.add_command(label="Abrir", command=self.open_files)
        mnArquivo.add_separator()
        mnArquivo.add_command(label="Fechar sistema", command=self.window.quit)
        mnBar.add_cascade(label="Arquivo: ",menu=mnArquivo)

        #CHECKBUTTON
        self.chk_value = BooleanVar()
        self.chk_value.set(True)
        self.chk_auto = Checkbutton(display_file, text="Detecção automática", var=self.chk_value, bg="orange")
        self.chk_auto.pack()

        #LABELS
        self.lbl_seta = Label(display_file,text="<<  0  >>", bg="orange")
        self.lbl_seta.pack(side=BOTTOM)

        #Label com endereço do arquivo
        self.file_path = StringVar()
        self.lbl_file_path = Label(left_frame, textvariable=self.file_path, anchor="w", bd=8, bg="orange")
        self.lbl_file_path.pack(fill=BOTH)

        #Label com título do quadro de telemetria
        self.lbl_telemetria = Label(left_frame_top, text="T E L E M E T R I A", font="Arial, 25", bd=15, bg=background)
        self.lbl_telemetria.grid(row=0, column=0)

        #Label que mostra a média de participantes
        self.list_media = []
        self.media = StringVar(master=left_frame, value=self.list_media)
        self.lbl_media = Label(left_frame, textvariable=self.media, bd=8, font="Arial, 10", bg="orange")
        self.lbl_media.pack(fill=BOTH)

        #Label que mostra o maior valor
        self.lbl_maior_valor = Label(left_frame, text="Maior valor " + str(self.var_maior_valor), bd=2, font="Arial, 12", width=25, bg=background, fg="red")
        self.lbl_maior_valor.pack(anchor=W, fill=BOTH)


        #LIST BOX COM SCROLLBAR
        self.my_list = []
        self.var_faces = StringVar(master=left_frame, value=self.my_list)

        self.myscroll = Scrollbar(left_frame) 
        self.myscroll.pack(side = RIGHT, fill = Y) 
        self.lb_report = Listbox(left_frame, yscrollcommand = self.myscroll.set, listvariable=self.var_faces )            
        self.lb_report.pack( fill = BOTH )    
        self.myscroll.config(command = self.lb_report.yview) 


        #BOTÕES
        # Selecionar
        self.btn_select=Button(tool_bar, text="Selecionar arquivo", width=15, command=self.open_files)
        self.btn_select.grid(row=0, column=0)

        # Play
        self.btn_play=Button(tool_bar, text="Play", width=15, command=self.play_video)
        self.btn_play.grid(row=0, column=1)

        # Botão de pausa
        #self.btn_pause=Button(tool_bar, text="Auto detect", width=15, command=self.play_video)
        #self.btn_pause.grid(row=0, column=2)

        # Detecção manual
        self.btn_detec_man=Button(tool_bar, text="Manual detect", width=15, command=self.get_frame_to_detect)
        self.btn_detec_man.grid(row=0, column=3)



        #CONFIGURAÇÕES DA INTERFACE
        self.window.configure(bg = background)
        #self.attributes('-fullscreen', True) #Tela cheia
        self.window.state('zoomed')
        self.window.config(menu=mnBar)
        self.delay = 15   # ms
        self.window.mainloop()
        

    #Função abrir arquivos   
    def open_files(self):
        self.filename = filedialog.askopenfilename(title="Selecione o arquivo", 
        filetypes=(("Arquivos MP4", "*.mp4"),("Arquivos WMV", "*.wmv"), 
        ("Arquivos AVI", "*.avi")))
        
        self.file_path.set("Arquivo: " + self.filename)
        self.cap = cv2.VideoCapture(self.filename)


    #Função para obter o frame
    def get_frame(self): 
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        except:
            messagebox.showerror(title='Vídeo não encontrado.', message='Selecione um arquivo de vídeo.')



    #Função para executar o video obtendo os frames em modo recursivo
    def play_video(self):
        
        ret, frame = self.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)
            self.window.after(self.delay, self.play_video)
            self.var_count_frame += 1

            #Verifica se o check está ativando a detecção automática
            if self.chk_value.get() == True:
                if (self.var_count_frame % 100) == 0:
                    self.get_frame_to_detect()
                    

    #Função para detectar as faces no frame capturado
    def get_frame_to_detect(self):
        
        #captura para detecção
        success, frame = self.get_frame()
        if success:
            #cv2.imwrite("frame20sec.jpg", frame)
                    
            #cria o detector
            detector = MTCNN()
            
            #Detecta as faces no frame capturado
            faces = detector.detect_faces(frame)

            #calcula os valores acrescentando as novas detecções
            self.var_leituras += 1
            self.var_acumulado.append(int(len(faces)))
            self.var_mediana = statistics.median_high(self.var_acumulado)
            
            #verifica se a detecção atual é o maior valor detectado
            x = int(len(faces))
            y = self.var_maior_valor
            if x > y:
                self.var_maior_valor = x

            #Configura o texto do label com o resultado
            self.lbl_maior_valor.config(text="Maior valor detectado: " + str(self.var_maior_valor) + " faces.")
            
        
            #Configura o texto do label com o resultado
            self.media.set("Mediana de " + str(self.var_mediana) + " participantes em " + str(self.var_leituras) + " leituras")

            #Adiciona o número de faces na lista
            self.my_list.append("Detectadas " + str(len(faces)) + " faces")

            #Configura a lista na variável do tipo StringVar()
            self.var_faces.set(self.my_list)

            #Chama a função para desenhar os quadros em cada face
            img = deep_faces_detec.draw_rectangle(frame, faces)
            #self.photo2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
            
                     
            
            if self.var_control_frame == 1:
                
                self.file_img1 = PIL.ImageTk.PhotoImage(Image.open('captura.png')) 
                self.canvas_frame1.create_image(0, 0, image = self.file_img1, anchor = NW)        
                self.var_control_frame = 0
                self.lbl_seta.config(text="<<  1    ") 
                
            elif self.var_control_frame == 0:
                self.file_img2 = PIL.ImageTk.PhotoImage(Image.open('captura.png')) 
                self.canvas_frame2.create_image(0, 0, image = self.file_img2, anchor = NW)  
                 
                self.var_control_frame = 1 
                self.lbl_seta.config(text="    2  >>")        

      

    ## END FUNCTIONS ##        
    
#### END CLASS ####



#Call to application
Application(Tk(),"DEEP LEARNING NA DETECÇÃO FACIAL PARA CONTAGEM AUTOMÁTICA DE PÚBLICO")