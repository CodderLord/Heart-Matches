#!/bin/env python3
# coding: utf-8

from PyQt6 import uic

from parsing.help_file import load_config_json

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QTransform, QMovie, QFont, QPalette, QColor
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QProgressBar, QPushButton, QWidget, QTableWidgetItem, QHeaderView
from multi_threading.q_thread_worker import ThreadLogic

from parsing.work_in_site import Connect

from DB.history_matches import DataBase

from about_gen.about_gen_ import GenTextAbout

from pptx_files.create_pptx import PowerPointPresentation


def error(message, title):
	error_ = QMessageBox()
	error_.setWindowTitle(title)
	error_.setText(message)
	error_.setIcon(QMessageBox.Icon.Warning)
	error_.setStandardButtons(QMessageBox.StandardButton.Ok)
	error_.exec()


class LinkInputWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.work_in_thread = None
		self.window = uic.loadUi('qt/uis/first_window.ui', self)
		self.progress_bar = QProgressBar(self)
		self.progress_bar.setGeometry(20, 520, 900, 40)
		self.progress_bar.setMinimum(0)
		self.progress_bar.setMaximum(100)
		self.progress_bar.setHidden(True)
		self.progress_bar.setTextVisible(False)
		self.progress_bar.setStyleSheet("""QProgressBar {border: 2px solid grey;border-radius:2px;padding:1px}
			QProgressBar::chunk {background:rgb(255, 255, 255)}""")
		self.window.setWindowIcon(QIcon('qt/icons/data-analytics-CSGO.ico'))
		self.window.setWindowTitle('CS-GO Analytics')
		self.window.next_button.clicked.connect(self.take_link)
		self.window.cancel_progress_button = QPushButton(self)
		self.window.cancel_progress_button.setGeometry(422, 580, 93, 28)
		self.window.cancel_progress_button.setText('Отмена')
		self.window.cancel_progress_button.setStyleSheet('color: rgb(255, 255, 255); background-color: rgb(25, 43, 69);')
		self.window.cancel_progress_button.setHidden(True)
		self.movie_1 = QMovie("qt/anims/OG.gif")
		self.movie_2 = QMovie("qt/anims/NAVI.gif")
		self.movie_3 = QMovie("qt/anims/ENCE.gif")
		self.movie_4 = QMovie("qt/anims/VITALITY.gif")
		self.window.first_movie.setMovie(self.movie_1)
		self.window.second_movie.setMovie(self.movie_2)
		self.window.third_movie.setMovie(self.movie_3)
		self.window.four_movie.setMovie(self.movie_4)
		self.window.first_movie.setStyleSheet("border: 3px solid black;")
		self.window.second_movie.setStyleSheet("border: 3px solid black;")
		self.window.third_movie.setStyleSheet("border: 3px solid black;")
		self.window.four_movie.setStyleSheet("border: 3px solid black;")
		self.window.list_futures.setStyleSheet("color: rgb(255, 255, 255);")
		self.name_link_exodus = {}
		font = QFont()
		font.setFamily("Open Sans")
		font.setPointSize(20)
		self.window.list_futures.setFont(font)
		self.list_funders()
		self.tab_history()
		self.window.show()

	def list_funders(self):
		name_ing = []
		coefficient_1 = []
		coefficient_2 = []
		time_zone = []
		exodus_list = []
		link_list = []
		con = Connect('https://game-tournaments.com/csgo')
		tab = con.redy_soup
		tab = tab.find(class_='matches table table-striped table-hover').find_all('tr')
		a = 0
		first_ = True
		for i in tab:
			try_mliv = i.find_next(class_='mlive')
			a += 1
			# if don`t use that -> first match is played
			if try_mliv is None:
				if first_ is not False and a > 1:
					first_ = False
					continue
				title = i.find_next(class_='mlink').get('title').strip()
				if title.find('TBD') != -1:  # if one team not determined
					continue
				name_ing.append(title)
				bet_coefficient_1 = i.find_next(class_='bet-percentage bet1').text.strip() \
					if i.find_next(class_='bet-percentage bet1') is not None else ''
				coefficient_1.append(bet_coefficient_1)
				bet_coefficient_2 = i.find_next(class_='bet-percentage bet2').text.strip() \
					if i.find_next(class_='bet-percentage bet1') is not None else ''
				coefficient_2.append(bet_coefficient_2)
				time_to_start = i.find_next(class_='live-in').text.strip()
				time_zone.append(time_to_start)
				link = 'https://game-tournaments.com/' + i.find_next('a').find_next(class_='mlink').get('href')
				link_list.append(link)
		a = 0
		for n in name_ing:
			title = n.replace('против', f' {coefficient_1[a]} против {coefficient_2[a]}') + '          ' + time_zone[a]
			exodus_list.append(title)
			self.name_link_exodus[title] = link_list[a]
			a += 1
		self.window.list_futures.addItems(exodus_list)
		self.window.list_futures.clicked.connect(self.item_clicked)
	
	def tab_history(self):
		all_matches = DataBase().show_all_matches()
		self.window.list_history.setRowCount(len(all_matches))
		row = 0
		for id_match, title, bo, result, real_result, time_zone, url in all_matches:
			self.window.list_history.setItem(row, 0, QTableWidgetItem(str(id_match)))
			self.window.list_history.setItem(row, 1, QTableWidgetItem(title))
			self.window.list_history.setItem(row, 2, QTableWidgetItem(str(bo)))
			self.window.list_history.setItem(row, 3, QTableWidgetItem(str(result)))
			self.window.list_history.setItem(row, 4, QTableWidgetItem(str(real_result)))
			self.window.list_history.setItem(row, 5, QTableWidgetItem(str(time_zone).split('.')[0]))
			row += 1
		new_font = QFont("Arial", 19)
		self.window.list_history.setFont(new_font)
		palette = self.window.list_history.palette()
		self.window.list_history.resizeColumnsToContents()
		self.window.list_history.resizeRowsToContents()
		palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
		palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
		self.window.list_history.setStyleSheet("background-color: rgb(25, 43, 69);")
		self.window.list_history.setPalette(palette)
	
	def item_clicked(self):
		item = self.window.list_futures.currentItem()
		self.window.input_link.setText(self.name_link_exodus[item.text()])

	def take_link(self):
		link = self.window.input_link.text()
		if link == '' or link.find('https://') != 0:
			error(message='Ссылка указана неверно.', title='Ошибка')
		else:
			self.window.next_button.hide()
			self.window.help_label.setHidden(True)
			self.window.input_link.hide()
			self.progress_bar.setHidden(False)
			self.window.cancel_progress_button.setHidden(False)
			self.window.tabWidgets.hide()
			self.start_work_in_site(link)
			self.movie_1.start()
			self.movie_2.start()
			self.movie_3.start()
			self.movie_4.start()

	def start_work_in_site(self, link):
		self.work_in_thread = ThreadLogic(link)
		self.work_in_thread.progress_bar_signal.connect(self.upp_value)
		self.work_in_thread.finished_signal.connect(self.after_finish)
		self.work_in_thread.error_signal.connect(lambda: error(message='Одна из команд неопределенна.', title='Ошибка'))
		self.work_in_thread.start()

	def upp_value(self, value):
		self.progress_bar.setValue(value)

	def after_finish(self, path):
		self.close()
		UI(path)


