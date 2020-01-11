import kivy
from kivy.app import App
from kivy.lang import Builder

from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.uix.widget import Widget

from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition

from kivy.core.window import Window

import random, time
from datetime import datetime
from random import randint as rn
from random import shuffle as rl


random.seed()
Builder.load_file('scrs.kv')
game_version = "0.0"

class MyButton(Button):
	pass
class Menu(Screen):
	pass
	def play(self):
		self.manager.current = "game"
		g = self.manager.get_screen("game")
		g.N0 = 1
		g.N1 = 9
		g.new_sesj()
		g.program_active = False
		
		
	def play_program(self):
		self.manager.current = "game"
		g = self.manager.get_screen("game")
		g.new_program()
		g.program_active = True
	
class Gamescr(Screen):
	pass

	def new_round(self):
		self.round_nr += 1
		N0, N1 = self.N0, self.N1 
		q = self.ids['Q']

		self.nr0 = rn(N0,N1)
		self.nr1 = rn(N0,N1)


		Q = str(self.nr0) + " X " + str(self.nr1)
		q.text = Q
		self.answer = self.nr0*self.nr1

		self.fill_answers(N0, N1)
			

	def fill_answers(self, N0, N1):
		a = []
		a.append(self.nr0*self.nr1)
		a.append((self.nr0 + (-1)**rn(0,1)*rn(0,1))*(self.nr1 + (-1)**rn(0,1)))
		a.append(abs(self.nr0*self.nr1 + (-1)**rn(0,1)*rn(1,10)))
		a.append(rn(N0,N1)*rn(N0,N1))

		rl(a)
		for i in range(len(self.buts)):
			self.buts[i].text = str(a[i])

	def init(self):

		#//init buts
		grid = self.ids['grid']
		self.buts = []
		for i in range(4):
			self.buts.append(MyButton())
			self.buts[i].bind(on_press=self.check_answer)
			grid.add_widget(self.buts[i])

		#//

		
	def new_sesj(self, rounds = 20):
		self.N_rounds = rounds
		self.round_nr = 0

		self.new_round()
		self.t0 = time.time()


	def new_program(self, prog_type=0):
		if prog_type == 0:
			self.prog0_init()
		
			
	def prog0_init(self):
		self.prog_type = 0
		self.phase = 0
		self.sesj_nr = 0

		self.prog_sesj = []

		rounds = 20
		Nps = 4
		N = 9
		
		for ps in range(Nps):
			ps+=1
			sesj_Ns = []

			for i in range(N):
				i+=1
				if i+ps > N+1:
					break
			
				p = [i, i+ps]
				sesj_Ns.append(p)
			self.prog_sesj.append(sesj_Ns)

		#self.prog_sesj = [[[1,2]],[[3,4]]] #deleteme
		self.prog_updt()
		self.new_sesj(rounds)
		self.sesj_max = len(self.prog_sesj[self.phase])
		self.phase_max = len(self.prog_sesj)
		

	def prog_updt(self):
		self.N0, self.N1 = self.prog_sesj[self.phase][self.sesj_nr]
		
	def prog0_next(self):
		self.sesj_max = len(self.prog_sesj[self.phase])
		self.phase_max = len(self.prog_sesj)
		
		if self.sesj_nr == self.sesj_max-1:
			self.sesj_nr = 0
			if self.phase == self.phase_max-1:
				self.phase = 0
			else:
				self.phase += 1
		else:
			self.sesj_nr+=1
		
		self.prog_updt()
		self.new_sesj(self.N_rounds)
		
	def prog_next(self):
		if self.prog_type == 0:
			self.prog0_next()
	
		
	def check_answer(self, btn):
		if int(btn.text) == self.answer:
			if self.round_nr == self.N_rounds:
				self.sesj_complete()
			else:
				self.new_round()
		else:
			self.sesj_failed()
	def sesj_complete(self):
		self.T = time.time() - self.t0
		
		with open("data.txt", "a") as file:

			mystr = ""
			mystr+=str(self.T) + ", "
			mystr+=str(self.round_nr) + ", "			
			mystr+=str(self.N0) + ", "
			mystr+=str(self.N1) + ", "
			mystr+=str(game_version) + ", "
			mystr+= datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			
			file.write(mystr + "\n")


		if self.program_active:
			self.manager.current = "post win prog"

			self.manager.get_screen("post win prog").refresh(self.T,
												self.sesj_nr, self.sesj_max,
												self.phase, self.phase_max)
			
		else:
			self.manager.current = "post win"
			
			self.manager.get_screen("post win").refresh(self.T)
				

	def sesj_failed(self):
		self.manager.current = "post lose"
		self.T = time.time() - self.t0
		self.Tavg = self.T/(self.round_nr)
		self.manager.get_screen("post lose").refresh(self.Tavg)
		

