#!/bin/env python3
# coding: utf-8

from PyQt6 import uic
from parsing.help_file import load_config_json
import json

from PyQt6.QtGui import QIcon, QPixmap, QTransform
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QProgressBar, QVBoxLayout, QDialog, QWidget
from multi_threading.q_thread_worker import ThreadLogic


class WindowPB(QDialog):
	def __init__(self, window):
		super().__init__(window)
		self.window = window
		self.setWindowIcon(QIcon('qt/icons/data-analytics-CSGO.ico'))
		self.setWindowTitle("Загрузка")
		self.setGeometry(500, 200, 300, 100)
		vbox = QVBoxLayout()
		self.progressbar = QProgressBar()
		self.progressbar.setMaximum(0)
		self.progressbar.setMaximum(100)
		self.progressbar.setTextVisible(False)
		self.progressbar.setStyleSheet("QProgre"
		                               "ssBar {border: 2px solid grey;border-radius:2px;padding:1px}"
		                               "QProgressBar::chunk {background:rgb(255, 255, 255)}")
		vbox.addWidget(self.progressbar)
		self.setLayout(vbox)

	def upp_value(self, value):
		self.progressbar.setValue(value)


class LinkInputWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.work_in_thread = None
		self.window = uic.loadUi('qt/uis/first_window.ui', self)
		self.progressbar_window = WindowPB(self.window)
		self.window.setWindowIcon(QIcon('qt/icons/data-analytics-CSGO.ico'))
		self.window.setWindowTitle('CS-GO Analytics')
		self.window.next_button.clicked.connect(self.take_link)
		self.window.show()

	def take_link(self):
		link = self.input_link.text()
		if link == '' or link.find('https://') != 0:
			error = QMessageBox()
			error.setWindowTitle('Ошибка ввода ссылки')
			error.setText('Ссылка на сайт указанна неверно.')
			error.setIcon(QMessageBox.Icon.Warning)
			error.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
			error.exec()
		else:
			try:
				self.window.hide()
				self.progressbar_window.show()
				self.start_work_in_site(link)
			except ValueError:
				error = QMessageBox()
				error.setWindowTitle('Ошибка работы с матчем')
				error.setText(
					'1.Матч уже начался, либо близок к началу.\n2.Ссылка на матч указана неверно.\n3.Одна из команд ещё не определена.')
				error.setIcon(QMessageBox.Icon.Warning)
				error.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
				error.exec()

	def start_work_in_site(self, link):
		self.work_in_thread = ThreadLogic(link)
		self.work_in_thread.progress_bar_signal.connect(self.progressbar_window.upp_value)
		self.work_in_thread.finished_signal.connect(self.after_finish)
		self.work_in_thread.start()

	def after_finish(self, path):
		self.close()
		self.progressbar_window.close()
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
		self.window.setWindowIcon(QIcon('qt/icons/data-analytics-CSGO.ico'))
		self.set_basis_info_tab()
		self.set_history_tab()
		self.set_coefficient_tab()
		self.set_old_scores_tab()
		self.set_ratio_old_scores_tab()
		self.window.show()

	def set_basis_info_tab(self):
		self.window.png_team_one.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/{self.dict_team_info["name_1"]}.jpg'))
		self.window.png_team_two.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/{self.dict_team_info["name_2"]}.jpg'))
		self.window.name_team_one.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">{self.dict_team_info["name_1"]}</span></p></body></html>')
		self.window.name_team_one.adjustSize()
		self.window.name_team_two.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">{self.dict_team_info["name_2"]}</span></p></body></html>')
		self.window.name_team_two.adjustSize()

	def set_history_tab(self):
		self.window.ratio_graphics_history.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/history_graphics.png'))
		self.window.text_first_team_percent_history_label.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Команда {self.dict_team_info["name_1"]} имеет {self.dict_team_info["percent_history_one"]} побед</span></p></body></html>')
		self.window.text_first_team_percent_history_label.adjustSize()
		self.window.text_second_team_percent_history_label.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Команда {self.dict_team_info["name_2"]} имеет {self.dict_team_info["percent_history_two"]} побед</span></p></body></html>')
		self.window.text_second_team_percent_history_label.adjustSize()
		self.window.trend_graphics_coefficient.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/history_trend_graphics.png'))
		self.window.all_col_matches_graphics_two.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Всего было сыгранно {len(self.dict_team_info["history_time_zone_list"])} матчей</span></p></body></html>')

	def set_coefficient_tab(self):
		self.window.coefficient_graphics.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/coefficient_graphics.png'))
		self.window.first_coefficient_label.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Коефициет команды {self.dict_team_info["name_1"]} от букмекеров : {(self.dict_team_info["coefficient_dict"])[self.dict_team_info["name_1"]]}</span></p></body></html>')
		self.window.first_coefficient_label.adjustSize()
		self.window.second_coefficient_label.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Коефициет команды {self.dict_team_info["name_2"]} от букмекеров : {(self.dict_team_info["coefficient_dict"])[self.dict_team_info["name_2"]]}</span></p></body></html>')
		self.window.second_coefficient_label.adjustSize()
		self.window.graphics_experience.setPixmap(QPixmap(f'{self.dict_team_info["path_on_disc"]}/experience_graphics.png'))
		self.window.col_win_team_one_label.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Количество игр команды {self.dict_team_info["name_1"]}: {self.dict_team_info["experience_1"]}</span></p></body></html>')
		self.window.col_win_team_two_label.setText(f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Количество игр команды {self.dict_team_info["name_2"]}: {self.dict_team_info["experience_2"]}</span></p></body></html>')

	def set_old_scores_tab(self):
		self.window.form_team_1_graphics.setPixmap(QPixmap(
			f'{self.dict_team_info["path_on_disc"]}/old_scores_trend_graphics_one.png'))
		self.window.form_team_label_one.setText(
			f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Всего была сыгранно {len(self.dict_team_info["list_old_scores_one"])} игр за последних 3 месяца</span></p></body></html>')
		self.window.form_team_label_one.adjustSize()
		self.window.form_team_2_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/old_scores_trend_graphics_two.png'))
		self.window.form_team_label_two.setText(
			f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Всего была сыгранно {len(self.dict_team_info["list_old_scores_two"])} игр за последних 3 месяца</span></p></body></html>')
		self.window.form_team_label_two.adjustSize()

	def set_ratio_old_scores_tab(self):
		self.window.ratio_form_wins_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/old_scores_ratio_graphics_win.png'))
		self.window.ratio_form_lose_graphics.setPixmap(
			QPixmap(f'{self.dict_team_info["path_on_disc"]}/old_scores_ratio_graphics_lose.png'))
		self.window.info_label_wins_team_1_old_scores.setText(
			f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_1"]} было выигранно {len(self.dict_team_info["team_one_old_scores_win"])} игр</span></p></body></html>')
		self.window.info_label_wins_team_2_old_scores.setText(
			f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_2"]} было выигранно {len(self.dict_team_info["team_two_old_scores_win"])} игр</span></p></body></html>')
		self.window.info_label_loses_team_1_old_scores.setText(
			f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_1"]} было проигранно {len(self.dict_team_info["team_one_old_scores_lose"])} игр</span></p></body></html>')
		self.window.info_label_loses_team_2_old_scores.setText(
			f'<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Командой {self.dict_team_info["name_2"]} было проигранно {len(self.dict_team_info["team_two_old_scores_lose"])} игр</span></p></body></html>')
		self.window.info_label_wins_team_1_old_scores.adjustSize()
		self.window.info_label_wins_team_2_old_scores.adjustSize()
		self.window.info_label_loses_team_1_old_scores.adjustSize()
		self.window.info_label_loses_team_2_old_scores.adjustSize()