class UI(QMainWindow):
	def __init__(self, path):
		super().__init__()
		self.dict_team_info = load_config_json(path)
		self.window = uic.loadUi('qt/uis/main_window.ui', self)
		self.transform = QTransform()
		self.transform.translate(500, 500)
		self.transform.rotate(450)
		self.transform.scale(0.5, 1.0)
		self.window.team_tabs.setDocumentMode(True)
		self.window.team_tabs.setMovable(True)
		self.window.setWindowIcon(QIcon('qt/icons/data-analytics-CSGO.ico'))
		self.set_basis_info_tab()
		self.set_history_tab()
		self.set_coefficient_tab()
		self.set_old_scores_tab()
		self.set_old_ratio_scores_tab()
		self.set_same_teams_scores_tab()
		self.set_exodus_tab()
		self.window.show()
	
	def set_basis_info_tab(self):
		self.window.png_team_one.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/{self.dict_team_info["name_1"]}.jpg'))
		self.window.png_team_two.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/{self.dict_team_info["name_2"]}.jpg'))
		self.window.name_team_one.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">{self.dict_team_info["name_1"]}
			</span></p></body></html>""")
		self.window.name_team_one.adjustSize()
		self.window.name_team_two.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">{self.dict_team_info["name_2"]}
			</span></p></body></html>""")
		self.window.name_team_two.adjustSize()
		self.window.bo_label.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">Всего карт:\n
				{self.dict_team_info["best_of_number"]}</span></p></body></html>""")
		team_one_about = GenTextAbout('RU', self.dict_team_info["name_1"], self.dict_team_info["name_1"], self.dict_team_info["name_2"], int(self.dict_team_info["history_score_dict"][self.dict_team_info["name_1"]]) + int(self.dict_team_info["history_score_dict"][self.dict_team_info["name_2"]]), self.dict_team_info["history_score_dict"][self.dict_team_info["name_1"]], str(self.dict_team_info["coefficient_dict"][self.dict_team_info["name_1"]])[0: 3], self.dict_team_info["experience_1"], len(self.dict_team_info["team_one_old_scores_win"])+len(self.dict_team_info["team_one_old_scores_lose"]), len(self.dict_team_info["team_one_old_scores_win"]), sum([int(i.split('-')[0]) for i in self.dict_team_info["first_same_dict"].values()]), sum([int(i.split('-')[1]) for i in self.dict_team_info["first_same_dict"].values()]) if self.dict_team_info["first_same_dict"] != {} else 0)
		text_1 = team_one_about.ret_about_text()
		self.window.text_Browser_for_team_one.setPlainText(f"""{text_1}""")
		self.window.text_Browser_for_team_one.setStyleSheet("background-color: rgb(25, 43, 69); color: white; text-align: center;")
		font = self.window.text_Browser_for_team_one.font()
		font.setPointSize(16)
		self.window.text_Browser_for_team_one.setFont(font)
		self.window.text_Browser_for_team_one.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.window.text_Browser_for_team_two.setFont(font)
		team_two_about = GenTextAbout('RU', self.dict_team_info["name_2"], self.dict_team_info["name_1"], self.dict_team_info["name_2"], int(self.dict_team_info["history_score_dict"][self.dict_team_info["name_1"]]) + int(self.dict_team_info["history_score_dict"][self.dict_team_info["name_2"]]), self.dict_team_info["history_score_dict"][self.dict_team_info["name_2"]], str(self.dict_team_info["coefficient_dict"][self.dict_team_info["name_2"]])[0: 3], self.dict_team_info["experience_2"], len(self.dict_team_info["team_two_old_scores_win"])+len(self.dict_team_info["team_two_old_scores_lose"]), len(self.dict_team_info["team_two_old_scores_win"]), sum([int(i.split('-')[0]) for i in self.dict_team_info["second_same_dict"].values()]), sum([int(i.split('-')[1]) for i in self.dict_team_info["second_same_dict"].values()]) if self.dict_team_info["second_same_dict"] != {} else 0)
		text_2 = team_two_about.ret_about_text()
		self.window.text_Browser_for_team_two.setPlainText(f"""{text_2}""")
		self.window.text_Browser_for_team_two.setStyleSheet("background-color: rgb(25, 43, 69); color: white; text-align: center;")
		self.window.text_Browser_for_team_two.setAlignment(Qt.AlignmentFlag.AlignCenter)
			
	def set_history_tab(self):
		if len(self.dict_team_info["history_time_zone_list"]) <= 1:
			self.window.team_tabs.setTabEnabled(1, False)
		self.window.ratio_graphics_history.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/history_graphics.png'))
		self.window.text_first_team_percent_history_label.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Команда {self.dict_team_info["name_1"]}
			имеет {self.dict_team_info["percent_history_one"]} побед</span></p></body></html>""")
		self.window.text_first_team_percent_history_label.adjustSize()
		self.window.text_second_team_percent_history_label.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Команда {self.dict_team_info["name_2"]}
			имеет {self.dict_team_info["percent_history_two"]} побед</span></p></body></html>""")
		self.window.text_second_team_percent_history_label.adjustSize()
		self.window.trend_graphics_coefficient.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/history_trend_graphics.png'))
		self.window.all_col_matches_graphics_two.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Всего было сыгранно
				{len(self.dict_team_info["history_time_zone_list"])} матчей</span></p></body></html>""")

	def set_coefficient_tab(self):
		self.window.coefficient_graphics.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/coefficient_graphics.png'))
		self.window.first_coefficient_label.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Коефициет команды
			{self.dict_team_info["name_1"]} от букмекеров :
			{(self.dict_team_info["coefficient_dict"])[self.dict_team_info["name_1"]]}</span></p></body></html>""")
		self.window.first_coefficient_label.adjustSize()
		self.window.second_coefficient_label.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Коефициет команды
			{self.dict_team_info["name_2"]} от букмекеров :
			{(self.dict_team_info["coefficient_dict"])[self.dict_team_info["name_2"]]}</span></p></body></html>""")
		self.window.second_coefficient_label.adjustSize()
		self.window.graphics_experience.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/experience_graphics.png'))
		self.window.col_win_team_one_label.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Количество игр команды
			{self.dict_team_info["name_1"]}: {self.dict_team_info["experience_1"]}</span></p></body></html>""")
		self.window.col_win_team_two_label.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Количество игр команды
			{self.dict_team_info["name_2"]}: {self.dict_team_info["experience_2"]}</span></p></body></html>""")

	def set_old_scores_tab(self):
		self.window.form_team_1_graphics.setPixmap(QPixmap(
			f'{self.dict_team_info["path_on_disc"]}/old_scores_trend_graphics_one.png'))
		self.window.form_team_label_one.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Всего была сыгранно
			{len(self.dict_team_info["list_old_scores_one"])} игр за последних 3 месяца</span></p></body></html>""")
		self.window.form_team_label_one.adjustSize()
		self.window.form_team_2_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/old_scores_trend_graphics_two.png'))
		self.window.form_team_label_two.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Всего была сыгранно
			{len(self.dict_team_info["list_old_scores_two"])} игр за последних 3 месяца</span></p></body></html>""")
		self.window.form_team_label_two.adjustSize()

	def set_old_ratio_scores_tab(self):
		self.window.ratio_form_wins_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/old_scores_ratio_graphics_win.png'))
		self.window.ratio_form_lose_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/old_scores_ratio_graphics_lose.png'))
		self.window.info_label_wins_team_1_old_scores.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_1"]}
			было выигранно {len(self.dict_team_info["team_one_old_scores_win"])} игр</span></p></body></html>""")
		self.window.info_label_wins_team_2_old_scores.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_2"]}
			было выигранно {len(self.dict_team_info["team_two_old_scores_win"])} игр</span></p></body></html>""")
		self.window.info_label_loses_team_1_old_scores.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_1"]}
			было проигранно {len(self.dict_team_info["team_one_old_scores_lose"])} игр</span></p></body></html>""")
		self.window.info_label_loses_team_2_old_scores.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_2"]}
			было проигранно {len(self.dict_team_info["team_two_old_scores_lose"])} игр</span></p></body></html>""")
		self.window.info_label_wins_team_1_old_scores.adjustSize()
		self.window.info_label_wins_team_2_old_scores.adjustSize()
		self.window.info_label_loses_team_1_old_scores.adjustSize()
		self.window.info_label_loses_team_2_old_scores.adjustSize()

	def set_same_teams_scores_tab(self):
		if self.dict_team_info["team_one_win"] == 0 and self.dict_team_info["team_two_win"] == 0 and \
				self.dict_team_info["team_one_lose"] == 0 and self.dict_team_info["team_two_lose"] == 0:
			self.window.team_tabs.setTabEnabled(5, False)
		self.window.same_team_win_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/same_win_graphics.png'))
		self.window.same_team_lose_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/same_lose_graphics.png'))
		self.window.first_team_win.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">{self.dict_team_info["name_1"]}
			команда победила {self.dict_team_info["team_one_win"]} раз</span></p></body></html>""")
		self.window.second_team_win.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">{self.dict_team_info["name_2"]}
			команда победила {self.dict_team_info["team_two_win"]} раз</span></p></body></html>""")
		self.window.first_team_lose.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">{self.dict_team_info["name_1"]}
			команда проиграла {self.dict_team_info["team_one_lose"]} раз</span></p></body></html>""")
		self.window.second_team_lose.setText(
			f"""<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">{self.dict_team_info["name_2"]}
			команда проиграла {self.dict_team_info["team_two_lose"]} раз</span></p></body></html>""")

	def set_exodus_tab(self):
		self.window.ratio_exodus_graphic.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/exodus_graphics.png'))
		self.window.exodus_pentagon_graphic.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/pentagon_graphics.png'))
		self.window.button_save_PDF.clicked.connect(self.create_pptx_file)

	def create_pptx_file(self):
		pptx_obj = PowerPointPresentation(self.dict_team_info)
		pptx_obj.create_presentation()
		