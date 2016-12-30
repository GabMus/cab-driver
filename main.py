#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf
import os
import sys
import detectHardware

EXEC_FOLDER = os.path.realpath(os.path.dirname(__file__)) + "/"
builder = Gtk.Builder()
builder.add_from_file(EXEC_FOLDER + "ui.glade")
HOME = os.environ.get('HOME')

# settings = Gtk.Settings.get_default()
# settings.set_property("gtk-application-prefer-dark-theme", True)

class App(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self,
								 application_id="org.gabmus.gcrawler",
								 flags=Gio.ApplicationFlags.FLAGS_NONE)
		self.connect("activate", self.activateCb)

	def do_startup(self):
		# start the application
		Gtk.Application.do_startup(self)

	def activateCb(self, app):
		window = builder.get_object("window")
		window.set_wmclass("Cab-Driver", "Cab-Driver")
		window.set_title("Cab-Driver")
		app.add_window(window)
		appMenu = Gio.Menu()
		appMenu.append("About", "app.about")
		appMenu.append("Quit", "app.quit")
		about_action = Gio.SimpleAction.new("about", None)
		about_action.connect("activate", self.on_about_activate)
		builder.get_object("aboutdialog").connect(
			"delete-event", lambda *_: builder.get_object("aboutdialog").hide() or True)
		app.add_action(about_action)
		quit_action = Gio.SimpleAction.new("quit", None)
		quit_action.connect("activate", self.on_quit_activate)
		app.add_action(quit_action)
		app.set_app_menu(appMenu)
		window.show_all()

	def on_about_activate(self, *agrs):
		builder.get_object("aboutdialog").show()

	def on_quit_activate(self, *args):
		self.quit()

app = App()

#dictionary for storing current config
current_config={
	'manualauto': '', # valid: 'manual', 'auto'
	'hybrid': '', #valid: 'no', 'intelnvidia', 'intelamd', 'amdnvidia', 'amdamd'
}

mainstack_special_pages = [ # page indexes where the next button should be locked waiting for user interaction
	1, # choose auto detect or manual config
]

special_pages_directions = {
	-3: -2,
	2: +2
}

IMG_PATH = EXEC_FOLDER+'/img/'
VENDOR_ICONS = {
	'NVIDIA Corporation': IMG_PATH+'nvidia-small.jpg',
	'Intel Corporation': IMG_PATH+'intel-small.jpg',
	# 'AMD WHATEVER': IMG_PATH+'amd-small.jpg'
}

main_stack = builder.get_object('mainStack')
main_stack_children = main_stack.get_children()

next_button = builder.get_object('nextButton')
back_button = builder.get_object('backButton')

detected_hw_label = builder.get_object('detectedHwLabel')
hardware_listbox = builder.get_object('hardwareListbox')

# fill static listboxes
# manual or auto configuration
manual_auto_config_listbox = builder.get_object('manualOrAutoChooseListbox')
moac_labels = [
	'Detect hardware automatically',
	'Select hardware manually'
]
moac_pics = [
	IMG_PATH+'search.svg',
	IMG_PATH+'touch.svg'
]
moac_values = [
	'auto',
	'manual'
]
for i in range(0,2):
	box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
	label = Gtk.Label()
	label.set_text(moac_labels[i])
	icon = Gtk.Image()
	icon.set_from_file(moac_pics[i])
	label.set_margin_left(12)
	label.set_margin_right(12)
	box.pack_start(icon, False, False, 0)
	box.pack_start(label, False, False, 0)
	row = Gtk.ListBoxRow()
	row.add(box)
	row.value = moac_values[i]
	manual_auto_config_listbox.add(row)
manual_auto_config_listbox.show_all()

class Handler:

	def onDeleteWindow(self, *args):
		app.quit()

	def _move_stack(self, direction):
		current_child_index = main_stack_children.index(
			main_stack.get_visible_child()
		)
		main_stack.set_visible_child(
			main_stack_children[current_child_index+direction]
		)

		if current_child_index+direction >= len(main_stack_children)-1:
			next_button.set_sensitive(False)
			back_button.set_sensitive(True)
		elif current_child_index+direction <= 0:
			next_button.set_sensitive(True)
			back_button.set_sensitive(False)
		else:
			next_button.set_sensitive(True)
			back_button.set_sensitive(True)
		if current_child_index + direction in mainstack_special_pages:
			next_button.set_sensitive(False)

	def on_nextButton_clicked(self, button):
		current_child_index = main_stack_children.index(
			main_stack.get_visible_child()
		)
		if current_child_index in special_pages_directions:
			self._move_stack(special_pages_directions[current_child_index])
		else:
			self._move_stack(1)

	def on_backButton_clicked(self, button):
		current_child_index = -1 * (main_stack_children.index(
			main_stack.get_visible_child()
		))
		if current_child_index in special_pages_directions.keys():
			self._move_stack(special_pages_directions[current_child_index])
		else:
			self._move_stack(-1)

	def on_detectHwButton_clicked(self, button):
		hw_l = detectHardware.get_relevant_info()
		# empty hardware list before filling
		while True:
			row = hardware_listbox.get_row_at_index(0)
			if row:
				hardware_listbox.remove(row)
			else:
				break
		# fill hardware list
		hardware_listbox.show()
		for i in hw_l:
			box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
			label = Gtk.Label()
			label.set_text(i[0]+' '+i[1]) #set text to hw
			icon = Gtk.Image()
			icon.set_from_file(VENDOR_ICONS[i[0]])
			label.set_margin_left(12)
			label.set_margin_right(12)
			box.pack_start(icon, False, False, 0)
			box.pack_start(label, False, False, 0)
			row = Gtk.ListBoxRow()
			row.add(box)
			hardware_listbox.add(row)
			row.show_all()
		#detected_hw_label.set_text(hw_str)

	def on_manualOrAutoChooseListbox_row_selected(self, list, row):
		current_config['manualauto']=row.value
		if row.value == 'manual':
			self._move_stack(1)
		else:
			self._move_stack(2)
		# next_button.set_sensitive(True)


builder.connect_signals(Handler())


if __name__ == "__main__":
	app.run(sys.argv)
