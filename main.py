#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf
import os
import sys
import detectHardware
import driverMatcher
import listboxHelper

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
	3, # autodetect page, need to press autodetect button
]

special_pages_directions = {
	-3: -2, # coming back from auto config, to choose manual or auto config
	2: +2 # next from manual config, to packages needed page
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

needed_packages_label = builder.get_object('neededPackagesLabel')

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
	row=listboxHelper.make_image_row(moac_labels[i], moac_pics[i])
	row.value = moac_values[i]
	manual_auto_config_listbox.add(row)
manual_auto_config_listbox.show_all()

# fill manual distro popover listbox
manual_distro_button = builder.get_object('manualChooseDistroButton')
manual_distro_listbox = builder.get_object('manualChooseDistroPopoverListbox')
manual_distro_label = builder.get_object('manualDistroLabel')
manual_distro_icon = builder.get_object('manualDistroIcon')
for d in driverMatcher.DISTROS:
	row=listboxHelper.make_image_row(d.capitalize(), IMG_PATH+'/'+d+'.png')
	manual_distro_listbox.add(row)
	row.show_all()
manual_distro_listbox.show_all()
manual_distro_listbox.select_row(None)
manual_distro_popover = builder.get_object('manualChooseDistroPopover')

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

		# add distro row
		distro_row=listboxHelper.make_image_row(
			driverMatcher.get_distro().capitalize(),
			IMG_PATH+'/'+driverMatcher.get_distro()+'.png')
		hardware_listbox.add(distro_row)
		distro_row.show_all()

		hardware_listbox.show()
		for i in hw_l:
			row=listboxHelper.make_image_row(i[0]+' '+i[1], VENDOR_ICONS[i[0]])
			hardware_listbox.add(row)
			row.show_all()

		builder.get_object('autoDetectWrongMaybeLabel').show()
		next_button.set_sensitive(True)
		needed_packages_label.set_text(' '.join(driverMatcher.get_packages(hw_l)))

	def on_manualOrAutoChooseListbox_row_selected(self, list, row):
		if row.value:
			current_config['manualauto']=row.value
		if row.value == 'manual':
			self._move_stack(1)
		else:
			self._move_stack(2)
		# next_button.set_sensitive(True)

	def on_manualChooseDistroPopoverListbox_row_selected(self, list, row):
		manual_distro_popover.hide()
		manual_distro_label.set_text(row.value.capitalize())
		manual_distro_icon.set_from_file(IMG_PATH+'/'+row.value+'.png')

	def on_manualChooseDistroButton_clicked(self, button):
		if not manual_distro_popover.get_visible():
			manual_distro_popover.show()

	#def on_GPU1SearchEntry_changed(self, *args):
	#	builder.get_object('GPUEntrycompletion').complete()
	#	print('dicks')

builder.connect_signals(Handler())


if __name__ == "__main__":
	app.run(sys.argv)