class PostGame(Screen):
	pass


	def to_menu(self, but):
		self.manager.current = "menu"


		
	def try_again(self, but):
		self.manager.current = "game"
		g = self.manager.get_screen("game")
		g.new_sesj(g.N_rounds)	
	



class PostLose(PostGame):
	def __init__(self, **kwargs):
		super(PostLose, self).__init__(**kwargs)
		self.init_buts()


	def init_buts(self, t=3):
		self.box = self.ids['box']


		self.lbl = Label(text = "Failed with avg time %.2f" %(t),
								background_color = (0,0,1,0.3),
								color = (0,1,0,1),
							   size_hint = (1,0.4))

		self.lbl.font_size = 0.07*Window.size[0]
		self.box.add_widget(self.lbl)



		self.buts = []		
		self.buts.append(MyButton(text = "Try again"))
		self.buts[-1].bind(on_press = self.try_again)

		self.buts.append(MyButton(text = "menu"))	
		self.buts[-1].bind(on_press = self.to_menu)	
		for i in range(len(self.buts)):
			self.box.add_widget(self.buts[i])		

		

	def refresh(self, tavg =3):
		fail_msg = "Failed with avg time %.2f" % tavg
		red = (1,0,0,1)
		self.lbl.text = fail_msg
		self.lbl.font_size = 0.06*Window.size[0]
		self.lbl.color = red

		
class PostWin(PostGame):
	def __init__(self, **kwargs):
		super(PostWin, self).__init__(**kwargs)


	def init_buts(self, t=3):
		self.box = self.ids['box']

		self.buts = []
		self.lbl = Label(text = "Completed at %.2f" %(t),
								background_color = (0,0,1,0.3),
								color = (0,1,0,1),
							   size_hint = (1,0.4))

		self.lbl.font_size = 0.07*Window.size[0]
		self.box.add_widget(self.lbl)

		self.buts.append(MyButton(text = "Try again"))
		self.buts[-1].bind(on_press = self.try_again)

		self.buts.append(MyButton(text = "menu"))	
		self.buts[-1].bind(on_press = self.to_menu)	
		for i in range(len(self.buts)):
			
			self.box.add_widget(self.buts[i])
		
		
	def refresh(self, t =3):
		win_msg = "Completed at %.2f" %t
		self.lbl.text = win_msg

	def go_next(self, but):
		self.manager.current = "game"
		self.manager.get_screen("game").prog_next()

class PostProg(PostWin):
	def __init__(self, **kwargs):
		super(PostProg, self).__init__(**kwargs)
		self.init_buts()

	def init_buts(self, t=3):
		self.box = self.ids['box']


		self.lbl = Label(text = "Completed at %.2f" %(t),
								background_color = (0,0,1,0.3),
								color = (0,1,0,1),
							   size_hint = (1,0.4))

		self.lbl.font_size = 0.07*Window.size[0]
		self.box.add_widget(self.lbl)
		self.lbl2 = Label(text = "SESJ %d/%d     PHASE %d/%d" %(1,1,1,1),
								background_color = (0,0,1,0.3),
								color = (1,1,1,1),
							   size_hint = (1,0.3))

		self.lbl2.font_size = 0.03*Window.size[0]
		self.box.add_widget(self.lbl2)


		self.buts = []		
		self.buts.append(MyButton(text = "Next",
								  size_hint = (1,1.8)))
		self.buts[-1].bind(on_press = self.go_next)


		self.buts.append(MyButton(text = "Try again"))
		self.buts[-1].bind(on_press = self.try_again)

		self.buts.append(MyButton(text = "menu"))	
		self.buts[-1].bind(on_press = self.to_menu)	
		for i in range(len(self.buts)):
			self.box.add_widget(self.buts[i])		
		

	def refresh(self, t, sesj,sesjmax, phase, phasemax):
		win_msg = "Completed at %.2f" %t		
		self.lbl.text = win_msg

		info_txt = "SESJ %d/%d     PHASE %d/%d" %(sesj+1,sesjmax,
												  phase+1,phasemax)
		self.lbl2.text = info_txt


sm = ScreenManager(transition = NoTransition())

m = Menu(name = "menu")
sm.add_widget(m)
#gamescr__
g = Gamescr(name = "game")
g.init()
#___________

sm.add_widget(g)
pgl = PostLose(name = "post lose")
sm.add_widget(pgl)
pgw = PostWin(name = "post win")
pgw.init_buts()
sm.add_widget(pgw)
pgp = PostProg(name = "post win prog")
sm.add_widget(pgp)
sm.current = "menu"

class MainApp(App):
	def build(self):
		return sm




if __name__ == '__main__':	
	MainApp().run()	
		
